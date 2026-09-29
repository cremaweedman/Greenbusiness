"use client";

import { FormEvent, useEffect, useState } from "react";

type Mode = "login" | "register";

type TokenResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
};

type Player = {
  user_id: string;
  email: string;
  display_name: string;
  business_id: string;
  business_name: string;
  room_id: string;
  room_slug: string;
  room_level: number;
  slots: Array<{ id: string; slot_index: number; status: string }>;
  level: number;
  xp: number;
  reputation: number;
  inventory_container_id: string;
};

type ApiError = {
  error?: {
    code?: string;
    message?: string;
  };
};

async function parseError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as ApiError;
    return body.error?.message ?? `Request failed (${response.status})`;
  } catch {
    return `Request failed (${response.status})`;
  }
}

async function getPlayer(accessToken: string): Promise<Player> {
  const response = await fetch("/api/v1/player", {
    headers: { Authorization: `Bearer ${accessToken}` },
    credentials: "include",
    cache: "no-store",
  });
  if (!response.ok) throw new Error(await parseError(response));
  return (await response.json()) as Player;
}

export default function AuthApp() {
  const [mode, setMode] = useState<Mode>("register");
  const [player, setPlayer] = useState<Player | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [restoring, setRestoring] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
        setPlayer(restored);
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

  async function authenticate(endpoint: "login" | "register", payload: object) {
    setSubmitting(true);
    setError(null);
    try {
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
      setPlayer(currentPlayer);
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
      setSubmitting(false);
    }
  }

  if (restoring) {
    return (
      <section className="panel" aria-live="polite">
        <p className="eyebrow">PHASE 1 · IDENTITY</p>
        <h1>GreenBusiness</h1>
        <p className="muted">Restoring secure session…</p>
      </section>
    );
  }

  if (player && accessToken) {
    return (
      <section className="panel dashboard">
        <div>
          <p className="eyebrow">BUSINESS ONLINE</p>
          <h1>{player.business_name}</h1>
          <p className="muted">
            {player.display_name} · Level {player.level} · Reputation {player.reputation}
          </p>
        </div>

        <div className="stats" aria-label="Starter business state">
          <article>
            <span>Room</span>
            <strong>{player.room_slug}</strong>
          </article>
          <article>
            <span>Room level</span>
            <strong>{player.room_level}</strong>
          </article>
          <article>
            <span>Production slots</span>
            <strong>{player.slots.length}</strong>
          </article>
          <article>
            <span>XP</span>
            <strong>{player.xp}</strong>
          </article>
        </div>

        <p className="account">{player.email}</p>
        <button className="secondary" onClick={logout} disabled={submitting}>
          Sign out
        </button>
      </section>
    );
  }

  return (
    <section className="panel auth">
      <p className="eyebrow">PHASE 1 · IDENTITY</p>
      <h1>GreenBusiness</h1>
      <p className="muted">
        {mode === "register"
          ? "Create the owner profile for your first business."
          : "Continue your existing business."}
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

        {error && <p className="error" role="alert">{error}</p>}

        <button className="primary" type="submit" disabled={submitting}>
          {submitting
            ? "Working…"
            : mode === "register"
              ? "Start business"
              : "Sign in"}
        </button>
      </form>
    </section>
  );
}
