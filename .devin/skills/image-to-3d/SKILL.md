---
name: image-to-3d
description: Full unattended pipeline — reference image to 95%+ accurate web-optimized 3D model (.blend + Draco .glb + render.png)
argument-hint: "<image-path> [model-name] [max-tris]"
allowed-tools:
  - read
  - exec
  - mcp__blender__*
---

You are the orchestrator. Given a reference image, produce a 95%+ accurate, web-ready 3D model with zero user interaction.

## 95% ACCURACY STANDARD

1. **Geometry**: Real-world dimensions, smooth curvature (64+ segments), authentic aerodynamic components (airfoils, flap track canoes, wing-body fairing, realistic turbofan engines with bypass ducting, curved sharklets).
2. **Texturing**: High-resolution UV texture maps (2048×1024+) generated programmatically with PIL for all branding, typography, livery swooshes, doors, windows, and flags. No crude per-face material painting.
3. **PBR Finish**: Aviation polyurethane gloss clearcoat, polished metal intake lips, realistic cockpit glazing.
4. **Lighting & Camera**: Matched directly to the reference image's environment, banking angle, and focal perspective.
5. **Web Optimization**: Clean Draco-compressed GLB under the triangle budget with applied transforms and normalized scale.

## Pipeline Steps

1. `/blender-connect` — ensure Blender is running and the MCP bridge is live.
2. `/blender-new-scene <model-name>` — fresh clean scene saved to `D:\code\3d\models\<model-name>\model.blend`.
3. `/blender-model-from-image <image-path>` — build 95% accurate geometry with clean UV unwraps.
4. `/blender-texture` — generate high-res livery texture maps and assign realistic PBR materials.
5. `/blender-optimize <max-tris>` — web optimization: merge draw calls, apply transforms, Draco compression prep.
6. `/blender-lighting` — match reference environment lighting and atmosphere.
7. `/blender-camera-render` — render showcase `render.png` matching reference perspective and framing.
8. `/blender-save` — full-res `model.blend` + Draco-compressed `model.glb`.

## Final Report
- File paths: `model.blend`, `model.glb`, `render.png`.
- Statistics: GLB size, final triangle count, texture resolution.
- DRACOLoader reminder for three.js / web viewer.
