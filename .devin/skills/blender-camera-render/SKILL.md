---
name: blender-camera-render
description: Frame and render high-fidelity showcase render matching the exact perspective, framing, and focal length of the reference image
allowed-tools:
  - read
  - exec
  - mcp__blender__*
---

Camera and render stage for high-accuracy showcase presentation.

## 95% ACCURACY STANDARD — MANDATORY REQUIREMENTS

1. **MATCH REFERENCE PERSPECTIVE**:
   - Match the reference image's exact vantage point:
     - For the IndiGo reference: low-angle 3/4 right view, looking up at the ascending aircraft against the sky with banking wings showing the right engine, right winglet, belly contour, and fuselage livery clearly.
   - Set focal length to 50–70mm to avoid wide-angle fish-eye distortion while preserving dynamic aerospace perspective.
   - Frame the subject so the entire aircraft (nose radome, both wings, sharklets, vertical fin, and engines) is elegantly captured with balanced margins.

2. **RENDER CONFIGURATION**:
   - Engine: EEVEE Next or Cycles (EEVEE at 64+ samples for speed, high quality color management).
   - Color Management: AgX or Filmic, Medium High Contrast for crisp punchy highlights.
   - Render resolution: 1024×1024 (or matching aspect ratio of reference).
   - Output to `D:/code/3d/models/<name>/render.png`.

3. **VERIFICATION**:
   - Read the output image with `read` and side-by-side compare with the reference photo. If angles or framing differ, refine camera position.
