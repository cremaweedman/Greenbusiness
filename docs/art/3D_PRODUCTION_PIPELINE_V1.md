# GreenBusiness 3D Production Pipeline v1

Status: CANONICAL ART-PRODUCTION WORKFLOW  
Applies to: VS-01 structural environment assets and future structural asset families.

## 1. Decision

GreenBusiness uses a **hybrid 2D/3D production pipeline**.

The purpose is to preserve the visual quality of AI-assisted concept art while eliminating geometry drift between gameplay states and upgrades.

### 3D-first asset families
Use 3D masters for:
- production slots;
- room shell;
- storage modules;
- contract station;
- workbench;
- desk;
- racks;
- upgradeable furniture;
- structural props;
- future room expansions.

### 2D-first asset families
Use 2D production for:
- Alex Rowan and other contact portraits;
- Mira Vale and other contact portraits;
- mission/key art;
- store/promotional illustration;
- narrative illustrations.

### Vector-first asset families
Use SVG/vector masters for:
- brand symbol;
- app icon where practical;
- UI glyphs;
- state icons;
- mastery badges where appropriate.

### Hybrid / optional 3D
Starter crops may remain 2D because their accepted visual direction is already strong. A future 3D crop pipeline is optional if animation or camera motion becomes necessary.

## 2. Toolchain

Recommended structural pipeline:

```
AI concept image
    ↓
Tripo or Meshy image-to-3D
    ↓
GLB/FBX/OBJ source model
    ↓
Blender cleanup + canonicalization
    ↓
.blend master (source of truth)
    ↓
state/upgrade variants inside Blender
    ↓
transparent PNG master renders
    ↓
WebP runtime exports
    ↓
Next.js asset registry
```

Unity is not part of the asset-authoring pipeline.

Reason:
- GreenBusiness runtime is currently web/PWA;
- Blender already covers modeling, cleanup, material work, camera, lighting and deterministic rendering;
- adding Unity only for asset creation introduces another engine and build workflow without improving the current runtime.

Unity/Godot/Three.js may be reconsidered only if GreenBusiness becomes a true real-time 3D game.

## 3. AI-to-3D role

Tripo and Meshy are **mesh bootstrap tools**, not the source of truth.

Their output may contain:
- topology noise;
- asymmetry;
- hidden geometry;
- fused pieces;
- material artifacts;
- poor pivots;
- incorrect scale.

Therefore no raw generated model is production-approved.

Every structural model must be normalized in Blender.

## 4. Blender is the canonical source

For each 3D asset family, the approved `.blend` file becomes the canonical art source.

Example:

`art/3d/masters/slots/gb_slot_starter_master_v01.blend`

That master owns:
- geometry;
- camera;
- object scale;
- materials;
- pivots;
- lighting;
- render framing;
- state variants.

Runtime PNG/WebP files are derivatives.

## 5. Starter production slot master

The starter slot must be created once.

Canonical master:

`gb_slot_starter_master_v01.blend`

Required state collections:

```
STATE_EMPTY
STATE_PLANTED
STATE_GROWING
STATE_READY
STATE_LOCKED
STATE_ATTENTION
STATE_BOOSTED
```

The chassis object is shared across all states.

Do not duplicate or regenerate the chassis per state.

Allowed state differences:
- tray contents;
- crop model;
- lock overlay;
- warning prop;
- emissive intensity;
- temporary boost effect.

Forbidden state differences:
- camera;
- chassis proportions;
- outer silhouette;
- base position;
- frame geometry;
- object scale;
- render crop.

## 6. Canonical slot camera

The camera must remain fixed for every state.

Target:
- mild elevated 3/4 perspective;
- front and one side visible;
- tray clearly visible;
- no extreme isometric distortion.

The approved camera object must be named:

`CAM_SLOT_MASTER`

Once SLOT-001 is approved, do not alter this camera for sibling states.

## 7. Canonical render frame

Slot master:
- master render: 1536 × 1536 PNG RGBA;
- runtime render: 512 × 512 WebP;
- optional compact runtime: 256 × 256 WebP.

Crop icons:
- master: 1024 × 1024 PNG RGBA;
- runtime: 256 × 256 WebP.

Room shell:
- master: 3840 × 2160 PNG;
- runtime: 1920 × 1080 WebP.

Room modules:
- master: 1536 × 1536 PNG RGBA where possible;
- runtime: 512 × 512 WebP.

## 8. Coordinate and scale convention

Blender:
- units: Metric;
- unit scale: 1.0;
- +Z = up;
- object origins at functional ground contact;
- no unapplied object scale on approved masters.

Slot master convention:
- chassis centered around world origin;
- floor contact at Z = 0;
- root parent: `ROOT_SLOT_STARTER`.

Room-module convention:
- floor contact at Z = 0;
- origin centered at intended placement anchor;
- forward orientation documented in the master spec.

## 9. Material system

Use physically plausible but stylized materials.

Core slot materials:
- `MAT_GB_FOREST_METAL`
- `MAT_GB_DARK_COMPOSITE`
- `MAT_GB_CREAM_LIGHT`
- `MAT_GB_GOLD_ACCENT`
- `MAT_GB_STATUS_GREEN`

Rules:
- PBR-compatible;
- moderate roughness;
- restrained metallic values;
- no chrome-heavy look;
- emissive surfaces limited to functional lights/status elements;
- avoid photoreal surface noise.

## 10. Lighting

Create canonical studio rigs.

Slot rig:
- `LIGHT_KEY`
- `LIGHT_FILL`
- `LIGHT_RIM`

Optional practical:
- slot's own task-light/emissive strip.

Lighting is fixed across states.

Do not relight READY/BOOSTED globally. State variation should come from local emissive/state effects only.

## 11. Rendering

Recommended renderer:
- Blender Eevee for production speed, unless Cycles materially improves a specific asset.

Requirements:
- transparent film for isolated modules;
- alpha enabled;
- no world background baked into transparent assets;
- consistent exposure;
- deterministic render settings;
- no compositing text or labels.

## 12. Naming

3D source:

`gb_<domain>_<asset>_<variant>_vNN.blend`

Rendered master:

`gb_<domain>_<asset>_<state>_<variant>_vNN.png`

Runtime:

`gb_<domain>_<asset>_<state>_<variant>_vNN.webp`

Examples:

- `gb_slot_starter_master_v01.blend`
- `gb_slot_starter_empty_default_v01.png`
- `gb_slot_starter_empty_default_v01.webp`

## 13. Repository structure

```
art/
  3d/
    inbound/
      tripo/
      meshy/
    masters/
      slots/
      environment/
      props/
      upgrades/
    exports/
      png/
    specs/
  prompts/
  reviews/

tools/
  blender/
    greenbusiness_scene_setup.py
    README.md

apps/web/public/assets/
  slots/
  environment/
  upgrades/
```

### inbound
Raw generated models. Never runtime-ready.

### masters
Approved Blender source-of-truth files.

### exports/png
Master renders before runtime compression.

### apps/web/public/assets
Only approved runtime assets.

## 14. Tripo / Meshy workflow

For a structural concept:

1. choose one approved concept image;
2. use image-to-3D;
3. prefer moderate geometry rather than maximum detail;
4. export GLB where possible;
5. import into Blender;
6. inspect silhouette;
7. delete hidden/garbage geometry;
8. separate fused logical components if required;
9. fix symmetry where design implies symmetry;
10. correct normals;
11. apply transforms;
12. set real pivot/origin;
13. rebuild weak materials;
14. fit canonical camera;
15. compare against concept;
16. save as Blender master.

Recommended initial geometry target for starter props:
- approximately 10k–30k triangles after cleanup;
- higher only if visual QA proves it is required.

Because runtime currently uses 2D renders, polygon count is primarily a maintainability concern, not a browser runtime limit.

## 15. Multi-view preference

If Tripo/Meshy supports multi-view input, use it when possible.

Best input set:
- front 3/4;
- opposite rear 3/4;
- side;
- optional elevated/top view.

A single concept image can bootstrap the model, but multi-view generation normally reduces invented rear geometry.

## 16. State-production sequence

For slots:

1. approve EMPTY 3D master;
2. freeze chassis;
3. create PLANTED collection;
4. create GROWING collection;
5. create READY collection;
6. create LOCKED overlay;
7. create ATTENTION overlay;
8. create BOOSTED effects;
9. batch-render all states;
10. compare via pixel-aligned contact sheet;
11. export runtime assets.

## 17. Room production sequence

1. create room shell master;
2. establish room camera;
3. establish anchor coordinates;
4. build/import modules individually;
5. fit modules into Stage 0;
6. create Stage 1 variants;
7. create Stage 2 variants;
8. create Stage 3 variants;
9. keep interactive/state-changing modules independent from room shell;
10. render runtime layers or future 3D exports as required.

## 18. Asset QA

A 3D-derived runtime asset is approved only if:
- silhouette matches approved concept direction;
- no obvious AI mesh corruption exists;
- camera matches canonical family camera;
- scale and anchor are correct;
- materials match Art Bible palette;
- transparent edges are clean;
- no unwanted cast/background exists;
- sibling states pixel-align;
- no text/watermark/signature exists;
- runtime file meets size budget;
- manifest status can move to APPROVED.

## 19. Source-control policy

Do commit:
- small/medium GLB reference models when useful;
- Blender automation scripts;
- JSON specs;
- prompt/reference metadata;
- approved runtime assets;
- approved source masters if repository size remains reasonable.

Do not commit:
- huge redundant generation dumps;
- dozens of rejected AI meshes;
- raw caches;
- simulation caches;
- temporary renders.

If `.blend` masters become too large for normal Git:
- use Git LFS or project object storage;
- keep repository metadata pointing to the canonical master.

## 20. Runtime strategy

GreenBusiness remains a 2D/HTML/CSS web application for VS-01.

3D is an **authoring pipeline**, not a runtime requirement.

Runtime consumes:
- WebP;
- PNG where alpha requires it;
- SVG.

This keeps:
- load times lower;
- frontend simpler;
- mobile compatibility stronger;
- art deterministic.

Future real-time 3D is an optional later decision.

## 21. Immediate production plan

### Batch 3D-A
- SLOT-001 EMPTY master

### Batch 3D-B
- PLANTED
- GROWING
- READY

### Batch 3D-C
- LOCKED
- ATTENTION
- BOOSTED

### Batch 3D-D
- room shell
- storage
- contracts anchor
- workbench
- desk

### Batch 3D-E
- Efficient Racks I–III

Parallel 2D:
- approved starter crops;
- Alex Rowan;
- Mira Vale.

Parallel vector:
- brand redesign;
- UI icon family.

## 22. Decision summary

For structural GreenBusiness assets:

> Concept with AI → generate mesh with Tripo/Meshy → canonicalize in Blender → render deterministic 2D assets → integrate into Next.js.

Do not continue mass-generating independent 2D slot states as final production assets.
