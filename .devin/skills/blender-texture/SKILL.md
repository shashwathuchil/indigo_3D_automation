---
name: blender-texture
description: Create and assign photorealistic 95%+ accurate materials and livery texture maps matching the reference image
allowed-tools:
  - read
  - exec
  - mcp__blender__*
---

You are the texturing stage of the image-to-3D pipeline. Target ≥95% visual accuracy.

## 95% ACCURACY STANDARD — MANDATORY REQUIREMENTS

1. **NEVER USE CRUDE SOLID-COLOR FACE ASSIGNMENTS FOR GRAPHICS**:
   - Per-face material switching produces jagged stair-stepped boundaries and cannot represent logos, typography, door frames, or curved swooshes.
   - For all liveries, typography ("IndiGo", "goIndiGo.in"), cockpit windshield frames, passenger windows, emergency exits, and curved stripes, **generate high-resolution UV texture maps** (2048×1024 or higher) using Pillow (`PIL.Image`, `ImageDraw`, `ImageFont`).

2. **AUTHENTIC LIVERY REPRODUCTION**:
   - Sample exact brand and reference colors:
     - Aviation White: sRGB (0.95, 0.95, 0.97) / Hex #F2F4F7
     - IndiGo Deep Navy Blue: sRGB (0.02, 0.05, 0.32) / Hex #050E52
     - IndiGo Sky Cyan Pinstripe: sRGB (0.12, 0.62, 0.78) / Hex #1F9EC7
     - Cockpit glass / Passenger window tint: sRGB (0.02, 0.03, 0.07)
     - Slat / Lip Titanium / Chrome: sRGB (0.75, 0.75, 0.78), metallic 0.9, roughness 0.2
     - Wing Corogard grey: sRGB (0.68, 0.68, 0.70)
   - Accurately draw:
     - Exact curved blue belly swoosh originating beneath cockpit, wrapping the wing-body fairing, and sweeping gracefully up the tail.
     - Bright cyan accent stripe along the boundary of the blue swoosh.
     - Bold "IndiGo" lettering in brand typography positioned correctly on the forward fuselage and vertical stabilizer.
     - "goIndiGo.in" lettering on the outer engine nacelles.
     - Crisp 6-pane cockpit windshield with black boundary mask.
     - Uniform rows of passenger windows with glass sheen.
     - Passenger doors (L1, L2) and overwing emergency exits with outline markings.
     - Indian national flag tricolor decal near the aft fuselage.

3. **REALISTIC PBR MATERIALS**:
   - Use `Principled BSDF` with realistic physical parameters:
     - White / Blue Livery: Roughness = 0.20–0.25, Clearcoat = 0.7 (aviation polyurethane gloss enamel).
     - Engine Intake Lip / Slat leading edges: Metallic = 0.92, Roughness = 0.22 (polished aerospace metal).
     - Cockpit / Window glass: Roughness = 0.05, IOR = 1.45, specular = 0.8.
     - Exhaust cone / Nozzle: Metallic = 0.85, Roughness = 0.50, dark heat-tinted titanium.

4. **VERIFICATION**:
   - Inspect with `mcp__blender__look` in `rendered` mode to confirm all markings, stripes, and logos match the reference photo.
