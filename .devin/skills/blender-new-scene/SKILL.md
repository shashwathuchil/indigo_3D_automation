---
name: blender-new-scene
description: Create a fresh empty Blender scene saved to models/<name>/model.blend
argument-hint: "<model-name>"
allowed-tools:
  - exec
  - mcp__blender__*
---

Create a clean scene and save it early so a recoverable .blend exists from this point on.

Prerequisite: /blender-connect has verified the bridge is live.

## Steps

1. Take the model name from the skill argument. If absent, derive it from the source image filename: lowercase stem, spaces/underscores to hyphens, strip non-alphanumeric except hyphens (e.g. `coffee-mug`).
2. Run via `mcp__blender__execute_blender_code` (substitute the name):

```python
import bpy, os
name = "MODEL_NAME"  # substitute
out = f"D:/code/3d/models/{name}"
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 1.0
sc.render.engine = 'BLENDER_EEVEE'
bpy.ops.wm.save_as_mainfile(filepath=f"{out}/model.blend")
print("SAVED:", f"{out}/model.blend")
```

3. Confirm the output printed `SAVED:`. Report the model name and output directory `D:\code\3d\models\<name>\`.

## Notes

- `read_factory_settings(use_empty=True)` wipes the current scene — only run this when starting a NEW model, never mid-pipeline.
- The world is left at default; /blender-lighting owns world/lights/camera.
- The scene is saved in `D:\code\3d\models\<name>\model.blend` — all later skills must save back to this same path.
