#!/usr/bin/env python3
"""JAM GHOST local UI server. It never relays peer messages."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse, os, threading, webbrowser
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
class GhostHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(WEB_DIR), **kwargs)
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(self), microphone=(), geolocation=()")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' https://cdn.jsdelivr.net; connect-src 'self'; media-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()
    def log_message(self, fmt, *args): return
def main():
    p=argparse.ArgumentParser(description="Start the JAM GHOST local interface")
    p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8765); p.add_argument("--no-open", action="store_true")
    a=p.parse_args()
    if a.host not in ("127.0.0.1", "localhost", "::1"): p.error("For safety, JAM GHOST only supports loopback binding.")
    server=ThreadingHTTPServer((a.host,a.port), GhostHandler); url=f"http://127.0.0.1:{a.port}"
    print("\n  JAM GHOST // v0.2\n  Local interface: "+url+"\n  This server only hosts the UI; messages use direct WebRTC.\n  Ctrl+C to stop.\n")
    if not a.no_open:
        def open_browser():
            opener=os.environ.get("PREFIX", "")+"/bin/termux-open-url"
            if Path(opener).exists(): os.system(f'"{opener}" "{url}" >/dev/null 2>&1')
            else:
                try: webbrowser.open(url)
                except Exception: pass
        threading.Timer(.8, open_browser).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print("\n[+] Shutting down JAM GHOST.")
    finally: server.server_close()
if __name__=="__main__": main()
