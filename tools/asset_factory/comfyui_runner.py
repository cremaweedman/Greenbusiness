#!/usr/bin/env python3
"""Minimal ComfyUI API runner for GreenBusiness Asset Factory.

Requires a ComfyUI workflow exported in API format containing string placeholders:
__PROMPT__, __NEGATIVE_PROMPT__, __SEED__, __FILENAME_PREFIX__.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path
from typing import Any


def replace(value: Any, mapping: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {k: replace(v, mapping) for k, v in value.items()}
    if isinstance(value, list):
        return [replace(v, mapping) for v in value]
    if isinstance(value, str):
        for key, replacement in mapping.items():
            value = value.replace(key, replacement)
        if value.isdigit():
            try:
                return int(value)
            except ValueError:
                pass
    return value


def request_json(url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--jobs", required=True)
    p.add_argument("--workflow", required=True)
    p.add_argument("--url", default="http://127.0.0.1:8188")
    p.add_argument("--receipts", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--variant")
    p.add_argument("--limit", type=int)
    p.add_argument("--wait", action="store_true")
    args = p.parse_args()

    jobs = json.loads(Path(args.jobs).read_text(encoding="utf-8"))["jobs"]
    if args.variant:
        jobs = [job for job in jobs if job.get("variant") == args.variant]
        if not jobs:
            raise SystemExit(f"no jobs found for variant: {args.variant}")
    workflow = json.loads(Path(args.workflow).read_text(encoding="utf-8"))
    receipts = Path(args.receipts)
    receipts.mkdir(parents=True, exist_ok=True)

    for index, job in enumerate(jobs):
        if args.limit is not None and index >= args.limit:
            break
        mapping = {
            "__PROMPT__": job["prompt"],
            "__NEGATIVE_PROMPT__": job.get("negative_prompt", ""),
            "__SEED__": str(job["seed"]),
            "__FILENAME_PREFIX__": Path(job["output_filename"]).stem,
            "__CHECKPOINT__": args.checkpoint,
        }
        graph = replace(workflow, mapping)
        created = request_json(f"{args.url.rstrip('/')}/prompt", {"prompt": graph})
        prompt_id = created["prompt_id"]
        receipt = {"job_id": job["job_id"], "prompt_id": prompt_id, "created": created}

        if args.wait:
            while True:
                history = request_json(f"{args.url.rstrip('/')}/history/{prompt_id}")
                if prompt_id in history:
                    receipt["history"] = history[prompt_id]
                    break
                time.sleep(1.0)

        (receipts / f"{job['job_id']}.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        print(job["job_id"], prompt_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
