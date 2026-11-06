#!/usr/bin/env python3
"""JAM GHOST v0.1 - local web interface host.

This server only serves static UI files on loopback. It is not a chat relay.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse
import os
import threading
import webbrowser

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

class GhostHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; img-src 'self' data:; "
                         "style-src 'self'; script-src 'self'; "
                         "connect-src 'self'; object-src 'none'; "
                         "base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()

    def log_message(self, fmt, *args):
        # Keep terminal output quiet; request details are not needed in v0.1.
        return

def main():
    parser = argparse.ArgumentParser(description="Start the JAM GHOST local interface")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Bind address (default: 127.0.0.1; do not expose publicly)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true",
                        help="Do not ask Android to open the browser")
    args = parser.parse_args()

    if args.host not in ("127.0.0.1", "localhost", "::1"):
        parser.error("For safety, v0.1 only supports loopback binding.")

    server = ThreadingHTTPServer((args.host, args.port), GhostHandler)
    url = f"http://127.0.0.1:{args.port}"
    print()
    print("  ╭────────────────────────────────────╮")
    print("  │          J A M   G H O S T         │")
    print("  │              v0.1                 │")
    print("  ╰────────────────────────────────────╯")
    print(f"  Local interface: {url}")
    print("  This is a local UI host, not a messaging server.")
    print("  Press Ctrl+C to stop.")
    print()

    if not args.no_open:
        def open_browser():
            # Termux:API is optional. The URL is always printed as fallback.
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
