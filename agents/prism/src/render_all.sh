#!/usr/bin/env bash
# crash-tolerant full render: resume-aware chunks + retry loop
set -uo pipefail
cd "$(dirname "$0")"
for attempt in $(seq 1 40); do
  echo "[render_all] attempt $attempt"
  pkill -9 -f "puppeteer_dev_chrome_profil[e]" 2>/dev/null || true
  if node render.mjs --from 0 --to 749 --chunk 10 --out /opt/prismframes/ > /tmp/render_attempt_$attempt.log 2>&1; then
    n=$(ls /opt/prismframes | wc -l)
    if [ "$n" = "750" ]; then echo "[render_all] COMPLETE 750/750 on attempt $attempt"; exit 0; fi
  fi
  n=$(ls /opt/prismframes 2>/dev/null | wc -l)
  echo "[render_all] attempt $attempt ended with $n/750"
  [ "$n" = "750" ] && { echo "[render_all] COMPLETE 750/750"; exit 0; }
done
echo "[render_all] FAILED after 40 attempts"; exit 1
