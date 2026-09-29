import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

test("identity shell exists", () => {
  assert.equal(fs.existsSync("app/page.tsx"), true);
  assert.equal(fs.existsSync("app/AuthApp.tsx"), true);
  const page = fs.readFileSync("app/page.tsx", "utf8");
  const auth = fs.readFileSync("app/AuthApp.tsx", "utf8");
  assert.match(page, /AuthApp/);
  assert.match(auth, /GreenBusiness/);
  assert.match(auth, /\/api\/v1\/auth\/refresh/);
  assert.match(auth, /credentials: "include"/);
});
