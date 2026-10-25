---
name: blender-model-from-image
description: Build professional-grade 3D geometry in Blender procedurally from a reference image, targeting ≥95% visual accuracy
argument-hint: "<image-path>"
allowed-tools:
  - read
  - exec
  - mcp__blender__*
---

You are the modeling stage of the image-to-3D pipeline. Target ≥95% visual and geometric accuracy. Build using Blender Python (`bpy`, `bmesh`, `mathutils`) via `mcp__blender__execute_blender_code`.

## 95% ACCURACY STANDARD — MANDATORY REQUIREMENTS

1. **PROPORTIONS & BLUEPRINTS**:
   - If the subject is a real-world manufactured object (aircraft, vehicle, electronics, furniture), use its actual manufacturer specifications and blueprint dimensions. Never guess or approximate key ratios.
   - For an aircraft (e.g. A320neo): length 37.57m, wingspan 35.80m, fuselage outer diameter 3.95m, engine fan diameter 1.98m, sharklet height 2.4m.
   - Subdivide curvature: at least 64-96 radial segments for fuselage/tubular bodies to ensure completely smooth, silhouette-accurate circular cross-sections.

2. **AERODYNAMIC & STRUCTURAL COMPONENTS**:
   - Primary airframe: fuselage with proper nose radome droop, cockpit brow, and tail cone upsweep with APU exhaust nozzle.
   - Wing-body fairing (belly bulge): the aerodynamic fairing where wings merge into the lower fuselage.
   - Wings: true cambered supercritical/NACA airfoil sections with thickness taper (12% root to 9% tip), sweep (25°), dihedral (5°), and wingtip twist.
   - Trailing-edge details: include flap track fairings ("canoes") under each wing (e.g., 3 canoes per wing on an A320).
   - Sharklets / Wingtips: continuous aerodynamic curve sweeping upward with correct toe-in and sweep.
   - Turbofan Engines: large high-bypass nacelles with flared intake, polished lip ring, internal intake duct, central spinner cone, core cowl, and rear exhaust nozzle. Connected to wing via aerodynamic swept pylons.
   - Empennage: vertical stabilizer with dorsal fin fillet and rudder seam; horizontal stabilizers with elevators.
   - Ancillary details: VHF antennas, satcom dome, pitot probes, and APU exhaust.

3. **CLEAN UV TOPOLOGY (CRITICAL FOR 95% LIVERY ACCURACY)**:
   - Every mesh MUST be UV-unwrapped cleanly with organized UV coordinates so high-resolution textures, liveries, logos, and panel lines can be applied without distortion.
   - Fuselage: Cylindrical unwrap mapped to [0, 1] UV space (U = 0..1 around circumference, V = 0..1 along nose-to-tail length), or standard left-side / right-side projection.
   - Vertical fin: Planar unwrap for side-profile branding and logos.
   - Engines: Cylindrical unwrap for nacelle branding ("goIndiGo.in") and chrome lip separation.
   - Wings: Top/bottom projection for wing box corogard panels and slat lines.

4. **VERIFICATION**:
   - Use `mcp__blender__look` to verify the geometry from multiple angles (front, side, 3/4) against the reference image before proceeding to texturing.
