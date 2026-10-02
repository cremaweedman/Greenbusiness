# P10-ART-2 — STARTER CROPS PRODUCTION GATE

Status: IN PROGRESS  
Target: Aurora Drift / Ember Leaf / Moon Sprout  
Runtime states: PLANTED / GROWING / FLOWERING / READY

## Production contract

ART-2 is complete only when all three starter crop identities have:
- one approved READY production master;
- one approved FLOWERING state derived from that identity;
- one approved GROWING state derived from that identity;
- one approved PLANTED state derived from that identity;
- matching fixed camera, lighting, anchor, scale and transparent background;
- mobile readability at 360–430 CSS px;
- optimized runtime exports committed under `apps/web/public/assets/crops/`;
- runtime manifest entries;
- in-room integration in the completed Starter Room;
- frontend/compose/security gates green.

## Batch

Canonical Asset Factory batch:

`tools/asset_factory/batches/P10-ART-2.json`

Expected shape:
- 3 crop identities
- 4 visual states
- 4 candidates per state
- 48 deterministic jobs

Production order:
1. READY candidate generation;
2. approve 1 READY per crop;
3. FLOWERING from approved identity;
4. GROWING from approved identity;
5. PLANTED from approved identity;
6. runtime export + integration.

## Current blocker

The approved Aurora Drift, Ember Leaf and Moon Sprout concept sheets were approved conversationally but are not currently committed as binary reference files in the repository.

Do not mark ART-2 complete until either:
- those approved reference sheets are committed; or
- new production masters are explicitly approved and committed as the canonical replacement references.

The absence of concept binaries must not be hidden by placeholder runtime art.

## Runtime naming

Recommended canonical paths:

```text
/apps/web/public/assets/crops/
  gb_crop_aurora-drift_planted_v01.webp
  gb_crop_aurora-drift_growing_v01.webp
  gb_crop_aurora-drift_flowering_v01.webp
  gb_crop_aurora-drift_ready_v01.webp
  gb_crop_ember-leaf_planted_v01.webp
  gb_crop_ember-leaf_growing_v01.webp
  gb_crop_ember-leaf_flowering_v01.webp
  gb_crop_ember-leaf_ready_v01.webp
  gb_crop_moon-sprout_planted_v01.webp
  gb_crop_moon-sprout_growing_v01.webp
  gb_crop_moon-sprout_flowering_v01.webp
  gb_crop_moon-sprout_ready_v01.webp
```

## Acceptance

ART-2 closes only after:
- 12 runtime crop assets exist;
- no placeholder or missing-file fallback is used for starter crops;
- all 12 appear correctly in the Starter Room;
- READY states are clearly distinguishable from FLOWERING;
- Aurora / Ember / Moon remain distinguishable at phone scale;
- initial room + active crop payload remains within the mobile budget;
- CI and Security Scan are green.
