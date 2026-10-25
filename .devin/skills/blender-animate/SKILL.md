---
name: blender-animate
description: Create web-ready 3D animations (takeoff, flight trajectories, engine spin, wind effects) exported to glTF/GLB
allowed-tools:
  - read
  - exec
  - mcp__blender__*
---

You are the animation stage of the Blender 3D pipeline. Create fluid, physically convincing keyframed and procedural animations exported seamlessly into glTF 2.0 / GLB for web usage (Three.js, model-viewer).

## 1. TIMELINE & FRAMERATE SETUP
- Frame rate: 30 fps or 60 fps standard for web viewers.
- Duration: Standard web hero animation is typically 3–6 seconds (90 to 180 frames at 30 fps).
- Scene frame range: `scene.frame_start = 1`, `scene.frame_end = <N>`.

## 2. AIRCRAFT TAKEOFF SEQUENCE PHASES
For a realistic runway takeoff:
1. **Initial / Taxi Roll (Frames 1–40)**:
   - Aircraft sits level on runway tarmac (pitch 0°).
   - High-speed turbofan rotation (continuous N1 spooling at TOGA thrust).
   - Rolls forward along runway centerline accelerating along Y.
2. **Rotation (V_r) (Frames 41–70)**:
   - Nose gear lifts off ground; pitch rotates smoothly up (+8° to +14°).
   - Main landing gear remains briefly in ground effect before liftoff.
   - Wingtips flex subtly upward under developing aerodynamic lift.
3. **Liftoff & Climb (V_2) (Frames 71–140)**:
   - Aircraft becomes airborne, climbing in positive rate of climb (+Z).
   - Slight aerodynamic bank angle (+2° to +6° roll) into climbing turn.
   - Aerodynamic wind ribbons / wingtip vortex contrails stream behind wingtips.
4. **Cruise / Exit Climb (Frames 141–180)**:
   - Clean climbing flight path into the sky.

## 3. SECONDARY ANIMATIONS & WIND EFFECTS
- **Turbofans**: Continuous rotation animation on spinner cones and fan discs (`rotation_euler.y` or spin axis rotating 360° repeatedly with linear extrapolation `CYCLES` modifier or keyframed spin).
- **Wind Streamers / Contrails**:
  - Sleek aerodynamic ribbon meshes attached to wingtip sharklets / flap edges.
  - Animate scale, opacity, and turbulence wave motion as airspeed increases during takeoff roll and rotation.
- **Wing Flex**:
  - Upward bend in wingtips (`rotation_euler` or shape key `WingFlex`) animating from 0 (ground resting weight) to 1.0 (inflight aerodynamic lift).

## 4. GLTF / GLB EXPORT SPECIFICATION
- When exporting to GLB, ensure:
  - `export_animations = True`
  - `export_animation_mode = 'ACTIONS'` or `'SCENE'`
  - `export_nla_strips = False` (or baked actions)
  - `export_frame_range = True`
  - `export_apply = True`
- All animated objects must have their actions preserved and keyframes baked.
