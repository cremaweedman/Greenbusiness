"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Mode = "login" | "register";

type TokenResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
};

type StarterVariety = {
  key: string;
  name: string;
  grow_seconds: number;
  base_yield: number;
  traits: string[];
  min_level: number;
  locked: boolean;
};

type Crop = {
  id: string;
  variety_key: string;
  variety_name: string;
  planted_at: string;
  ready_at: string;
  cared_at: string | null;
  is_ready: boolean;
};

type Slot = {
  id: string;
  slot_index: number;
  status: "available" | "planted" | "ready" | string;
  crop: Crop | null;
};

type InventoryItem = {
  item_key: string;
  display_name: string;
  quantity: number;
};

type InventoryLot = {
  item_key: string;
  display_name: string;
  quality: string;
  quantity: number;
};

type ContractOffer = {
  offer_id: string;
  offer_bucket: number;
  key: string;
  title: string;
  archetype: string;
  item_key: string;
  item_name: string;
  required_quantity: number;
  required_quality: string | null;
  required_trait: string | null;
  reward_cash: number;
  reward_reputation: number;
  min_level: number;
  min_reputation: number;
  specialized: boolean;
  locked: boolean;
  expires_at: string;
};

type PlayerContract = {
  id: string;
  offer_id: string;
  offer_bucket: number;
  contract_key: string;
  archetype: string;
  item_key: string;
  required_quantity: number;
  required_quality: string | null;
  required_trait: string | null;
  reward_cash: number;
  reward_reputation: number;
  status: string;
  accepted_at: string;
  completed_at: string | null;
};

type UpgradeOffer = {
  key: string;
  name: string;
  tier: number;
  cost_cash: number;
  yield_bonus: number;
  min_level: number;
  prerequisite_key: string | null;
  locked: boolean;
  locked_reason: string | null;
};

type SkillBranch = {
  branch: string;
  label: string;
  points: number;
  max_points: number;
  next_tier: string | null;
};

type Contact = {
  key: string;
  name: string;
  role: string;
  tone: string;
  intro_message: string;
};

type MissionReward = {
  cash: number;
  xp: number;
  reputation: number;
};

type PlayerMission = {
  key: string;
  sequence: number;
  contact_key: string;
  arc_key: string;
  arc_title: string;
  title: string;
  description: string;
  objective_type: string;
  objective_key: string | null;
  target: number;
  progress: number;
  status: "locked" | "active" | "completed" | string;
  reward: MissionReward;
  inbox_message: string;
  completed_at: string | null;
};

type VarietyMastery = {
  variety_key: string;
  variety_name: string;
  harvest_quantity: number;
  contract_quantity: number;
  points: number;
  tier: number;
  next_threshold: number | null;
  unlocked_cosmetic_keys: string[];
};

type SocialProfile = {
  user_id: string;
  friend_code: string;
  deep_link: string;
};

type ClubObjective = {
  id: string;
  period_key: string;
  objective_key: string;
  target_amount: number;
  progress_amount: number;
  reward_cash: number;
  status: string;
  completed_at: string | null;
};

type ClubMember = {
  user_id: string;
  display_name: string;
  role: string;
  joined_at: string;
};

type ClubState = {
  id: string;
  name: string;
  slug: string;
  invite_code: string;
  max_members: number;
  member_count: number;
  user_role: string | null;
  objective: ClubObjective | null;
  members: ClubMember[];
};

type SocialState = {
  profile: SocialProfile;
  friends: { user_id: string; display_name: string; friend_code: string; since: string }[];
  club: ClubState | null;
  pending_invites: { id: string; club_id: string; club_name: string; status: string }[];
};

type StoreProduct = {
  key: string;
  title: string;
  product_type: string;
  price_cents: number;
  currency_code: string;
  premium_credits: number;
  entitlement_keys: string[];
  cosmetic_keys: string[];
  consumable: boolean;
  disabled: boolean;
};

type StoreCatalog = {
  products: StoreProduct[];
  season_pass_enabled: boolean;
};

type PurchaseValidation = {
  purchase: { id: string; product_key: string; status: string; premium_credits_delta: number };
  premium_credits: number;
  duplicate_receipt: boolean;
};

type DecorationItem = {
  key: string;
  name: string;
  category: string;
  cost_cash: number;
  min_level: number;
  owned: boolean;
  equipped_slot: number | null;
  locked: boolean;
};

type DecorationState = {
  cash: number;
  items: DecorationItem[];
};

type NotificationState = {
  preferences: {
    production_enabled: boolean;
    events_enabled: boolean;
    social_enabled: boolean;
    quiet_hours_enabled: boolean;
    quiet_hours_start: string;
    quiet_hours_end: string;
    timezone: string;
  };
  push_tokens: { id: string; platform: string; token_label: string; enabled: boolean }[];
  deep_links: Record<string, string>;
  pwa: Record<string, boolean | string>;
};

type Player = {
  server_time: string;
  user_id: string;
  email: string;
  display_name: string;
  business_id: string;
  business_name: string;
  room_id: string;
  room_slug: string;
  room_level: number;
  slots: Slot[];
  level: number;
  xp: number;
  next_level_xp: number | null;
  reputation: number;
  skill_points_unspent: number;
  skill_branches: SkillBranch[];
  unlocked_keys: string[];
  tutorial_step: number;
  tutorial_completed: boolean;
  inventory_container_id: string;
  inventory: InventoryItem[];
  inventory_lots: InventoryLot[];
  starter_varieties: StarterVariety[];
  cash: number;
  premium_credits: number;
  active_entitlement_keys: string[];
  contract_offers: ContractOffer[];
  contract_refresh_at: string;
  active_contract: PlayerContract | null;
  active_contracts: PlayerContract[];
  upgrade_offers: UpgradeOffer[];
  owned_upgrade_keys: string[];
  contacts: Contact[];
  missions: PlayerMission[];
  daily_mission_keys: string[];
  weekly_mission_keys: string[];
  mastery: VarietyMastery[];
  unlocked_cosmetic_keys: string[];
};

type ApiError = {
  error?: {
    code?: string;
    message?: string;
  };
};

type ApiStatus = "checking" | "online" | "offline";

async function parseError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as ApiError;
    return body.error?.message ?? `Request failed (${response.status})`;
  } catch {
    return `Request failed (${response.status})`;
  }
}

async function requestJson<T>(
  path: string,
  accessToken: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...init.headers,
      Authorization: `Bearer ${accessToken}`,
    },
    credentials: "include",
    cache: "no-store",
  });
  if (!response.ok) throw new Error(await parseError(response));
  return (await response.json()) as T;
}

async function getPlayer(accessToken: string): Promise<Player> {
  return requestJson<Player>("/api/v1/player", accessToken);
}

async function getSocialState(accessToken: string): Promise<SocialState> {
  return requestJson<SocialState>("/api/v1/social/me", accessToken);
}

async function getStoreCatalog(): Promise<StoreCatalog> {
  const response = await fetch("/api/v1/store/catalog", { cache: "no-store" });
  if (!response.ok) throw new Error(await parseError(response));
  return (await response.json()) as StoreCatalog;
}

async function getNotificationState(accessToken: string): Promise<NotificationState> {
  return requestJson<NotificationState>("/api/v1/notifications/me", accessToken);
}

async function getDecorationState(accessToken: string): Promise<DecorationState> {
  return requestJson<DecorationState>("/api/v1/decorations/me", accessToken);
}

function formatRemaining(readyAt: string, now: number): string {
  const remainingSeconds = Math.max(0, Math.ceil((new Date(readyAt).getTime() - now) / 1000));
  if (remainingSeconds === 0) return "Ready";
  const minutes = Math.floor(remainingSeconds / 60);
  const seconds = remainingSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

function absoluteTimestamp(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function tutorialObjective(player: Player): string {
  if (player.tutorial_completed) return "First harvest complete";
  if (player.tutorial_step >= 2) return "Bring a ready crop in";
  if (player.tutorial_step >= 1) return "Care is available";
  return "Set the first crop";
}

function slotState(slot: Slot, now: number): "available" | "planted" | "ready" {
  if (!slot.crop) return "available";
  return new Date(slot.crop.ready_at).getTime() <= now ? "ready" : "planted";
}

export default function AuthApp() {
  const [mode, setMode] = useState<Mode>("register");
  const [player, setPlayer] = useState<Player | null>(null);
  const [social, setSocial] = useState<SocialState | null>(null);
  const [storeCatalog, setStoreCatalog] = useState<StoreCatalog | null>(null);
  const [notifications, setNotifications] = useState<NotificationState | null>(null);
  const [decorations, setDecorations] = useState<DecorationState | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [selectedVariety, setSelectedVariety] = useState<string | null>(null);
  const [restoring, setRestoring] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [actionSlotId, setActionSlotId] = useState<string | null>(null);
  const [economyBusy, setEconomyBusy] = useState<string | null>(null);
  const [skillBusy, setSkillBusy] = useState<string | null>(null);
  const [decorationBusy, setDecorationBusy] = useState<string | null>(null);
  const [feedbackKind, setFeedbackKind] = useState<"bug" | "feedback">("feedback");
  const [feedbackSeverity, setFeedbackSeverity] = useState<
    "blocker" | "major" | "minor" | "suggestion"
  >("suggestion");
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [feedbackBusy, setFeedbackBusy] = useState(false);
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [serverClockOffsetMs, setServerClockOffsetMs] = useState(0);

  const chosenVariety = useMemo(
    () => player?.starter_varieties.find((variety) => variety.key === selectedVariety) ?? null,
    [player?.starter_varieties, selectedVariety],
  );

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;
    void navigator.serviceWorker.register("/sw.js");
  }, []);

  useEffect(() => {
    if (!player || selectedVariety) return;
    setSelectedVariety(player.starter_varieties[0]?.key ?? null);
  }, [player, selectedVariety]);

  function applyPlayerState(nextPlayer: Player) {
    setServerClockOffsetMs(new Date(nextPlayer.server_time).getTime() - Date.now());
    setPlayer(nextPlayer);
  }

  useEffect(() => {
    let mounted = true;

    async function restoreSession() {
      try {
        const response = await fetch("/api/v1/auth/refresh", {
          method: "POST",
          credentials: "include",
        });
        if (!response.ok) return;
        const token = (await response.json()) as TokenResponse;
        const restored = await getPlayer(token.access_token);
        let restoredSocial: SocialState | null = null;
        try {
          restoredSocial = await getSocialState(token.access_token);
        } catch {
          restoredSocial = null;
        }
        let restoredNotifications: NotificationState | null = null;
        try {
          restoredNotifications = await getNotificationState(token.access_token);
        } catch {
          restoredNotifications = null;
        }
        if (!mounted) return;
        setAccessToken(token.access_token);
        applyPlayerState(restored);
        setSocial(restoredSocial);
        setNotifications(restoredNotifications);
      } catch {
        // A missing/expired session is a normal anonymous state.
      } finally {
        if (mounted) setRestoring(false);
      }
    }

    void restoreSession();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    let mounted = true;
    async function loadCatalog() {
      try {
        const catalog = await getStoreCatalog();
        if (mounted) setStoreCatalog(catalog);
      } catch {
        if (mounted) setStoreCatalog(null);
      }
    }
    void loadCatalog();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    const token = accessToken;
    if (!token) {
      setDecorations(null);
      return;
    }
    let mounted = true;
    async function loadDecorations() {
      try {
        const state = await getDecorationState(token);
        if (mounted) setDecorations(state);
      } catch {
        if (mounted) setDecorations(null);
      }
    }
    void loadDecorations();
    return () => {
      mounted = false;
    };
  }, [accessToken]);

  useEffect(() => {
    let mounted = true;

    async function checkApi() {
      try {
        const response = await fetch("/api/health/live", {
          cache: "no-store",
        });
        if (!mounted) return;
        setApiStatus(response.ok ? "online" : "offline");
      } catch {
        if (mounted) setApiStatus("offline");
      }
    }

    void checkApi();
    const interval = window.setInterval(() => {
      void checkApi();
    }, 15_000);

    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, []);

  async function refreshPlayer(token = accessToken) {
    if (!token) return;
    applyPlayerState(await getPlayer(token));
    try {
      setSocial(await getSocialState(token));
    } catch {
      setSocial(null);
    }
    try {
      setNotifications(await getNotificationState(token));
    } catch {
      setNotifications(null);
    }
    try {
      setDecorations(await getDecorationState(token));
    } catch {
      setDecorations(null);
    }
  }

  async function authenticate(endpoint: "login" | "register", payload: object) {
    setSubmitting(true);
    setError(null);
    setNotice(null);
    try {
      if (apiStatus === "offline") {
        throw new Error("API is offline. Start the backend, then try again.");
      }
      const response = await fetch(`/api/v1/auth/${endpoint}`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error(await parseError(response));

      const token = (await response.json()) as TokenResponse;
      const currentPlayer = await getPlayer(token.access_token);
      let currentSocial: SocialState | null = null;
      try {
        currentSocial = await getSocialState(token.access_token);
      } catch {
        currentSocial = null;
      }
      let currentNotifications: NotificationState | null = null;
      try {
        currentNotifications = await getNotificationState(token.access_token);
      } catch {
        currentNotifications = null;
      }
      setAccessToken(token.access_token);
      applyPlayerState(currentPlayer);
      setSocial(currentSocial);
      setNotifications(currentNotifications);
      setSelectedVariety(currentPlayer.starter_varieties.find((item) => !item.locked)?.key ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed.");
    } finally {
      setSubmitting(false);
    }
  }

  async function enterAsCreator() {
    setSubmitting(true);
    setError(null);
    setNotice(null);
    try {
      if (apiStatus === "offline") {
        throw new Error("API is offline. Start the backend, then try again.");
      }
      const response = await fetch("/api/v1/auth/dev/creator", {
        method: "POST",
        credentials: "include",
      });
      if (!response.ok) throw new Error(await parseError(response));

      const token = (await response.json()) as TokenResponse;
      const currentPlayer = await getPlayer(token.access_token);
      let currentSocial: SocialState | null = null;
      try {
        currentSocial = await getSocialState(token.access_token);
      } catch {
        currentSocial = null;
      }
      let currentNotifications: NotificationState | null = null;
      try {
        currentNotifications = await getNotificationState(token.access_token);
      } catch {
        currentNotifications = null;
      }
      setAccessToken(token.access_token);
      applyPlayerState(currentPlayer);
      setSocial(currentSocial);
      setNotifications(currentNotifications);
      setSelectedVariety(currentPlayer.starter_varieties.find((item) => !item.locked)?.key ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Creator access failed.");
    } finally {
      setSubmitting(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const email = String(data.get("email") ?? "");
    const password = String(data.get("password") ?? "");

    if (mode === "register") {
      await authenticate("register", {
        email,
        password,
        display_name: String(data.get("display_name") ?? ""),
      });
    } else {
      await authenticate("login", { email, password });
    }
  }

  async function runProductionAction(slot: Slot, action: "plant" | "care" | "harvest") {
    if (!accessToken) return;
    setActionSlotId(slot.id);
    setError(null);
    setNotice(null);
    try {
      if (action === "plant") {
        if (!selectedVariety) throw new Error("Choose a starter variety first.");
        await requestJson<Slot>(`/api/v1/production/slots/${slot.id}/plant`, accessToken, {
          method: "POST",
          body: JSON.stringify({ variety_key: selectedVariety }),
        });
        setNotice(`${chosenVariety?.name ?? "Starter crop"} planted.`);
      } else if (action === "care") {
        await requestJson<Slot>(`/api/v1/production/slots/${slot.id}/care`, accessToken, {
          method: "POST",
        });
        setNotice("Care applied.");
      } else {
        const harvest = await requestJson<{
          yield_quantity: number;
          quality: string;
          harvested_item: InventoryItem;
          xp_reward: number;
        }>(`/api/v1/production/slots/${slot.id}/harvest`, accessToken, { method: "POST" });
        setNotice(
          `Harvested ${harvest.yield_quantity} ${harvest.harvested_item.display_name} (${harvest.quality}) +${harvest.xp_reward} XP.`,
        );
      }
      await refreshPlayer();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed.");
      await refreshPlayer();
    } finally {
      setActionSlotId(null);
    }
  }

  async function runEconomyAction(
    action: "accept" | "complete" | "upgrade",
    target: string,
  ) {
    if (!accessToken) return;
    setEconomyBusy(`${action}:${target}`);
    setError(null);
    setNotice(null);
    try {
      if (action === "accept") {
        await requestJson<PlayerContract>(
          `/api/v1/economy/offers/${encodeURIComponent(target)}/accept`,
          accessToken,
          { method: "POST" },
        );
        setNotice("Contract accepted.");
      } else if (action === "complete") {
        await requestJson(
          `/api/v1/economy/contracts/${target}/complete`,
          accessToken,
          {
            method: "POST",
            headers: { "Idempotency-Key": crypto.randomUUID() },
          },
        );
        setNotice("Contract completed. Cash received.");
      } else {
        await requestJson(
          `/api/v1/economy/upgrades/${target}/purchase`,
          accessToken,
          {
            method: "POST",
            headers: { "Idempotency-Key": crypto.randomUUID() },
          },
        );
        setNotice("Upgrade purchased. Future harvest yield improved.");
      }
      await refreshPlayer();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Economic action failed.");
      await refreshPlayer();
    } finally {
      setEconomyBusy(null);
    }
  }

  async function allocateSkill(branch: string) {
    if (!accessToken) return;
    setSkillBusy(branch);
    setError(null);
    setNotice(null);
    try {
      const result = await requestJson<SkillBranch>(
        `/api/v1/economy/skills/${encodeURIComponent(branch)}/allocate`,
        accessToken,
        { method: "POST" },
      );
      setNotice(`${result.label} advanced to ${result.points}/${result.max_points}.`);
      await refreshPlayer();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Skill allocation failed.");
      await refreshPlayer();
    } finally {
      setSkillBusy(null);
    }
  }

  async function logout() {
    setSubmitting(true);
    try {
      await fetch("/api/v1/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } finally {
      setAccessToken(null);
      setPlayer(null);
      setSocial(null);
      setNotifications(null);
      setSelectedVariety(null);
      setSubmitting(false);
    }
  }

  async function createStarterClub() {
    if (!accessToken || !player) return;
    setError(null);
    setNotice(null);
    try {
      await requestJson<ClubState>("/api/v1/clubs", accessToken, {
        method: "POST",
        body: JSON.stringify({ name: `${player.display_name}'s Crew` }),
      });
      setSocial(await getSocialState(accessToken));
      setNotice("Club created. Share the invite code with trusted players.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Club action failed.");
    }
  }

  async function buySandboxProduct(productKey: string) {
    if (!accessToken) return;
    setError(null);
    setNotice(null);
    try {
      const product = storeCatalog?.products.find((item) => item.key === productKey);
      const confirmed = window.confirm(
        `Confirm sandbox purchase: ${product?.title ?? productKey}. Premium spend and entitlement grants always require confirmation.`,
      );
      if (!confirmed) return;
      const receiptId = `sandbox:${productKey}:${crypto.randomUUID()}`;
      const result = await requestJson<PurchaseValidation>(
        "/api/v1/store/purchases/validate",
        accessToken,
        {
          method: "POST",
          body: JSON.stringify({
            provider: "sandbox",
            receipt_id: receiptId,
            product_key: productKey,
          }),
        },
      );
      await refreshPlayer();
      setNotice(
        result.purchase.premium_credits_delta > 0
          ? `Sandbox purchase granted ${result.purchase.premium_credits_delta} Credits.`
          : "Sandbox entitlement granted.",
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Store action failed.");
    }
  }

  async function purchaseDecoration(decorationKey: string) {
    if (!accessToken) return;
    setDecorationBusy(`purchase:${decorationKey}`);
    setError(null);
    setNotice(null);
    try {
      await requestJson(
        `/api/v1/decorations/${encodeURIComponent(decorationKey)}/purchase`,
        accessToken,
        {
          method: "POST",
          headers: { "Idempotency-Key": crypto.randomUUID() },
        },
      );
      setDecorations(await getDecorationState(accessToken));
      await refreshPlayer();
      setNotice("Decoration purchased.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Decoration purchase failed.");
    } finally {
      setDecorationBusy(null);
    }
  }

  async function equipDecoration(decorationKey: string, slotIndex: number) {
    if (!accessToken) return;
    setDecorationBusy(`equip:${decorationKey}`);
    setError(null);
    setNotice(null);
    try {
      await requestJson(
        `/api/v1/decorations/${encodeURIComponent(decorationKey)}/equip`,
        accessToken,
        {
          method: "PUT",
          body: JSON.stringify({ slot_index: slotIndex }),
        },
      );
      setDecorations(await getDecorationState(accessToken));
      setNotice(`Decoration equipped in cosmetic slot ${slotIndex + 1}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Decoration equip failed.");
    } finally {
      setDecorationBusy(null);
    }
  }

  async function submitAlphaFeedback(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!accessToken || feedbackMessage.trim().length < 3) return;
    setFeedbackBusy(true);
    setError(null);
    setNotice(null);
    try {
      await requestJson("/api/v1/alpha/feedback", accessToken, {
        method: "POST",
        body: JSON.stringify({
          kind: feedbackKind,
          severity: feedbackSeverity,
          category: "closed-alpha",
          message: feedbackMessage.trim(),
        }),
      });
      setFeedbackMessage("");
      setNotice("Alpha feedback submitted.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Feedback submission failed.");
    } finally {
      setFeedbackBusy(false);
    }
  }

  async function toggleNotificationCategory(
    key: "production_enabled" | "events_enabled" | "social_enabled",
  ) {
    if (!accessToken || !notifications) return;
    setError(null);
    try {
      await requestJson("/api/v1/notifications/preferences", accessToken, {
        method: "PATCH",
        body: JSON.stringify({ [key]: !notifications.preferences[key] }),
      });
      setNotifications(await getNotificationState(accessToken));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Notification update failed.");
    }
  }

  if (restoring) {
    return (
      <section className="panel" aria-live="polite">
        <p className="eyebrow">PHASE 4 - MISSIONS</p>
        <h1>GreenBusiness</h1>
        <p className="muted">Restoring secure session...</p>
      </section>
    );
  }

  if (player && accessToken) {
    const serverNow = now + serverClockOffsetMs;

    return (
      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">STARTER ROOM ONLINE</p>
            <h1>{player.business_name}</h1>
            <p className="muted">
              {player.display_name} - Level {player.level} - XP {player.xp}
              {player.next_level_xp ? `/${player.next_level_xp}` : " (MAX)"} - Reputation{" "}
              {player.reputation} - Skill points {player.skill_points_unspent}
            </p>
          </div>
          <div className="topbar-actions">
            <div className="cash-chip" aria-label={`Cash balance ${player.cash}`}>
              Cash <strong>{player.cash}</strong>
            </div>
            <div className="cash-chip" aria-label={`Credits balance ${player.premium_credits}`}>
              Credits <strong>{player.premium_credits}</strong>
            </div>
            <button className="secondary compact" onClick={logout} disabled={submitting}>
              Sign out
            </button>
          </div>
        </header>

        <section className="clubhouse-panel" aria-label="Clubhouse social layer">
          <div>
            <p className="section-label">Clubhouse</p>
            <h2>Social layer</h2>
            <p className="muted">
              Friend code {social?.profile.friend_code ?? "loading"} ·{" "}
              {social?.friends.length ?? 0} friends
            </p>
          </div>

          {social?.club ? (
            <div className="clubhouse-card">
              <strong>{social.club.name}</strong>
              <span>
                {social.club.member_count}/{social.club.max_members} members · invite{" "}
                {social.club.invite_code}
              </span>
              {social.club.objective && (
                <span>
                  Weekly objective {social.club.objective.progress_amount}/
                  {social.club.objective.target_amount} · {social.club.objective.status} · +
                  {social.club.objective.reward_cash} Cash
                </span>
              )}
            </div>
          ) : (
            <div className="clubhouse-card">
              <strong>No club yet</strong>
              <span>Create a small crew when you are ready to test assists and rewards.</span>
              <button className="secondary compact" onClick={() => void createStarterClub()}>
                Create club
              </button>
            </div>
          )}
        </section>

        <section className="store-panel" aria-label="Room decorations">
          <div>
            <p className="section-label">Decorations</p>
            <h2>Alpha room cosmetics</h2>
            <p className="muted">
              40 cosmetic items · no gameplay power · purchased with earned Cash
            </p>
          </div>
          <div className="store-grid">
            {(decorations?.items ?? []).slice(0, 8).map((item, index) => (
              <article key={item.key} className="store-card">
                <strong>{item.name}</strong>
                <span>
                  {item.category} · {item.cost_cash} Cash · level {item.min_level}
                </span>
                {item.owned ? (
                  <button
                    className="secondary compact"
                    disabled={decorationBusy !== null}
                    onClick={() => void equipDecoration(item.key, index % 12)}
                  >
                    {item.equipped_slot === null
                      ? "Equip"
                      : `Equipped slot ${item.equipped_slot + 1}`}
                  </button>
                ) : (
                  <button
                    className="secondary compact"
                    disabled={
                      decorationBusy !== null ||
                      item.locked ||
                      (decorations?.cash ?? 0) < item.cost_cash
                    }
                    onClick={() => void purchaseDecoration(item.key)}
                  >
                    {item.locked ? `Unlocks L${item.min_level}` : "Buy cosmetic"}
                  </button>
                )}
              </article>
            ))}
          </div>
        </section>

        <section className="notification-panel" aria-label="Closed alpha feedback">
          <div>
            <p className="section-label">Closed Alpha</p>
            <h2>Send tester feedback</h2>
            <p className="muted">
              Report blockers separately from suggestions so the alpha queue stays actionable.
            </p>
          </div>
          <form className="alpha-feedback-form" onSubmit={submitAlphaFeedback}>
            <select
              value={feedbackKind}
              onChange={(event) => setFeedbackKind(event.target.value as "bug" | "feedback")}
              aria-label="Feedback type"
            >
              <option value="feedback">Feedback</option>
              <option value="bug">Bug</option>
            </select>
            <select
              value={feedbackSeverity}
              onChange={(event) =>
                setFeedbackSeverity(
                  event.target.value as "blocker" | "major" | "minor" | "suggestion",
                )
              }
              aria-label="Feedback severity"
            >
              <option value="suggestion">Suggestion</option>
              <option value="minor">Minor</option>
              <option value="major">Major</option>
              <option value="blocker">Blocker</option>
            </select>
            <textarea
              value={feedbackMessage}
              onChange={(event) => setFeedbackMessage(event.target.value)}
              placeholder="What happened, what did you expect, and what were you doing?"
              maxLength={2000}
              required
            />
            <button
              className="primary"
              type="submit"
              disabled={feedbackBusy || feedbackMessage.trim().length < 3}
            >
              {feedbackBusy ? "Sending..." : "Send feedback"}
            </button>
          </form>
        </section>

        <section className="store-panel" aria-label="Store and entitlements">
          <div>
            <p className="section-label">Store</p>
            <h2>Ethical monetization sandbox</h2>
            <p className="muted">
              Season Pass disabled · {player.active_entitlement_keys.length} active entitlements
            </p>
          </div>
          <div className="store-grid">
            {(storeCatalog?.products ?? []).slice(0, 3).map((product) => (
              <article key={product.key} className="store-card">
                <strong>{product.title}</strong>
                <span>
                  {product.price_cents / 100} {product.currency_code} ·{" "}
                  {product.premium_credits > 0
                    ? `${product.premium_credits} Credits`
                    : `${product.entitlement_keys.length} entitlement(s)`}
                </span>
                <button
                  className="secondary compact"
                  disabled={product.disabled}
                  onClick={() => void buySandboxProduct(product.key)}
                >
                  Sandbox buy
                </button>
              </article>
            ))}
          </div>
        </section>

        <section className="notification-panel" aria-label="Notifications and accessibility">
          <div>
            <p className="section-label">Notifications</p>
            <h2>Convenience, never coercion</h2>
            <p className="muted">
              Core gameplay works without push · Quiet hours{" "}
              {notifications?.preferences.quiet_hours_start ?? "22:00"}-
              {notifications?.preferences.quiet_hours_end ?? "08:00"}
            </p>
            <p className="muted">
              PWA installable · Offline read cache · Deep links ready for production, club and store
            </p>
          </div>
          <div className="notification-grid" role="group" aria-label="Notification categories">
            {[
              ["production_enabled", "Production timers"],
              ["events_enabled", "Events & seasons"],
              ["social_enabled", "Club & social"],
            ].map(([key, label]) => {
              const typedKey = key as "production_enabled" | "events_enabled" | "social_enabled";
              const enabled = notifications?.preferences[typedKey] ?? false;
              return (
                <button
                  key={key}
                  type="button"
                  className={enabled ? "toggle-card enabled" : "toggle-card"}
                  onClick={() => void toggleNotificationCategory(typedKey)}
                  aria-pressed={enabled}
                >
                  <strong>{enabled ? "On" : "Off"}</strong>
                  <span>{label}</span>
                </button>
              );
            })}
          </div>
        </section>

        <div className="game-grid">
          <aside className="tool-panel">
            <div className="objective">
              <p className="section-label">Current objective</p>
              <strong>{tutorialObjective(player)}</strong>
              <span>{player.tutorial_completed ? "Reward secured" : "Starter loop"}</span>
            </div>

            <div>
              <p className="section-label">Starter varieties</p>
              <div className="variety-list" role="radiogroup" aria-label="Starter varieties">
                {player.starter_varieties.map((variety) => (
                  <button
                    key={variety.key}
                    type="button"
                    className={`${selectedVariety === variety.key ? "variety active" : "variety"} ${variety.locked ? "locked" : ""}`}
                    onClick={() => !variety.locked && setSelectedVariety(variety.key)}
                    disabled={variety.locked}
                  >
                    <strong>{variety.name}</strong>
                    <span>
                      {variety.locked
                        ? `Unlocks at level ${variety.min_level}`
                        : `${Math.ceil(variety.grow_seconds / 60)} min - Yield ${variety.base_yield}`}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <p className="section-label">Skills</p>
              <div className="economy-list">
                {player.skill_branches.map((skill) => (
                  <article key={skill.branch} className="economy-card">
                    <strong>{skill.label} · {skill.points}/{skill.max_points}</strong>
                    <span>{skill.next_tier ? `Next: ${skill.next_tier}` : "Tree complete"}</span>
                    <button
                      className="secondary"
                      onClick={() => void allocateSkill(skill.branch)}
                      disabled={
                        skillBusy !== null ||
                        player.skill_points_unspent <= 0 ||
                        skill.points >= skill.max_points
                      }
                    >
                      {skill.points >= skill.max_points ? "Maxed" : "Allocate point"}
                    </button>
                  </article>
                ))}
              </div>
            </div>

            <div>
              <p className="section-label">Inventory</p>
              <div className="inventory-list">
                {player.inventory.length === 0 ? (
                  <p className="empty-state">No harvested inventory yet.</p>
                ) : (
                  player.inventory.map((item) => (
                    <article key={item.item_key} className="inventory-item">
                      <span>{item.display_name}</span>
                      <strong>{item.quantity}</strong>
                    </article>
                  ))
                )}
              </div>
            </div>

            <div>
              <p className="section-label">Economy</p>
              <div className="economy-list">
                <p className="empty-state">
                  Offers refresh in {formatRemaining(player.contract_refresh_at, serverNow)}
                </p>

                {player.contract_offers.map((offer) => (
                  <article
                    key={offer.offer_id}
                    className={offer.locked ? "economy-card locked" : "economy-card"}
                  >
                    <strong>
                      {offer.specialized ? "Specialized · " : ""}
                      {offer.title}
                    </strong>
                    <span>
                      {offer.archetype} · Deliver {offer.required_quantity} {offer.item_name}
                      {offer.required_quality ? ` · ${offer.required_quality} quality` : ""}
                      {offer.required_trait ? ` · ${offer.required_trait} trait` : ""}
                    </span>
                    <span>
                      +{offer.reward_cash} Cash · +{offer.reward_reputation} Reputation
                    </span>
                    {offer.locked && (
                      <span>
                        Requires level {offer.min_level} / reputation {offer.min_reputation}
                      </span>
                    )}
                    <button
                      className="secondary"
                      onClick={() => void runEconomyAction("accept", offer.offer_id)}
                      disabled={economyBusy !== null || offer.locked}
                    >
                      {offer.locked ? "Locked" : "Accept contract"}
                    </button>
                  </article>
                ))}

                {player.active_contracts.map((contract) => (
                  <article key={contract.id} className="economy-card">
                    <strong>Active · {contract.contract_key}</strong>
                    <span>
                      Deliver {contract.required_quantity}
                      {contract.required_quality ? ` · ${contract.required_quality} quality` : ""}
                      {contract.required_trait ? ` · ${contract.required_trait} trait` : ""}
                    </span>
                    <span>
                      +{contract.reward_cash} Cash · +{contract.reward_reputation} Reputation
                    </span>
                    <button
                      className="primary"
                      onClick={() => void runEconomyAction("complete", contract.id)}
                      disabled={economyBusy !== null}
                    >
                      Complete contract
                    </button>
                  </article>
                ))}

                {player.upgrade_offers.map((upgrade) => (
                  <article
                    key={upgrade.key}
                    className={upgrade.locked ? "economy-card locked" : "economy-card"}
                  >
                    <strong>{upgrade.name} · Tier {upgrade.tier}</strong>
                    <span>
                      {upgrade.cost_cash} Cash · +{upgrade.yield_bonus} yield per harvest
                    </span>
                    {upgrade.locked_reason && <span>{upgrade.locked_reason}</span>}
                    <button
                      className="primary"
                      onClick={() => void runEconomyAction("upgrade", upgrade.key)}
                      disabled={
                        economyBusy !== null ||
                        upgrade.locked ||
                        player.cash < upgrade.cost_cash
                      }
                    >
                      {upgrade.locked ? "Locked" : "Buy upgrade"}
                    </button>
                  </article>
                ))}

                {player.owned_upgrade_keys.length > 0 && (
                  <article className="economy-card complete">
                    <strong>Owned upgrades</strong>
                    <span>{player.owned_upgrade_keys.join(", ")}</span>
                  </article>
                )}
              </div>
            </div>
          </aside>

          <div className="room-board" aria-label="Starter production slots">
            <div className="room-scene" aria-hidden="true">
              <div className="room-wall" />
              <div className="room-floor">
                {player.slots.map((slot) => {
                  const state = slotState(slot, serverNow);
                  return (
                    <span
                      key={slot.id}
                      className={`iso-plot slot-${slot.slot_index} ${state}`}
                    >
                      <span />
                    </span>
                  );
                })}
              </div>
            </div>

            <div className="slot-list">
              {player.slots.map((slot) => {
                const busy = actionSlotId === slot.id;
                const remaining = slot.crop ? formatRemaining(slot.crop.ready_at, serverNow) : null;
                const isReady = slotState(slot, serverNow) === "ready";
                return (
                  <article key={slot.id} className={`slot-card ${slot.status}`}>
                    <div className="slot-head">
                      <span>Slot {slot.slot_index + 1}</span>
                      <strong>{slot.crop ? slot.crop.variety_name : "Available"}</strong>
                    </div>

                    {slot.crop ? (
                      <>
                        <div className="crop-meter" aria-hidden="true">
                          <span style={{ width: isReady ? "100%" : "48%" }} />
                        </div>
                        <div className="slot-meta">
                          <span title={`Ready at ${absoluteTimestamp(slot.crop.ready_at)}`}>
                            {remaining} · {absoluteTimestamp(slot.crop.ready_at)}
                          </span>
                          <span>{slot.crop.cared_at ? "Cared" : "Care optional"}</span>
                        </div>
                        <div className="slot-actions">
                          <button
                            className="secondary"
                            onClick={() => void runProductionAction(slot, "care")}
                            disabled={busy || Boolean(slot.crop.cared_at)}
                          >
                            Care
                          </button>
                          <button
                            className="primary"
                            onClick={() => void runProductionAction(slot, "harvest")}
                            disabled={busy || !isReady}
                          >
                            Harvest
                          </button>
                        </div>
                      </>
                    ) : (
                      <>
                        <p className="empty-state">Ready for the next fictional starter crop.</p>
                        <button
                          className="primary"
                          onClick={() => void runProductionAction(slot, "plant")}
                          disabled={busy || !selectedVariety}
                        >
                          Plant {chosenVariety?.name ?? "variety"}
                        </button>
                      </>
                    )}
                  </article>
                );
              })}
            </div>
          </div>
        </div>

        <section className="phone-panel" aria-label="Phone missions and mastery">
          <div className="phone-head">
            <div>
              <p className="section-label">Phone</p>
              <h2>Missions & mastery</h2>
            </div>
            <div className="pool-chips" aria-label="Mission pools">
              <span>Daily {player.daily_mission_keys.length}</span>
              <span>Weekly {player.weekly_mission_keys.length}</span>
            </div>
          </div>

          <div className="meta-grid">
            <div>
              <p className="section-label">Contacts</p>
              <div className="contact-list">
                {player.contacts.map((contact) => (
                  <article key={contact.key} className="contact-card">
                    <div>
                      <strong>{contact.name}</strong>
                      <span>{contact.role}</span>
                    </div>
                    <p>{contact.intro_message}</p>
                  </article>
                ))}
              </div>
            </div>

            <div>
              <p className="section-label">Narrative arcs</p>
              <p className="empty-state">
                {player.missions.filter((mission) => mission.status === "completed").length} completed ·{" "}
                {player.missions.filter((mission) => mission.status === "active").length} active
              </p>
              <div className="mission-list">
                {player.missions.map((mission) => {
                  const percentage =
                    mission.target > 0 ? Math.min(100, (mission.progress / mission.target) * 100) : 0;
                  return (
                    <article key={mission.key} className={`mission-card ${mission.status}`}>
                      <div className="mission-head">
                        <span>#{mission.sequence}</span>
                        <strong>{mission.title}</strong>
                        <em>{mission.status}</em>
                      </div>
                      <p className="muted">{mission.arc_title}</p>
                      <p>{mission.description}</p>
                      {mission.status === "completed" && (
                        <p className="muted">Inbox: {mission.inbox_message}</p>
                      )}
                      <div
                        className="progress-track"
                        aria-label={`${mission.progress} of ${mission.target}`}
                      >
                        <span style={{ width: `${percentage}%` }} />
                      </div>
                      <div className="mission-meta">
                        <span>
                          {mission.progress}/{mission.target}
                        </span>
                        <span>
                          +{mission.reward.xp} XP
                          {mission.reward.cash > 0 ? ` · +${mission.reward.cash} Cash` : ""}
                          {mission.reward.reputation > 0
                            ? ` · +${mission.reward.reputation} Rep`
                            : ""}
                        </span>
                      </div>
                    </article>
                  );
                })}
              </div>
            </div>

            <div>
              <p className="section-label">Collection mastery</p>
              <div className="mastery-list">
                {player.mastery.length === 0 ? (
                  <p className="empty-state">Harvest a variety to start its mastery track.</p>
                ) : (
                  player.mastery.map((item) => (
                    <article key={item.variety_key} className="mastery-card">
                      <div className="mission-head">
                        <strong>{item.variety_name}</strong>
                        <em>Tier {item.tier}</em>
                      </div>
                      <div className="mission-meta">
                        <span>{item.points} mastery</span>
                        <span>
                          {item.next_threshold ? `Next: ${item.next_threshold}` : "Max starter tier"}
                        </span>
                      </div>
                      <p>
                        Harvest {item.harvest_quantity} · Contracts {item.contract_quantity}
                      </p>
                      {item.unlocked_cosmetic_keys.length > 0 && (
                        <span className="cosmetic-unlock">
                          {item.unlocked_cosmetic_keys.length} cosmetic reward
                          {item.unlocked_cosmetic_keys.length === 1 ? "" : "s"} unlocked
                        </span>
                      )}
                    </article>
                  ))
                )}
              </div>
            </div>
          </div>
        </section>

        {(notice || error) && (
          <p className={error ? "error" : "notice"} role={error ? "alert" : "status"}>
            {error ?? notice}
          </p>
        )}

        <p className="account">{player.email}</p>
      </section>
    );
  }

  return (
    <section className="panel auth">
      <p className="eyebrow">PHASE 3 - ECONOMY</p>
      <h1>GreenBusiness</h1>
      <p className="muted">
        {mode === "register"
          ? "Create the owner profile for your first business."
          : "Continue your existing business."}
      </p>

      <p className={`api-status ${apiStatus}`} aria-live="polite">
        {apiStatus === "checking"
          ? "Checking API..."
          : apiStatus === "online"
            ? "API online"
            : "API offline - start the backend before creating an account"}
      </p>

      <div className="tabs" role="tablist" aria-label="Authentication mode">
        <button
          type="button"
          className={mode === "register" ? "active" : ""}
          onClick={() => {
            setMode("register");
            setError(null);
          }}
        >
          Create account
        </button>
        <button
          type="button"
          className={mode === "login" ? "active" : ""}
          onClick={() => {
            setMode("login");
            setError(null);
          }}
        >
          Sign in
        </button>
      </div>

      <form onSubmit={onSubmit}>
        {mode === "register" && (
          <label>
            Display name
            <input
              name="display_name"
              minLength={1}
              maxLength={32}
              autoComplete="nickname"
              required
            />
          </label>
        )}
        <label>
          Email
          <input name="email" type="email" autoComplete="email" required />
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            minLength={10}
            maxLength={128}
            autoComplete={mode === "register" ? "new-password" : "current-password"}
            required
          />
        </label>

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <button className="primary" type="submit" disabled={submitting}>
          {submitting ? "Working..." : mode === "register" ? "Start business" : "Sign in"}
        </button>
      </form>

      <button className="secondary creator-access" onClick={() => void enterAsCreator()} disabled={submitting}>
        Entrar como creador
      </button>
    </section>
  );
}
