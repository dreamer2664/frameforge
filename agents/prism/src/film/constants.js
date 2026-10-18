// PRISM / "PROOF" — global constants. The only place temporal and spatial truth is declared.
export const FPS = 30;
export const FRAMES = 750;            // 0..749 inclusive = exactly 25.00 s
export const W = 1920;
export const H = 1080;
export const SEED = 0x50524f4f;       // "PROO"

// Title-safe: 90% box => margins >= 5% each side (96 px x, 54 px y)
export const SAFE = { x: W * 0.05, y: H * 0.05 };

// Locked colour language (ckpt2): amber = claim, ice = measurement,
// white = verdict, paper = receipt.
export const PAL = {
  voidWarm: 0x0a0705,
  voidCold: 0x04070c,
  voidInk:  0x070707,
  amber:    0xffb347,
  amberHot: 0xff8a00,
  amberDeep:0x7a3d00,
  ice:      0xbfe3ff,
  iceMid:   0x7fd4ff,
  iceDeep:  0x1d3550,
  white:    0xffffff,
  paper:    0xf2efe9,
  ink:      0x141210,
};

export const HEX = (n) => '#' + n.toString(16).padStart(6, '0');

// Acts (frame ranges, inclusive)
export const ACT = {
  I:   [0, 179],
  II:  [180, 449],
  III: [450, 659],
  IV:  [660, 749],
};

export const actOf = (f) =>
  f <= ACT.I[1] ? 1 : f <= ACT.II[1] ? 2 : f <= ACT.III[1] ? 3 : 4;
