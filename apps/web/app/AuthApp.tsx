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
  reputation: number;
  tutorial_step: number;
  tutorial_completed: boolean;
  inventory_container_id: string;
  inventory: InventoryItem[];
  starter_varieties: StarterVariety[];
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

function formatRemaining(readyAt: string, now: number): string {
  const remainingSeconds = Math.max(0, Math.ceil((new Date(readyAt).getTime() - now) / 1000));
  if (remainingSeconds === 0) return "Ready";
  const minutes = Math.floor(remainingSeconds / 60);
  const seconds = remainingSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
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
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [selectedVariety, setSelectedVariety] = useState<string | null>(null);
  const [restoring, setRestoring] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [actionSlotId, setActionSlotId] = useState<string | null>(null);
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
        if (!mounted) return;
        setAccessToken(token.access_token);
        applyPlayerState(restored);
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
      setAccessToken(token.access_token);
      applyPlayerState(currentPlayer);
      setSelectedVariety(currentPlayer.starter_varieties[0]?.key ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed.");
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
      setSelectedVariety(null);
      setSubmitting(false);
    }
  }

  if (restoring) {
    return (
      <section className="panel" aria-live="polite">
        <p className="eyebrow">PHASE 2 - PRODUCTION</p>
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
              {player.display_name} - Level {player.level} - XP {player.xp} - Reputation{" "}
              {player.reputation}
            </p>
          </div>
          <button className="secondary compact" onClick={logout} disabled={submitting}>
            Sign out
          </button>
        </header>

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
                    className={selectedVariety === variety.key ? "variety active" : "variety"}
                    onClick={() => setSelectedVariety(variety.key)}
                  >
                    <strong>{variety.name}</strong>
                    <span>
                      {Math.ceil(variety.grow_seconds / 60)} min - Yield {variety.base_yield}
                    </span>
                  </button>
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
                          <span>{remaining}</span>
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
      <p className="eyebrow">PHASE 2 - PRODUCTION</p>
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
    </section>
  );
}
