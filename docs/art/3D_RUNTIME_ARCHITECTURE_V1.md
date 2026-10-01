# GREENBUSINESS 3D RUNTIME ARCHITECTURE V1

Status: **SUPERSEDED / NON-CANONICAL**  
Superseded by: `docs/art/2D_RUNTIME_ARCHITECTURE_V1.md`

## Decision

The temporary real-time 3D runtime direction has been rejected for the core GreenBusiness gameplay experience.

The accepted direction is:
- premium 2D/2.5D isometric runtime;
- Next.js + React composition;
- optimized WebP/AVIF/SVG gameplay assets;
- 3D tools such as Blender, Meshy or Tripo may be used upstream to create consistent source masters;
- those masters are rendered from a fixed isometric camera into deterministic runtime assets;
- FastAPI/Postgres/Redis remain unchanged and server-authoritative.

## Historical note

The React Three Fiber / Three.js Starter Room spike remains useful as a technical experiment. It demonstrated that the existing state model can drive a 3D scene, but it is not the target production renderer.

Do not continue P10 by replacing procedural primitives with runtime GLB assets.

Continue from:
- `docs/art/2D_RUNTIME_ARCHITECTURE_V1.md`;
- `07_BUILD_HANDOFF.md`;
- `docs/art/MASTER_ASSET_CATALOG_V1.md`.

A future return to real-time 3D requires a new explicit architecture decision and must justify the additional asset, performance, mobile, QA and accessibility cost.
