# P10 Closed Alpha Runbook

## Status

P10-M1 is in progress. This document separates repository work from validation that requires invited players.

## Alpha content matrix

| Target | Current state | Next action |
| --- | --- | --- |
| 1 complete district/location | starter room exists | finish production art/content pass |
| 10-12 fictional varieties | 10 implemented | validate balance and unlock pacing |
| 20-25 levels | 20 implemented | validate pacing with cohort telemetry |
| 3 compact skill trees | branch foundations exist | finish meaningful branch choices |
| 25-40 missions | 30 implemented | validate 7-day progression |
| 40-60 decorations | not production-complete | implement catalog + ownership/equip path |
| club weekly objective | implemented | validate adoption and abuse controls |
| one LiveOps mini-arc | LiveOps engine exists | author and schedule alpha mini-arc |
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

The first P10 slice expands the fictional variety catalog from 3 to 10 and adds server-authoritative level gates. Locked varieties remain visible for progression clarity but cannot be planted by a modified client.

## Remaining repository work

- complete three compact skill trees rather than branch placeholders;
- implement 40-60 decoration definitions plus ownership/equip state;
- author one complete LiveOps mini-arc;
- add alpha cohort/retention dashboarding and feedback triage persistence;
- add reproducible alpha seed/reset tooling;
- validate the full P10 content path in CI.

## Non-goals

Public launch, paid UA, open chat, P2P marketplace, Web3/NFT/cash-out and production iOS release before policy review remain out of scope.
