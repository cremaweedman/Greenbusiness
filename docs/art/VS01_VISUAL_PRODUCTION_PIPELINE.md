# VS-01 VISUAL PRODUCTION PIPELINE — GREENBUSINESS

Status: PRODUCTION WORKFLOW
Depends on:
- docs/canon/04_ART_BIBLE_AND_ASSET_SPEC_GREENBUSINESS_v1.0.md
- docs/canon/05_VS01_ASSET_MANIFEST_TEMPLATE.json

## 1. Goal

Produce VS-01 as a reproducible, reviewable visual pack for Closed Alpha without introducing visual drift or placeholder debt.

The pipeline is asset-driven. Every produced file must map to one manifest ID.

## 2. Production order

### Wave A — P0 visual foundation
1. Brand emblem
2. App icon
3. Starter Room background
4. Slot EMPTY
5. Slot PLANTED
6. Slot GROWING
7. Slot READY
8. Aurora Drift icon
9. Ember Leaf icon
10. Moon Sprout icon
11. Alex Rowan portrait
12. Mira Vale portrait
13. P0 UI icon set

### Wave B — P1 gameplay polish
1. LOCKED / ATTENTION / BOOSTED slot states
2. Efficient Racks I–III
3. Starter cosmetic bundle
4. Founder/supporter pack
5. Mission key art
6. Mastery badge set
7. Club and notification icons

Do not start Wave B before Wave A has a coherent approved visual language.

## 3. Asset lifecycle

Each asset follows:

TODO
-> CONCEPT
-> REVIEW
-> APPROVED
-> INTEGRATED

### TODO
Specification exists only.

### CONCEPT
One or more candidate directions exist. Not production-safe.

### REVIEW
Candidate selected and checked against:
- Art Bible
- original-IP requirement
- asset dimensions
- small-size readability
- consistency with sibling assets

### APPROVED
Source is frozen for the current version.

### INTEGRATED
Runtime export is in apps/web/public/assets and rendered by the frontend.

## 4. Review gate

Every raster asset must pass:

- composition;
- silhouette;
- palette;
- lighting;
- crop/canvas;
- anatomy/object integrity;
- unwanted text/logo check;
- artifact check;
- IP similarity check;
- 25% scale readability;
- mobile crop check;
- compression check.

Every SVG must pass:

- viewBox correctness;
- no embedded raster;
- no external font dependency;
- readable at 16, 24, 32, 48, 64 px;
- currentColor-compatible where practical;
- accessible semantic usage in frontend.

## 5. Source retention

For AI-assisted assets retain:

```
art/prompts/<asset-id>.md
art/source/<domain>/<asset-id>/
  candidate-01.*
  candidate-02.*
  approved-master.*
  notes.md
```

Do not put discarded generation output in runtime directories.

## 6. Runtime export

Runtime path:
`apps/web/public/assets/<domain>/...`

Raster:
- WebP default
- quality target 78–88 depending on artifacting
- strip unnecessary metadata
- preserve alpha only where needed

SVG:
- remove editor metadata
- normalize viewBox
- remove hidden layers
- minify after approval

## 7. P0 integration contract

The Closed Alpha frontend should consume asset paths through a central mapping rather than hardcoding paths throughout components.

Recommended file:

`apps/web/app/gameAssets.ts`

Example conceptual shape:

```ts
export const gameAssets = {
  environment: {
    starterRoom: "/assets/environment/gb_environment_starter-room_bg_default_v01.webp",
  },
  slots: {
    empty: "/assets/slots/gb_slot_starter_empty_default_v01.webp",
    planted: "/assets/slots/gb_slot_starter_planted_default_v01.webp",
    growing: "/assets/slots/gb_slot_starter_growing_default_v01.webp",
    ready: "/assets/slots/gb_slot_starter_ready_default_v01.webp",
  },
  crops: {
    "aurora-drift": "/assets/crops/gb_crop_aurora-drift_icon_default_v01.webp",
    "ember-leaf": "/assets/crops/gb_crop_ember-leaf_icon_default_v01.webp",
    "moon-sprout": "/assets/crops/gb_crop_moon-sprout_icon_default_v01.webp",
  },
  contacts: {
    "alex-rowan": "/assets/characters/gb_character_alex-rowan_portrait_default_v01.webp",
    "mira-vale": "/assets/characters/gb_character_mira-vale_portrait_default_v01.webp",
  },
} as const;
```

## 8. Canonical crop mapping

Current game-data mapping:

### Aurora Drift
Key: `aurora-drift`
Traits:
- fast
- efficient

Visual archetype:
- Broadleaf
- compact silhouette
- vivid green
- fastest-looking of the three
- clean, energetic leaf posture

### Ember Leaf
Key: `ember-leaf`
Traits:
- stable
- resilient

Visual archetype:
- Spearleaf
- taller structure
- elongated leaves
- restrained amber/warm accent
- sturdy silhouette

### Moon Sprout
Key: `moon-sprout`
Traits:
- premium
- night

Visual archetype:
- Veinleaf
- bushier silhouette
- dark green body
- restrained cool violet accent
- visually premium without glow-heavy fantasy styling

## 9. Canonical contact mapping

### Alex Rowan
Role: Neighborhood coordinator
Tone: grounded

Art direction:
- adult
- practical
- calm
- dependable
- neighborhood/business coordination rather than scientist archetype
- visually simple, credible contemporary workwear

Avoid:
- lab-coat scientist stereotype
- luxury executive stereotype
- hyperreal portrait

### Mira Vale
Role: Botanical product designer
Tone: precise

Art direction:
- adult
- design/product-oriented
- observant
- controlled and polished
- more visual/design cues than Alex

Avoid:
- generic influencer styling
- glamour-first portrait
- hyperreal portrait

## 10. Starter Room composition

The environment must support the existing web UX.

Required zones:
- central production/read area
- secondary storage zone
- management/desk zone
- optional inbox/contract visual anchor
- enough negative space to place HTML UI

Do not create a perspective that forces gameplay objects to be baked permanently into the background if they need independent state changes.

Preferred architecture:
- room background = static
- slots/equipment = layered independent assets
- UI = HTML/CSS above art

## 11. Slot production rule

Create SLOT-001 EMPTY first.

Once approved, all other slot states must be derivatives of that exact master geometry.

No independent regeneration of every state.

The following must remain fixed:
- camera
- framing
- chassis
- outer silhouette
- canvas
- anchor point
- shadow footprint

Only the state-specific contents and indicators should change.

## 12. Character consistency rule

Once Alex and Mira masters are approved:
- save face/shape reference sheets;
- future expressions/outfits must derive from approved identity;
- no fresh independent character reinterpretation.

## 13. Prompting strategy

Prompts must describe:
- gameplay function first;
- silhouette second;
- visual style third;
- palette/materials fourth;
- technical export requirements last.

Do not overprompt decorative detail.

Negative constraints must explicitly include:
- no text
- no logos
- no watermark
- no photorealism
- no cannabis leaf iconography
- no drug paraphernalia
- no celebrity likeness
- no cyberpunk neon overload

## 14. Asset acceptance scorecard

Score each candidate 0–2 in:

- function readability
- silhouette
- art-style match
- palette match
- sibling consistency
- small-size readability
- technical cleanliness
- originality

Maximum: 16.

Approval threshold:
- minimum 13/16
- no zero in originality, function readability or technical cleanliness

## 15. Frontend acceptance

After each integrated batch:

```
cd apps/web
npm run lint
npm run typecheck
npm test
npm run build
```

Then:
- desktop visual smoke;
- 390px mobile visual smoke;
- reduced-motion check;
- dark/high-contrast readability check.

## 16. Performance budget

Initial target:
- environment background <= 450 KB runtime
- character portrait <= 180 KB each
- slot state <= 140 KB each
- crop icon <= 70 KB each
- SVG glyph <= 8 KB each

Treat these as targets, not permission to visibly damage art quality.

## 17. VS-01 stop condition

Stop art expansion when:
- all P0 assets are INTEGRATED;
- no placeholder dominates the five-minute loop;
- visual language is coherent enough for Closed Alpha feedback.

Do not produce a huge content library before alpha feedback.
