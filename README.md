# JAM GHOST

**Private by design. Peer-to-peer by architecture.**

JAM GHOST is an experimental peer-to-peer chat. The Python process serves the local web interface and a short-lived signaling API. The signaling API exchanges only WebRTC setup data (SDP offer/answer) and connection requests. Chat messages travel directly between browsers over a WebRTC DataChannel and are never relayed by the JAM GHOST server.

## Features

- English and Persian interface with RTL layout and bundled Vazirmatn font.
- One-way QR invitation: the guest scans once and sends a join request.
- Host receives incoming requests through 2-second polling and explicitly approves or rejects them.
- WebRTC offer/answer exchange happens automatically after approval; no answer QR round-trip.
- Direct text messaging over a WebRTC DataChannel.
- DTLS transport encryption supplied by WebRTC and an out-of-band safety-code comparison.
- Short-lived in-memory rooms and requests (10-minute invitation expiry).
- Chat messages are memory-only and are not persisted.

## Pairing flow

1. Device A creates a room. JAM GHOST generates an invitation QR containing a random room ID and a high-entropy invitation token.
2. Device B scans the QR once and posts a join request to the signaling API.
3. Device A polls for requests every two seconds and displays Approve / Reject controls.
4. If approved, Device B receives the WebRTC offer, creates an answer, and submits it to the signaling API.
5. Device A polls for the answer and completes the WebRTC handshake.
6. Both devices compare the safety code out-of-band and explicitly enable chat.

The signaling service never receives chat messages. It temporarily holds room metadata and SDP connection descriptions only. Rooms are held in process memory and disappear on server restart or expiry.

## Run locally

Requires Python 3.9+ (standard library only).

```bash
git clone https://github.com/Lucifer-ir/jam-ghost.git
cd jam-ghost
python core/server.py
```

Open http://127.0.0.1:8765. Camera QR scanning works on localhost in modern browsers. You can also paste the invitation text.

On Windows PowerShell:

```powershell
python core/server.py
```

## Public internet deployment

For users on different networks, both browsers must reach the same signaling origin. Deploy the Python service on a public server and put it behind an HTTPS reverse proxy (for example Nginx with a valid TLS certificate). Keep the Python service bound to loopback; do not expose its port directly.

Example service command:

```bash
python3 core/server.py --host 127.0.0.1 --port 8765 --no-open
```

The reverse proxy must forward normal web requests and `/api/` requests to the same Python process and preserve request headers, including `X-JG-Owner` and `X-JG-Peer`. Serve the app at the HTTPS origin so browser camera permissions and secure-context APIs work.

Example Nginx location (inside the HTTPS server block):

```nginx
location / {
    proxy_pass http://127.0.0.1:8765;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Do not enable public internet access by changing the Python bind address to 0.0.0.0. Terminate TLS at the reverse proxy and firewall the Python port.

## Important deployment limitations

- This initial signaling implementation uses in-memory state in one Python process. Do not run multiple workers or multiple replicas: each process would have a different room registry. A production multi-instance deployment needs shared storage (for example Redis) and atomic state transitions.
- Rooms expire after 10 minutes and are lost on process restart.
- This prototype does not yet include durable rate limiting, abuse reporting, monitoring, or a hardened production security review. Put reasonable network-level rate limits in front of the API before public launch.
- The service must be served over HTTPS for public use. The included Python server is not an HTTPS server.
- STUN helps discover direct routes. No TURN relay is configured, so some carrier NATs, restrictive firewalls, or networks may prevent peer-to-peer connectivity. A TURN relay can improve connectivity but would relay encrypted WebRTC traffic.
- The signaling provider can observe public IP addresses, request timing, room identifiers, and SDP metadata. WebRTC DTLS encrypts the peer transport, but the safety code is a basic out-of-band fingerprint check, not an audited identity or key-management system.
- Experimental software; no independent security audit has been performed. Do not use for high-risk, life-critical, or highly sensitive communication.

## Bundled third-party assets

- Vazirmatn font — SIL Open Font License 1.1 (`web/assets/Vazirmatn-OFL.txt`).
- QRCode.js — MIT License.
- jsQR — Apache License 2.0.

## License

MIT — see [LICENSE](LICENSE).
