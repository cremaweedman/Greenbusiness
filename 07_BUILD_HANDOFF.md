# 07 — BUILD HANDOFF — GREENBUSINESS

**Version:** 1.0  
**Purpose:** Single canonical continuation point for any developer, coding agent or future ChatGPT/Work session.  
**Repository:** cremaweedman/Greenbusiness  
**Branch:** main  
**Current state:** Phase 6 is completed and validated through P6-M1. Phase 7 is ready but not started.

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
- narrative history/inbox metadata is exposed to the frontend.

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
**P5-M1 — LiveOps / Remote Config / Analytics / Admin Foundation — READY, NOT STARTED**

## Goal
Make GreenBusiness operable and measurable after launch without introducing monetization, clubs or seasonal pass systems yet.

## Planned deliverables
- versioned remote-config storage for balance/content flags;
- safe config publish/rollback primitives;
- feature flags and kill switches;
- analytics event schema for acquisition, tutorial, production, contracts, economy, progression and missions;
- server-side event emission for the core funnel;
- initial admin authentication/authorization boundary;
- read-only admin views for players, wallets, ledger, missions and config;
- audited admin mutation scaffolding without broad write powers;
- first operational dashboards/data endpoints for economy and tutorial/core-loop health;
- PostgreSQL integration tests for config versioning and auditability;
- full Docker E2E for config read/rollback and analytics emission.

## Explicitly excluded from P5-M1
- clubs;
- monetization/IAP;
- season pass;
- push notifications;
- open chat;
- P2P marketplace;
- employee systems;
- complex A/B experimentation UI.

---

# 9. P5-M1 acceptance criteria

Do not mark P5-M1 complete until:
- active config is versioned and immutable once published;
- a previous config version can be restored safely;
- feature flags can disable a system without client redeploy;
- core gameplay actions emit canonical analytics events;
- analytics payloads do not contain secrets or raw credentials;
- admin access is separated from player auth;
- admin reads player/economy/config state without direct DB access from the browser;
- every admin mutation path is audited;
- config rollback and analytics persistence have PostgreSQL integration coverage;
- backend/frontend/full-stack CI is green.

**Current status:** ready, not started.

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
`Phase 7 — Monetization & Entitlements`

## Current milestone
`P7-M1 — Monetization & Entitlements — READY, NOT STARTED`

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
- P6-M1 Docker/PostgreSQL validation passed with Alembic head, full backend pytest, backend Ruff, frontend lint/typecheck/test, production web build and HTTP smoke checks.

## In progress
- None.

## Next action
Begin Phase 7 with Monetization & Entitlements exactly as scoped in `06_IMPLEMENTATION_ROADMAP.md`. Keep all purchase validation server-side and do not introduce Web3, trading, transferable assets or pay-to-win mechanics.

Local validation already passed without Docker:
- `python -m ruff check apps\api\app apps\api\tests\test_liveops_foundation.py apps\api\tests\integration\test_liveops_admin_analytics.py`
- `python -m compileall apps\api\app apps\api\tests\test_liveops_foundation.py apps\api\tests\integration\test_liveops_admin_analytics.py`
- `python -m pytest apps\api\tests\test_liveops_foundation.py`
- `npm run lint`
- `npm run typecheck`
- `npm test`
- `npm run build`

Docker/PostgreSQL validation passed:
- `docker compose up --build -d`
- `docker compose exec -T api alembic upgrade head`
- `docker compose exec -T api pytest -q` (`25 passed`)
- `docker compose exec -T api ruff check .`
- `docker compose run --rm web npm run lint`
- `docker compose run --rm web npm run typecheck`
- `docker compose run --rm web npm test`
- `docker compose up --build -d` production web build
- HTTP smoke passed for `/api/health/live`, `/api/health/ready` and `/api/v1/system/ping`.

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
