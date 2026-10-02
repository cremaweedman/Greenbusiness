import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "factory.py"
SPEC = importlib.util.spec_from_file_location("factory", MODULE_PATH)
factory = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(factory)


class AssetFactoryTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {
            "assets": [
                {
                    "id": "A1",
                    "key": "aurora",
                    "name": "Aurora",
                    "category": "crops",
                    "method": "2d-first",
                    "priority": "P0",
                    "prompt": "Base prompt."
                }
            ]
        }
        self.batch = {
            "batch_id": "TEST",
            "base_asset_ids": ["A1"],
            "candidates_per_variant": 2,
            "variants": [
                {"key": "ready", "order": 10, "prompt_suffix": "Ready.", "depends_on_variant": None},
                {"key": "growing", "order": 20, "prompt_suffix": "Growing.", "depends_on_variant": "ready"}
            ]
        }
        self.style = {"style_id": "v1", "prompt_suffix": "Style.", "negative_prompt": "bad"}

    def test_job_count_and_stable_seed(self):
        first = factory.build_jobs(self.catalog, self.batch, self.style)
        second = factory.build_jobs(self.catalog, self.batch, self.style)
        self.assertEqual(len(first), 4)
        self.assertEqual(first[0]["seed"], second[0]["seed"])
        self.assertEqual(first[0]["output_filename"], "aurora_ready_c01.png")

    def test_variant_order(self):
        jobs = factory.build_jobs(self.catalog, self.batch, self.style)
        self.assertEqual([j["variant"] for j in jobs], ["ready", "ready", "growing", "growing"])

    def test_validate_unknown_asset(self):
        bad = dict(self.batch)
        bad["base_asset_ids"] = ["NOPE"]
        errors = factory.validate(self.catalog, bad, self.style)
        self.assertTrue(any("unknown base asset" in error for error in errors))

    def test_manifest_shape_via_approvals_contract(self):
        approvals = {
            "aurora__ready": {
                "approved_job_id": "TEST__aurora__ready__c01",
                "approved_filename": "aurora_ready.webp"
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "approvals.json"
            path.write_text(json.dumps(approvals), encoding="utf-8")
            loaded = factory.read_json(path)
            self.assertEqual(loaded["aurora__ready"]["approved_filename"], "aurora_ready.webp")


if __name__ == "__main__":
    unittest.main()
