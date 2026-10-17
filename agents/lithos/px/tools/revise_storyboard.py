#!/usr/bin/env python3
"""Revision 1 — whole-cut rhythm.

The film's pacing curve is re-shaped: the establishing hall and the carved-wall
reveal arrive earlier and faster, the release/gate middle is tightened, and the
arrival at the monument is given the time it needs to become the final image.

A single piecewise-linear time map is applied to every timed element of the
storyboard (camera keys, key/fill light keys, fog keys, copy windows and the
stage times), so picture and score stay in step.  The old times are kept in
`revision_log` so the change is auditable.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SB = HERE / "storyboard.json"

ANCHORS = [(0.0, 0.0), (6.0, 4.2), (15.0, 12.2), (22.4, 19.4), (29.4, 26.4), (40.0, 40.0)]


def remap(t):
    if t <= ANCHORS[0][0]:
        return ANCHORS[0][1]
    for (t0, n0), (t1, n1) in zip(ANCHORS, ANCHORS[1:]):
        if t <= t1:
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return n0 + u * (n1 - n0)
    return ANCHORS[-1][1]


def main():
    st = json.loads(SB.read_text())
    log = {"revision": 1, "name": "whole-cut rhythm", "anchors": ANCHORS, "changed": []}

    for key in st["camera"]["keys"]:
        old = key["t"]
        key["t"] = round(remap(old), 3)
        log["changed"].append({"what": "camera", "old_t": old, "new_t": key["t"]})
    for name in ("key", "fill"):
        for key in st["lights"][name]["keys"]:
            old = key["t"]
            key["t"] = round(remap(old), 3)
            log["changed"].append({"what": f"light.{name}", "old_t": old, "new_t": key["t"]})
    for key in st["fog"]["keys"]:
        old = key["t"]
        key["t"] = round(remap(old), 3)
        log["changed"].append({"what": "fog", "old_t": old, "new_t": key["t"]})
    for c in st["copy"]:
        old_in, old_out = c["t_in"], c["t_out"]
        c["t_in"] = round(remap(old_in), 3)
        c["t_out"] = round(remap(old_out), 3)
        log["changed"].append({"what": f"copy:{c['text']}", "old_t": old_in, "new_t": c["t_in"],
                               "old_out": old_out, "new_out": c["t_out"]})

    stages = st["stages"]
    old_stages = dict(stages)
    for k in ("release", "field", "assemble", "gate", "fly", "row"):
        stages[k] = round(remap(stages[k]), 3)
    log["stages_before"] = old_stages
    log["stages_after"] = dict(stages)

    # --- the gate approach: converge on the gate's centre line before the crossing,
    #     so the camera never passes within arm's reach of a letter.
    for key in st["camera"]["keys"]:
        if abs(key["t"] - 20.0) < 0.05:
            key["eye"] = [-1.0, 1.95, 3.0]
            key["target"] = [-2.6, 2.6, -3.4]
            log.setdefault("gate_path", []).append({"t": key["t"], "eye": key["eye"]})
        if abs(key["t"] - 23.2) < 0.05:
            key["eye"] = [-3.8, 1.90, 0.2]
            key["target"] = [-4.4, 3.2, -4.2]
            log.setdefault("gate_path", []).append({"t": key["t"], "eye": key["eye"]})

    # --- material values for revision 2 (the wall must read as stone, not a void)
    st["palette"]["wall"] = [0.105, 0.098, 0.088]
    st["palette"]["letter"] = [0.300, 0.278, 0.246]
    st["palette"]["plinth"] = [0.088, 0.082, 0.074]

    # --- chamber geometry: a room, not a lit card
    st["world"]["chamber_z"] = -34.0
    st["world"]["chamber_x"] = 20.0
    st["world"]["chamber_h"] = 13.0

    st["revision_log"] = log
    SB.write_text(json.dumps(st, indent=2) + "\n")
    print("stages", old_stages, "->", stages)
    print("camera keys:")
    for key in st["camera"]["keys"]:
        print("  t=%6.2f eye=%s target=%s fov=%s" % (key["t"], key["eye"], key["target"], key["fov"]))
    print("copy:", [(c["text"], c["t_in"], c["t_out"]) for c in st["copy"]])


if __name__ == "__main__":
    main()
