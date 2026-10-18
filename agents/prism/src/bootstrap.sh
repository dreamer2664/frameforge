#!/usr/bin/env bash
# PRISM environment bootstrap — idempotent. The sandbox resets /usr between
# sessions, so every render session starts here. Safe to re-run at any time.
# Installs: ffmpeg (encode/QC), Chrome shared libs (headless WebGL), npm deps.
set -euo pipefail
cd "$(dirname "$0")"   # this script lives in src/

log() { echo "[bootstrap] $*"; }

if ! command -v ffmpeg >/dev/null 2>&1; then
  log "installing ffmpeg"
  sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg
else
  log "ffmpeg present: $(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f3)"
fi

NEED="libnspr4.so libnss3.so libatk-1.0.so.0 libatk-bridge-2.0.so.0 libcups.so.2 libdrm.so.2 libxkbcommon.so.0 libXcomposite.so.1 libXdamage.so.1 libXfixes.so.3 libXrandr.so.2 libgbm.so.1 libasound.so.2 libpango-1.0.so.0 libcairo.so.2"
CHROME=$(ls -d "$HOME"/.cache/puppeteer/chrome/linux-*/chrome-linux64/chrome 2>/dev/null | head -1 || true)
if [ -z "$CHROME" ]; then log "chrome binary absent — npm install will fetch it"; fi
MISSING=0
if [ -n "$CHROME" ]; then
  for _ in $(ldd "$CHROME" 2>/dev/null | grep "not found" || true); do MISSING=1; done
fi
if [ "$MISSING" = "1" ] || [ -z "$CHROME" ]; then
  log "installing chrome shared libraries"
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    libnss3 libnspr4 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2t64 libpango-1.0-0 libcairo2 libxshmfence1 libatspi2.0-0t64
fi
if [ -n "$CHROME" ]; then
  N=$(ldd "$CHROME" 2>/dev/null | grep -c "not found" || true)
  log "chrome unresolved libs now: $N"
fi

if [ ! -d node_modules/three ] || [ ! -d node_modules/puppeteer ] || [ ! -d node_modules/esbuild ]; then
  log "installing npm deps (three, puppeteer, esbuild, fonts)"
  npm install --no-audit --no-fund \
    three@0.186.1 puppeteer@25.14.0 esbuild \
    @fontsource/archivo-black @fontsource/ibm-plex-mono
  mkdir -p film/fonts
  cp -f node_modules/@fontsource/archivo-black/files/archivo-black-latin-400-normal.woff2 film/fonts/ 2>/dev/null || true
  for w in 400 500 600 700; do
    cp -f node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-$w-normal.woff2 film/fonts/ 2>/dev/null || true
  done
else
  log "npm deps present"
fi

log "bundle rebuild"
npx esbuild film/page.js --bundle --format=iife --outfile=film/page.bundle.js \
  --loader:.woff2=dataurl --target=chrome120 --log-level=warning
log "OK"
