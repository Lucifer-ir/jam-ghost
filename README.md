# JAM GHOST

**Private by design. Peer-to-peer by architecture.**

JAM GHOST is an experimental, open-source private messaging project. The first release establishes a local Android/Termux launcher and browser interface.

> **Version 0.1 is not a working messenger yet.** It does not connect peers, send messages, generate pairing QR codes, or provide end-to-end encrypted chat. Those are planned milestones.

## v0.1 features

- Termux installer and `jam-ghost` command
- Local-only web interface at `http://127.0.0.1:8765`
- Mobile-responsive interface
- Local browser preference for message-history mode
- QR and invite-code flows shown as roadmap previews
- Python standard library only; no third-party Python packages

## Install on Android / Termux

```bash
pkg update
pkg install python git
git clone https://github.com/Lucifer-ir/jam-ghost.git
cd jam-ghost
bash install.sh
jam-ghost
```

Optional: install **Termux:API** to let the launcher open the browser automatically. If it is unavailable, open the printed URL manually.

Stop the local interface with `Ctrl+C`.

## Uninstall

From the cloned repository:

```bash
bash uninstall.sh
```

This removes the installed application and launcher. It does not remove the cloned source repository.

## Technical architecture

### v0.1 — Local shell

- Termux runs a Python `ThreadingHTTPServer`.
- The server binds only to `127.0.0.1`; it is not exposed to the LAN or public internet.
- The browser loads static HTML/CSS/JS.
- No account, remote API, VPS, database, or message relay is used.

### Planned milestones

**v0.2 — Pairing**
- WebRTC offer/answer exchange through QR.
- Text invitation fallback.
- Wait for ICE gathering to complete before encoding the SDP.
- Add payload compression and multi-part QR handling if required.

**v0.3 — Peer transport and identity**
- WebRTC DataChannel for direct transport.
- DTLS transport encryption.
- Device identity keypair plus ephemeral session keypair.
- Show a short authentication string / key fingerprint and require out-of-band verification.
- Add an explicit connection state and clear disconnect action.

**v0.4 — Message history**
- User choice: memory-only or encrypted local history.
- Do not persist plaintext messages.
- Use Web Crypto APIs and a reviewed key-derivation/encryption design before claiming encrypted-at-rest storage.

**v1.0 — Security review and release**
- Threat model, independent review, tests across Android devices and carrier/Wi-Fi networks.
- Document network metadata and limitations.

## Important networking limitations

Manual QR exchange removes the need for a central signaling server, but it does not guarantee a direct connection across every network. STUN can help peers discover NAT mappings; it does not carry chat messages. Some restrictive NAT/CGNAT combinations require TURN relay, which needs a server and should be an explicit opt-in. A strict direct-only mode may fail to connect on some networks.

WebRTC's DTLS protects the data channel in transit, but encryption alone does not prove who the peer is. Users must verify the peer identity fingerprint / short authentication string to reduce man-in-the-middle risk.

## Security status

Do not use v0.1 for sensitive communication. The current release is a local UI shell only. No cryptographic security claim is made.

## Project structure

```text
jam-ghost/
├── install.sh
├── uninstall.sh
├── core/
│   └── server.py
├── web/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── README.md
```

## License

MIT — see `LICENSE`.
