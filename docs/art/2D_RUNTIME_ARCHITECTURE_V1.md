# GREENBUSINESS 2D / 2.5D RUNTIME ARCHITECTURE V1

Status: CANONICAL DIRECTION  
Phase: P10-ART  
Runtime strategy: Next.js + React + layered 2D/2.5D isometric assets

## 1. Product decision

GreenBusiness ships its core gameplay as a **premium 2D/2.5D isometric management game**.

The visual target is a rich diorama-like scene with strong depth, lighting and material quality, but the player-facing room is composed from optimized 2D assets rather than a continuously rendered real-time 3D world.

This decision is intentional:
- stronger readability for management gameplay;
- faster load and lower mobile GPU cost;
- simpler PWA deployment;
- easier deterministic art direction;
- lower production/QA burden for a small team;
- easier layering of UI, state badges, timers and interactions;
- no WebGL dependency for the core game loop.

## 2. Runtime split

### 2D / 2.5D scene
Use layered raster/vector assets for:
- room shell;
- production slots;
- crop states;
- furniture;
- storage;
- workbench;
- desk;
- decorations;
- upgrades;
- environmental overlays;
- state effects.

### HTML / React
Use conventional UI for:
- navigation;
- contracts;
- missions;
- inventory;
- store;
- settings;
- currencies;
- timers;
- tooltips;
- accessibility-critical controls;
- admin surfaces.

## 3. Canonical art pipeline

```text
Concept / reference
  ↓
3D source generation when useful
(Meshy / Tripo / manual modeling)
  ↓
Blender canonical master
  ↓
fixed isometric camera + fixed lighting rig
  ↓
deterministic state renders
  ↓
cleanup / alpha / color QA
  ↓
WebP / AVIF / SVG runtime assets
  ↓
Next.js layered scene
```

3D is an authoring tool, not the required runtime.

## 4. Source of truth

For structural art:
- Blender files are the canonical source when a 3D master exists;
- camera, scale, anchors and lighting are versioned;
- all state variants derive from the same master family;
- do not independently generate each state as unrelated final art.

For vector/UI art:
- SVG/vector master is canonical.

For illustration/key art:
- approved high-resolution source is canonical.

## 5. Runtime asset formats

Primary:
- WebP for transparent gameplay assets;
- AVIF for large opaque backgrounds where browser support and decode cost are acceptable;
- SVG for icons, badges and UI geometry.

PNG is reserved for cases where WebP/AVIF is unsuitable.

GLB/GLTF is not part of the default gameplay delivery path.

## 6. Scene composition

The room uses a fixed isometric composition and explicit layer ordering.

Recommended logical layers:

```text
background
room-shell
floor
rear-furniture
production-slots
crops
front-furniture
decorations
state-effects
interaction-hotspots
HTML HUD
modals/panels
```

Every placeable object has:
- canonical anchor point;
- baseline/floor position;
- z-order or scene layer;
- interaction bounds;
- optional state variants.

## 7. Interaction model

The visual scene is presentation only.

Clickable/tappable hotspots may open:
- production slot;
- crop/state panel;
- workbench;
- storage;
- contracts;
- decorations;
- upgrades.

All consequential actions still call the existing server-authoritative API.

## 8. Animation strategy

Prefer lightweight animation:
- CSS transforms;
- opacity;
- sprite sequences where justified;
- Web Animations API;
- small Canvas overlays for particles if needed.

Avoid requiring a persistent 3D renderer for ambient motion.

Animation must respect reduced-motion preferences.

## 9. Performance targets

Closed Alpha targets:
- meaningful room visible quickly after authenticated state arrives;
- core interaction usable on mid-range mobile devices;
- no GPU-heavy continuous scene rendering;
- lazy-load non-critical decoration assets;
- preload only visible/likely-next state variants;
- use responsive asset sizes;
- avoid oversized alpha textures;
- keep layout stable during loading.

The primary KPI is interaction latency/readability, not FPS.

## 10. State rendering

Production slots must derive visual state from API state:
- empty;
- planted;
- growing;
- ready;
- locked;
- attention;
- boosted.

State visuals must preserve the same chassis, camera and anchor.

Use overlays/effects for temporary states when that avoids duplicating entire assets.

## 11. Responsive behavior

Desktop/tablet:
- full isometric room with side/top management UI.

Mobile:
- preserve the same scene composition;
- scale/crop intentionally rather than freely rotating the world;
- provide direct HTML controls for all core actions;
- no hover-only interaction.

## 12. Accessibility

Core actions must remain reachable outside image hotspots.

Requirements:
- keyboard-accessible alternatives;
- ARIA labels;
- visible focus;
- text labels for state;
- color-independent state indicators;
- reduced-motion support.

## 13. Relationship to 3D tooling

Three.js / React Three Fiber may remain in the repository for prototypes or isolated optional visual experiments, but:
- they are not part of the canonical gameplay renderer;
- P10 must not require them to complete the vertical slice;
- production art should optimize for deterministic 2D exports;
- a future return to real-time 3D requires a new explicit architecture decision.

## 14. Immediate production milestone

**P10-ART-1 — Production-quality Starter Room**

Deliver:
- one final isometric room background/shell;
- three production-slot positions;
- empty/planted/growing/ready states for the starter slot family;
- three starter crops;
- storage, contracts station, workbench and desk;
- interaction hotspots;
- HTML state/timer overlays;
- responsive mobile/desktop composition;
- optimized WebP/AVIF exports;
- visual QA against the Art Bible.

This vertical slice must look close to shippable before expanding the remaining asset catalog.
