# ComfyUI workflows

## Canonical baseline template

`comfyui_sd15_api.template.json` uses only standard ComfyUI nodes:

- CheckpointLoaderSimple
- CLIPTextEncode
- EmptyLatentImage
- KSampler
- VAEDecode
- SaveImage

It is intentionally checkpoint-agnostic.

The runner replaces:

- `__CHECKPOINT__`
- `__PROMPT__`
- `__NEGATIVE_PROMPT__`
- `__SEED__`
- `__FILENAME_PREFIX__`

Example:

```bash
python tools/asset_factory/comfyui_runner.py \
  --jobs art/factory/generated/P10-ART-2-ready/jobs.json \
  --workflow tools/asset_factory/workflows/comfyui_sd15_api.template.json \
  --checkpoint your-approved-model.safetensors \
  --variant ready \
  --receipts art/factory/generated/P10-ART-2-ready/provider/comfyui \
  --wait
```

## Important

This baseline workflow does not assume any custom background-removal node. Transparent runtime output must be produced in the post-processing/approval pipeline unless the approved local ComfyUI installation later standardizes a specific alpha-removal node.

Do not commit model weights or licensed checkpoints to this repository.
