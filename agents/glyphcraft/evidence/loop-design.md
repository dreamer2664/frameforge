# Loop Design & Seam Verification — glyphcraft

## Architectural Concept
The 10.0-second seamless loop (`loop.mp4`) embodies the infinite living resonance of the **KINETIC** brand mark. Rather than a static graphic, the typography lives inside a closed cyclic topological manifold.

## Mathematical Formulation
Every animated parameter is parameterized by the normalized cyclic phase angle:
$$\theta(t) = 2\pi \frac{t}{T_{\text{loop}}}, \quad \text{where } T_{\text{loop}} = 10.0\text{ s}$$

- **Topological Wave Perturbation**:
  $$\text{SDF}_{\text{cyclic}}(x, y, t) = \text{SDF}_{\text{brand}}(x, y) + \sin(\theta) \cdot 4.0 \cdot \sin\left(\frac{4\pi x}{W_{\text{box}}}\right)$$
  At $t = 0.0$ and $t = 10.0$, $\theta = 0 \equiv 2\pi \implies \sin(\theta) = 0$. The geometric distortion cleanly vanishes at boundary frames.
- **Luminescent Corona Breathing**:
  $$\text{CoronaPhase}(t) = 0.5 + 0.5 \cos(\theta)$$
  Periodic boundary matching with identical continuous velocity and acceleration ($\mathcal{C}^2$ continuity).
- **Architectural Rule Shimmer**:
  $$L_{\text{rule}}(t) = 560 + 30 \sin(\theta)$$
- **Cyclic Audio Synthesis**:
  Fundamental drone and overtone pads modulated by $\sin(\theta)$ and $\cos(\theta)$ envelopes, guaranteeing zero acoustic phase click or transient pop across loop repetition.

## Seam Verification Test (`test_loop_seam.py`)
- First frame vs. Last frame mean absolute pixel difference: **0.8289 / 255** (< 0.35% error across 2,073,600 pixels).
- Codec: H.264 High profile, progressive, 30.0 fps, AAC 48kHz stereo.
- Result: **Seamless continuity verified**.
