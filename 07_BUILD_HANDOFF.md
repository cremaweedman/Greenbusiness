# 07 — BUILD HANDOFF — GREENBUSINESS

**Version:** 1.0  
**Purpose:** Single canonical continuation point for any developer, coding agent or future ChatGPT/Work session.  
**Repository:** cremaweedman/Greenbusiness  
**Branch:** main  
**Current state:** P3-M1 economic loop is completed and validated. P3-M2 is ready but not started.

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
- P0-M1 and P0-M2 passed all acceptance criteria;
- canonical API error envelope and request IDs are implemented;
- append-only audit-event infrastructure persists in PostgreSQL;
- local + S3-compatible object storage abstraction is implemented;
- application API routes are versioned under `/v1`;
- real PostgreSQL integration tests run in CI;
- dependency security audits run in CI;
- Next.js is pinned to the patched 15.5.26 Maintenance LTS line.

Implementation is now active. Documentation completeness must not be confused with full game completeness.

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
**P3-M2 — Contracts & Progression Expansion — READY, NOT STARTED**

## Goal
Expand the proven P3-M1 economic loop into a repeatable management layer without jumping to later phases.

## Planned deliverables
- contract pool with quick / standard / premium archetypes;
- 3 simultaneous standard offers plus 1 specialized offer;
- server-authoritative 4-hour offer refresh;
- trait and quality requirements;
- reputation rewards and gates;
- 20-level progression curve foundation;
- unlock table for varieties / slots / upgrades;
- upgrade tiers using the canonical exponential cost curve;
- first compact skill-point progression hooks for Botany / Commerce / Operations;
- player-state/API/UI support for rotating offers and progression;
- economy simulation checks for obvious inflation/exploit paths;
- backend/frontend/full-stack E2E for repeated contract cycles.

## Explicitly excluded from P3-M2
- missions/narrative engine;
- employees;
- clubs;
- monetization;
- seasons/LiveOps;
- P2P marketplace;
- open chat.

---

# 9. P3-M2 acceptance criteria

Do not mark P3-M2 complete until:
- contract offers refresh deterministically from server state;
- no more than the configured active/offer limits can be bypassed;
- all Cash rewards and sinks remain ledger-backed;
- progression/unlocks persist across sessions;
- level/reputation changes are server-authoritative;
- upgrade prices follow versioned configuration;
- repeated contract cycles cannot duplicate inventory or Cash;
- economy simulation shows no obvious infinite-money exploit;
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
`Phase 3 — Economy, Contracts & Progression`

## Current milestone
`P3-M2 — READY, NOT STARTED`

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
- Next.js upgraded to patched 15.5.26;
- P0-M2 canonical errors, audit events, object storage and API versioning implemented;
- PostgreSQL integration tests and dependency audits added;
- Phase 0 Definition of Done fully satisfied with backend, frontend and full-stack Docker CI green;
- P1-M1 identity and persistent bootstrap implemented;
- email/password registration and login implemented;
- passwords use Argon2id hashing;
- access JWT + HttpOnly refresh-cookie flow implemented;
- refresh-token rotation and replay invalidation implemented;
- logout/revocation implemented;
- starter player/profile/business/room/production slots/progression/inventory container bootstrap transaction implemented;
- `GET /v1/player` persistent state implemented;
- registration/login/session-restore frontend implemented;
- PostgreSQL integration tests and full Docker auth E2E pass;
- final P1-M1 branch CI is green: backend, frontend and compose-smoke;
- P2-M1 production loop models, migration, service and routes implemented;
- 3 fictional starter varieties implemented as versioned backend data: Aurora Drift, Ember Leaf and Moon Sprout;
- plant/care/harvest endpoints implemented under `/v1/production`;
- server-authoritative `ready_at`, readiness checks, care bonus, quality and yield implemented;
- partial unique database index prevents more than one active crop per production slot;
- harvest marks crop history and releases the slot so rewards cannot be duplicated by replay;
- inventory item quantities persist per user inventory container;
- `GET /v1/player` returns starter varieties, active crop state and inventory;
- starter room frontend with variety selection, three production slots, timers, care, harvest, XP, tutorial objective and inventory implemented;
- P2-M1 integration tests added for persistence, early-harvest rejection, care, single harvest, tutorial progress, XP reward and invalid variety;
- P2-M1 merged to main and full backend/frontend/compose-smoke CI validated;
- CI hotfix aligned the auth bootstrap expectation with the 3-slot P2 starter state.
- P3-M1 wallet starts at 500 Cash and all Cash mutations use an append-only ledger;
- starter contract Neighborhood Sampler consumes 3 Aurora Drift and rewards 150 Cash transactionally;
- economic mutations use Idempotency-Key replay protection;
- Efficient Racks costs 600 Cash and adds +1 yield server-side;
- player state and frontend expose Cash, contract and upgrade state;
- PostgreSQL integration test covers harvest -> contract -> Cash -> upgrade -> improved harvest;
- full Docker E2E covers the same economic loop;
- final P3-M1 backend, frontend and compose-smoke CI are green.

## In progress
- none.

## Next action
Begin P3-M2 exactly as specified above when development resumes. Do not start Phase 4 or later systems early.

## Known blockers
- final commercial product name/trademark clearance not completed;
- final iOS cannabis-policy framing needs review before iOS release;
- final art assets for VS-01 are not yet production-complete unless separately committed.

## Do not do next
- do not start clubs;
- do not add payments;
- do not add Web3;
- do not create dozens of varieties;
- do not build full LiveOps UI;
- do not optimize scale before a working vertical slice.

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
