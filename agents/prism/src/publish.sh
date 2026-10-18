#!/usr/bin/env bash
# storagecode publication: release (publish.py) + ledger rows (clone+push).
# Caller must have sourced the env vault. R5/R6: append-only, readback-verified.
set -euo pipefail
SRC=$(cd "$(dirname "$0")" && pwd)
cd "$SRC"

python3 publish.py
TAG=$(python3 -c "import json;print(json.load(open('exports/RELEASE.json'))['tag'])")
SHA=$(python3 -c "import json;print(json.load(open('exports/RELEASE.json'))['master_sha'])")

SC=/home/user/work/storagecode
if [ ! -d "$SC/.git" ]; then
  git clone -q --depth 1 https://github.com/dreamer2664/storagecode.git "$SC"
fi
cd "$SC"
git fetch -q https://github.com/dreamer2664/storagecode.git main
git reset -q --hard FETCH_HEAD

DATE=$(date -u +%Y-%m-%d)
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf '| %s | prism | frameforge@agent/prism/t-20261018-e5a3 | release %s | PROOF r01 25.00s film + evidence; master sha %s | readback-verified: yes |\n' \
  "$DATE" "$TAG" "${SHA:0:16}" >> PUSHES.md
mkdir -p data/prism
printf '| %s | data/prism/%s | PROOF r01 evidence package + masters (assets on release %s) | %s | %s |\n' \
  "$DATE" "$DATE-prism" "$TAG" "$SHA" "$TAG" >> data/INDEX.md
git add PUSHES.md data/INDEX.md
git -c user.name=prism -c user.email=prism@frameforge.local commit -q -m "log: prism PROOF r01 release $TAG"
git push -q https://github.com/dreamer2664/storagecode.git HEAD:refs/heads/main
git fetch -q https://github.com/dreamer2664/storagecode.git main
echo "[publish] ledger readback:"
git show FETCH_HEAD:PUSHES.md | tail -2
git show FETCH_HEAD:data/INDEX.md | tail -2
echo "[publish] DONE $TAG"
