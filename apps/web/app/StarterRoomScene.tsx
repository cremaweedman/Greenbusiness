"use client";

import { gameAssets, type StarterSlotVisualState } from "./gameAssets";

type SceneSlot = {
  id: string;
  slotIndex: number;
  state: StarterSlotVisualState;
  label: string;
};

type StarterRoomSceneProps = {
  slots: SceneSlot[];
};

function SceneModule({
  className,
  asset,
  label,
}: {
  className: string;
  asset: string;
  label: string;
}) {
  return (
    <div className={`scene-module ${className}`} aria-label={label}>
      <img src={asset} alt="" aria-hidden="true" />
      <span className="scene-placeholder" aria-hidden="true" />
    </div>
  );
}

export default function StarterRoomScene({ slots }: StarterRoomSceneProps) {
  return (
    <div className="starter-room-scene" aria-label="Starter workshop visual">
      <div className="starter-room-shell" aria-hidden="true">
        <img src={gameAssets.environment.starterRoomShell} alt="" />
      </div>

      <SceneModule
        className="scene-storage"
        asset={gameAssets.environment.starterStorage}
        label="Starter storage"
      />
      <SceneModule
        className="scene-contracts"
        asset={gameAssets.environment.contractAnchor}
        label="Contracts station"
      />
      <SceneModule
        className="scene-workbench"
        asset={gameAssets.environment.starterWorkbench}
        label="Workbench"
      />
      <SceneModule
        className="scene-desk"
        asset={gameAssets.environment.starterDesk}
        label="Management desk"
      />

      <div className="scene-slot-band" aria-label="Production slot positions">
        {slots.map((slot) => (
          <div
            key={slot.id}
            className={`scene-slot scene-slot-${slot.slotIndex} ${slot.state}`}
            aria-label={slot.label}
          >
            <img src={gameAssets.slots[slot.state]} alt="" aria-hidden="true" />
            <span className="scene-slot-placeholder" aria-hidden="true" />
          </div>
        ))}
      </div>
    </div>
  );
}
