#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
APP_DIR="$HOME/.jam-ghost"
BIN_DIR="${PREFIX:-$HOME/.local}/bin"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo
echo "  JAM GHOST // Installer"
echo "  ----------------------"
if ! command -v python >/dev/null 2>&1; then
  echo "[!] Python is required. Install it with: pkg install python"
  exit 1
fi
mkdir -p "$APP_DIR" "$BIN_DIR"
rm -rf "$APP_DIR/core" "$APP_DIR/web"
cp -R "$SCRIPT_DIR/core" "$APP_DIR/"
cp -R "$SCRIPT_DIR/web" "$APP_DIR/"
cp "$SCRIPT_DIR/README.md" "$APP_DIR/"
if [ -f "$APP_DIR/web/assets/Vazirmatn.woff2.b64" ]; then
  base64 -d "$APP_DIR/web/assets/Vazirmatn.woff2.b64" > "$APP_DIR/web/assets/Vazirmatn.woff2"
  chmod 644 "$APP_DIR/web/assets/Vazirmatn.woff2"
else
  echo "[!] Persian font asset is missing."
  exit 1
fi
cat > "$BIN_DIR/jam-ghost" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
exec python "$APP_DIR/core/server.py" "\$@"
EOF
chmod +x "$BIN_DIR/jam-ghost"
echo "[+] Installed JAM GHOST with offline QR tools and Persian font."
echo "[+] Command: jam-ghost"
echo "Run: jam-ghost"
