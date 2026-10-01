# P10 Closed Alpha Runbook

## Status

P10-M1 is in progress. This document separates repository work from validation that requires invited players.

## Alpha content matrix

| Target | Current state | Next action |
| --- | --- | --- |
| 1 complete district/location | starter room exists | finish production art/content pass |
| 10-12 fictional varieties | 10 implemented | validate balance and unlock pacing |
| 20-25 levels | 20 implemented | validate pacing with cohort telemetry |
| 3 compact skill trees | implemented with server-authoritative effects | validate balance/pacing |
| 25-40 missions | 30 implemented | validate 7-day progression |
| 40-60 decorations | 40 implemented with ownership/equip persistence | validate cosmetic value |
| club weekly objective | implemented | validate adoption and abuse controls |
| one LiveOps mini-arc | Night Market Week authored | publish for alpha window |
| complete economy config | economy_v2 exists | rebalance from alpha source/sink data |

## Closed-alpha gates

P10 must not be marked complete until real invited-user data exists for tutorial completion, first harvest conversion, D1, early D7, return-to-timer behavior, club adoption, economy source/sink behavior, blocker reliability, and tagged feedback.

## Cohort procedure

1. Deploy an isolated production-like alpha environment.
2. Reset/seed only the alpha environment.
3. Invite a small cohort in waves.
4. Tag every build with commit SHA and active LiveOps config version.
5. Separate blocker/major/minor feedback from feature requests.
6. Review core-loop and economy dashboards daily.
7. Fix P0/P1 exploits or crashes before expanding the cohort.
8. Do not begin paid acquisition or Phase 11 before P10 gates pass.

## Current technical slice

The P10 technical alpha baseline is implemented and validated. It includes 10 fictional varieties, three compact skill trees with authoritative gameplay effects, 40 cosmetic decorations with ownership/equip persistence, explicit alpha cohort membership, tagged feedback/bug triage, D1/D7/tutorial/first-harvest dashboarding and the first versioned LiveOps mini-arc.

## Remaining work

- deploy an isolated production-like alpha environment;
- enroll invited testers in small waves;
- publish the Night Market Week LiveOps preset for the selected alpha window;
- run the guarded reproducible alpha reset/seed procedure (`scripts/alpha_reset.sh`, `scripts/alpha_seed.sh`) for that isolated environment;
- observe D1 and early D7 rather than estimating them;
- inspect economy source/sink behavior and club adoption from real cohort data;
- triage blocker/major feedback and fix regressions;
- finish the production-art pass for the starter location;
- keep Phase 11 blocked until the real cohort gates pass.

## Non-goals

Public launch, paid UA, open chat, P2P marketplace, Web3/NFT/cash-out and production iOS release before policy review remain out of scope.


## Operational scripts

- `scripts/alpha_reset.sh`: destructive reset guarded by exact `APP_ENV=alpha`, instance ID and confirmation phrase.
- `scripts/alpha_seed.sh`: publishes the canonical Night Market LiveOps preset through admin auth.
- `scripts/alpha_enroll.sh`: enrolls one real invited tester into an explicit wave.
- `scripts/alpha_smoke.sh`: checks health/readiness and the alpha admin dashboard.
- `docs/P10_ALPHA_WAVE_CHECKLIST.md`: canonical first-wave procedure.

Never run the reset script against staging or production.
