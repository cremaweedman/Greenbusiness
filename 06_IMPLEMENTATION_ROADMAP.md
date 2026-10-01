# 06 — IMPLEMENTATION ROADMAP — GREENBUSINESS

**Version:** 1.0  
**Status:** Canonical execution plan  
**Target:** Full production path from empty repository to validated live product  
**Reference product name:** GreenBusiness / Green District (working product identity; final trademark clearance pending)

---

## 0. Execution rules

This roadmap is sequential. Do not implement a later phase because it is technically interesting.

A phase is complete only when:
1. its Definition of Done is satisfied;
2. tests are green;
3. required telemetry exists;
4. no P0/P1 blocker remains;
5. canonical docs are updated if implementation changes a contract.

### Product constraints that remain frozen until soft launch

- Original IP only. Do not copy Weeds names, characters, dialogue, art, UI, music or protected expression.
- Adult management/tycoon framing.
- Fictional/regulatory botanical business framing; no real cultivation instructions.
- Server-authoritative economy and timers.
- Append-only currency ledger.
- No PvP in MVP.
- No free P2P marketplace in MVP.
- No open chat in MVP.
- No paid random rewards / loot boxes.
- No NFTs/Web3.
- No Kubernetes/microservices before measured need.
- No season pass until baseline retention is validated.

---

# Phase 0 — Repository & Production Foundation

## Objective
Create a reproducible production-grade skeleton that boots from a clean clone.

## Deliverables

### Repository
- monorepo:
  - `apps/web`
  - `apps/api`
  - `packages/contracts`
  - `infra`
  - `docs`
- root `README.md`
- `.env.example`
- `.gitignore`
- conventional commits
- branch protection recommendations

### Backend
- FastAPI
- Python 3.12+
- SQLAlchemy 2.x async
- PostgreSQL
- Alembic
- Pydantic Settings
- structured error schema
- request IDs
- health and readiness endpoints

### Frontend
- Next.js + TypeScript
- responsive/mobile-first shell
- API client
- auth/session shell
- design tokens
- accessibility baseline

### Infra
- Dockerfiles
- Docker Compose
- PostgreSQL
- Redis available but only used when a real need appears
- Nginx/reverse proxy
- local object storage adapter or S3-compatible interface

### Quality
- Ruff/format
- type checking
- pytest
- frontend lint/typecheck/tests
- Playwright smoke test
- GitHub Actions
- dependency + secret scanning

## Definition of Done
- `docker compose up --build` works from a clean clone.
- Empty database migrates to head.
- Web, API and DB health checks pass.
- CI is green.
- No production secret exists in git.
- One E2E smoke flow reaches web -> API -> DB.

---

# Phase 1 — Identity, Save State & Core Domain

## Objective
Create persistent accounts and the canonical game state before implementing content-heavy gameplay.

## Deliverables

### Identity
- guest account
- email authentication
- Google sign-in adapter
- Apple sign-in adapter interface
- access + refresh token rotation
- logout/revoke
- age gate / adult positioning
- GDPR-oriented account deletion/export hooks

### Core entities
- users
- player_profiles
- businesses
- rooms
- production_slots
- varieties
- inventory_items
- player_inventory
- progression
- skill_points
- audit_events

### Persistence rules
- no client-authoritative balances
- no client-authoritative timestamps
- versioned content/config references
- transactional writes

## Definition of Done
- New player can create/sign in, receive a profile and business, close the app, return and recover identical state.
- Refresh rotation is tested.
- Account deletion path is technically possible.
- All state-changing endpoints emit audit events.

---

# Phase 2 — Vertical Slice: Plant → Timer → Care → Harvest

## Objective
Prove the primary 5-minute loop before building meta systems.

## Deliverables
- one playable isometric room
- 3 production slots
- 3 fictional varieties
- plant action
- server timestamp start
- offline timer
- optional care opportunity
- ready state
- harvest
- quality result
- first cash + XP reward
- basic inventory
- minimal tutorial

## UX target
- first meaningful action < 60 seconds
- first harvest < 3 minutes
- first reward/contract < 5 minutes

## Technical requirements
- idempotency on plant/harvest
- DB constraints preventing duplicate harvest
- row locking or equivalent transaction safety
- server-side RNG where required
- absolute ready timestamps
- grace period; no crop destruction for lateness

## Definition of Done
A brand-new user can complete the entire core loop without admin intervention and without monetization.

**Gate:** Do not build clubs, IAP or deep LiveOps until this loop is fun enough to test repeatedly.

---

# Phase 3 — Economy, Contracts & Progression

## Objective
Turn the core loop into a management game with decisions.

## Deliverables

### Economy
- append-only currency ledger
- soft currency: Cash
- meta progression: XP / Reputation
- premium currency data model, disabled for real purchases until Phase 6
- sources/sinks taxonomy
- transaction IDs
- balance-before/balance-after
- config version on every economic mutation

### Contracts
- quick / standard / premium contracts
- trait requirements
- quality requirements
- time/value trade-offs
- rotating demand
- contract reroll with soft currency limits

### Progression
- 20–25 level curve
- unlock table
- 3 skill branches:
  - Botany
  - Commerce
  - Operations
- reversible/reasonable respec policy
- business upgrades
- capacity/automation progression

### Content target
- 10–12 fictional varieties
- 25–40 missions
- 40–60 decorations for MVP content set

## Definition of Done
- Economy simulation shows no obvious infinite-money exploit.
- Every unit of Cash is attributable to a ledger event.
- Player has meaningful choices between spending, saving and upgrading.
- E2E test: plant -> harvest -> contract -> cash -> upgrade -> changed production outcome.

---

# Phase 4 — Missions, Narrative & Collection Meta

## Objective
Add reasons to return beyond raw timers.

## Deliverables
- mission engine
- objectives and rewards
- short episodic narrative arcs
- collection/mastery per variety
- cosmetic variants unlocked through mastery
- NPC/contact abstraction using original IP
- inbox/phone-style mission surface
- daily/weekly mission pools
- catch-up rules

## Definition of Done
- Minimum 7 days of coherent playable progression without repeating identical mission chains.
- Narrative/config content can be added without backend deployment.
- No copyrighted Weeds expression appears in production content.

---

# Phase 5 — LiveOps, Remote Config, Analytics & Admin

## Objective
Make the game operable after launch without shipping a client update for every balance/content change.

## Deliverables

### Remote config
- seasons
- featured traits
- contract multipliers
- event windows
- content enable/disable
- A/B experiment assignments
- notification copy/settings
- kill switches

### Analytics
Minimum events:
- acquisition
- tutorial
- production lifecycle
- contracts
- progression
- economy sources/sinks
- store funnel
- social
- LiveOps
- push
- errors/performance

### Admin
- player lookup
- account status
- economy ledger inspection
- grant/revoke dev/test items with audit
- content/config editor
- season scheduling
- economy dashboard
- anomaly dashboard
- feature flags

## Definition of Done
- A balance value can be changed remotely, versioned and rolled back.
- Analytics reconstruct the tutorial and core loop funnel.
- Economy dashboard exposes minted/burned cash and wallet distributions.
- All admin mutations are audited.

---

# Phase 6 — Social Layer: Clubs

## Objective
Test whether cooperation materially improves retention.

## Deliverables
- own social graph
- friend codes/deep links
- clubs of approximately 20–30 members
- join/leave/invite
- structured reactions/emotes
- weekly club objective
- contribution ledger
- limited assists
- club rewards
- basic anti-abuse

## Explicit exclusions
- open chat
- unrestricted gifting
- free trading
- P2P marketplace
- user-created economic assets

## Definition of Done
- Club lifecycle is E2E tested.
- Contributions are idempotent.
- Multi-account reward abuse has hard limits.
- Club features can be disabled independently with a feature flag.

---

# Phase 7 — Monetization & Entitlements

## Objective
Add ethical monetization only after the core game is measurable.

## Deliverables
- product catalog
- entitlement service
- purchase ledger
- receipt validation server-side
- refund/revocation handling
- premium currency
- cosmetics
- founder/supporter bundle
- optional convenience with hard P2W limits
- no-ads entitlement only if ads are actually used
- rewarded ads experiment framework

## Initial test products
- Starter cosmetic bundle
- Credits S/M/L
- Founder/Supporter pack

## Season Pass gate
Season Pass remains disabled until retention quality is demonstrated.

Recommended activation gate:
- tutorial completion >= 75%
- D1 >= 35%
- D7 >= 15%
- stable economy
- no critical monetization/fraud incidents

## Definition of Done
- Fake/replayed receipt cannot grant duplicate value.
- Entitlements survive reinstall/device changes.
- Refund can reverse entitlement safely.
- No real-money purchase grants a random paid reward.

---

# Phase 8 — Push, Cross-Platform UX & Accessibility

## Objective
Make asynchronous play convenient rather than coercive.

## Deliverables
- web/PWA installability
- Android packaging path
- iOS adapter/packaging path prepared but release depends on policy review
- push tokens
- quiet hours
- notification categories:
  - production
  - events/seasons
  - club/social
- deep links
- offline/read cache
- accessibility:
  - scalable text
  - reduced motion
  - keyboard web support
  - screen-reader labels
  - color-independent states
  - icon + text state indicators
  - confirmation on premium spend
  - absolute timer timestamps

## Definition of Done
- All core gameplay is usable without push.
- Notifications can be independently disabled.
- No punitive “return now or lose everything” mechanic.
- Keyboard/accessibility smoke audit passes.

---

# Phase 9 — Security, Fraud, Reliability & Production Hardening

## Objective
Reach closed-alpha production standards.

## Deliverables
- rate limiting
- replay prevention
- receipt fraud controls
- anomaly detection
- economic exploit logging
- backups
- restore drill
- Sentry/error monitoring
- structured logs
- metrics/tracing
- staging environment
- production migrations as explicit release step
- CSP/security headers
- dependency/container scanning
- data retention policy
- privacy policy inputs
- Terms/Community rules inputs
- trademark/IP clearance checkpoint

## Definition of Done
- Restore from backup tested.
- Duplicate harvest/purchase replay tests pass.
- P0/P1 security issues = 0.
- Crash-free sessions target >= 99.5% during alpha.
- Production runbook exists.

---

# Phase 10 — Content Completion & Closed Alpha

## Objective
Validate the product with real players before scaling scope.

## Alpha content
- 1 complete district/local
- 10–12 fictional varieties
- 20–25 levels
- 3 small skill trees
- 25–40 missions
- 40–60 decorations
- club weekly objective
- minimum one LiveOps mini-arc
- first complete economy configuration

## Alpha cohort
Start small and instrumented. Prefer invited users/community over paid UA.

## Core questions
1. Is the production loop fun?
2. Do users return for timers?
3. Does economy create decisions?
4. Do clubs improve retention?
5. Will users pay for cosmetics/content without P2W?

## Definition of Done
- Feedback tagged and triaged.
- Economy exploits resolved.
- Tutorial completion measured.
- D1 and early D7 cohorts measurable.
- No blocker preventing soft launch.

---

# Phase 11 — Soft Launch

## Objective
Find product-market/economy fit before worldwide release.

## Required dashboards
- acquisition funnel
- tutorial funnel
- D1/D7/D30
- DAU/MAU
- sessions/user
- crop start -> harvest conversion
- contract completion
- source/sink economy
- upgrade affordability
- club adoption and club retention delta
- store view -> checkout -> purchase
- ARPDAU / ARPPU
- payer conversion
- crash/API reliability
- notification opt-in/open/unsubscribe

## Internal performance gates
Targets are decision gates, not promises:
- Tutorial completion >= 75%
- First harvest >= 85% of tutorial starters
- D1 >= 35%
- D7 >= 15%
- D30 >= 7%
- DAU/MAU >= 22%
- Club adoption before D7 >= 25%
- Store viewer -> first purchase target >= 3%
- Crash-free sessions >= 99.5%

## Decision rules
- If D1 fails: fix onboarding/core loop.
- If D1 works but D7 fails: fix meta progression/content/timers.
- If retention works but economy inflates: rebalance sources/sinks.
- If retention works but payer conversion fails: improve value proposition, not pressure.
- Do not scale paid UA until retention and LTV evidence justify it.

---

# Phase 12 — Launch Candidate & Public Release

## Objective
Ship only what soft launch proved.

## Deliverables
- final onboarding
- balanced economy v1
- release content pack
- first real season
- support workflow
- incident runbook
- moderation/reporting for implemented social features
- store assets
- rating/compliance submissions
- privacy/terms
- production backups/monitoring
- release checklist
- rollback plan

## Channel order
1. Web/PWA
2. Android
3. iOS after policy/framing review
4. Steam/desktop only when commercial evidence supports it

## Definition of Done
- Release candidate passes regression suite.
- Store/compliance blockers resolved for target channel.
- Metrics and rollback are live before traffic is opened.

---

# Phase 13 — Post-Launch Scale

Only execute after real measured need.

Possible additions:
- deeper seasons
- additional districts
- staff system expansion
- asynchronous competitions
- richer club systems
- more social sharing
- creator/community tools
- localization
- Steam
- additional analytics warehouse
- Redis-heavy caching
- job queues/workers
- read replicas
- CDN
- dedicated event pipeline

Still excluded unless separately approved:
- free P2P economy
- open chat without moderation infrastructure
- speculative tokens/NFTs
- cash-out
- paid RNG
- real cultivation simulation

---

# Critical path

```text
Foundation
  -> Identity/Persistence
    -> Core Vertical Slice
      -> Economy/Contracts
        -> Missions/Meta
          -> LiveOps/Analytics/Admin
            -> Clubs
            -> Monetization
              -> Hardening
                -> Closed Alpha
                  -> Soft Launch
                    -> Public Release
```

Parallel art/content work may run beside engineering, but it must not change canonical mechanics without updating the GDD/TDD.

---

# Recommended solo-founder execution cadence

Use 1-2 week implementation slices.

Each slice:
1. select one phase objective;
2. convert it into <= 5 concrete issues;
3. implement;
4. add tests;
5. run E2E;
6. update HANDOFF;
7. commit;
8. only then start the next slice.

Never run more than one major product phase in parallel as a solo founder.

---

# First executable milestone

The immediate next milestone is:

**P0-M1 — Repository & Foundation**

Success means:
- source repository exists beyond documentation;
- `docker compose up --build` boots web/api/postgres;
- migrations run;
- health/readiness are green;
- CI executes backend/frontend checks;
- a baseline Playwright smoke test passes.

After P0-M1, continue inside Phase 0 until its Definition of Done is fully satisfied.


---

## P10-3D — Diorama Runtime Migration

### Objective
Validate GreenBusiness as a real-time 3D diorama management game before the invited Closed Alpha.

### Architecture
- retain FastAPI/Postgres/Redis server authority;
- retain Next.js/React for text-heavy UI;
- add Three.js + React Three Fiber for the room/gameplay scene;
- consume optimized GLB/GLTF authored through Blender;
- do not move contracts, inventory, store or settings into 3D.

### P10-3D-0 — Runtime Spike
Deliver:
- procedural 3D Starter Room;
- 3 visible production slots;
- server-state mapping into the scene;
- constrained orbit/zoom;
- desktop/mobile responsive viewport;
- fallback-safe HTML gameplay.

Gate:
- frontend lint/typecheck/test/build green;
- compose-smoke green;
- security scan green;
- normal gameplay loop remains intact;
- acceptable mobile interaction and >=30 FPS target on a representative mid-range device.

### P10-3D-1 — GLB Starter Room
Replace procedural primitives with:
- room shell;
- canonical starter slot;
- storage;
- contract anchor;
- workbench;
- desk.

### P10-3D-2 — Crops
Add:
- Aurora Drift;
- Ember Leaf;
- Moon Sprout;
- growth-stage meshes or state variants.

### P10-3D-3 — Direct Interaction
Add:
- slot selection by tap/click;
- visual plant/grow/ready/harvest transitions;
- HTML action surfaces remain accessible and authoritative.

### P10-3D-4 — Upgrades & Decoration
Add:
- rack tiers;
- room evolution;
- owned decoration placement;
- visual progression.

### P10-3D-5 — Optimization
Add:
- compressed GLB;
- KTX2/Basis where practical;
- quality tiers;
- asset preload priorities;
- 3D load/FPS telemetry.

### Decision gate
Do not run the real invited Closed Alpha on the old 2D room if P10-3D-0 succeeds. If P10-3D-0 fails mobile/performance/reliability gates, revert the runtime scene and keep 3D as an authoring pipeline only.
