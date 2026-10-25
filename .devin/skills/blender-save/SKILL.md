---
name: blender-save
description: Save the .blend and export the web-optimized Draco-compressed GLB
allowed-tools:
  - exec
  - mcp__blender__*
---

Final packaging stage. Produces `model.blend` (full source) + `model.glb` (web asset) in `D:\code\3d\models\<name>\`.

## Steps

1. Via `mcp__blender__execute_blender_code` (substitute the real name):

```python
import bpy, os
out = "D:/code/3d/models/<NAME>"  # substitute
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=f"{out}/model.blend")

kwargs = dict(
    filepath=f"{out}/model.glb",
    export_format='GLB',
    export_apply=True,                        # apply modifiers at export
    export_yup=True,                          # +Y up for web viewers
    export_texcoords=True,
    export_normals=True,
    export_materials='EXPORT',
    export_cameras=False,
    export_lights=False,
    export_extras=False,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_image_format='WEBP',               # Blender 5.2 supports AUTO/JPEG/WEBP/NONE
)
# drop any arg this exporter version doesn't have, then export
valid = set(bpy.ops.export_scene.gltf.get_rna_type().properties.keys())
kwargs = {k: v for k, v in kwargs.items() if k in valid}
try:
    bpy.ops.export_scene.gltf(**kwargs)
except TypeError as e:
    # e.g. WEBP enum missing on older versions — retry with AUTO
    print("export retry with AUTO images:", e)
    kwargs['export_image_format'] = 'AUTO'
    bpy.ops.export_scene.gltf(**kwargs)
print("GLB bytes:", os.path.getsize(f"{out}/model.glb"))
```

2. Via exec, verify `D:\code\3d\models\<name>` contains `model.blend`, `model.glb`, `render.png`, all non-empty:

```powershell
Get-ChildItem "D:\code\3d\models\<NAME>" | Select Name, Length
```

3. Report the GLB size. If > 5 MB, flag it — suggest re-running /blender-optimize with a lower max-tris or smaller textures, but still deliver the files.

## Rules

- The GLB intentionally excludes lights and cameras — it's the product model for the website.
- The .blend keeps everything (lights, camera, full-res data) as the editable source.
- Do not change `export_yup` — +Y-up is what three.js/GLTFLoader expects.
- Note for the user's website: the GLB is Draco-compressed and WebP-textured — the loader needs `DRACOLoader` wired in, and WebP requires `EXT_texture_webp` support (built into three.js GLTFLoader; all modern browsers support WebP).
