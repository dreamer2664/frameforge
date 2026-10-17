#!/usr/bin/env python3
"""lithos journal — lane-restricted clone of ops/field.py's event schema.

Why this exists: ops/field.py's AGENTS tuple is frozen and predates this
producer. The laws say new code lives in agents/<name>/ only, so the frozen
ops tree is untouched; this tool emits the identical events.jsonl schema and
regenerates HANDOFF.md + status/lithos.json the same way.

Usage:
  python3 tools/journal.py event --kind K --stage S --state ST \
      --action A --result R --artifact P --next N
  python3 tools/journal.py publish          # git add agents/lithos status/lithos.json + commit/push hint
"""
import argparse, datetime as dt, json, os
from pathlib import Path

AGENT = "lithos"
ROOT = Path(__file__).resolve().parents[4]          # .../frameforge
HOME = ROOT / "agents" / AGENT


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def redact(value: str) -> str:
    text = str(value)
    for key in ("CHATCODE_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
        secret = os.environ.get(key)
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return text


def update_handoff(state):
    journal = HOME / "events.jsonl"
    records = [json.loads(l) for l in journal.read_text().splitlines() if l.strip()] if journal.exists() else []
    lines = [f"# {AGENT} — LIVE HANDOFF / ACTION RECORD", "",
             "> Public working memory. No token, cookie, password, auth header, private prompt or hidden chain-of-thought belongs here.", "",
             "## Resume here", "",
             f"- Updated: {state['updated_at']}",
             f"- State: **{state['state']}**",
             f"- Stage: {state['stage']}",
             f"- Last observed activity: {state['observed_activity']}",
             f"- Latest evidence/artifact: {state.get('artifact') or 'not supplied'}",
             f"- Next concrete action: {state.get('next_action') or 'see most recent action below'}",
             f"- Source: your own agents/{AGENT}/ tree; never wait for another producer.",
             "- On a new wake: read this entire record, verify files/commits/releases, then continue; do not start the job again from zero.", "",
             "## Every recorded action and discovery (append-only source = events.jsonl)", ""]
    for r in records:
        lines.extend([f"### {r['ts']} — {r['kind']}",
                      f"- Action: {r['action']}",
                      f"- Result/discovery: {r['result']}",
                      f"- Evidence: {r.get('artifact') or 'none yet'}",
                      f"- Next: {r.get('next_action') or 'continue current stage'}", ""])
    (HOME / "HANDOFF.md").write_text("\n".join(lines) + "\n")


def event(kind, action, result, stage, state, artifact, next_action):
    if state not in ("working", "process-running", "checkpoint", "blocked", "delivered", "stopped", "failed", "not-started"):
        raise SystemExit("invalid state")
    now = utc()
    r = {"ts": now, "kind": kind, "action": redact(action), "result": redact(result),
         "artifact": redact(artifact), "next_action": redact(next_action)}
    HOME.mkdir(parents=True, exist_ok=True)
    with (HOME / "events.jsonl").open("a") as f:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
    status = {"agent": AGENT, "updated_at": now, "state": state, "stage": redact(stage),
              "observed_activity": r["result"], "artifact": r["artifact"], "next_action": r["next_action"],
              "heartbeat_interval_seconds": 300,
              "note": "Fresh timestamp is evidence of this observation, NOT a promise that an AI session continues after it stops."}
    s = ROOT / "status"; s.mkdir(parents=True, exist_ok=True)
    (s / f"{AGENT}.json").write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n")
    update_handoff(status)
    print(json.dumps(status, indent=2))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("event")
    e.add_argument("--kind", default="action")
    e.add_argument("--stage", default="production")
    e.add_argument("--state", default="working")
    e.add_argument("--action", required=True)
    e.add_argument("--result", required=True)
    e.add_argument("--artifact", default="")
    e.add_argument("--next", default="")
    sub.add_parser("publish")
    a = ap.parse_args()
    if a.cmd == "event":
        event(a.kind, a.action, a.result, a.stage, a.state, a.artifact, a.next)
    else:
        print(f"stage exactly: git add -- agents/{AGENT} status/{AGENT}.json && git commit && git push")


if __name__ == "__main__":
    main()
