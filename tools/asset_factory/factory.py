#!/usr/bin/env python3
"""GreenBusiness Asset Factory v1.

Stdlib-first CLI that turns the canonical asset catalog + batch specs into
reproducible generation jobs, prompt packets, review sheets and runtime manifests.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "art/prompts/MASTER_ASSET_PROMPTS_V1.json"
DEFAULT_BATCH_DIR = ROOT / "tools/asset_factory/batches"
DEFAULT_STYLE = ROOT / "tools/asset_factory/config/style.greenbusiness_v1.json"


class FactoryError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FactoryError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise FactoryError(f"invalid JSON: {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def deterministic_seed(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) & 0x7FFFFFFF


def load_batch(name_or_path: str) -> tuple[Path, dict[str, Any]]:
    candidate = Path(name_or_path)
    if not candidate.exists():
        candidate = DEFAULT_BATCH_DIR / f"{name_or_path}.json"
    return candidate, read_json(candidate)


def validate(catalog: dict[str, Any], batch: dict[str, Any], style: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    assets = catalog.get("assets")
    if not isinstance(assets, list):
        return ["catalog.assets must be a list"]

    ids = [a.get("id") for a in assets]
    duplicate_ids = sorted({x for x in ids if x and ids.count(x) > 1})
    if duplicate_ids:
        errors.append(f"duplicate asset ids: {duplicate_ids}")

    index = {a.get("id"): a for a in assets}
    for asset_id in batch.get("base_asset_ids", []):
        if asset_id not in index:
            errors.append(f"unknown base asset id: {asset_id}")

    variants = batch.get("variants", [])
    keys = [v.get("key") for v in variants]
    if not variants:
        errors.append("batch.variants must not be empty")
    if len(keys) != len(set(keys)):
        errors.append("batch variant keys must be unique")
    for variant in variants:
        if not variant.get("key") or not variant.get("prompt_suffix"):
            errors.append("every variant needs key + prompt_suffix")

    candidates = batch.get("candidates_per_variant", 0)
    if not isinstance(candidates, int) or candidates < 1 or candidates > 16:
        errors.append("candidates_per_variant must be an integer in [1,16]")

    if not style.get("style_id") or not style.get("prompt_suffix"):
        errors.append("style config needs style_id + prompt_suffix")
    return errors


def build_jobs(catalog: dict[str, Any], batch: dict[str, Any], style: dict[str, Any]) -> list[dict[str, Any]]:
    assets = {a["id"]: a for a in catalog["assets"]}
    candidates = int(batch["candidates_per_variant"])
    jobs: list[dict[str, Any]] = []
    variants = sorted(batch["variants"], key=lambda v: int(v.get("order", 0)))

    for asset_id in batch["base_asset_ids"]:
        asset = assets[asset_id]
        key = asset.get("key") or asset_id.lower()
        for variant in variants:
            variant_key = variant["key"]
            family_key = f"{key}__{variant_key}"
            for candidate in range(1, candidates + 1):
                job_key = f"{batch['batch_id']}__{family_key}__c{candidate:02d}"
                prompt = " ".join(
                    p.strip()
                    for p in (
                        asset["prompt"],
                        variant["prompt_suffix"],
                        style["prompt_suffix"],
                    )
                    if p and p.strip()
                )
                jobs.append(
                    {
                        "job_id": job_key,
                        "batch_id": batch["batch_id"],
                        "asset_id": asset_id,
                        "asset_key": key,
                        "asset_name": asset["name"],
                        "category": asset["category"],
                        "method": asset["method"],
                        "priority": asset["priority"],
                        "variant": variant_key,
                        "variant_order": int(variant.get("order", 0)),
                        "candidate": candidate,
                        "seed": deterministic_seed(job_key),
                        "style_id": style["style_id"],
                        "prompt": prompt,
                        "negative_prompt": style.get("negative_prompt", ""),
                        "output_filename": f"{key}_{variant_key}_c{candidate:02d}.png",
                        "depends_on_variant": variant.get("depends_on_variant"),
                    }
                )
    return jobs


def make_review_html(batch_id: str, jobs: list[dict[str, Any]], image_root: str = "./images") -> str:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for job in jobs:
        groups.setdefault((job["asset_name"], job["variant"]), []).append(job)

    sections = []
    for (asset_name, variant), group in groups.items():
        cards = []
        for job in group:
            src = f"{image_root.rstrip('/')}/{job['output_filename']}"
            cards.append(
                f"""<figure><img src="{html.escape(src)}" alt="{html.escape(job['job_id'])}" loading="lazy">
<figcaption><b>C{job['candidate']:02d}</b><code>{html.escape(job['job_id'])}</code><small>seed {job['seed']}</small></figcaption></figure>"""
            )
        sections.append(
            f"<section><h2>{html.escape(asset_name)} · {html.escape(variant.upper())}</h2>"
            f"<div class=\"grid\">{''.join(cards)}</div></section>"
        )

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(batch_id)} review</title>
<style>
body{{font:14px system-ui;margin:24px;background:#101713;color:#edf3ee}}
h1,h2{{margin:0 0 16px}} section{{margin:32px 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}}
figure{{margin:0;background:#18231c;border:1px solid #2b3d31;border-radius:14px;padding:10px}}
img{{width:100%;aspect-ratio:1;object-fit:contain;background:#0b100d;border-radius:10px}}
figcaption{{display:grid;gap:4px;margin-top:8px}}code{{font-size:10px;overflow-wrap:anywhere}}small{{opacity:.7}}
</style></head><body><h1>{html.escape(batch_id)} — candidate review</h1>{''.join(sections)}</body></html>"""


def cmd_validate(args: argparse.Namespace) -> int:
    catalog = read_json(Path(args.catalog))
    _, batch = load_batch(args.batch)
    style = read_json(Path(args.style))
    errors = validate(catalog, batch, style)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    jobs = build_jobs(catalog, batch, style)
    print(f"OK {batch['batch_id']}: {len(jobs)} jobs")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    catalog = read_json(Path(args.catalog))
    _, batch = load_batch(args.batch)
    style = read_json(Path(args.style))
    errors = validate(catalog, batch, style)
    if errors:
        raise FactoryError("; ".join(errors))
    jobs = build_jobs(catalog, batch, style)
    summary = {
        "batch_id": batch["batch_id"],
        "base_assets": len(batch["base_asset_ids"]),
        "variants": len(batch["variants"]),
        "candidates_per_variant": batch["candidates_per_variant"],
        "total_jobs": len(jobs),
        "style_id": style["style_id"],
    }
    print(json.dumps(summary, indent=2))
    if args.output:
        write_json(Path(args.output), {"summary": summary, "jobs": jobs})
    return 0


def cmd_prepare(args: argparse.Namespace) -> int:
    catalog = read_json(Path(args.catalog))
    _, batch = load_batch(args.batch)
    style = read_json(Path(args.style))
    errors = validate(catalog, batch, style)
    if errors:
        raise FactoryError("; ".join(errors))

    jobs = build_jobs(catalog, batch, style)
    out = Path(args.output_dir) if args.output_dir else ROOT / "art/factory/generated" / batch["batch_id"]
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "jobs.json", {"batch": batch, "style": style, "jobs": jobs})

    with (out / "prompts.jsonl").open("w", encoding="utf-8") as handle:
        for job in jobs:
            handle.write(json.dumps(job, ensure_ascii=False) + "\n")

    prompt_dir = out / "prompts"
    prompt_dir.mkdir(exist_ok=True)
    for job in jobs:
        (prompt_dir / f"{job['job_id']}.txt").write_text(job["prompt"] + "\n", encoding="utf-8")

    approval_template: dict[str, dict[str, str | None]] = {}
    for job in jobs:
        family = f"{job['asset_key']}__{job['variant']}"
        approval_template.setdefault(family, {"approved_job_id": None, "approved_filename": None})
    write_json(out / "approvals.template.json", approval_template)
    (out / "review.html").write_text(make_review_html(batch["batch_id"], jobs), encoding="utf-8")
    print(f"Prepared {len(jobs)} jobs in {out}")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    payload = read_json(Path(args.jobs))
    jobs = payload["jobs"]
    batch_id = payload.get("batch", {}).get("batch_id") or jobs[0]["batch_id"]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(make_review_html(batch_id, jobs, args.image_root), encoding="utf-8")
    print(output)
    return 0


def cmd_manifest(args: argparse.Namespace) -> int:
    approvals = read_json(Path(args.approvals))
    runtime: dict[str, Any] = {"version": 1, "assets": {}}
    for family, item in approvals.items():
        filename = item.get("approved_filename")
        job_id = item.get("approved_job_id")
        if not filename or not job_id:
            continue
        asset_key, variant = family.split("__", 1)
        runtime["assets"].setdefault(asset_key, {})[variant] = {
            "src": f"{args.public_prefix.rstrip('/')}/{filename}",
            "source_job_id": job_id,
        }
    write_json(Path(args.output), runtime)
    print(f"{args.output}: {sum(len(v) for v in runtime['assets'].values())} approved variants")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="GreenBusiness Asset Factory v1")
    p.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    p.add_argument("--style", default=str(DEFAULT_STYLE))
    sub = p.add_subparsers(dest="command", required=True)

    for name in ("validate", "plan", "prepare"):
        sp = sub.add_parser(name)
        sp.add_argument("--batch", required=True)
        if name == "plan":
            sp.add_argument("--output")
        if name == "prepare":
            sp.add_argument("--output-dir")

    review = sub.add_parser("review")
    review.add_argument("--jobs", required=True)
    review.add_argument("--image-root", default="./images")
    review.add_argument("--output", required=True)

    manifest = sub.add_parser("manifest")
    manifest.add_argument("--approvals", required=True)
    manifest.add_argument("--public-prefix", default="/assets/generated")
    manifest.add_argument("--output", required=True)
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        return {
            "validate": cmd_validate,
            "plan": cmd_plan,
            "prepare": cmd_prepare,
            "review": cmd_review,
            "manifest": cmd_manifest,
        }[args.command](args)
    except FactoryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
