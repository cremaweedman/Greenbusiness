# 3D Asset Source of Truth

## Canonical rule

For any asset family marked **3D-first**, the `.blend` master is the source of truth.

Generated PNG/WebP files are build artifacts derived from that master.

## Asset family ownership

| Family | Source of truth |
|---|---|
| Starter production slot | Blender master |
| Slot states | Blender master collections |
| Room shell | Blender master |
| Storage / desk / workbench / contracts | Blender master |
| Upgrade racks | Blender master |
| Starter crops | Approved 2D master image |
| Contact portraits | Approved 2D master image |
| UI glyphs | SVG |
| Brand | SVG |

## Review rule

A screenshot, concept sheet or AI generation is not a production source of truth unless explicitly promoted to an approved 2D master.

## Structural versioning

If chassis geometry changes:
- increment master version;
- rerender every dependent state;
- never mix state renders derived from different chassis versions.

Example:

`gb_slot_starter_master_v02.blend`

requires rerendering:
- EMPTY v02
- PLANTED v02
- GROWING v02
- READY v02
- LOCKED v02
- ATTENTION v02
- BOOSTED v02

## Camera lock

Each family owns a canonical camera object.

Changing that camera is equivalent to a family-wide visual breaking change and requires rerendering all siblings.

## Runtime integration

The frontend references only versioned runtime exports through `gameAssets.ts`.

Components must not depend on source-model paths.
