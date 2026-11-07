#!/usr/bin/env python3
"""JAM GHOST web UI and short-lived WebRTC signaling API.

The API only exchanges connection setup data (SDP offer/answer). Chat payloads
remain on the peer-to-peer WebRTC DataChannel and are never handled here.
Run behind HTTPS for public internet use; bind this process to loopback and
reverse-proxy both the UI and /api/ to the same origin.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import hmac
import json
import os
import secrets
import threading
import time
import webbrowser

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
ROOM_TTL = 600
MAX_BODY = 65536
ROOMS = {}
LOCK = threading.RLock()


def _cleanup():
    now = time.time()
    expired = [key for key, room in ROOMS.items() if room["expires"] <= now]
    for key in expired:
        ROOMS.pop(key, None)


def _token_matches(supplied, expected):
    return isinstance(supplied, str) and hmac.compare_digest(supplied, expected)


class GhostHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(self), microphone=(), geolocation=()")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; media-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()

    def log_message(self, fmt, *args):
        # Do not log request URLs: authorization data must never enter access logs.
        return

    def _json(self, status, payload):
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _body(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("Invalid content length")
        if length < 0 or length > MAX_BODY:
            raise ValueError("Request body too large")
        raw = self.rfile.read(length)
        value = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(value, dict):
            raise ValueError("JSON object required")
        return value

    def _room(self, room_id):
        _cleanup()
        room = ROOMS.get(room_id)
        if not room:
            self._json(404, {"error": "room_not_found_or_expired"})
            return None
        return room

    def _owner(self, room):
        if not _token_matches(self.headers.get("X-JG-Owner"), room["owner_token"]):
            self._json(403, {"error": "forbidden"})
            return False
        return True

    def _peer(self, room, request):
        if not _token_matches(self.headers.get("X-JG-Peer"), request["peer_token"]):
            self._json(403, {"error": "forbidden"})
            return False
        return True

    def do_GET(self):
        path = urlsplit(self.path).path.rstrip("/") or "/"
        parts = path.split("/")
        if len(parts) >= 4 and parts[1] == "api" and parts[2] == "rooms":
            room_id = parts[3]
            with LOCK:
                room = self._room(room_id)
                if room is None:
                    return
                if len(parts) == 5 and parts[4] == "requests":
                    if not self._owner(room):
                        return
                    pending = [
                        {"requestId": rid, "label": req["label"], "createdAt": req["created"]}
                        for rid, req in room["requests"].items()
                        if req["state"] == "pending"
                    ]
                    self._json(200, {"requests": pending, "expiresAt": room["expires"]})
                    return
                if len(parts) == 6 and parts[4] == "requests":
                    request = room["requests"].get(parts[5])
                    if not request:
                        self._json(404, {"error": "request_not_found"})
                        return
                    if not self._peer(room, request):
                        return
                    result = {"state": request["state"]}
                    if request["state"] == "approved":
                        result["offer"] = room.get("offer")
                    self._json(200, result)
                    return
                if len(parts) == 5 and parts[4] == "answer":
                    if not self._owner(room):
                        return
                    approved = next((r for r in room["requests"].values() if r["state"] == "approved"), None)
                    if not approved:
                        self._json(200, {"state": "waiting"})
                    elif room.get("answer"):
                        self._json(200, {"state": "ready", "answer": room["answer"]})
                    else:
                        self._json(200, {"state": "waiting"})
                    return
        self.send_error(404)

    def do_POST(self):
        path = urlsplit(self.path).path.rstrip("/") or "/"
        parts = path.split("/")
        try:
            body = self._body()
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})
            return

        if path == "/api/rooms":
            with LOCK:
                _cleanup()
                if len(ROOMS) >= 1000:
                    self._json(503, {"error": "signaling_capacity_reached"})
                    return
                room_id = secrets.token_urlsafe(18)
                owner_token = secrets.token_urlsafe(32)
                invite_token = secrets.token_urlsafe(24)
                ROOMS[room_id] = {
                    "owner_token": owner_token,
                    "invite_token": invite_token,
                    "offer": None,
                    "answer": None,
                    "requests": {},
                    "expires": time.time() + ROOM_TTL,
                }
                self._json(201, {"roomId": room_id, "ownerToken": owner_token, "inviteToken": invite_token, "expiresIn": ROOM_TTL})
            return

        if len(parts) >= 4 and parts[1] == "api" and parts[2] == "rooms":
            room_id = parts[3]
            with LOCK:
                room = self._room(room_id)
                if room is None:
                    return
                if len(parts) == 5 and parts[4] == "offer":
                    if not self._owner(room):
                        return
                    offer = body.get("sdp")
                    if not isinstance(offer, str) or len(offer) > 48000:
                        self._json(400, {"error": "invalid_offer"})
                        return
                    room["offer"] = offer
                    self._json(200, {"ok": True})
                    return
                if len(parts) == 5 and parts[4] == "requests":
                    if not _token_matches(body.get("inviteToken"), room["invite_token"]):
                        self._json(403, {"error": "invalid_invitation"})
                        return
                    if not room.get("offer"):
                        self._json(409, {"error": "host_not_ready"})
                        return
                    if len(room["requests"]) >= 8:
                        self._json(429, {"error": "request_limit_reached"})
                        return
                    if any(req["state"] in ("pending", "approved") for req in room["requests"].values()):
                        self._json(409, {"error": "room_already_has_active_request"})
                        return
                    request_id = secrets.token_urlsafe(12)
                    peer_token = secrets.token_urlsafe(32)
                    room["requests"][request_id] = {
                        "peer_token": peer_token,
                        "state": "pending",
                        "created": int(time.time()),
                        "label": "Guest",
                    }
                    self._json(201, {"requestId": request_id, "peerToken": peer_token})
                    return
                if len(parts) == 7 and parts[4] == "requests" and parts[6] == "decision":
                    if not self._owner(room):
                        return
                    request = room["requests"].get(parts[5])
                    if not request or request["state"] != "pending":
                        self._json(409, {"error": "request_not_pending"})
                        return
                    approved = body.get("approve") is True
                    request["state"] = "approved" if approved else "rejected"
                    self._json(200, {"state": request["state"]})
                    return
                if len(parts) == 5 and parts[4] == "answer":
                    approved = next((r for r in room["requests"].values() if r["state"] == "approved"), None)
                    if not approved or not self._peer(room, approved):
                        if approved is None:
                            self._json(409, {"error": "request_not_approved"})
                        return
                    answer = body.get("sdp")
                    if not isinstance(answer, str) or len(answer) > 48000:
                        self._json(400, {"error": "invalid_answer"})
                        return
                    room["answer"] = answer
                    self._json(200, {"ok": True})
                    return
                if len(parts) == 5 and parts[4] == "close":
                    if not self._owner(room):
                        return
                    ROOMS.pop(room_id, None)
                    self._json(200, {"ok": True})
                    return
        self.send_error(404)


def main():
    parser = argparse.ArgumentParser(description="Start the JAM GHOST UI and signaling service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        parser.error("Bind to loopback and expose the service through an HTTPS reverse proxy.")
    server = ThreadingHTTPServer((args.host, args.port), GhostHandler)
    url = f"http://127.0.0.1:{args.port}"
    print("\n  JAM GHOST // signaling enabled\n  Local interface: " + url +
          "\n  Signaling exchanges SDP only; chat remains peer-to-peer.\n  Ctrl+C to stop.\n")
    if not args.no_open:
        def open_browser():
            opener = os.environ.get("PREFIX", "") + "/bin/termux-open-url"
            if Path(opener).exists():
                os.system(f'"{opener}" "{url}" >/dev/null 2>&1')
            else:
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
        threading.Timer(0.8, open_browser).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[+] Shutting down JAM GHOST.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
