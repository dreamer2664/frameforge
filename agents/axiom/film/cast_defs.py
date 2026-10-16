#!/usr/bin/env python3
"""axiom cast definitions — the recurring, story-specific characters of this film.

Costume/identity cues are deliberately readable: an archbishop's band and 17th-century
hair for Ussher, plain-coat Scottish field geologists for Hutton/Playfair, a Victorian
beard and frock coat for Kelvin, the period laboratory aprons for Boltwood and Patterson.
These are respectful original caricatures built from documented period dress, not
likenesses; jewellery, decoration and props are all original drawings.
"""
from __future__ import annotations

from film.cast import Character

DARK_COAT = (52, 52, 64)
LECTURE_COAT = (58, 62, 78)
HODEN = (96, 84, 66)

CURATOR = Character(name="Curator", hair="auburn", hair_style="bob", head="oval",
                    shirt=(96, 108, 122), trousers=(58, 62, 74), shoes=(46, 48, 56),
                    extras=("coat",), kind="adult")

USSHER = Character(name="Ussher", hair="grey", hair_style="wig17", head="tall",
                   shirt=(44, 42, 54), trousers=(52, 48, 46), shoes=(38, 36, 40),
                   extras=("coat", "cravat", "beard"), kind="elder")

HUTTON = Character(name="Hutton", hair="sand", hair_style="swept", head="wide",
                   shirt=(72, 84, 62), trousers=(84, 74, 58), shoes=(52, 44, 36),
                   extras=("coat", "cravat"), kind="elder")

PLAYFAIR = Character(name="Playfair", hair="brown", hair_style="short", head="oval",
                     shirt=(64, 84, 112), trousers=(66, 60, 52), shoes=(48, 44, 40),
                     extras=("coat", "cravat"), kind="adult")

HALL = Character(name="Hall", hair="auburn", hair_style="curly", head="round",
                 shirt=(122, 96, 70), trousers=(76, 68, 56), shoes=(50, 46, 40),
                 extras=("coat",), kind="adult")

KELVIN = Character(name="Kelvin", hair="grey", hair_style="wig19", head="square",
                   shirt=(50, 54, 70), trousers=(44, 46, 56), shoes=(38, 38, 44),
                   extras=("coat", "tie", "beard", "moustache"), kind="elder")

PERRY = Character(name="Perry", hair="brown", hair_style="short", head="wide",
                  shirt=(88, 96, 108), trousers=(56, 58, 64), shoes=(44, 44, 48),
                  extras=("tie", "moustache", "glasses"), kind="adult")

RUTHERFORD = Character(name="Rutherford", hair="brown", hair_style="swept", head="round",
                       shirt=(46, 58, 78), trousers=(52, 50, 54), shoes=(40, 40, 44),
                       extras=("coat", "tie", "moustache"), kind="adult")

BOLTWOOD = Character(name="Boltwood", hair="ink", hair_style="short", head="oval",
                     shirt=(78, 90, 96), trousers=(52, 54, 58), shoes=(42, 42, 46),
                     extras=("apron", "glasses", "moustache"), kind="adult")

PATTERSON = Character(name="Patterson", hair="brown", hair_style="short", head="oval",
                      shirt=(92, 104, 118), trousers=(58, 60, 68), shoes=(44, 44, 50),
                      extras=("apron",), kind="adult")

PATTERSON_OLD = Character(name="Patterson (later)", hair="grey", hair_style="short", head="oval",
                          shirt=(84, 92, 104), trousers=(56, 58, 64), shoes=(44, 44, 50),
                          extras=("apron", "glasses"), kind="elder")

NATURALIST = Character(name="Naturalist", hair="brown", hair_style="ponytail", head="oval",
                       shirt=(104, 116, 92), trousers=(84, 76, 62), shoes=(56, 48, 40),
                       extras=("coat", "hat"), kind="adult")   # generic, not a real person

CLERK = Character(name="Archivist", hair="ink", hair_style="bun", head="round",
                  shirt=(112, 104, 92), trousers=(70, 66, 60), shoes=(50, 48, 46),
                  extras=("glasses",), kind="adult")

CHILD = Character(name="Child", hair="gold", hair_style="short", head="round",
                  shirt=(202, 148, 96), trousers=(88, 96, 120), shoes=(60, 56, 54),
                  kind="child", scale=0.72)

SCRIBE = Character(name="Scribe", hair="ink", hair_style="short", head="oval",
                   shirt=(70, 62, 56), trousers=(58, 52, 46), shoes=(46, 42, 38), kind="adult")

ALL = {c.name: c for c in (CURATOR, USSHER, HUTTON, PLAYFAIR, HALL, KELVIN, PERRY, RUTHERFORD,
                           BOLTWOOD, PATTERSON, PATTERSON_OLD, NATURALIST, CLERK, CHILD, SCRIBE)}
