export const gameAssets = {
  environment: {
    starterRoomShell: "/assets/environment/gb_environment_starter-room_shell_v01.webp",
    starterStorage: "/assets/environment/gb_room_storage_starter_v01.webp",
    contractAnchor: "/assets/environment/gb_room_contract-anchor_default_v01.webp",
    starterWorkbench: "/assets/environment/gb_room_workbench_starter_v01.webp",
    starterDesk: "/assets/environment/gb_room_desk_starter_v01.webp",
  },
  slots: {
    empty: "/assets/slots/gb_slot_starter_empty_default_v01.webp",
    planted: "/assets/slots/gb_slot_starter_planted_default_v01.webp",
    growing: "/assets/slots/gb_slot_starter_growing_default_v01.webp",
    ready: "/assets/slots/gb_slot_starter_ready_default_v01.webp",
    locked: "/assets/slots/gb_slot_starter_locked_default_v01.webp",
    attention: "/assets/slots/gb_slot_starter_attention_default_v01.webp",
    boosted: "/assets/slots/gb_slot_starter_boosted_default_v01.webp",
  },
  crops: {
    "aurora-drift": "/assets/crops/gb_crop_aurora-drift_icon_default_v01.webp",
    "ember-leaf": "/assets/crops/gb_crop_ember-leaf_icon_default_v01.webp",
    "moon-sprout": "/assets/crops/gb_crop_moon-sprout_icon_default_v01.webp",
  },
  contacts: {
    "alex-rowan": "/assets/characters/gb_character_alex-rowan_portrait_default_v01.webp",
    "mira-vale": "/assets/characters/gb_character_mira-vale_portrait_default_v01.webp",
  },
} as const;

export type StarterSlotVisualState = keyof typeof gameAssets.slots;
