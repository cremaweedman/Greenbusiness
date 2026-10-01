"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { Suspense } from "react";

type SceneSlot = {
  id: string;
  slotIndex: number;
  state: "empty" | "planted" | "growing" | "ready" | "locked" | "attention" | "boosted";
  label: string;
};

type StarterRoom3DSceneProps = {
  slots: SceneSlot[];
};

const SLOT_X = [-2.2, 0, 2.2] as const;

function Crop({ state }: { state: SceneSlot["state"] }) {
  if (state === "empty" || state === "locked") return null;

  const scale =
    state === "planted" ? 0.35 :
    state === "growing" ? 0.7 :
    1;

  const color =
    state === "attention" ? "#d9a12f" :
    state === "boosted" ? "#93cf9f" :
    "#6fbf64";

  return (
    <group position={[0, 0.72, 0]} scale={scale}>
      <mesh castShadow>
        <sphereGeometry args={[0.42, 18, 18]} />
        <meshStandardMaterial color={color} roughness={0.75} />
      </mesh>
      <mesh position={[0, 0.35, 0]} castShadow>
        <sphereGeometry args={[0.28, 18, 18]} />
        <meshStandardMaterial color={color} roughness={0.7} />
      </mesh>
    </group>
  );
}

function ProductionSlot({ slot }: { slot: SceneSlot }) {
  const x = SLOT_X[slot.slotIndex] ?? 0;
  const emissive =
    slot.state === "ready" ? "#e0ba78" :
    slot.state === "boosted" ? "#77d9d7" :
    slot.state === "attention" ? "#d9a12f" :
    "#4da96b";

  return (
    <group position={[x, 0, 0]}>
      <mesh position={[0, 0.32, 0]} castShadow receiveShadow>
        <boxGeometry args={[1.55, 0.62, 1.35]} />
        <meshStandardMaterial color="#102016" roughness={0.72} metalness={0.08} />
      </mesh>

      <mesh position={[0, 0.68, 0]} receiveShadow>
        <boxGeometry args={[1.28, 0.16, 1.08]} />
        <meshStandardMaterial color="#2c2923" roughness={0.9} />
      </mesh>

      {[
        [-0.64, 1.45, -0.48],
        [0.64, 1.45, -0.48],
        [-0.64, 1.45, 0.48],
        [0.64, 1.45, 0.48],
      ].map((position, index) => (
        <mesh key={index} position={position as [number, number, number]} castShadow>
          <boxGeometry args={[0.13, 1.55, 0.13]} />
          <meshStandardMaterial color="#244d2e" roughness={0.62} metalness={0.14} />
        </mesh>
      ))}

      <mesh position={[0, 2.18, 0]} castShadow>
        <boxGeometry args={[1.5, 0.16, 0.17]} />
        <meshStandardMaterial color="#244d2e" roughness={0.62} metalness={0.14} />
      </mesh>

      <mesh position={[0, 2.08, 0.02]}>
        <boxGeometry args={[1.15, 0.05, 0.08]} />
        <meshStandardMaterial
          color="#f4f0e6"
          emissive="#e0ba78"
          emissiveIntensity={0.8}
        />
      </mesh>

      <mesh position={[0, 0.34, 0.69]}>
        <boxGeometry args={[0.72, 0.12, 0.05]} />
        <meshStandardMaterial
          color={emissive}
          emissive={emissive}
          emissiveIntensity={slot.state === "boosted" ? 2.2 : 1.15}
        />
      </mesh>

      {slot.state === "locked" && (
        <mesh position={[0, 1.2, 0]} castShadow>
          <boxGeometry args={[1.15, 1.2, 1.0]} />
          <meshStandardMaterial color="#151718" roughness={0.8} />
        </mesh>
      )}

      <Crop state={slot.state} />
    </group>
  );
}

function StarterRoomGeometry({ slots }: StarterRoom3DSceneProps) {
  return (
    <>
      <color attach="background" args={["#0d120f"]} />
      <ambientLight intensity={1.25} />
      <directionalLight position={[4, 7, 5]} intensity={2.1} color="#f4e8cf" />
      <directionalLight position={[-5, 3, 1]} intensity={0.8} color="#93cf9f" />

      <mesh position={[0, -0.08, 0]} receiveShadow>
        <boxGeometry args={[10, 0.18, 7]} />
        <meshStandardMaterial color="#17231c" roughness={0.95} />
      </mesh>

      <mesh position={[0, 2.3, -3.25]} receiveShadow>
        <boxGeometry args={[10, 4.6, 0.18]} />
        <meshStandardMaterial color="#132019" roughness={0.92} />
      </mesh>

      <mesh position={[-4.2, 1.0, -1.55]} castShadow>
        <boxGeometry args={[1.25, 2.0, 1.05]} />
        <meshStandardMaterial color="#324038" roughness={0.9} />
      </mesh>

      <mesh position={[4.0, 0.7, -1.7]} castShadow>
        <boxGeometry args={[2.2, 1.4, 0.95]} />
        <meshStandardMaterial color="#5a4633" roughness={0.9} />
      </mesh>

      {slots.map((slot) => (
        <ProductionSlot key={slot.id} slot={slot} />
      ))}
    </>
  );
}

export default function StarterRoom3DScene({ slots }: StarterRoom3DSceneProps) {
  return (
    <div className="starter-room-3d" aria-label="Interactive 3D starter workshop">
      <Canvas
        dpr={[1, 1.5]}
        camera={{ position: [7.1, 5.7, 8.2], fov: 39 }}
        gl={{ antialias: true, powerPreference: "high-performance" }}
      >
        <Suspense fallback={null}>
          <StarterRoomGeometry slots={slots} />
          <OrbitControls
            enablePan={false}
            minDistance={8}
            maxDistance={12}
            minPolarAngle={0.75}
            maxPolarAngle={1.25}
            minAzimuthAngle={-0.45}
            maxAzimuthAngle={0.45}
            target={[0, 1.0, 0]}
          />
        </Suspense>
      </Canvas>
    </div>
  );
}
