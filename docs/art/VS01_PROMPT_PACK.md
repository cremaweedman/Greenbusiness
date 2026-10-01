# VS-01 PROMPT PACK — GREENBUSINESS

Status: SOURCE PROMPTS / NOT PRODUCTION ART
Canon:
- 04_ART_BIBLE_AND_ASSET_SPEC_GREENBUSINESS_v1.0.md
- 05_VS01_ASSET_MANIFEST_TEMPLATE.json

These prompts are generation briefs. Generated output must still pass the production pipeline and manual review.

## Global style prefix

Use this semantic prefix for all raster generation:

> Original GreenBusiness game asset. Stylized 2.5D premium management-game illustration. Clean readable forms, simplified believable geometry, crisp silhouette, moderate detail, soft controlled shading, premium but approachable botanical-business aesthetic. Deep forest green, muted green, warm cream and restrained gold accents. Contemporary and organized, optimistic rather than gritty. No photorealism.

## Global negative constraints

Always append semantically:

> No readable text, no letters, no numbers, no logos, no watermark, no signature, no cannabis-leaf symbol, no drug paraphernalia, no weapons, no police imagery, no celebrity likeness, no cyberpunk neon overload, no photoreal rendering, no excessive bloom, no dirty industrial grime.

---

# P0

## GB-VS01-BRAND-001 — Primary emblem

Deliverable:
- vector concept
- original botanical-business symbol
- works at 24px

Prompt brief:

> Design a minimal original emblem for GreenBusiness, a fictional botanical business management game. Use a simple abstract growth motif built from geometric leaf-like or sprout-like forms combined subtly with a business/progression concept. Strong silhouette, compact geometry, rounded contemporary construction, suitable for SVG recreation and recognizable at 24 pixels. Use one-color first; color is secondary. Avoid literal cannabis leaves and avoid resemblance to existing eco or cannabis brands.

Production note:
AI raster output is reference only. Final asset should be manually recreated as SVG.

## GB-VS01-BRAND-002 — App icon

Prompt brief:

> Create an app-icon composition derived from the approved GreenBusiness emblem. Centered single mark, generous maskable safe zone, strong silhouette at 48 pixels, dark forest base with restrained mint or cream foreground and optional small gold accent. No wordmark and no tiny details.

---

## GB-VS01-ENV-001 — Starter Room

Prompt brief:

> Create the Starter Room background for GreenBusiness. A small but credible fictional botanical production business at the beginning of its progression. The room is clean, contemporary and organized but modest: simple modular shelving, storage, a small management desk, practical lighting, empty expansion space and clear production zones. Stylized 2.5D management-game environment, not realistic photography. Use a wide 16:9 composition with a central gameplay-safe area and side zones that can support independent HTML/UI overlays. Keep production slots and state-changing equipment mostly separate from the baked background. The room should visibly have room to improve.

Technical:
- 3840x2160 master
- 16:9
- no characters
- no baked UI

---

## GB-VS01-SLOT-001 — EMPTY

Prompt brief:

> Create the canonical empty starter production slot for GreenBusiness. Square transparent game asset, slightly elevated three-quarter camera, compact modular tray/rack designed for a fictional botanical management game. Simple dark-green coated structure, dark composite tray, minimal cream functional lighting and very restrained gold hardware. Modest starter-tier equipment, not luxury, not sci-fi. Empty substrate/tray clearly visible. Strong silhouette and broad shapes for readability at 128 pixels.

Critical:
This becomes the immutable geometry reference for all later slot states.

---

## GB-VS01-SLOT-002 — PLANTED

Reference:
GB-VS01-SLOT-001 approved master.

Prompt brief:

> Preserve the exact approved EMPTY slot geometry, camera, canvas, lighting direction and chassis. Modify only the internal production state: newly planted substrate with small clear planting markers or tiny fictional sprouts. It must read as an early planted state at thumbnail size without relying on text or color alone.

---

## GB-VS01-SLOT-003 — GROWING

Reference:
GB-VS01-SLOT-001 approved master.

Prompt brief:

> Preserve the exact approved starter-slot geometry, camera, canvas and chassis. Show active mid-growth fictional botanical foliage occupying roughly 40–60 percent of the usable tray volume. Healthy but unfinished. Keep plant silhouette clearly below the READY state. Functional light active. No additional machinery.

---

## GB-VS01-SLOT-004 — READY

Reference:
GB-VS01-SLOT-001 approved master.

Prompt brief:

> Preserve the exact approved starter-slot geometry, camera, canvas and chassis. Show a fully mature fictional crop occupying most of the tray, visibly ready for collection. Use fullness, silhouette and a small shape-based readiness indicator to communicate completion. A restrained warm/mint accent is allowed, but readiness must remain understandable without color alone. No text.

---

# Starter crops

## GB-VS01-CROP-001 — Aurora Drift

Canonical:
- key: aurora-drift
- traits: fast, efficient

Prompt brief:

> Create Aurora Drift, a fictional starter botanical variety for GreenBusiness. Compact broadleaf silhouette with rounded layered leaves, energetic upward posture and clean vivid green coloration. It should visually imply fast, efficient growth. Stylized game inventory icon, centered, isolated transparent background, readable at 64 pixels. Make it botanically plausible but clearly fictional and not identifiable as a controlled-substance cultivar.

## GB-VS01-CROP-002 — Ember Leaf

Canonical:
- key: ember-leaf
- traits: stable, resilient

Prompt brief:

> Create Ember Leaf, a fictional starter botanical variety for GreenBusiness. Taller sturdy spearleaf silhouette with elongated leaves and a stable symmetrical structure. Deep green base with a restrained warm amber accent in stems, tips or small non-literal botanical details. It should visually imply resilience and consistency. Stylized inventory icon, isolated transparent background, readable at 64 pixels.

## GB-VS01-CROP-003 — Moon Sprout

Canonical:
- key: moon-sprout
- traits: premium, night

Prompt brief:

> Create Moon Sprout, a fictional premium starter botanical variety for GreenBusiness. Bushy medium-height silhouette with layered oval leaves, dark forest-green body and restrained cool violet accents in veins or undersides. Elegant rather than magical; no glowing fantasy plant. Stylized inventory icon, isolated transparent background, readable at 64 pixels.

---

# Characters

## GB-VS01-CHAR-001 — Alex Rowan

Canonical:
- Neighborhood coordinator
- grounded

Prompt brief:

> Create Alex Rowan, an original adult character for GreenBusiness. Stylized 2.5D game portrait, not photoreal. Alex is a grounded neighborhood coordinator: practical, calm, credible and approachable. Contemporary simple workwear rather than laboratory clothing or executive luxury. Subtle utility details, green/cream neutral palette, relaxed posture, clear readable face and silhouette. The portrait should suggest someone who understands local operations and reliable business relationships. Half-body 4:5 composition with restrained environmental context.

Do not:
- turn Alex into a scientist
- make him a celebrity lookalike
- use hyperreal skin

## GB-VS01-CHAR-002 — Mira Vale

Canonical:
- Botanical product designer
- precise

Prompt brief:

> Create Mira Vale, an original adult character for GreenBusiness. Stylized 2.5D game portrait, not photoreal. Mira is a precise botanical product designer: observant, controlled, creative and professional. Contemporary product/design workwear with subtle crafted details, clean silhouette and restrained green/cream palette with a small gold accent. Her visual identity should read as design and product quality rather than laboratory science or influencer glamour. Half-body 4:5 composition with restrained environmental context.

Do not:
- glamour-first styling
- celebrity resemblance
- hyperreal skin

---

# P0 UI icon family

Global icon rule:

> Create a simple rounded-geometric UI glyph for GreenBusiness. Strong silhouette, minimal internal detail, visually consistent stroke/shape weight, SVG-friendly, readable at 16–64 pixels, no text.

## Cash
Concept:
- compact wallet / note / business-cash abstraction
- avoid dollar/euro glyph dependency if possible

## Premium currency
Concept:
- faceted seed/token/medallion
- distinct from cash
- premium without gambling-chip appearance

## Contract
Concept:
- document/card + simple handshake/check motif

## Upgrade
Concept:
- modular block/rack + upward chevron

## Mission
Concept:
- waypoint/flag/checklist hybrid

## Mastery
Concept:
- badge/leaf-ring progression mark

## Timer
Concept:
- simple clock/progress dial

## Inventory
Concept:
- storage crate/grid

## Ready
Concept:
- checkmark within harvest/box silhouette

## Warning
Concept:
- exclamation + structural alert shape
- must remain obvious without red

---

# P1 SLOT states

## LOCKED

> Preserve exact slot geometry. Add a clear structural closure or padlock-shaped overlay integrated with the slot silhouette. State must be understandable in grayscale.

## ATTENTION

> Preserve exact slot geometry. Show a shape-based warning marker attached to the slot and a subtle physical attention cue such as raised alert tab or interrupted indicator pattern. Do not rely only on red.

## BOOSTED

> Preserve exact slot geometry. Add a temporary enhancement cue using a secondary ring/bolt/light motif, without changing the underlying production hardware.

---

# Efficient Racks

## Tier I

> Create a modest practical starter rack upgrade for GreenBusiness. Simple modular construction, limited capacity, functional and affordable-looking, dark coated metal, minimal accents.

## Tier II

> Preserve the same rack family but show a clear functional improvement: better organization, additional support, cleaner lighting or increased modular capacity. Still practical rather than luxurious.

## Tier III

> Show the mature version of the same rack family. Highest efficiency and finish, visibly optimized, clean modular details and restrained premium accents. Do not turn it into futuristic laboratory sci-fi.

---

# Store art

## Starter Cosmetic Bundle

> Create a 4:5 store-card illustration presenting a small set of purely cosmetic GreenBusiness customization items. Cohesive starter-room decorative theme, premium presentation but no gameplay-power implication. Leave clear area for HTML product title and price outside the image. No text baked into art.

## Founder / Supporter Pack

> Create a 4:5 supporter-pack illustration for GreenBusiness using brand emblem motifs, tasteful room cosmetics and profile/badge-style decorative elements. It should communicate support and identity, not competitive advantage. No price, no text and no loot-box presentation.

---

# Mission key art

> Create a 16:9 onboarding mission illustration for GreenBusiness showing the early business loop symbolically: a modest production space, one active fictional crop, a small contract/order cue and a visible sense of first progression. No characters required. No baked text. Composition should support a UI title and CTA layered separately.

---

# Mastery badges

> Design a three-tier mastery badge family for GreenBusiness. Same core emblem evolves across tiers through shape complexity and framing, not just color. Tier 1 simple, Tier 2 expanded, Tier 3 prestigious but restrained. SVG-friendly and readable at 32 pixels.

