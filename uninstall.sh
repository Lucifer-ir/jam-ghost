#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
APP_DIR="$HOME/.jam-ghost"
BIN_DIR="${PREFIX:-$HOME/.local}/bin"

rm -rf "$APP_DIR"
rm -f "$BIN_DIR/jam-ghost"
echo "[+] JAM GHOST application files and launcher removed."
echo "[i] This does not delete any future user chat backups."
