---
name: blender-lighting
description: Set up environment lighting matching the reference image's mood, sun angle, and atmosphere
allowed-tools:
  - exec
  - mcp__blender__*
---

Lighting stage for high-accuracy visual presentation.

## 95% ACCURACY STANDARD — MANDATORY REQUIREMENTS

1. **ENVIRONMENT MATCHING**:
   - Analyze the reference image's environment:
     - In-flight aircraft (like the IndiGo reference photo): high-altitude daytime lighting with strong directional sunlight (Sun light, energy 4.0–6.0, slight warm white) and deep azure/sky blue atmospheric fill (Nishita sky texture or sky-blue World background with soft ambient bounce).
     - Studio product: 3-point key/fill/rim with soft area lights.
   - Ground/Horizon: If high-altitude flight, create a realistic cloud layer or atmospheric haze horizon rather than a flat dark studio floor.

2. **HIGHLIGHTS & REFLECTIONS**:
   - Position the primary light so specular highlights accentuate the curvature of the fuselage, wing gloss, engine nacelles, and polished silver intake lips.
   - Add a subtle rim light or fill to prevent shadows from clipping to pure black.

3. **VERIFY**:
   - Test render at 1024px with EEVEE. Confirm natural contrast and vivid colors without blown highlights.
