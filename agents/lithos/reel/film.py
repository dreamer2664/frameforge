#!/usr/bin/env python3
"""reel.film - render_frame(t) -> RGB uint8 (1920, 1080, 3) for the reel."""
import numpy as np
import acts
import stage


def screen_frame(t):
    """Screen content for instant t (flat 1536x960 RGB)."""
    if t < 1.55:
        return acts.act_dot(t)
    if t < 4.35:
        return acts.act_type(t)
    if t < 5.20:
        return acts.act_shape(t)
    if t < 5.60:
        return acts.act_pattern(t)
    if t < 6.00:
        return acts.act_smear(t)
    if t < 8.00:
        return acts.act_particle(t)
    if t < 10.00:
        return acts.act_organic(t)
    if t < 11.20:
        return acts.act_data(t)
    if t < 11.55:
        return acts.act_defocus(t)
    if t < 11.95:
        return acts.act_montage(t)
    return acts.act_end(t)


class _S:
    st = None


def render_frame(t):
    if _S.st is None:
        _S.st = stage.Stage()
    return _S.st.frame(t, screen_frame(t))
