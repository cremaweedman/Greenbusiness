import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

test("production shell exists", () => {
  assert.equal(fs.existsSync("app/page.tsx"), true);
  assert.equal(fs.existsSync("app/AuthApp.tsx"), true);
  assert.equal(fs.existsSync("next.config.mjs"), true);
  const page = fs.readFileSync("app/page.tsx", "utf8");
  const auth = fs.readFileSync("app/AuthApp.tsx", "utf8");
  const nextConfig = fs.readFileSync("next.config.mjs", "utf8");
  assert.match(page, /AuthApp/);
  assert.match(auth, /GreenBusiness/);
  assert.match(auth, /\/api\/v1\/auth\/refresh/);
  assert.match(auth, /\/api\/v1\/production\/slots/);
  assert.match(auth, /Starter varieties/);
  assert.match(auth, /room-scene/);
  assert.match(auth, /credentials: "include"/);
  assert.match(nextConfig, /API_INTERNAL_URL/);
  assert.match(nextConfig, /source: "\/api\/:path\*"/);
});
