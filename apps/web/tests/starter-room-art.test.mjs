import assert from "node:assert/strict";
import { readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

const webRoot = process.cwd();
const publicRoot = join(webRoot, "public");
const manifest = JSON.parse(
  readFileSync(join(publicRoot, "assets/starter-room-manifest.json"), "utf8"),
);

function toDiskPath(publicPath) {
  return join(publicRoot, publicPath.replace(/^\//, ""));
}

test("P10-ART-1 manifest contains canonical layered runtime", () => {
  assert.equal(manifest.milestone, "P10-ART-1");
  assert.equal(manifest.runtime, "2d-2.5d-layered");
  assert.deepEqual(manifest.baselineViewport, { width: 390, height: 844 });
  assert.equal(manifest.layers.length, 5);
  assert.equal(manifest.slots.anchors.length, 3);
  assert.ok(manifest.slots.states.flowering);
});

test("all Starter Room runtime assets exist and stay inside mobile payload gate", () => {
  const paths = [
    ...manifest.layers.map((layer) => layer.src),
    ...Object.values(manifest.slots.states),
  ];
  let totalBytes = 0;
  for (const assetPath of paths) {
    const diskPath = toDiskPath(assetPath);
    const stats = statSync(diskPath);
    assert.ok(stats.isFile(), `missing runtime asset: ${assetPath}`);
    totalBytes += stats.size;
  }
  assert.ok(totalBytes <= 2 * 1024 * 1024, `Starter Room assets exceed 2MB: ${totalBytes}`);
});

test("gameplay uses canonical StarterRoomScene instead of realtime 3D spike", () => {
  const authApp = readFileSync(join(webRoot, "app/AuthApp.tsx"), "utf8");
  assert.match(authApp, /import StarterRoomScene from "\.\/StarterRoomScene"/);
  assert.doesNotMatch(authApp, /StarterRoom3DScene/);
  assert.match(authApp, /sceneSlotState/);
  assert.match(authApp, /crop-bottom-sheet/);
  assert.match(authApp, /mobile-bottom-nav/);
  assert.match(authApp, /Business/);
  assert.match(authApp, /Production/);
  assert.match(authApp, /Missions/);
  assert.match(authApp, /Club/);
  assert.match(authApp, /Store/);
});
