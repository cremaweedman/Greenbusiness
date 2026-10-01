# STARTER ROOM LAYOUT V1 — GREENBUSINESS

Status: CANONICAL VS-01 ENVIRONMENT LAYOUT
Depends on:
- docs/canon/04_ART_BIBLE_AND_ASSET_SPEC_GREENBUSINESS_v1.0.md
- docs/canon/05_VS01_ASSET_MANIFEST_TEMPLATE.json

## 1. Goal

Define the Starter Room as a modular gameplay diorama rather than a single decorative illustration.

The room must:
- support the five-minute core loop;
- make progression visible;
- allow independent asset replacement;
- avoid baking changing gameplay state into one background image;
- work on desktop and mobile.

## 2. Visual model

Canonical direction:

**Botanical Workshop Diorama**

The room is:
- compact;
- contemporary;
- practical;
- slightly stylized;
- warm;
- modular;
- visibly upgradeable.

It is not:
- a futuristic lab;
- an industrial warehouse;
- a luxury showroom;
- a photoreal greenhouse.

## 3. Layout map

Conceptual layout:

```
┌──────────────────────────────────────────────┐
│                                              │
│   STORAGE                     CONTRACTS      │
│   [S-01]                      [C-01]         │
│                                              │
│                                              │
│   [ SLOT 1 ]   [ SLOT 2 ]   [ SLOT 3 ]      │
│                                              │
│                                              │
│   WORKBENCH                  SMALL DESK      │
│   [W-01]                     [D-01]          │
│                                              │
└──────────────────────────────────────────────┘
```

Initial gameplay state:
- SLOT 1: available
- SLOT 2: unlockable
- SLOT 3: locked

## 4. Layer architecture

### Layer 0 — room shell
Static:
- rear wall;
- floor;
- architectural trim;
- permanent light fixtures;
- door/window if present.

Runtime asset:
`environment/gb_environment_starter-room_shell_v01.webp`

### Layer 1 — storage zone
Independent asset family:
- starter crates;
- organized shelf upgrade;
- expanded storage upgrade.

Suggested IDs:
- GB-VS01-ROOM-STORAGE-001 starter
- GB-VS01-ROOM-STORAGE-002 upgraded

### Layer 2 — contract zone
Independent asset:
- inbox board / order terminal / simple contract surface.

Must not include baked text.

Suggested runtime:
`environment/gb_room_contract-anchor_default_v01.webp`

### Layer 3 — production slots
Three anchored positions:
- slot-a
- slot-b
- slot-c

Each slot renders one of:
- empty
- planted
- growing
- ready
- locked
- attention
- boosted

All states use the exact same anchor and footprint.

### Layer 4 — workbench
Starter workbench:
- simple;
- practical;
- slightly worn but clean;
- hand-tool / packaging / preparation cues;
- not laboratory equipment.

Upgradeable later.

### Layer 5 — desk
Starter desk:
- small;
- basic terminal/laptop;
- ledger/device;
- simple chair;
- management cue.

Avoid sci-fi holograms.

### Layer 6 — ambient decor
Optional:
- small neutral botanical accents;
- box labels without readable text;
- lamp;
- wall clock;
- simple framed shape/art;
- utility hooks.

Decor must never compete with gameplay state.

## 5. Camera

Preferred:
- fixed 3/4 room view;
- mild elevated angle;
- no extreme isometric distortion;
- readable front faces on props;
- consistent asset projection.

Target:
- feels like a playable room;
- not a cinematic background.

## 6. Composition priorities

Priority order:
1. production slots;
2. contract area;
3. storage / workbench;
4. desk;
5. decorative details.

The player's eye should land on production first.

## 7. Starter-state art direction

### Room shell
- painted wall surfaces;
- simple floor;
- limited decorative finish;
- practical lighting;
- enough negative space for expansion.

### Storage
- basic crates and shelf;
- functional, not messy.

### Workbench
- compact;
- inexpensive;
- visibly used;
- no heavy grime.

### Desk
- small and basic;
- functional business setup;
- not executive.

### Lighting
- warm practical overhead light;
- slightly brighter production zone;
- softer desk/ambient light;
- no neon.

## 8. Upgrade progression

### Stage 0 — Starter workshop
- 1 active slot
- basic storage
- small desk
- minimal workbench
- visible unused room

### Stage 1 — Organized workshop
- 2 active slots
- improved shelving
- cleaner storage
- better task lighting

### Stage 2 — Professional studio
- 3 active slots
- upgraded racks
- improved surfaces
- stronger contract/management station
- more coherent branding

### Stage 3 — Mature business
Future:
- expanded zones
- better materials
- more efficient layout
- additional staff / social spaces if gameplay warrants it

## 9. Asset anchors

Recommended normalized canvas coordinates:

- storage: x 0.18 / y 0.24
- contracts: x 0.80 / y 0.24
- slot-a: x 0.28 / y 0.53
- slot-b: x 0.50 / y 0.53
- slot-c: x 0.72 / y 0.53
- workbench: x 0.22 / y 0.80
- desk: x 0.78 / y 0.80

These are layout guides, not final CSS positions.

## 10. Mobile behavior

Desktop:
- full room visible where possible.

Mobile:
- preserve slot band first;
- allow room shell crop;
- stack or overlay secondary controls;
- do not shrink gameplay state until unreadable.

Mobile visual priority:
1. active slot
2. crop/state
3. action controls
4. contracts
5. secondary room detail

## 11. Frontend implementation recommendation

Use one scene component:

`StarterRoomScene.tsx`

Suggested structure:

```
StarterRoomScene
 ├─ RoomShell
 ├─ StorageModule
 ├─ ContractAnchor
 ├─ SlotAnchor A
 ├─ SlotAnchor B
 ├─ SlotAnchor C
 ├─ WorkbenchModule
 ├─ DeskModule
 └─ HtmlUiLayer
```

Do not render the whole room as one stateful image.

## 12. VS-01 additions

The room system introduces these additional assets:

- starter room shell
- starter storage module
- contract anchor
- starter workbench
- starter desk

These should be added to the VS-01 manifest before art production.

## 13. Definition of Done

Starter Room Layout v1 is complete when:
- scene can be built from independent layers;
- all three slot anchors align correctly;
- locked/unlocked slot states can change without changing the room background;
- mobile crop preserves primary gameplay;
- upgrade modules can be swapped independently;
- no baked text is required;
- the scene visually reads as a small business with clear growth potential.
