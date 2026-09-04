# RGB Prismatics — Specification

This document defines the canonical mapping from an RGB matrix (HxWx3) into the Prismatics operation stream (`pitch`, `roll`, `index`, `scatter`) and the conventions a GPU backend should expect when consuming the resulting payloads.

Purpose
- Provide a deterministic contract so backends (OpenGL, Vulkan, WebGL, compute shaders) can interpret RGB-derived operations consistently.
- Link the ASCII RGB Graphics matrix into an actionable scheme for Prismatics.

Quick mapping summary
- Red (R) → PITCH (rotation angle)
- Green (G) → ROLL (rotation angle)
- Blue (B) → INDEX / SCALE (used to derive golden-ratio-scaled lengths)
- SCATTER → bright-pixel point set (x_norm, y_norm, channel_index)

Prismatics operation sequence
- The wire_rgb helper emits the following ordered operations when called:
  1. ("pitch", pitch_deg)
  2. ("roll", roll_deg)
  3. ("index", index_payload)
  4. ("scatter", scatter_points)

Operation schemas

- pitch: float
  - Degrees in the default mapping: pitch_deg = (r_mean * 360.0) - 180.0
  - r_mean is the normalized channel mean in [0, 1]

- roll: float
  - Degrees in the default mapping: roll_deg = (g_mean * 360.0) - 180.0
  - g_mean is the normalized channel mean in [0, 1]

- index: dict
  - Fields:
    - r_mean, g_mean, b_mean: floats in [0, 1]
    - golden_lengths: dict with keys short/middle/long and scale_factor
      - short: 1.0
      - middle: φ ≈ 1.61803398875
      - long: φ² ≈ 2.61803398875
      - scale_factor: multiplier derived from channel intensity (e.g. b_mean or combined mean)
    - derived: { pitch_deg, roll_deg }

- scatter: list[ (x_norm, y_norm, channel_index) ]
  - x_norm: float in [0, 1] (0=left, 1=right)
  - y_norm: float in [0, 1] (0=top, 1=bottom)
  - channel_index: integer {0=R, 1=G, 2=B}
  - Max default points: 128 (configurable by implementation)
  - Points selected: pixels where any channel value > threshold (default threshold 0.8 for normalized data)

Coordinate & normalization conventions
- Accepted input shapes: (H, W, 3), (N, 3), or a single (3,) RGB tuple.
- Accepted value ranges: 0..1 floats or 0..255 ints; implementations SHOULD normalize to 0..1 before computing means.
- Pixel coordinate normalization:
  - x_norm = col_index / max(1, width - 1)
  - y_norm = row_index / max(1, height - 1)
- Origin and Y direction:
  - Origin is top-left. Y increases downward. Backends that render in NDC (OpenGL/Vulkan) should convert y as needed (e.g., y_ndc = 1.0 - (2.0 * y_norm - 1.0)).

Model / View / Projection usage guidance
- MODEL: use scatter points as model-space positions or point-cloud inputs. Multiply positions by `golden_lengths.scale_factor` to establish model scale.
- VIEW: use pitch/roll to create view or camera rotations. Backends may also rotate the model instead depending on semantics.
- PROJECTION: index data (or golden_lengths) can influence projection (fov or orthographic scale) if desired by the application.

Backend recommendations
- Upload `index` as a small uniform buffer / push constant for shader configuration.
- Pack `scatter` into a SSBO / storage buffer (vec2 + int) for GPU compute/vertex processing.
- Convert pitch/roll to radians and form rotation matrices in the backend or pass degrees and let shader code convert.
- Apply gamma or sRGB decoding before mean computation for color-accurate mappings if the input is in sRGB space.

API knobs / optional parameters
- angle_range: allow mapping to [-90, 90] instead of [-180, 180]
- threshold: float in [0,1] to control bright-pixel selection
- max_points: integer limit for the scatter buffer
- sampling_strategy: one of {"mask", "grid", "random", "centroid"}
- gamma: optional gamma value for pre-correction

Examples
- Example operations sequence:

```
[
  ["pitch", -18.3],
  ["roll", 27.5],
  ["index", { "r_mean": 0.45, "g_mean": 0.57, "b_mean": 0.12, "golden_lengths": {"short":1.0,"middle":1.618,"long":2.618,"scale_factor":0.12}, "derived": {"pitch_deg": -18.3, "roll_deg": 27.5} }],
  ["scatter", [ [0.0,0.0,0], [0.5,0.25,1], [0.75,0.9,2] ]]
]
```

See also: ../assets/rgb-golden-ratio.svg — visual reference for channel/axis mapping.

Credits
- Spec authored for the BOA Prismatics subsystem to provide a stable, backend-neutral contract for RGB-based visual parameterization.
