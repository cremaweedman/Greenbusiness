# 07 — BUILD HANDOFF — GREENBUSINESS

**Version:** 1.0  
**Purpose:** Single canonical continuation point for any developer, coding agent or future ChatGPT/Work session.  
**Repository:** cremaweedman/Greenbusiness  
**Branch:** main  
**Current state:** Phase 9 is completed. Phase 10 Closed Alpha is in progress on `feat/p10-m1-closed-alpha`.

---

# 1. Product mission

Build an original modern spiritual successor to the design strengths of the 2011 Facebook game Weeds Social Club without copying the Weeds IP.

Working product concept:
- adult social management/tycoon game;
- original fictional botanical/cannabis-adjacent regulated business universe;
- asynchronous production timers;
- contracts/economy;
- RPG-style skills;
- collection/mastery;
- room decoration;
- episodic LiveOps;
- clubs/cooperation;
- ethical F2P monetization.

The product must be able to stand on its own without Weeds branding.

---

# 2. Canon priority

When documents conflict, use this priority:

1. `00_MASTER_CANON_INDEX.md`
2. `01_GDD_GREENBUSINESS_v1.0.md`
3. `02_TDD_ECONOMY_GREENBUSINESS_v1.0.md`
4. `03_PRODUCTION_BUILD_SPEC_GREENBUSINESS_v1.0.md`
5. `04_ART_BIBLE_AND_ASSET_SPEC_GREENBUSINESS_v1.0.md`
6. `05_VS01_ASSET_MANIFEST_TEMPLATE.json`
7. `06_IMPLEMENTATION_ROADMAP.md`
8. this `07_BUILD_HANDOFF.md`

Research material is evidence/context, not authority over the canon.

Never silently invent a rule when the canon is explicit.

---

# 2.1 Canonical presentation decision — 2D/2.5D runtime

**Status: ACCEPTED — overrides the temporary real-time 3D spike.**

GreenBusiness ships its core gameplay as a premium 2D/2.5D isometric management interface. The room may be authored from 3D masters, but runtime gameplay uses optimized layered raster/vector assets rather than a continuously rendered WebGL scene.

Canonical pipeline:

```text
Concept / reference
  -> Blender / Meshy / Tripo when useful
  -> canonical 3D master in Blender
  -> fixed isometric camera + lighting
  -> deterministic state renders
  -> WebP / AVIF / SVG runtime assets
  -> Next.js layered scene + HTML UI + lightweight effects
```

Rules:
- the player must not need orbit/pan camera controls for the core loop;
- gameplay state remains DOM/API driven and server-authoritative;
- room, slot, crop, upgrade and decoration assets preserve fixed camera, scale and anchors;
- 3D masters are production sources, not mandatory runtime payloads;
- Three.js/R3F is experimental only unless a later ADR explicitly re-approves it;
- mobile/PWA performance and state readability take priority over real-time 3D fidelity;
- `StarterRoom3DScene.tsx` is an experiment, not the target presentation architecture.

Canonical runtime document: `docs/art/2D_RUNTIME_ARCHITECTURE_V1.md`.

---

# 2.2 Canonical platform decision — mobile portrait first

**Status: ACCEPTED.**

GreenBusiness is designed primarily for mobile portrait use. Desktop and tablet are secondary adaptations.

Baseline:
- canonical viewport: ~390×844 CSS px;
- required phone width range: 360–430 px;
- portrait information architecture is authoritative;
- bottom navigation is the primary global navigation;
- contextual gameplay detail opens in bottom sheets;
- no persistent left sidebar on mobile;
- no core action may exist only on desktop;
- minimum tap target: 44×44 CSS px;
- safe-area insets and virtual keyboard behavior must be tested;
- the Starter Room art composition is authored for narrow portrait framing first.

Canonical UX document: `docs/MOBILE_FIRST_UX_V1.md`.

---

# 3. Frozen architectural direction

Initial production stack:

```text
Client / Web
  Next.js + TypeScript
        |
        v
API
  FastAPI + Python
        |
        +--> PostgreSQL
        |
        +--> Redis only where justified
        |
        +--> Object storage adapter (S3-compatible)
        |
        +--> Analytics / error monitoring
```

Deployment:
- Docker
- Docker Compose for dev
- Nginx/reverse proxy
- staging mirrors production topology where practical
- managed PostgreSQL preferred in production
- no Kubernetes before operational need

Game/economy:
- server-authoritative
- append-only economy ledger
- idempotent economy endpoints
- server timestamps
- server RNG for consequential outcomes
- versioned remote config

---

# 4. Frozen MVP scope

Must build:
- 1 isometric business location
- 10–12 fictional varieties
- plant -> timer -> optional care -> harvest
- contracts
- Cash + XP/Reputation
- 20–25 levels
- 3 compact skill trees
- upgrades
- inventory
- 40–60 decorations
- 25–40 missions
- basic clubs
- weekly club objective
- LiveOps config
- analytics
- admin panel
- push
- account/auth
- purchases/entitlements after retention instrumentation

Do not build in MVP:
- PvP
- free P2P marketplace
- open chat
- NFTs/Web3
- cash-out
- paid loot boxes
- complex UGC
- multiple giant districts
- microservices/Kubernetes

---

# 5. Non-negotiable legal/product constraints

- Do not use Weeds Social Club as the shipped product name.
- Do not copy Weeds characters, dialogue, art, logos, audio, missions or visual assets.
- Do not reproduce a pixel-identical UI.
- Avoid real cultivation instructions.
- Do not frame the gameplay around illegal dealing/evading police for store-facing builds.
- Treat 18+ as the working positioning until formal ratings/compliance review.
- No paid random rewards.
- No real-money transferable player assets.
- No cash-out economy.

---

# 6. Current repository state

Current repository status:

- repository and `main` exist;
- canonical ZIP exists and has passed integrity verification;
- executable source foundation exists under `apps/api`, `apps/web`, `packages/contracts` and `infra`;
- FastAPI + async SQLAlchemy + PostgreSQL + Alembic boot through Docker Compose;
- Next.js + TypeScript web shell boots behind Nginx;
- liveness/readiness endpoints are implemented;
- CI runs backend lint/tests/migration sanity, frontend lint/typecheck/tests/build and full Docker-stack smoke tests;
- Phase 0, P1-M1, P2-M1, P3-M1 and P3-M2 passed their acceptance gates;
- server-authoritative production, economy, timers, contract rotation and progression are implemented;
- Cash mutations are ledger-backed and economic mutations are idempotent;
- inventory supports aggregate quantities plus quality-specific lots;
- current contract system serves deterministic four-hour windows with 3 standard + 1 specialized offer;
- progression foundation supports levels 1–20, reputation, unlocks and skill-point hooks;
- Efficient Racks tiers I–III are versioned and prerequisite/level gated;
- backend/frontend/full-stack Docker E2E is green through P4-M2;
- 30 authored missions across 4 original narrative arcs are implemented;
- 4 original contacts are implemented;
- daily/weekly mission assignments persist per period;
- mastery supports 3 cosmetic-only thresholds;
- narrative history/inbox metadata is exposed to the frontend;
- P9 production hardening is implemented and validated;
- insecure production defaults fail closed;
- sandbox purchases/refunds/rewarded ads are disabled outside development/local/test;
- admin access uses short-lived admin JWTs with viewer/operator/superadmin role boundaries;
- sensitive auth/admin/store/social endpoints are rate limited with Redis required in production-like environments;
- CSP/security headers, exploit/replay logging and request correlation are implemented;
- push delivery tokens are encrypted at rest while retaining one-way hashes for dedupe;
- LiveOps config publishing is concurrency-safe through PostgreSQL advisory locking;
- social profile creation uses savepoints instead of full transaction rollback;
- request performance analytics are sampled and successful-request writes are dispatched asynchronously;
- service-worker caching is allow-listed and excludes `/api/`;
- API/web containers run non-root and the web image uses a minimal standalone runtime;
- backup/restore drill, privacy/terms/IP inputs and security disclosure docs are committed;
- dependency, filesystem, secret, misconfiguration and container scans are automated with Trivy;
- CI and Security Scan are green on the final P9 branch state.

Implementation is active. Documentation completeness must not be confused with full game completeness.

---

# 7. Mandatory implementation order

Follow `06_IMPLEMENTATION_ROADMAP.md`.

Immediate order:

```text
P0 Foundation
  -> P1 Identity & persistence
    -> P2 Core vertical slice
      -> P3 Economy/contracts/progression
        -> P4 Missions/narrative/collection
          -> P5 LiveOps/analytics/admin
            -> P6 Clubs
            -> P7 Monetization
              -> P8 UX/accessibility/push
                -> P9 Hardening
                  -> P10 Closed alpha
                    -> P11 Soft launch
                      -> P12 Release
```

Later phases may be mocked behind interfaces, but not fully implemented early.

---

# 8. Immediate task for the next build session

## Task ID
**P10-M1 — Content Completion & Closed Alpha — IN PROGRESS**

## Goal
Validate GreenBusiness with a small invited player cohort before expanding scope or entering soft launch.

## Alpha content target
- 1 complete district/location;
- 10–12 fictional varieties;
- 20–25 levels;
- 3 compact skill trees;
- 25–40 missions;
- 40–60 decorations;
- club weekly objective;
- minimum one LiveOps mini-arc;
- first complete economy configuration.

## Closed-alpha operating work
- finalize the playable content gaps required by the alpha target;
- seed/reset a clean alpha environment;
- invite a small instrumented cohort;
- capture tagged player feedback and bug reports;
- measure tutorial completion, first harvest, return-to-timer behavior and early D1/D7 cohorts;
- inspect economy source/sink behavior and affordability;
- inspect club adoption/retention impact;
- verify ethical cosmetic/supporter monetization value without P2W pressure;
- resolve blocker exploits/crashes before soft launch.

## Explicitly excluded from P10-M1
- paid user acquisition;
- worldwide/public launch;
- open chat;
- free P2P marketplace;
- Web3/NFT/cash-out;
- Kubernetes/microservices;
- production iOS release before policy review.

---

# 9. P10-M1 acceptance criteria

Do not mark P10-M1 complete until:
- alpha content target is materially complete;
- invited-user feedback is tagged and triaged;
- economy exploits found in alpha are resolved;
- tutorial completion is measurable;
- D1 and early D7 cohorts are measurable;
- crash/API blocker issues are resolved or explicitly blocking;
- no blocker remains that prevents Phase 11 soft launch;
- backend/frontend/full-stack CI remains green.

**Current status:** technical alpha baseline implemented and validated; real invited-cohort execution remains pending.

---

# 10. Engineering conventions

## Backend
- typed Python
- service/domain separation where it reduces coupling
- no business logic inside route handlers
- DB constraints for invariants
- transactions for economy mutations
- UTC internally
- UUIDs or equivalent non-sequential public identifiers
- explicit API versioning: `/v1`

## Frontend
- strict TypeScript
- no direct DB logic
- API contracts generated/shared where practical
- mobile-first
- accessibility from base components
- avoid premature global state complexity

## Database
- Alembic only; no production `create_all`
- migrations reversible where practical
- indexes tied to actual query patterns
- money-like virtual values stored as integers
- audit/economy ledgers append-only

## Tests
Critical invariants receive tests even if coverage percentage is modest.

Priority tests:
1. idempotency;
2. duplicate harvest prevention;
3. balance/ledger consistency;
4. auth token rotation;
5. timer authority;
6. receipt replay prevention;
7. club reward duplication prevention;
8. remote config versioning.

---

# 11. Economy invariants

Every economic mutation must be explainable.

Each ledger event should preserve at minimum:
- transaction_id
- user/player
- currency
- amount
- source_or_sink
- reference entity
- config version
- experiment assignment if relevant
- balance_before
- balance_after
- created_at

Never implement only:
```text
player.cash += reward
```

without a canonical transaction record.

---

# 12. Timer invariants

- server sets start and ready timestamps;
- client clock cannot complete a production;
- reconnect derives state from server time;
- late return does not destroy production;
- optional care windows add bonuses but do not block baseline completion;
- harvest endpoint is idempotent.

---

# 13. Definition of a completed development slice

At the end of every slice:
1. code committed;
2. tests green;
3. E2E relevant to the slice green;
4. migrations committed;
5. docs/contracts updated when required;
6. no secrets;
7. handoff state updated below;
8. next task written explicitly.

---

# 14. Handoff state block

Future agents/sessions must update this section after meaningful implementation.

## Current phase
`Phase 10 — Content Completion & Closed Alpha`

## Current milestone
`P10-ART-2 — Starter Crops via Asset Factory — IN PROGRESS`

## Completed
- research and product reconstruction;
- original successor direction established;
- GDD/TDD/production/art canon prepared;
- canonical ZIP v1.1 uploaded and integrity checked;
- implementation roadmap and build handoff prepared;
- P0-M1 repository foundation implemented;
- FastAPI/PostgreSQL/Alembic foundation implemented;
- Next.js/TypeScript frontend shell implemented;
- Docker Compose + Nginx stack implemented;
- backend/frontend/full-stack CI validated;
- P0-M2 canonical errors, audit events, object storage and API versioning implemented;
- P1-M1 identity/auth/session/bootstrap implemented and validated;
- P2-M1 3-slot production loop, inventory, quality and tutorial implemented and validated;
- P3-M1 wallet, ledger, starter contract, idempotency and first upgrade implemented and validated;
- P3-M2 economy config advanced to `economy_v2`;
- 10 versioned quick/standard/premium contract definitions implemented;
- contract board generates deterministic 4-hour windows with 3 standard + 1 specialized offer;
- maximum 3 active contracts enforced server-side;
- accepted contracts snapshot quantity, quality, trait, rewards and config version;
- inventory quality lots implemented and quality requirements consumed transactionally;
- starter varieties now expose fictional traits for contract matching;
- contract completion grants reputation server-side while preserving ledger-backed Cash;
- 20-level XP foundation and level unlock table implemented;
- Botany / Commerce / Operations skill-point hooks and persistent branch rows implemented;
- Efficient Racks tiers I–III implemented with level/prerequisite gates and cumulative server-side yield bonus;
- P3-M2 frontend exposes offer refresh, locks, multiple active contracts, reputation/level/skill points and upgrade tiers;
- integration tests cover deterministic rotation, active-contract limit, quality lots and progression;
- full Docker E2E covers 4-offer board, active-contract limit and persisted progression state;
- final P3-M2 branch CI is green: backend, frontend and compose-smoke;
- P4-M1 versioned mission engine implemented;
- 10 sequential starter missions implemented with plant/care/harvest/contract/Cash/upgrade objectives;
- mission progress is driven only by authoritative production/economy actions;
- mission event receipts prevent duplicate progress and rewards;
- mission Cash rewards reuse the append-only economy ledger;
- mission XP/reputation rewards reuse the existing progression model;
- original contacts Alex Rowan and Mira Vale implemented with phone-style presentation;
- deterministic daily (2) and weekly (3) mission-pool foundations implemented;
- variety mastery implemented from authoritative harvest quantity and contract consumption;
- cosmetic-only mastery hooks implemented at versioned thresholds;
- player state/API/frontend now expose contacts, missions, pools, mastery and cosmetic hooks;
- integration tests cover persistence, reward idempotency and mastery replay protection;
- full Docker E2E covers plant -> care -> harvest -> mission rewards -> mastery -> replay protection;
- final P4-M1 branch CI is green: backend, frontend and compose-smoke;
- P4-M2 mission catalog expanded to 30 authored missions;
- P4-M2 narrative content spans 4 original arcs and 4 original contacts;
- mission definitions are versioned as `missions_v2`;
- persisted daily/weekly mission assignments implemented with migration `0008_narrative_collection`;
- story missions remain permanent and are not deleted by missed periods;
- mission response now exposes arc metadata and inbox/history copy;
- variety mastery now has three cosmetic-only thresholds;
- variety-specific mission objectives filter authoritative plant/harvest events correctly;
- PostgreSQL tests cover mission-pool persistence, mastery thresholds and replay protection;
- frontend exposes narrative arcs, completion history/inbox messages and mastery cosmetic counts;
- final P4-M2 branch CI is green: backend, frontend and compose-smoke.
- P5-M1 LiveOps/admin foundation started;
- migration `0009_liveops_admin_analytics` adds immutable LiveOps config versions and analytics events;
- active LiveOps config is exposed through `/v1/liveops/config`;
- remote config payload now includes seasons, featured traits, content toggles, event windows, notification copy, kill switches and experiments;
- deterministic authenticated experiment assignments are exposed through `/v1/liveops/experiments`;
- admin access is separated from player JWTs through `X-Admin-Key`;
- admin endpoints added for active config, config publish, config rollback, player lookup, economy dashboard, core-funnel dashboard and recent analytics events;
- published config versions are not mutated; rollback creates a new active version restored from an earlier version;
- production, contract and upgrade actions are guarded by LiveOps feature flags/kill switches;
- active LiveOps contract multipliers now change newly generated contract rewards and are snapshotted into accepted contracts;
- admin config history endpoint exposes immutable published/restored versions;
- admin ledger inspection endpoint exposes recent economy ledger entries, optionally filtered by player;
- audited admin Cash grant/revoke endpoints implemented for dev/test operations;
- economy dashboard now includes wallet distribution buckets in addition to minted/burned totals;
- auth, production and economy core actions emit canonical analytics events with payload sanitization;
- mission completion now emits canonical analytics events;
- request middleware records best-effort performance analytics and failed-request error analytics without storing credentials;
- admin core-loop dashboard added for tutorial, production, contract, upgrade, mission and failed-request funnel counts;
- P5-M1 integration test extended for publish, feature disable, rollback, audit trail, analytics emission, admin Cash mutation, ledger inspection and economy dashboard;
- P5-M1 Docker/PostgreSQL validation passed with Alembic head, full backend pytest, backend Ruff, frontend lint/typecheck/test and HTTP smoke checks;
- P6-M1 Social Layer: Clubs implemented;
- migration `0010_social_clubs` adds social profiles, friendships, clubs, memberships, club invites, weekly objectives, contribution ledger, assists, structured reactions and club reward claims;
- authenticated social endpoints expose `/v1/social/me`, `/v1/social/profile`, friend list and friend-code redemption with deep-link payloads;
- authenticated club endpoints expose create, join by invite code, leave, invite, accept/decline invite, contribute, assist, react and claim reward flows;
- club membership is capped at 30 members and every player is limited to one active club;
- weekly club objective progress is driven by an idempotent contribution ledger keyed by event keys;
- limited assists enforce one assist per helper/receiver/week and a hard weekly helper cap;
- structured club reactions are constrained to an allow-list and are idempotent per target;
- club rewards are claim-once per player/objective and write to the append-only economy ledger;
- LiveOps remote config now has an independent `clubs` feature flag and kill switch;
- frontend exposes a Clubhouse panel with friend code, friend count, current club, invite code and weekly objective state;
- P6-M1 integration test covers friend codes, invite accept, idempotent contribution, assist abuse limit, completed objective, idempotent reaction, idempotent reward claim and LiveOps clubs feature-disable behavior;
- P6-M1 Docker/PostgreSQL validation passed with Alembic head, full backend pytest, backend Ruff, frontend lint/typecheck/test, production web build and HTTP smoke checks;
- P7-M1 Monetization & Entitlements implemented;
- migration `0011_monetization_entitlements` adds premium wallets, purchase ledger and player entitlements;
- versioned `store_v1` catalog includes Starter Cosmetic Bundle, Credits S/M/L and Founder/Supporter Pack;
- `/v1/store/catalog` exposes deterministic product metadata and keeps Season Pass disabled;
- `/v1/store/me` exposes persistent premium credits, entitlements and purchase history;
- `/v1/store/purchases/validate` validates sandbox receipts server-side and prevents duplicate/replayed receipts;
- purchase ledger records provider, receipt id, receipt hash, product, credit delta, entitlement grants and status;
- premium credits are deterministic and never randomize paid rewards;
- cosmetics/supporter/no-ads entitlements persist by user and survive session/device changes;
- `/v1/store/purchases/{purchase_id}/refund` reverses credits when safe and revokes entitlements idempotently;
- `/v1/store/rewarded-ads/claim` adds an idempotent rewarded-ad framework without requiring ads for core play;
- player bootstrap response now exposes `premium_credits` and active entitlement keys;
- frontend exposes an ethical monetization sandbox panel with Credits balance, catalog products and sandbox purchase buttons;
- P7-M1 integration test covers catalog, invalid receipt rejection, receipt replay prevention, cross-user receipt theft block, entitlement grant, refund/revocation, premium-credit reversal and rewarded-ad idempotency;
- P7-M1 validation passed with Alembic head, full backend pytest, backend Ruff, frontend lint/typecheck/test and production web build;
- P8-M1 Push, Cross-Platform UX & Accessibility implemented;
- migration `0012_notifications_accessibility` adds notification preferences and push token registry tables;
- authenticated notification endpoints expose `/v1/notifications/me`, `/v1/notifications/preferences`, `/v1/notifications/push-tokens` and `/v1/notifications/push-tokens/{token_id}/disable`;
- `/v1/platform/readiness` documents PWA installability, Android packaging path, iOS adapter path and iOS policy-review requirement;
- push token values are stored as hashes with non-secret labels for display;
- notification categories for production, events/seasons and club/social can be independently disabled;
- quiet hours default to 22:00-08:00 Europe/Madrid and reject invalid times;
- deep links are exposed for home, production, club and store;
- PWA manifest, maskable SVG icon, offline page and service worker read cache are implemented;
- service worker avoids intercepting `/api/` and keeps core gameplay usable without push;
- frontend exposes a notification/accessibility panel with independent toggles, quiet-hours copy and non-coercive copy;
- premium sandbox purchases require explicit confirmation before validating the receipt;
- timer displays now include absolute ready timestamps in addition to relative countdowns;
- keyboard focus-visible outlines, reduced-motion CSS, scalable text baseline, aria labels and color-independent On/Off indicators are implemented;
- P8-M1 integration test covers notification defaults, preference updates, invalid quiet-hour rejection, push-token replay/idempotency, token disable, unsupported platform rejection and platform readiness;
- P8-M1 validation passed with Alembic head, full backend pytest (`28 passed`), backend Ruff, frontend lint/typecheck/test and production web build;
- P9-M1 production-like configuration now fails closed on weak JWT/admin secrets, development DB credentials, insecure cookies, creator access, sandbox monetization, disabled rate limiting, non-Redis production rate limiting and missing push-token encryption;
- creator access is opt-in and development/local/test only;
- sandbox purchase, refund and rewarded-ad flows are development/local/test only and production provider paths fail closed;
- receipt replay/cross-user abuse and rate-limit abuse emit sanitized security events;
- admin bootstrap exchanges a strong key for short-lived admin JWTs and role boundaries separate viewer/operator/superadmin capabilities;
- sensitive auth/admin/store/social routes have explicit abuse limits with Redis-backed production enforcement;
- API/Nginx security headers and CSP are present;
- push tokens now persist encrypted ciphertext plus a dedupe hash/label;
- LiveOps config version allocation is serialized with a PostgreSQL advisory transaction lock;
- social-code allocation uses nested transactions/savepoints and friend/invite codes use a larger entropy space;
- request analytics sampling is configurable and successful-request telemetry is dispatched asynchronously;
- service-worker read cache is allow-listed and excludes API traffic;
- API and web containers run as non-root users;
- web runtime uses Next standalone output and removes npm/dev dependency trees from the final image;
- automated Security Scan covers filesystem vulnerabilities, secrets, misconfiguration and API/web images;
- backup/restore drill helper, security disclosure, hardening runbook and privacy/terms/IP input docs are committed;
- final P9 CI is green: backend, frontend and compose-smoke;
- final P9 Security Scan is green.
- P10 technical alpha baseline is implemented on `feat/p10-m1-closed-alpha`;
- fictional variety catalog expanded to 10 entries with server-authoritative level gates;
- three compact skill trees are functional: Botany boosts yield, Commerce improves contract Cash, Operations reduces grow time;
- 40-item cosmetic decoration catalog implemented with ledger-backed Cash purchase and persistent room equip slots;
- alpha feedback/bug reporting is persistent and severity-tagged, with admin triage;
- explicit invited alpha cohort membership prevents retention dashboards from being polluted by dev/creator accounts;
- alpha dashboard measures tutorial completion, first harvest, D1, D7 and open blocker/major feedback;
- first versioned Closed Alpha LiveOps mini-arc, Night Market Week, is authored and schema-tested;
- web app exposes skill allocation, decoration purchase/equip and Closed Alpha feedback submission;
- migrations `0014_alpha_feedback`, `0015_decorations` and `0016_alpha_cohort` are chained after P9;
- final P10 technical-baseline CI is green: backend, frontend and compose-smoke;
- final P10 technical-baseline Security Scan is green.

- Asset Factory v1 is implemented under `tools/asset_factory/`;
- canonical 93-asset prompt catalog remains the single source of truth;
- ART-2 batch derives Aurora Drift, Ember Leaf and Moon Sprout into READY/GROWING/PLANTED states;
- 4 deterministic candidates per state produce 36 reproducible generation jobs;
- ComfyUI API runner, HTML review sheet, approval template, runtime-manifest generation, unit tests and CI are included;

## In progress
- P0 #11 Moon Sprout Concept Sheet — approved with canonical notes;
- P0 #12 Starter Crops Comparison Board — current concept-art target;

- P0 #10 Ember Leaf Concept Sheet — approved with canonical notes;
- P0 #11 Moon Sprout Concept Sheet — current concept-art target;

- P0 #9 Aurora Drift Concept Sheet — approved with canonical notes;
- P0 #10 Ember Leaf Concept Sheet — current concept-art target;

- P0 #8 Slot States Board — approved with canonical notes;
- P0 #9 Aurora Drift Concept Sheet — current concept-art target;

- P0 #7 Starter Slot Master Concept — approved with canonical corrections;
- P0 #8 Slot States Board — current concept-art target;

- P0 #5 Starter Room Hero Concept — next concept-art target using the approved Master Style Board;

- P10-ART-1 production-quality 2.5D Starter Room vertical slice;
- final fixed-camera isometric room composition;
- deterministic slot/crop state renders;
- integration of optimized WebP/AVIF/SVG scene assets into the existing Next.js gameplay surface;
- real invited Closed Alpha cohort execution after the visual vertical slice is credible;
- alpha economy/pacing validation from measured player behavior;
- D1 and early D7 cohort observation;
- return-to-timer and club-adoption analysis;
- blocker/major feedback triage before Phase 11.

## Historical experiment
- the Three.js/React Three Fiber procedural Starter Room spike was implemented and validated as a technical experiment;
- the spike is not the production target;
- `docs/art/3D_RUNTIME_ARCHITECTURE_V1.md` is superseded;
- do not continue by replacing its primitives with runtime GLB assets.

## Next action
**EXECUTE P10-ART-2 — STARTER CROPS.** Use `tools/asset_factory/factory.py` to prepare the deterministic ART-2 batch, generate the READY candidates first, approve one identity per crop, then derive GROWING and PLANTED from the approved READY references. Do not mass-produce later crops before the three starter families pass mobile readability and style-consistency QA.

Local validation already passed without Docker:
- `python -m compileall apps\api\app apps\api\tests\integration\test_notifications_accessibility.py`
- `python -m ruff check apps\api\app apps\api\tests\integration\test_notifications_accessibility.py`
- `npm run lint`
- `npm run typecheck`
- `npm test`
- `npm run build`

Docker/PostgreSQL validation passed:
- `docker compose up --build -d`
- `docker compose exec -T api alembic upgrade head`
- `docker compose exec -T api pytest -q` (`28 passed`)
- `docker compose exec -T api ruff check .`
- `docker compose run --rm web npm run lint`
- `docker compose run --rm web npm run typecheck`
- `docker compose run --rm web npm test`
- `docker compose up --build -d` production web build
- HTTP smoke passed for `/api/health/live`, `/api/health/ready`, `/api/v1/system/ping`, `/api/v1/platform/readiness`, `/manifest.webmanifest`, `/offline.html` and `/sw.js`.

## Known blockers
- final commercial product name/trademark clearance not completed;
- final iOS cannabis-policy framing needs review before iOS release;
- final art assets for VS-01 are not yet production-complete unless separately committed.

## Do not do next
- do not add Web3;
- do not add free trading or P2P marketplaces;
- do not add unrestricted gifting;
- do not create dozens of varieties;
- do not build full LiveOps UI;
- do not optimize scale before measured need.

---

# 15. Standard prompt for the next coding agent/session

Use this instruction verbatim or semantically equivalent:

> Continue GreenBusiness from the canonical repository state. Read the canon and `06_IMPLEMENTATION_ROADMAP.md` plus `07_BUILD_HANDOFF.md`. Execute only the current milestone from the Handoff State Block. Do not implement later phases early. Produce production-grade code, migrations, Docker configuration, tests and documentation. Run the relevant test/build checks, fix failures, commit the finished milestone, update the Handoff State Block with completed/in-progress/next action, and stop when that milestone's acceptance criteria are satisfied.

---

# 16. Stop conditions

Stop and report rather than silently changing product direction if:
- canon contradicts implementation;
- a store/legal constraint invalidates a core mechanic;
- a migration would destroy existing production data;
- a security design requires weakening server authority;
- implementation requires adding real-money transferable assets;
- current milestone cannot pass its acceptance criteria.

For normal technical choices inside the frozen architecture, make the engineering decision and proceed.


---

## Art production pipeline decision

VS-01 structural art now follows a hybrid production pipeline:

- structural assets: concept → Tripo/Meshy → Blender canonical master → deterministic 2D renders;
- portraits/mission/store art: 2D-first;
- brand/UI icons: vector-first;
- starter crops: accepted 2D visual direction unless future animation needs justify 3D.

Canonical references:
- `docs/art/3D_PRODUCTION_PIPELINE_V1.md`
- `docs/art/3D_ASSET_SOURCE_OF_TRUTH.md`
- `art/3d/specs/slot_master_v1.json`
- `tools/blender/greenbusiness_scene_setup.py`

Immediate art-production next step:
1. run `python tools/asset_factory/factory.py validate --batch P10-ART-2`;
2. run `python tools/asset_factory/factory.py prepare --batch P10-ART-2`;
3. generate the 12 READY candidates (4 per starter crop);
4. approve one READY identity for Aurora Drift, Ember Leaf and Moon Sprout;
5. derive GROWING, then PLANTED, from those approved references;
6. export approved runtime WebP/AVIF variants and generate the runtime manifest.

Do not generate all remaining crop/decor families before the starter crop style lock is approved.


---

## Concept art backlog

Canonical concept-art planning:
- `docs/art/CONCEPT_ART_MASTER_LIST_V1.md`
- 73 concept images/boards total;
- 15 P0 concepts must be approved before large-scale art production;
- do not create one concept image per runtime asset;
- do not mass-produce an asset family before its governing concept board is approved.

## Master art backlog

The canonical visual backlog is now:
- `docs/art/MASTER_ASSET_CATALOG_V1.md`
- `art/prompts/MASTER_ASSET_PROMPTS_V1.json`

Current known inventory:
- 93 total visual assets;
- 26 P0;
- 45 P1;
- 22 P2;
- 55 3D-first;
- 20 2D-first;
- 18 vector-first.

All new visual game-data items must be added to this catalog before production.
