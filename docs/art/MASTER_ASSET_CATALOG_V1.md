# GREENBUSINESS MASTER ASSET CATALOG V1

Status: CANONICAL ART BACKLOG  
Purpose: Single source for all currently known visual assets and their generation/modeling prompts.

## Rules

- One asset = one production item.
- Do not create final production assets as collages/contact sheets.
- 3D-first assets: concept → Tripo/Meshy/manual modeling → Blender cleanup/master → fixed-camera isometric render → optimized WebP/AVIF runtime asset.
- 2D-first assets: generate individually → cleanup → approved master → runtime export.
- Vector-first assets: concept if needed → manually recreate/clean as SVG.
- No baked UI text unless explicitly approved.
- Every runtime asset must pass the Art Bible and QA checklist.
- GLB/GLTF files are production-source/intermediate assets unless a later ADR explicitly approves a specific real-time 3D use.
- All gameplay renders must preserve the canonical isometric camera, scale, anchor points, lighting rig and state-family consistency.
- If a game-data item is added later, this catalog must be extended.

## Current inventory

- Total planned visual assets: **93**
- P0: **26**
- P1: **45**
- P2: **22**
- 3D-first: **55**
- 2D-first: **20**
- Vector-first: **18**

## Production order

1. P10-ART-1: Starter Room + production slot family
2. P10-ART-2: starter crops
3. characters + core UI
4. P10-ART-4: upgrades + first decorations
5. remaining crops/contacts/decorations
6. store/mission/mastery polish
7. brand finalization and marketing derivatives


---

## BRAND

### GB-MASTER-BRAND-001 — Primary Brand Symbol
- Key: `n/a`
- Priority: **P0**
- Method: **vector-first**
- Phase: **Brand**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Design an original geometric symbol that communicates growth, business progression and modular construction. Avoid generic eco-leaf or cannabis-leaf marks. Must work in monochrome and at 24px.

### GB-MASTER-BRAND-002 — App Icon
- Key: `n/a`
- Priority: **P0**
- Method: **vector-first**
- Phase: **Brand**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the GreenBusiness app icon from the approved brand symbol, centered, maskable-safe, strong at 48px, dark forest background with cream/mint foreground and restrained gold accent, no wordmark.

---

## SLOTS

### GB-MASTER-SLOT-001 — Starter Slot — EMPTY
- Key: `n/a`
- Priority: **P0**
- Method: **3d-first**
- Phase: **3D-1**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create the canonical starter production slot state EMPTY. Use the exact same chassis, scale, camera, root transform and materials as gb_slot_starter_master_v01. Only state-specific tray contents, lock/warning/boost overlays or local emissive effects may change. Blender-master structural asset; render approved fixed-camera isometric WebP/AVIF runtime variants.

### GB-MASTER-SLOT-002 — Starter Slot — PLANTED
- Key: `n/a`
- Priority: **P0**
- Method: **3d-first**
- Phase: **3D-1**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create the canonical starter production slot state PLANTED. Use the exact same chassis, scale, camera, root transform and materials as gb_slot_starter_master_v01. Only state-specific tray contents, lock/warning/boost overlays or local emissive effects may change. Blender-master structural asset; render approved fixed-camera isometric WebP/AVIF runtime variants.

### GB-MASTER-SLOT-003 — Starter Slot — GROWING
- Key: `n/a`
- Priority: **P0**
- Method: **3d-first**
- Phase: **3D-1**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create the canonical starter production slot state GROWING. Use the exact same chassis, scale, camera, root transform and materials as gb_slot_starter_master_v01. Only state-specific tray contents, lock/warning/boost overlays or local emissive effects may change. Blender-master structural asset; render approved fixed-camera isometric WebP/AVIF runtime variants.

### GB-MASTER-SLOT-004 — Starter Slot — READY
- Key: `n/a`
- Priority: **P0**
- Method: **3d-first**
- Phase: **3D-1**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create the canonical starter production slot state READY. Use the exact same chassis, scale, camera, root transform and materials as gb_slot_starter_master_v01. Only state-specific tray contents, lock/warning/boost overlays or local emissive effects may change. Blender-master structural asset; render approved fixed-camera isometric WebP/AVIF runtime variants.

### GB-MASTER-SLOT-005 — Starter Slot — LOCKED
- Key: `n/a`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-3**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create the canonical starter production slot state LOCKED. Use the exact same chassis, scale, camera, root transform and materials as gb_slot_starter_master_v01. Only state-specific tray contents, lock/warning/boost overlays or local emissive effects may change. Blender-master structural asset; render approved fixed-camera isometric WebP/AVIF runtime variants.

### GB-MASTER-SLOT-006 — Starter Slot — ATTENTION
- Key: `n/a`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-3**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create the canonical starter production slot state ATTENTION. Use the exact same chassis, scale, camera, root transform and materials as gb_slot_starter_master_v01. Only state-specific tray contents, lock/warning/boost overlays or local emissive effects may change. Blender-master structural asset; render approved fixed-camera isometric WebP/AVIF runtime variants.

### GB-MASTER-SLOT-007 — Starter Slot — BOOSTED
- Key: `n/a`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-3**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create the canonical starter production slot state BOOSTED. Use the exact same chassis, scale, camera, root transform and materials as gb_slot_starter_master_v01. Only state-specific tray contents, lock/warning/boost overlays or local emissive effects may change. Blender-master structural asset; render approved fixed-camera isometric WebP/AVIF runtime variants.

---

## ENVIRONMENT

### GB-MASTER-ROOM-001 — Starter Room Shell
- Key: `room-shell`
- Priority: **P0**
- Method: **3d-first**
- Phase: **3D-1**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create the compact Starter Room architectural shell only: floor, walls, structural trim, permanent practical fixtures and warm window/ceiling light anchors. Keep central gameplay area open. No baked furniture, slots or characters. Isolated modular Blender master where applicable, correct floor pivot and clean topology; export approved fixed-camera isometric WebP/AVIF runtime asset.

### GB-MASTER-ROOM-002 — Starter Storage Module
- Key: `storage-module`
- Priority: **P0**
- Method: **3d-first**
- Phase: **3D-1**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create a modest modular starter storage unit with practical shelves, crates and neutral botanical-business supplies. Upgradeable, clean, not cluttered. Isolated modular Blender master where applicable, correct floor pivot and clean topology; export approved fixed-camera isometric WebP/AVIF runtime asset.

### GB-MASTER-ROOM-003 — Contracts Station
- Key: `contracts-anchor`
- Priority: **P0**
- Method: **3d-first**
- Phase: **3D-1**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create a compact contracts/order station with board, terminal or pinned card surfaces but no readable text. It must clearly read as the business order hub. Isolated modular Blender master where applicable, correct floor pivot and clean topology; export approved fixed-camera isometric WebP/AVIF runtime asset.

### GB-MASTER-ROOM-004 — Starter Workbench
- Key: `workbench`
- Priority: **P0**
- Method: **3d-first**
- Phase: **3D-1**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create a practical starter workbench with simple tools, trays and packaging/preparation cues. Not laboratory equipment. Isolated modular Blender master where applicable, correct floor pivot and clean topology; export approved fixed-camera isometric WebP/AVIF runtime asset.

### GB-MASTER-ROOM-005 — Starter Desk
- Key: `desk`
- Priority: **P0**
- Method: **3d-first**
- Phase: **3D-1**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create a small management desk with laptop/terminal, notebook and practical office supplies. Modest, contemporary, non-luxury. Isolated modular Blender master where applicable, correct floor pivot and clean topology; export approved fixed-camera isometric WebP/AVIF runtime asset.

---

## UPGRADES

### GB-MASTER-UPGRADE-001 — Efficient Racks I
- Key: `starter-yield-boost`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create a practical tier-1 rack upgrade, modest capacity, simple modular construction and affordable starter-business finish. Blender master with room-placement pivot at floor level; export approved fixed-camera isometric WebP/AVIF runtime asset.

### GB-MASTER-UPGRADE-002 — Efficient Racks II
- Key: `efficient-racks-2`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create tier-2 of the same rack family, visibly improved organization, capacity and task lighting while preserving family silhouette. Blender master with room-placement pivot at floor level; export approved fixed-camera isometric WebP/AVIF runtime asset.

### GB-MASTER-UPGRADE-003 — Efficient Racks III
- Key: `efficient-racks-3`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create tier-3 of the same rack family, optimized and premium but not futuristic, with clear progression from tier 2. Blender master with room-placement pivot at floor level; export approved fixed-camera isometric WebP/AVIF runtime asset.

---

## CROPS

### GB-MASTER-CROP-001 — Aurora Drift
- Key: `aurora-drift`
- Priority: **P0**
- Method: **2d-first**
- Phase: **3D-2**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Aurora Drift, a fictional GreenBusiness botanical variety. compact lush plant, strong triangular silhouette, healthy green leaves, pale cream clustered flower heads, energetic and efficient feel Centered isolated crop master on transparent background, strong 64px readability, no pot unless required, no labels.

### GB-MASTER-CROP-002 — Ember Leaf
- Key: `ember-leaf`
- Priority: **P0**
- Method: **2d-first**
- Phase: **3D-2**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Ember Leaf, a fictional GreenBusiness botanical variety. bold warm-toned plant, red-orange foliage accents, coral/ember hues, sturdy symmetrical silhouette, resilient feel Centered isolated crop master on transparent background, strong 64px readability, no pot unless required, no labels.

### GB-MASTER-CROP-003 — Moon Sprout
- Key: `moon-sprout`
- Priority: **P0**
- Method: **2d-first**
- Phase: **3D-2**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Moon Sprout, a fictional GreenBusiness botanical variety. premium cool-toned plant, dark violet/purple foliage accents, pale lilac clustered flower forms, elegant night-associated feel Centered isolated crop master on transparent background, strong 64px readability, no pot unless required, no labels.

### GB-MASTER-CROP-004 — Velvet Mist
- Key: `velvet-mist`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Content**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Velvet Mist, a fictional GreenBusiness botanical variety. soft layered silhouette, muted sage-green leaves with dusty mauve accents, balanced and aromatic visual identity Centered isolated crop master on transparent background, strong 64px readability, no pot unless required, no labels.

### GB-MASTER-CROP-005 — Cinder Bloom
- Key: `cinder-bloom`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Content**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Cinder Bloom, a fictional GreenBusiness botanical variety. sturdy bush form, deep green with ember-red and copper accents, warm resilient identity Centered isolated crop master on transparent background, strong 64px readability, no pot unless required, no labels.

### GB-MASTER-CROP-006 — Jade Comet
- Key: `jade-comet`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Content**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Jade Comet, a fictional GreenBusiness botanical variety. sleek upward silhouette, jade green foliage with pale mint highlights, efficient premium identity Centered isolated crop master on transparent background, strong 64px readability, no pot unless required, no labels.

### GB-MASTER-CROP-007 — Sunset Veil
- Key: `sunset-veil`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Content**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Sunset Veil, a fictional GreenBusiness botanical variety. layered balanced plant, green base with sunset peach and warm rose accents, stable calm identity Centered isolated crop master on transparent background, strong 64px readability, no pot unless required, no labels.

### GB-MASTER-CROP-008 — Opal Rush
- Key: `opal-rush`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Content**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Opal Rush, a fictional GreenBusiness botanical variety. dynamic compact plant, pale opal/iridescent accents over rich green, fast premium identity Centered isolated crop master on transparent background, strong 64px readability, no pot unless required, no labels.

### GB-MASTER-CROP-009 — Northstar
- Key: `northstar`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Content**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Northstar, a fictional GreenBusiness botanical variety. cool dark-green plant with silver-blue highlights, star-like radial silhouette, stable night identity Centered isolated crop master on transparent background, strong 64px readability, no pot unless required, no labels.

### GB-MASTER-CROP-010 — Quiet Thunder
- Key: `quiet-thunder`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Content**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Quiet Thunder, a fictional GreenBusiness botanical variety. dense powerful plant, deep forest green with muted violet/bronze accents, resilient premium identity Centered isolated crop master on transparent background, strong 64px readability, no pot unless required, no labels.

---

## CHARACTERS

### GB-MASTER-CHAR-001 — Alex Rowan
- Key: `alex-rowan`
- Priority: **P0**
- Method: **2d-first**
- Phase: **Characters**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Alex Rowan, an original adult character portrait, half-body 4:5. Role: Neighborhood coordinator. Visual direction: grounded neighborhood coordinator; calm, dependable, approachable; contemporary practical workwear; optional tablet or clipboard. Clean removable background, expressive readable face, no celebrity likeness, no glamour-first styling.

### GB-MASTER-CHAR-002 — Mira Vale
- Key: `mira-vale`
- Priority: **P0**
- Method: **2d-first**
- Phase: **Characters**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Mira Vale, an original adult character portrait, half-body 4:5. Role: Botanical product designer. Visual direction: precise botanical product designer; observant, polished, creative; practical design-oriented clothing; optional sample tray, notebook or tablet. Clean removable background, expressive readable face, no celebrity likeness, no glamour-first styling.

### GB-MASTER-CHAR-003 — Tessa Ward
- Key: `tessa-ward`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Characters**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Tessa Ward, an original adult character portrait, half-body 4:5. Role: Operations liaison. Visual direction: operations liaison; practical, efficient, organized; functional work jacket and scheduling/device cues; confident but understated. Clean removable background, expressive readable face, no celebrity likeness, no glamour-first styling.

### GB-MASTER-CHAR-004 — Jules Mercer
- Key: `jules-mercer`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Characters**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create Jules Mercer, an original adult character portrait, half-body 4:5. Role: Brand curator. Visual direction: brand curator; observant, tasteful, detail-oriented; modern creative-professional styling with restrained premium accents. Clean removable background, expressive readable face, no celebrity likeness, no glamour-first styling.

---

## UI

### GB-MASTER-UI-001 — Cash
- Key: `currency-cash`
- Priority: **P0**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Cash icon: wallet/note abstraction without relying on a currency letter. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

### GB-MASTER-UI-002 — Premium Credits
- Key: `currency-premium`
- Priority: **P0**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Premium Credits icon: distinct faceted token/seed medallion, premium but not gambling-chip-like. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

### GB-MASTER-UI-003 — Contract
- Key: `contract`
- Priority: **P0**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Contract icon: document/card plus agreement/check motif. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

### GB-MASTER-UI-004 — Upgrade
- Key: `upgrade`
- Priority: **P0**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Upgrade icon: modular block or rack with upward progression cue. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

### GB-MASTER-UI-005 — Mission
- Key: `mission`
- Priority: **P0**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Mission icon: waypoint/flag/checklist hybrid. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

### GB-MASTER-UI-006 — Mastery
- Key: `mastery`
- Priority: **P0**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Mastery icon: badge/ring progression motif. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

### GB-MASTER-UI-007 — Timer
- Key: `timer`
- Priority: **P0**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Timer icon: simple clock/progress dial. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

### GB-MASTER-UI-008 — Inventory
- Key: `inventory`
- Priority: **P0**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Inventory icon: storage crate/grid. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

### GB-MASTER-UI-009 — Ready
- Key: `ready`
- Priority: **P0**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Ready icon: checkmark plus harvest/box silhouette. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

### GB-MASTER-UI-010 — Warning
- Key: `warning`
- Priority: **P0**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Warning icon: shape-based alert symbol understandable without red. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

### GB-MASTER-UI-011 — Club
- Key: `club`
- Priority: **P1**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Club icon: small group/community emblem. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

### GB-MASTER-UI-012 — Notification
- Key: `notification`
- Priority: **P1**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create the Notification icon: simple bell/inbox alert. Consistent filled-plus-cutout family, 16–64px readability, currentColor-friendly.

---

## DECORATIONS

### GB-MASTER-DECOR-001 — Warm Lantern
- Key: `warm-lantern`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Warm Lantern, a decorative lighting object with warm practical illumination. Category: lighting. It should feel appropriate to unlock around level 1: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-002 — Paper Pendant
- Key: `paper-pendant`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Paper Pendant, a decorative lighting object with warm practical illumination. Category: lighting. It should feel appropriate to unlock around level 2: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-003 — Neon Leaf
- Key: `neon-leaf`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Neon Leaf, a decorative lighting object with warm practical illumination. Category: lighting. It should feel appropriate to unlock around level 5: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-004 — Track Lights
- Key: `track-lights`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Track Lights, a decorative lighting object with warm practical illumination. Category: lighting. It should feel appropriate to unlock around level 7: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-005 — Moon Lamp
- Key: `moon-lamp`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Moon Lamp, a decorative lighting object with warm practical illumination. Category: lighting. It should feel appropriate to unlock around level 10: premium, collectible and visually memorable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-006 — Canvas Chair
- Key: `canvas-chair`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Canvas Chair, a comfortable seating object for the workshop/social corner. Category: seating. It should feel appropriate to unlock around level 1: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-007 — Low Bench
- Key: `low-bench`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Low Bench, a comfortable seating object for the workshop/social corner. Category: seating. It should feel appropriate to unlock around level 2: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-008 — Modular Sofa
- Key: `modular-sofa`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Modular Sofa, a comfortable seating object for the workshop/social corner. Category: seating. It should feel appropriate to unlock around level 6: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-009 — Reading Stool
- Key: `reading-stool`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Reading Stool, a comfortable seating object for the workshop/social corner. Category: seating. It should feel appropriate to unlock around level 4: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-010 — Lounge Pod
- Key: `lounge-pod`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Lounge Pod, a comfortable seating object for the workshop/social corner. Category: seating. It should feel appropriate to unlock around level 12: premium, collectible and visually memorable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-011 — Ceramic Planter
- Key: `ceramic-planter`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Ceramic Planter, a decorative planter object for non-gameplay ambient plants. Category: planters. It should feel appropriate to unlock around level 1: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-012 — Tall Planter
- Key: `tall-planter`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Tall Planter, a decorative planter object for non-gameplay ambient plants. Category: planters. It should feel appropriate to unlock around level 2: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-013 — Hanging Planter
- Key: `hanging-planter`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Hanging Planter, a decorative planter object for non-gameplay ambient plants. Category: planters. It should feel appropriate to unlock around level 4: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-014 — Stone Planter
- Key: `stone-planter`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Stone Planter, a decorative planter object for non-gameplay ambient plants. Category: planters. It should feel appropriate to unlock around level 6: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-015 — Glass Planter
- Key: `glass-planter`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Glass Planter, a decorative planter object for non-gameplay ambient plants. Category: planters. It should feel appropriate to unlock around level 11: premium, collectible and visually memorable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-016 — Grid Poster
- Key: `grid-poster`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Grid Poster, a wall-mounted decorative piece. Category: wall. It should feel appropriate to unlock around level 1: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-017 — District Map
- Key: `district-map`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create District Map, a wall-mounted decorative piece. Category: wall. It should feel appropriate to unlock around level 3: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-018 — Botanical Print
- Key: `botanical-print`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Botanical Print, a wall-mounted decorative piece. Category: wall. It should feel appropriate to unlock around level 4: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-019 — Abstract Panel
- Key: `abstract-panel`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Abstract Panel, a wall-mounted decorative piece. Category: wall. It should feel appropriate to unlock around level 7: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-020 — Founder Plaque
- Key: `founder-plaque`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Founder Plaque, a wall-mounted decorative piece. Category: wall. It should feel appropriate to unlock around level 15: premium, collectible and visually memorable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-021 — Woven Rug
- Key: `woven-rug`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Woven Rug, a floor decoration or surface accent. Category: floor. It should feel appropriate to unlock around level 1: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-022 — Checker Rug
- Key: `checker-rug`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Checker Rug, a floor decoration or surface accent. Category: floor. It should feel appropriate to unlock around level 3: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-023 — Cork Mat
- Key: `cork-mat`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Cork Mat, a floor decoration or surface accent. Category: floor. It should feel appropriate to unlock around level 2: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-024 — Terrazzo Inlay
- Key: `terrazzo-inlay`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Terrazzo Inlay, a floor decoration or surface accent. Category: floor. It should feel appropriate to unlock around level 8: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-025 — Soft Runner
- Key: `soft-runner`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Soft Runner, a floor decoration or surface accent. Category: floor. It should feel appropriate to unlock around level 6: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-026 — Crate Stack
- Key: `crate-stack`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Crate Stack, a decorative storage/furniture piece. Category: storage. It should feel appropriate to unlock around level 1: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-027 — Label Shelf
- Key: `label-shelf`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Label Shelf, a decorative storage/furniture piece. Category: storage. It should feel appropriate to unlock around level 2: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-028 — Metal Locker
- Key: `metal-locker`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Metal Locker, a decorative storage/furniture piece. Category: storage. It should feel appropriate to unlock around level 5: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-029 — Display Cabinet
- Key: `display-cabinet`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Display Cabinet, a decorative storage/furniture piece. Category: storage. It should feel appropriate to unlock around level 9: premium, collectible and visually memorable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-030 — Archive Drawers
- Key: `archive-drawers`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Archive Drawers, a decorative storage/furniture piece. Category: storage. It should feel appropriate to unlock around level 13: premium, collectible and visually memorable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-031 — Small Sculpture
- Key: `small-sculpture`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Small Sculpture, a tasteful art object or sculpture. Category: art. It should feel appropriate to unlock around level 3: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-032 — Kinetic Mobile
- Key: `kinetic-mobile`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Kinetic Mobile, a tasteful art object or sculpture. Category: art. It should feel appropriate to unlock around level 6: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-033 — Color Study
- Key: `color-study`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Color Study, a tasteful art object or sculpture. Category: art. It should feel appropriate to unlock around level 5: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-034 — Glass Orb
- Key: `glass-orb`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Glass Orb, a tasteful art object or sculpture. Category: art. It should feel appropriate to unlock around level 10: premium, collectible and visually memorable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-035 — District Trophy
- Key: `district-trophy`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create District Trophy, a tasteful art object or sculpture. Category: art. It should feel appropriate to unlock around level 18: premium, collectible and visually memorable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-036 — Counter Clock
- Key: `counter-clock`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Counter Clock, a small utility/decor object. Category: utility. It should feel appropriate to unlock around level 2: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-037 — Notice Board
- Key: `notice-board`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Notice Board, a small utility/decor object. Category: utility. It should feel appropriate to unlock around level 3: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-038 — Welcome Sign
- Key: `welcome-sign`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Welcome Sign, a decorative sign/banner form with no baked readable text. Category: signage. It should feel appropriate to unlock around level 2: simple and affordable. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-039 — Open Hours Sign
- Key: `open-hours-sign`
- Priority: **P1**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Open Hours Sign, a decorative sign/banner form with no baked readable text. Category: signage. It should feel appropriate to unlock around level 4: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

### GB-MASTER-DECOR-040 — Club Banner
- Key: `club-banner`
- Priority: **P2**
- Method: **3d-first**
- Phase: **3D-4**
- Status: **TODO**

**Prompt**

> Original GreenBusiness asset. Stylized 3D diorama management-game art, Botanical Workshop Diorama direction, clean readable silhouette, matte forest-green and neutral materials, warm practical lighting, restrained cream and gold accents, contemporary small-business aesthetic, premium but approachable, original IP, no text, no watermark, no cyberpunk, no photorealism. Create Club Banner, a decorative sign/banner form with no baked readable text. Category: signage. It should feel appropriate to unlock around level 8: more distinctive and refined. Isolated Blender-master prop with correct floor/wall pivot; export approved fixed-camera isometric WebP/AVIF runtime asset, no readable text.

---

## STORE

### GB-MASTER-STORE-001 — Starter Cosmetic Bundle
- Key: `starter-cosmetic-bundle`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Store**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create a 4:5 store illustration presenting a cohesive starter-room cosmetic set, decorative only, no gameplay-power implication, leave clean space for HTML title/price. No baked price or readable marketing copy.

### GB-MASTER-STORE-002 — Credits S
- Key: `credits-small`
- Priority: **P1**
- Method: **vector-first**
- Phase: **Store**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create a small premium-credit pack icon using the approved premium currency symbol and a restrained small-stack composition. No baked price or readable marketing copy.

### GB-MASTER-STORE-003 — Credits M
- Key: `credits-medium`
- Priority: **P1**
- Method: **vector-first**
- Phase: **Store**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create a medium premium-credit pack icon using the approved premium currency symbol and a clearly larger stack than Credits S. No baked price or readable marketing copy.

### GB-MASTER-STORE-004 — Credits L
- Key: `credits-large`
- Priority: **P1**
- Method: **vector-first**
- Phase: **Store**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Create a large premium-credit pack icon using the approved premium currency symbol and a clearly larger premium stack than Credits M. No baked price or readable marketing copy.

### GB-MASTER-STORE-005 — Founder/Supporter Pack
- Key: `founder-supporter-pack`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Store**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create a 4:5 supporter-pack illustration using brand motifs, tasteful cosmetics and badge/plate elements, communicating support and identity rather than competitive advantage. No baked price or readable marketing copy.

---

## MISSIONS

### GB-MASTER-MISSION-001 — Arc Key Art — Open the Doors
- Key: `open-the-doors`
- Priority: **P1**
- Method: **2d-first**
- Phase: **Missions**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create 16:9 key art for the Open the Doors mission arc: modest starter workshop, first active crop, small order cue and sense of opening the business. No baked text, leave UI-safe negative space.

### GB-MASTER-MISSION-002 — Arc Key Art — Reliable Supply
- Key: `reliable-supply`
- Priority: **P2**
- Method: **2d-first**
- Phase: **Missions**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create 16:9 key art for the Reliable Supply mission arc: more organized room, multiple active production cycles and dependable supply rhythm. No baked text, leave UI-safe negative space.

### GB-MASTER-MISSION-003 — Arc Key Art — Signature Line
- Key: `signature-line`
- Priority: **P2**
- Method: **2d-first**
- Phase: **Missions**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create 16:9 key art for the Signature Line mission arc: three distinct varieties displayed as an intentional product lineup, stronger visual identity and refined room. No baked text, leave UI-safe negative space.

### GB-MASTER-MISSION-004 — Arc Key Art — Neighborhood Standard
- Key: `neighborhood-standard`
- Priority: **P2**
- Method: **2d-first**
- Phase: **Missions**
- Status: **TODO**

**Prompt**

> Original GreenBusiness game art. Stylized 2.5D premium management-game illustration, Botanical Workshop Diorama direction, clean readable forms, soft controlled shading, forest green, warm cream and restrained gold accents, original IP, no text, no watermark, no photorealism. Create 16:9 key art for the Neighborhood Standard mission arc: busy mature local business, organized inventory, trusted-client atmosphere and visible professional growth. No baked text, leave UI-safe negative space.

---

## MASTERY

### GB-MASTER-MASTERY-001 — Starter Mastery Badge Set
- Key: `n/a`
- Priority: **P1**
- Method: **vector-first**
- Phase: **UI**
- Status: **TODO**

**Prompt**

> Original GreenBusiness vector asset. Minimal rounded-geometric game UI style, strong silhouette, SVG-friendly, readable at small size, original IP, no text unless explicitly required. Design a 3-tier mastery badge family. Same core emblem evolves through shape complexity and framing, not color alone. Tier 1 simple, tier 2 expanded, tier 3 prestigious but restrained.
