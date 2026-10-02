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
  onSelectSlot?: (slotId: string) => void;
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
    <div
      className={`scene-module ${className}`}
      aria-label={label}
      style={{ backgroundImage: `url("${asset}")` }}
    >
      <span className="scene-placeholder" aria-hidden="true" />
    </div>
  );
}

export default function StarterRoomScene({ slots, onSelectSlot }: StarterRoomSceneProps) {
  return (
    <div className="starter-room-scene" aria-label="Starter workshop visual">
      <div
        className="starter-room-shell"
        aria-hidden="true"
        style={{ backgroundImage: `url("${gameAssets.environment.starterRoomShell}")` }}
      />

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

      <div className="scene-expansion-zone" aria-hidden="true" />
      <div className="scene-slot-band" aria-label="Production slot positions">
        {slots.map((slot) => (
          <button
            key={slot.id}
            type="button"
            className={`scene-slot scene-slot-${slot.slotIndex} ${slot.state}`}
            aria-label={`${slot.label}. Open slot controls.`}
            onClick={() => onSelectSlot?.(slot.id)}
            style={{ backgroundImage: `url("${gameAssets.slots[slot.state]}")` }}
          >
            <span className="scene-slot-placeholder" aria-hidden="true" />
          </button>
        ))}
      </div>
    </div>
  );
}
