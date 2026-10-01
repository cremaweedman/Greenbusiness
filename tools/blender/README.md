# Blender tooling

## Starter slot bootstrap

Run:

```bash
blender --background --python tools/blender/greenbusiness_scene_setup.py
```

Or execute the script inside Blender's Scripting workspace.

It creates:
- metric scene setup;
- 1536×1536 transparent PNG render settings;
- `ROOT_SLOT_STARTER`;
- canonical state collections;
- `CAM_SLOT_MASTER`;
- key/fill/rim light scaffold.

The initial camera/light values are a starting point only.

Once SLOT-001 EMPTY is visually approved:
1. adjust the camera and lighting;
2. freeze them;
3. do not change them for sibling states.

See `docs/art/3D_PRODUCTION_PIPELINE_V1.md`.
