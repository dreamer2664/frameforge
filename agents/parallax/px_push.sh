#!/bin/bash
# parallax collision-safe checkpoint push. Usage: px_push.sh
# Resolves rebase conflicts with the concurrent twin wake:
#   events.jsonl -> keep-both union (append-only journal)
#   HANDOFF.md   -> theirs (regenerated from merged events by field.py)
#   status/*.json-> ours (latest observation of this wake)
set -e
cd "$(git rev-parse --show-toplevel)"
set -a; . "$HOME/.private/parallax.env"; set +a
export GIT_ASKPASS="$HOME/.private/frameforge-askpass.sh" GIT_TERMINAL_PROMPT=0
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
  python3 - <<'PY'
import subprocess, sys
from pathlib import Path
def stage(n):
    return subprocess.run(['git','show',f':{n}:agents/parallax/events.jsonl'],capture_output=True,text=True).stdout.splitlines()
try:
    theirs, ours = stage(2), stage(3)
    seen=set(); union=[l for l in theirs+ours if l.strip() and not (l in seen or seen.add(l))]
    Path('agents/parallax/events.jsonl').write_text('\n'.join(union)+'\n')
    subprocess.run(['git','checkout','--theirs','agents/parallax/HANDOFF.md'],check=True)
    subprocess.run(['git','checkout','--ours','status/parallax.json'],check=True)
    subprocess.run(['git','add','agents/parallax/events.jsonl','agents/parallax/HANDOFF.md','status/parallax.json'],check=True)
    print('px_push: resolved keep-both union', len(union), 'events')
except Exception as e:
    print('px_push: resolver failed:', e); sys.exit(1)
PY
  GIT_EDITOR=true git rebase --continue
fi
git push origin HEAD:main
echo "px_push: ok $(git log --oneline -1)"
