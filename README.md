# JAM GHOST

**Private by design. Peer-to-peer by architecture.**

JAM GHOST is an experimental peer-to-peer chat for Android/Termux. The Python process only serves the local web interface. Chat messages travel directly between browsers over a WebRTC DataChannel.

## v0.2 features

- English and Persian interface with RTL layout.
- Manual WebRTC offer/answer exchange using QR codes or copied invitation text.
- QR scanning through the device camera.
- Direct text messaging over a WebRTC DataChannel.
- DTLS transport encryption supplied by WebRTC.
- Short safety code derived from both peers' DTLS SHA-256 fingerprints. Compare it out-of-band before enabling chat.
- Local UI server bound only to 127.0.0.1.
- Messages are memory-only; they are not persisted in this release.

## Install on Android / Termux

```bash
pkg update
pkg install python git
git clone https://github.com/Lucifer-ir/jam-ghost.git
cd jam-ghost
bash install.sh
jam-ghost
```

Open the printed URL if the browser does not launch. Use a current Android browser and allow camera access for QR scanning. QR generation, QR scanning, and the Vazirmatn Persian font are bundled locally and do not need a CDN or internet connection after installation. The installer converts the bundled base64 font into WOFF2. Internet is still needed for WebRTC connectivity and STUN.

## Pairing

1. Device A selects **Create connection** and displays an offer QR/text.
2. Device B selects **Join with invite**, scans or pastes the offer, and displays an answer QR/text.
3. Device A scans or pastes the answer.
4. After WebRTC connects, both devices display the same safety code.
5. Compare the codes over a separate trusted channel or in person. If they match, both users can approve and chat.

There is no central signaling service or message relay. Manual QR/text exchange is the signaling mechanism.

## Network and privacy limitations

- A public STUN service (stun.l.google.com:19302) helps discover direct routes. The STUN provider may observe public IP addresses and connection metadata.
- No TURN relay is configured. Carrier NAT/CGNAT, firewalls, or restrictive networks may prevent a direct connection. This release will fail rather than silently relay messages.
- QR scanning requires camera permission and a secure context. Android browsers generally treat localhost as secure.
- QR generation and scanning libraries are bundled under `web/assets/`; no CDN is used for QR.
- WebRTC encrypts transport with DTLS. The short safety code is a basic out-of-band fingerprint comparison, not an audited identity/key-management system.
- The Python process serves static files only. It does not receive or forward chat messages.
- Chat content exists in browser memory and disappears when the page is closed or refreshed. The history selector is informational only in this version.

## Bundled third-party assets

- Vazirmatn font — SIL Open Font License 1.1 (`web/assets/Vazirmatn-OFL.txt`).
- QRCode.js — MIT (`web/assets/QRCode-MIT-LICENSE.txt`).
- jsQR — Apache License 2.0 (`web/assets/jsQR-APACHE-LICENSE.txt`).

## Security status

Experimental software; no independent security audit has been performed. Do not use for high-risk, life-critical, or highly sensitive communication. Review the code and threat model before relying on it.

## Uninstall

```bash
bash uninstall.sh
```

## License

MIT — see [LICENSE](LICENSE).
