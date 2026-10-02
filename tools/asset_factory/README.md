# GreenBusiness Asset Factory v1

Production tooling for turning the canonical art catalog into reproducible batches.

## Source of truth

Do not duplicate the 93-asset catalog.

- canonical catalog: `art/prompts/MASTER_ASSET_PROMPTS_V1.json`
- style lock: `tools/asset_factory/config/style.greenbusiness_v1.json`
- batch definitions: `tools/asset_factory/batches/*.json`

A batch may derive multiple state/candidate jobs from one canonical asset. ART-2 therefore keeps Aurora Drift, Ember Leaf and Moon Sprout as the three canonical crop records and derives READY/GROWING/PLANTED states from them.

## ART-2 quick start

Validate:

```bash
python tools/asset_factory/factory.py validate --batch P10-ART-2
```

Inspect plan:

```bash
python tools/asset_factory/factory.py plan --batch P10-ART-2
```

Prepare the complete batch:

```bash
python tools/asset_factory/factory.py prepare --batch P10-ART-2
```

Default output:

```text
art/factory/generated/P10-ART-2/
  jobs.json
  prompts.jsonl
  prompts/
  approvals.template.json
  review.html
```

ART-2 currently yields:

- 3 starter crop identities
- 3 states per crop
- 4 candidates per state
- 36 deterministic jobs

Seeds are derived from stable job IDs, so rerunning the same batch preserves reproducibility.

## Approval workflow

Production order remains:

1. generate READY candidates;
2. approve one READY identity per crop;
3. use the approved READY references when producing GROWING;
4. approve GROWING;
5. produce PLANTED;
6. approve PLANTED;
7. export runtime variants and generate the runtime manifest.

The factory records dependency metadata (`depends_on_variant`) so provider workflows can enforce this order.

## Review sheet

The generated `review.html` expects images under `./images` by default.

Regenerate for another path:

```bash
python tools/asset_factory/factory.py review \
  --jobs art/factory/generated/P10-ART-2/jobs.json \
  --image-root ./images \
  --output art/factory/generated/P10-ART-2/review.html
```

## Runtime manifest

Copy `approvals.template.json` to `approvals.json` and fill only approved job IDs + filenames.

```bash
python tools/asset_factory/factory.py manifest \
  --approvals art/factory/generated/P10-ART-2/approvals.json \
  --public-prefix /assets/generated/crops \
  --output apps/web/public/assets/generated/crops/manifest.json
```

Unapproved variants are omitted.

## ComfyUI

Export a ComfyUI workflow in API format and replace the relevant workflow string values with:

- `__PROMPT__`
- `__NEGATIVE_PROMPT__`
- `__SEED__`
- `__FILENAME_PREFIX__`

Then:

```bash
python tools/asset_factory/comfyui_runner.py \
  --jobs art/factory/generated/P10-ART-2/jobs.json \
  --workflow path/to/workflow_api.json \
  --receipts art/factory/generated/P10-ART-2/provider/comfyui \
  --wait
```

The runner deliberately does not hard-code a checkpoint/model. The approved GreenBusiness style workflow is a production input and should be versioned only after its model/licensing/quality is approved.

## Meshy / external 3D

3D services are upstream source-generation tools only. Do not make external 3D APIs part of the gameplay runtime.

For future 3D-first batches, implement provider adapters that consume the same `jobs.json` contract and store immutable provider receipts. Never place API keys in the catalog, batch files or repository.

## Generated files

Generated images and provider receipts are working artifacts and should not be committed by default. Approved masters/runtime exports are committed through the normal art QA process.
