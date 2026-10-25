---
name: blender-optimize
description: Web-optimize the model — triangle budget, applied transforms, merged meshes, normalized origin/scale, capped textures
argument-hint: "[max-tris]"
allowed-tools:
  - read
  - exec
  - mcp__blender__*
---

Optimization pass for web delivery. The .blend keeps full history; these changes make the exported GLB small and well-behaved in three.js.

Take `max-tris` from the skill argument (default **50000**; use 10000–20000 for simple props).

Run these as `mcp__blender__execute_blender_code` calls, in order:

## 1. Convert + apply

```python
import bpy
# curves/lattices that are part of the model → mesh first
for o in list(bpy.data.objects):
    if o.type in {'CURVE', 'SURFACE', 'FONT', 'META'}:
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.convert(target='MESH')
# apply modifiers
for o in bpy.data.objects:
    if o.type == 'MESH':
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        for m in list(o.modifiers):
            try:
                bpy.ops.object.modifier_apply(modifier=m.name)
            except Exception as e:
                print("skip modifier:", o.name, m.name, e)
# apply transforms
bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active = next((o for o in bpy.data.objects if o.type == 'MESH'), None)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
```

## 2. Triangle budget

```python
def tri_count():
    n = 0
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.data.calc_loop_triangles()
            n += len(o.data.loop_triangles)
    return n
```

If `tri_count() > max_tris`: `ratio = max_tris / tris`; add a `Decimate` modifier (`decimate_type='COLLAPSE'`, `ratio=ratio`) to each mesh and apply it. Then `mcp__blender__look` — the silhouette must still read. If decimation visibly breaks shading/UVs, raise the budget (lower the decimation) rather than ship a broken mesh.

## 3. Merge for draw calls

If there are more than ~4 static mesh objects, select meshes sharing the same material(s) and `bpy.ops.object.join()` them (active = first of the group). Skip rigged/animated objects entirely. Keep a single parent empty named after the model.

## 4. Origin & scale for the web

```python
import bpy
from mathutils import Vector
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
mins = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
maxs = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
size = maxs - mins
center_xy = Vector(((mins.x + maxs.x) / 2, (mins.y + maxs.y) / 2, mins.z))
# translate so bottom-center sits at origin
for o in meshes:
    o.location -= center_xy
bpy.ops.object.transform_apply(location=True)
# normalize largest dimension to ~1.5 m
target = 1.5 / max(size)
for o in meshes:
    o.scale *= target
bpy.ops.object.transform_apply(scale=True)
```

Result: model centered on XY, base on z=0, largest side ~1.5 m — sane default sizing in a web viewer.

## 5. Texture & data budget

- For each `img` in `bpy.data.images` with `img.size[0] > 1024`: `img.scale(1024, max(1, round(1024 * img.size[1] / img.size[0])))`.
- Per mesh object: `bpy.ops.object.material_slot_remove_unused()` (with that object active).
- `bpy.data.orphans_purge(do_recursive=True)`.

## 6. Report + save

`bpy.ops.wm.save_as_mainfile()` (same filepath), then print and relay: final tri count, mesh count, material count, image count, largest texture dimensions.

## Rules

- Never decimate empties, lights, cameras, or armatures.
- Order matters: apply modifiers before decimating; convert curves before applying.
- If any apply fails on one object, log it and continue — don't halt the pass.
