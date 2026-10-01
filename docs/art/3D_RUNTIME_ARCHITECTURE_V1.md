# GREENBUSINESS 3D RUNTIME ARCHITECTURE V1

Status: CANONICAL DIRECTION
Phase: P10-3D-SPIKE
Runtime strategy: Next.js + React Three Fiber + Three.js

## 1. Product decision

GreenBusiness is evolving from a primarily 2D web management interface into a **3D Diorama Management Game**.

The application remains web/PWA-first and keeps its existing backend stack.

### Existing systems retained
- FastAPI
- Postgres
- Redis
- existing auth
- production/economy/contracts
- missions/mastery
- store/entitlements
- clubs/social
- LiveOps
- analytics
- admin tools

### New rendering layer
The core room/gameplay scene is rendered in 3D using:
- Three.js
- React Three Fiber
- Drei helpers
- GLB/GLTF assets authored through Blender

Complex interface surfaces remain HTML/React.

## 2. Rendering split

### 3D
Use the 3D scene for:
- room shell
- production slots
- crop meshes
- furniture
- storage
- workbench
- desk
- decorations
- upgrades
- lighting
- ambient effects
- later: lightweight NPC presence

### HTML / React
Keep these as conventional UI:
- contracts
- mission text
- inventory
- store
- settings
- numbers/currency
- admin information
- forms
- accessibility-critical controls

Do not rebuild text-heavy UI in 3D.

## 3. Runtime architecture

```
Next.js
├── React UI layer
│   ├── Contracts
│   ├── Missions
│   ├── Inventory
│   ├── Store
│   └── Settings
│
└── React Three Fiber scene
    ├── StarterRoom
    ├── ProductionSlots
    ├── Crops
    ├── Furniture
    ├── Upgrades
    └── Decorations

        │
        ▼
      REST/API

FastAPI
├── authoritative production state
├── economy
├── missions
├── social
└── LiveOps

Postgres + Redis
```

## 4. Server authority

The 3D client is presentation only.

It must not become authoritative for:
- crop timers
- harvest outcomes
- inventory
- contract completion
- purchases
- progression
- currency
- upgrade ownership

The scene reflects state received from the API.

## 5. Asset pipeline

```
Concept image
  ↓
Tripo / Meshy
  ↓
Blender cleanup
  ↓
GLB master export
  ↓
runtime optimization
  ↓
/public/assets/3d/
  ↓
React Three Fiber
```

Blender remains the canonical source for structural assets.

## 6. Runtime asset formats

Primary:
- GLB / glTF

Textures:
- KTX2/Basis where practical
- otherwise optimized WebP/PNG depending on tooling

Compression:
- Meshopt preferred where pipeline supports it
- Draco acceptable when asset/tool compatibility requires it

Avoid raw high-poly generation outputs in production.

## 7. Performance targets

Closed Alpha target on mid-range mobile:

- first meaningful 3D scene visible <= 4 s on typical broadband/Wi-Fi
- sustained >= 30 FPS during normal room interaction
- desktop target 60 FPS
- no uncontrolled DPR > 1.5 on mobile
- no continuous heavy post-processing
- no large dynamic shadows by default
- no unbounded particle effects

Starter room target:
- approximately 130k–250k visible triangles maximum
- aggressively reuse geometry/materials
- use instancing for repeated small props where useful

## 8. Camera

The game uses a constrained diorama camera.

Allowed:
- small horizontal rotation
- small vertical orbit range
- limited zoom

Not allowed by default:
- free-fly camera
- first-person controls
- unrestricted room traversal

The scene should feel tactile while preserving composition and UX.

## 9. Interaction model

3D objects may be clickable/tappable.

Examples:
- slot → select production slot
- crop → open crop/state panel
- workbench → open crafting/process surface
- desk → open management
- contract anchor → open contracts
- decoration → inspect or edit placement

All gameplay actions still call existing server-authoritative APIs.

## 10. Mobile interaction

Primary controls must work by tap.

Camera:
- one-finger drag may orbit only when gesture begins inside scene
- page vertical scrolling must remain usable
- pinch zoom optional
- no interaction may require hover

Provide non-3D HTML access to core actions where necessary for accessibility and reliability.

## 11. Progressive loading

Load order:

1. HTML shell
2. critical game state
3. basic 3D room shell
4. active production slots
5. crop meshes
6. secondary furniture
7. decorations/effects

Do not block the whole page on non-critical 3D assets.

## 12. Fallback strategy

If WebGL/WebGPU scene initialization fails:
- retain the HTML game controls
- render a simple fallback visual/state panel
- do not block harvesting, contracts, purchases or progression

3D improves presentation; it must not become a single point of gameplay failure.

## 13. Current spike

The first implementation uses procedural primitive geometry to validate:

- R3F/Next compatibility
- camera controls
- state mapping
- responsive sizing
- CI/build compatibility
- mobile performance baseline

This spike is temporary.

It must later be replaced by optimized GLB assets without rewriting gameplay state logic.

## 14. Migration sequence

### 3D-0 — Runtime spike
- R3F dependencies
- procedural Starter Room
- 3 production slots
- restricted camera
- existing slot state mapping
- CI green

### 3D-1 — GLB room
- room shell
- starter slot GLB
- storage
- desk
- workbench
- contract anchor

### 3D-2 — Crop models
- Aurora Drift
- Ember Leaf
- Moon Sprout
- growth-stage variants

### 3D-3 — Interaction
- direct slot selection
- visual planting
- growing/ready transitions
- harvest animation
- HTML action panels remain canonical controls

### 3D-4 — Upgrades/decor
- rack tiers
- room progression
- decoration placement
- stage evolution

### 3D-5 — Optimization
- mesh/texture compression
- LOD where required
- asset preload priorities
- mobile quality tiers
- telemetry for scene load and FPS

## 15. Quality tiers

Recommended runtime tiers:

### LOW
- DPR <= 1.0
- reduced lights
- no dynamic shadows
- lower texture resolution

### MEDIUM
- DPR <= 1.25
- limited soft shadows
- normal textures

### HIGH
- DPR <= 1.5
- richer lighting
- selective shadows

Do not infer tier only from user agent. Prefer measured capability/performance when implemented.

## 16. Analytics additions

Future 3D telemetry:
- scene_load_ms
- first_interactive_3d_ms
- approximate_fps_bucket
- 3d_init_failure
- quality_tier
- glb_load_failure
- device memory bucket where available

Do not collect unnecessary fingerprinting data.

## 17. Definition of Done for 3D-0

- Three.js/R3F dependencies installed
- Starter Room renders inside existing app
- slot states visibly map to server state
- camera interaction is constrained
- mobile layout remains usable
- production/economy actions continue working
- lint passes
- typecheck passes
- tests pass
- Next production build passes
- compose-smoke passes
- security scan passes

## 18. Stop condition

Do not migrate the rest of the client to 3D until the spike proves:
- acceptable mobile performance
- stable build/CI
- no degradation of core management UX

If the spike fails those conditions, retain the hybrid 2D/3D authoring pipeline and continue using deterministic renders.
