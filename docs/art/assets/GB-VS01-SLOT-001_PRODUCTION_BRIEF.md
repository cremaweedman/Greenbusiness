# GB-VS01-SLOT-001 — STARTER SLOT EMPTY — PRODUCTION BRIEF

Status: SPEC READY
Manifest ID: GB-VS01-SLOT-001
Priority: P0
Role: canonical geometry master for all starter-slot states

## 1. Purpose

This asset defines the immutable visual chassis for the starter production-slot family.

Every later state:
- PLANTED
- GROWING
- READY
- LOCKED
- ATTENTION
- BOOSTED

must derive from this exact approved geometry.

No later state may independently reinterpret the slot.

## 2. Visual direction

Canonical direction:
**Botanical Workshop Diorama**

The slot must look like:
- affordable starter-business equipment;
- contemporary;
- modular;
- practical;
- clean;
- mildly stylized;
- visually upgradeable.

It must NOT look like:
- futuristic laboratory hardware;
- premium sci-fi machinery;
- luxury furniture;
- industrial factory equipment;
- photoreal cultivation hardware.

## 3. Camera

Fixed:
- three-quarter view;
- mild elevated angle;
- no extreme isometric distortion;
- front and one side visible;
- tray/interior clearly visible.

The camera used here becomes canonical for the slot family.

## 4. Silhouette

Primary silhouette:
- compact rectangular grow module;
- low-to-medium height;
- sturdy outer frame;
- open central tray;
- simple top task-light or frame element allowed if visually modest.

At 128px:
- outer frame must remain readable;
- tray opening must remain obvious;
- no dependence on micro-detail.

## 5. Geometry

Required:
- fixed square master canvas;
- centered object;
- consistent ground/shadow footprint;
- generous transparent margin;
- no decorative foliage attached to chassis;
- no baked crop state;
- no moving-state effects.

Recommended object occupancy:
- 72–80% of canvas width;
- 68–78% of canvas height.

## 6. Materials

Preferred:
- matte dark-green painted metal;
- dark composite/plastic tray;
- small cream functional light;
- small muted-brass fasteners only if needed.

Avoid:
- chrome;
- glass-heavy construction;
- luminous sci-fi panels;
- holograms;
- gold framing as a dominant material;
- exposed complex machinery.

## 7. Palette

Base:
- GB Forest 900 #102016
- GB Forest 700 #244D2E
- GB Forest 500 #547A5D

Secondary:
- GB Cream 100 #F4F0E6

Accent:
- GB Gold 300 #E0BA78 — maximum ~5% of visible asset area

The slot should still read correctly in grayscale.

## 8. EMPTY state cues

The asset must communicate:
- usable;
- currently empty;
- ready to receive a starter crop.

Use:
- visible empty tray/substrate surface;
- inactive or low-intensity task lighting;
- open access.

Do not use:
- text;
- giant plus symbols;
- bright readiness effects;
- warning colors.

## 9. Technical specification

Master:
- 1536 × 1536 minimum
- transparent background
- sRGB
- clean alpha
- no baked floor/background

Runtime:
- 512 × 512 WebP
- optional 256 × 256 WebP

Runtime target:
- <= 140 KB where visually acceptable

Filename:
`gb_slot_starter_empty_default_v01.webp`

Runtime path:
`apps/web/public/assets/slots/gb_slot_starter_empty_default_v01.webp`

## 10. Canonical anchor

Anchor:
- visual center x = 50%
- ground contact baseline ≈ y 82%
- shadow footprint centered under chassis

Every sibling state must preserve:
- canvas dimensions;
- camera;
- chassis position;
- scale;
- footprint;
- baseline.

## 11. State derivation contract

PLANTED:
- same chassis
- only tray content/state changes

GROWING:
- same chassis
- foliage added inside tray

READY:
- same chassis
- mature crop + restrained shape-based ready cue

LOCKED:
- same chassis
- structural closure/overlay

ATTENTION:
- same chassis
- warning element attached to slot

BOOSTED:
- same chassis
- temporary enhancement cue

## 12. Negative constraints

Reject any candidate with:
- photorealism;
- cannabis-leaf symbolism;
- real-brand resemblance;
- sci-fi lab language;
- excessive gold;
- excessive glow;
- decorative plants permanently attached to chassis;
- unreadable tray opening;
- asymmetric camera drift;
- text/logo/watermark/signature;
- AI geometry errors;
- impossible supports;
- inconsistent perspective.

## 13. Review views required

Before approval inspect at:
- 1536px
- 512px
- 256px
- 128px
- grayscale
- dark UI background

## 14. Approval gate

Minimum:
- 13/16 QA score;
- originality >= 1;
- function readability = 2;
- technical cleanliness = 2;
- sibling-family readiness = 2.

## 15. Production sequence

1. produce 3–5 rough concepts;
2. choose one geometry only;
3. refine selected geometry;
4. normalize camera/canvas;
5. approve master;
6. export runtime;
7. set manifest asset to APPROVED;
8. only then derive SLOT-002/003/004.

No PLANTED/GROWING/READY production before SLOT-001 is approved.
