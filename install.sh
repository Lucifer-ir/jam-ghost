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
cp -R "$SCRIPT_DIR/core" "$APP_DIR/"
cp -R "$SCRIPT_DIR/web" "$APP_DIR/"
cp "$SCRIPT_DIR/README.md" "$APP_DIR/"

cat > "$BIN_DIR/jam-ghost" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
exec python "$APP_DIR/core/server.py" "\$@"
EOF
chmod +x "$BIN_DIR/jam-ghost"

echo "[+] Installed to: $APP_DIR"
echo "[+] Command: jam-ghost"
echo
echo "If the command is not found, restart Termux or run:"
echo '  export PATH="$PREFIX/bin:$PATH"'
echo
echo "Run: jam-ghost"
