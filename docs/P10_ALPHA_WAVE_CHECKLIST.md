# P10 First Alpha Wave Checklist

Use this only after the P10 technical baseline is merged/deployed to an isolated alpha environment.

## 0. Environment contract

Required:

- `APP_ENV=alpha`;
- unique `ALPHA_INSTANCE_ID` that does not contain `prod`, `production`, `main` or `live`;
- strong production-like JWT/admin secrets;
- secure cookies;
- Redis-backed rate limiting;
- encrypted push tokens;
- creator access disabled;
- sandbox monetization disabled.

`alpha` is intentionally production-like. Weak development defaults must fail closed.

## 1. Clean environment

Only on the isolated alpha instance:

```bash
export APP_ENV=alpha
export ALPHA_INSTANCE_ID=gb-alpha-eu1
export ALPHA_RESET_CONFIRM="RESET_GREENBUSINESS_ALPHA:$ALPHA_INSTANCE_ID"
./scripts/alpha_reset.sh
```

The reset script refuses to run for any environment other than exactly `alpha`.

## 2. Publish canonical mini-arc

```bash
export APP_ENV=alpha
export ADMIN_API_KEY="<strong alpha bootstrap key>"
export ALPHA_BASE_URL="https://alpha.example.com"
./scripts/alpha_seed.sh
```

This publishes `apps/api/app/game_data/liveops_alpha_mini_arc.json` through the audited admin API.

## 3. Create tester accounts

Testers register normally. Do not seed fake activity into retention metrics.

After registration, obtain each user UUID from the admin player workflow and enroll only invited testers:

```bash
export ALPHA_USER_ID="<tester uuid>"
export ALPHA_WAVE="wave-1"
./scripts/alpha_enroll.sh
```

Start with a small wave. Do not enroll dev/creator/test accounts.

## 4. Pre-wave verification

```bash
./scripts/alpha_smoke.sh
```

Verify:

- liveness/readiness;
- admin auth;
- active LiveOps config;
- cohort dashboard reachable;
- zero unexpected blocker feedback;
- expected build SHA deployed.

## 5. Wave 1 operating rule

Recommended first wave: 5-10 invited testers.

Do not expand the cohort while any of these are true:

- blocker feedback is open;
- major economy exploit is reproducible;
- auth/session loss blocks play;
- planting/harvest/contract core loop is broken;
- migrations or readiness checks are unstable.

## 6. What to observe

Daily:

- cohort size;
- tutorial completion;
- first harvest users;
- D1 eligible / returned / rate;
- D7 eligible / returned / rate;
- blocker and major feedback;
- economy minted vs burned;
- wallet distribution;
- contract completion;
- club creation/join/contribution;
- decoration purchase/equip adoption.

Do not interpret D1/D7 before users are actually eligible.

## 7. Feedback policy

Testers submit through the in-app Closed Alpha form.

Triage:

- blocker: prevents meaningful play or risks data/economy integrity;
- major: materially damages a core loop but has a workaround;
- minor: localized defect;
- suggestion: preference/feature idea.

Feature requests do not block P10 unless they expose a missing core acceptance requirement.

## 8. Exit gate

P10 remains open until real cohort evidence exists. Phase 11 remains blocked until:

- no unresolved blockers;
- major exploits fixed;
- tutorial and first harvest are measurable;
- D1 and early D7 are measurable;
- economy source/sink behavior has been reviewed;
- club impact has been reviewed;
- feedback queue is triaged;
- CI and Security Scan remain green.
