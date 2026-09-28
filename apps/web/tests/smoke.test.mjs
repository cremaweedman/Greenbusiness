import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

test("app shell exists", () => {
  assert.equal(fs.existsSync("app/page.tsx"), true);
  const page = fs.readFileSync("app/page.tsx", "utf8");
  assert.match(page, /GreenBusiness/);
});
