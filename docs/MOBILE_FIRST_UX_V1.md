# GREENBUSINESS MOBILE-FIRST UX V1

Status: CANONICAL  
Primary platform: mobile portrait  
Secondary: tablet  
Tertiary: desktop/PWA

## 1. Product posture

GreenBusiness is designed primarily for mobile use. Desktop support exists, but desktop must adapt from the mobile product rather than define it.

Target baseline viewport:
- 390 x 844 CSS px
- portrait 9:19.5 class
- test range: 360–430 px width

## 2. Primary layout

Recommended vertical allocation:

- top resources/status: 8–12%
- interactive 2.5D room: 55–65%
- contextual action surface: 15–25%
- bottom navigation: 8–12%

The room remains the visual focus. Text-heavy information should appear on demand rather than permanently surrounding the room.

## 3. Navigation

Primary bottom navigation contains five destinations:

- Business
- Production
- Missions
- Club
- Store

Do not use a persistent desktop-style left sidebar on mobile.

Contracts should open contextually from the business/production flow unless later testing proves a dedicated tab is necessary.

## 4. Interaction model

Core gameplay must be comfortable with one thumb.

Preferred interactions:
- tap
- bottom sheet
- short vertical scroll
- large primary actions
- contextual cards
- optional long-press for secondary detail

Avoid:
- hover requirements
- precision drag
- tiny hit targets
- mandatory pinch/zoom
- free camera movement
- dense permanent side panels

Minimum interactive target: 44 x 44 CSS px.

## 5. Room interaction

Tap a room object to open a contextual bottom sheet.

Examples:
- crop -> state, timer, care/harvest/details
- empty slot -> seed selection
- contract station -> current offers
- storage -> inventory
- workbench -> processing/upgrades
- decoration -> inspect/equip

The room itself must remain visually readable without labels permanently covering every object.

## 6. Bottom sheets

Bottom sheets are the default detail pattern.

Use three states where useful:
- peek
- half
- expanded

They should:
- preserve room context
- be swipe-dismissable where safe
- expose a clear close action
- keep the main CTA in thumb reach
- avoid full-screen takeover unless content complexity requires it

## 7. Orientation

Portrait is canonical.

Landscape is supported only as a compatibility mode unless data later shows meaningful usage.

Do not design gameplay around a wide 16:9 viewport.

## 8. Responsive hierarchy

Mobile portrait:
- canonical layout
- bottom nav
- bottom sheets
- room-focused composition

Tablet:
- same information architecture
- larger room
- optional split contextual panel

Desktop:
- preserve mobile IA
- may show contextual panel beside the room
- must not introduce desktop-only core actions

## 9. Asset composition

Art must be produced for portrait composition first.

Rules:
- critical gameplay objects stay inside a mobile-safe central composition
- decorative edges may crop
- no essential object may depend on the extreme left/right of a desktop render
- text is HTML/UI, not baked into scene art
- room framing must tolerate narrow screens without free camera movement

## 10. Runtime performance budgets

Closed Alpha mobile targets:
- first useful UI visible as quickly as possible
- interactive gameplay target within 2–3 seconds on typical broadband/Wi-Fi after authentication
- starter-room initial visual payload target <= 2 MB where practical
- avoid individual oversized alpha assets
- preload only P0 and likely-next state assets
- lazy-load decoration and non-critical content
- use responsive image variants
- prefer WebP; use AVIF selectively for large opaque assets
- no continuous GPU-heavy renderer required for core play

## 11. Motion

Motion should communicate state, not decorate continuously.

Use:
- small scale/opacity transitions
- glow/pulse for ready states
- restrained particles for rewards
- short harvest/upgrade feedback

Respect reduced-motion settings.

## 12. Accessibility

Required:
- text alternatives for visual states
- 44 px minimum tap targets
- sufficient contrast
- no color-only state meaning
- accessible HTML controls for every consequential action
- scalable text
- reduced-motion support

## 13. Mobile QA matrix

At minimum test:
- 360 x 800
- 390 x 844
- 393 x 852
- 412 x 915
- 430 x 932
- tablet portrait
- desktop fallback

Validate:
- no clipped primary CTA
- no overlap with bottom navigation
- safe-area insets
- virtual keyboard behavior
- bottom sheet reachability
- tap targets
- room readability
- asset memory/load behavior

## 14. Immediate implication for P10-ART-1

The Starter Room must be composed first for portrait mobile.

Acceptance requires:
- 390 x 844 canonical mock/runtime view
- 360 px minimum-width pass
- bottom navigation implemented
- crop/slot interaction through bottom sheet
- no persistent left sidebar
- no desktop-only control
- initial asset payload within the agreed mobile budget
