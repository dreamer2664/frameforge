#!/usr/bin/env bash
# Push my own tree to frameforge on branch agent/prism/<task-id>.
# No token in any URL/config: auth via the global credential helper that
# reads $GITHUB_TOKEN from the environment (sourced by the caller). R6:
# fetch first, branch from fresh main, verify by remote readback.
set -euo pipefail
TASK=${1:-t-20261018-e5a3}
FF=/home/user/work/frameforge
TREE=/home/user/work/frameforge/agents/prism
SRC=$(cd "$(dirname "$0")" && pwd)

cd "$FF"
git fetch -q https://github.com/dreamer2664/frameforge.git main
BASE=$(git rev-parse FETCH_HEAD)
echo "[push] base main = $BASE"
git checkout -q -B "agent/prism/$TASK" "$BASE"

# assemble my tree from the working source dir
mkdir -p agents/prism
rsync -a --delete \
  --exclude node_modules --exclude exports/master_video.mp4 \
  --exclude exports/master.mp4 --exclude exports/master_audio.wav \
  --exclude exports/dist_video.mp4 --exclude 'probe/out' --exclude styleframes \
  "$SRC/" agents/prism/src/
for f in README.md HANDOFF.md LICENSE RIGHTS.md THIRD_PARTY.md FAILED_ATTEMPTS.md SELF_REVIEW.md; do
  [ -f "$SRC/$f" ] && cp "$SRC/$f" agents/prism/
done
cat > status/prism.json <<JSON
{
  "agent": "prism",
  "task": "$TASK",
  "status": "review",
  "updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "env": "B",
  "release": "$(python3 -c "import json;print(json.load(open('$SRC/exports/RELEASE.json'))['tag'])" 2>/dev/null || echo pending)",
  "note": "PROOF 25.00s three.js film delivered; independent acceptance pending"
}
JSON

git add -A agents/prism status/prism.json
git -c user.name=prism -c user.email=prism@frameforge.local commit -q -m "prism: PROOF r01 — 25.00s three.js motion film + evidence package ($TASK)"
SHA=$(git rev-parse HEAD)
echo "[push] commit $SHA"
git push -q "https://github.com/dreamer2664/frameforge.git" "HEAD:refs/heads/agent/prism/$TASK"
echo "[push] pushed; verifying remote readback"
git fetch -q "https://github.com/dreamer2664/frameforge.git" "refs/heads/agent/prism/$TASK"
RB=$(git rev-parse FETCH_HEAD)
echo "[push] remote head = $RB"
[ "$RB" = "$SHA" ] && echo "[push] READBACK OK" || { echo "[push] READBACK MISMATCH"; exit 1; }
