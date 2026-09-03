"use client";

import { useState, useSyncExternalStore } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";

const SESSION_KEY = "pm-authenticated";

const sessionListeners = new Set<() => void>();
const subscribeToSession = (listener: () => void) => {
  sessionListeners.add(listener);
  return () => sessionListeners.delete(listener);
};
const notifySessionChange = () => {
  sessionListeners.forEach((listener) => listener());
};
const getSessionAuth = () => sessionStorage.getItem(SESSION_KEY) === "true";
const getServerSessionAuth = () => false;

const LoginForm = ({ onLogin }: { onLogin: () => void }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [hasError, setHasError] = useState(false);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (username === "user" && password === "password") {
      sessionStorage.setItem(SESSION_KEY, "true");
      notifySessionChange();
      onLogin();
      return;
    }
    setHasError(true);
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <form
        onSubmit={handleSubmit}
        className="flex w-full max-w-md flex-col gap-5 rounded-[32px] border border-[var(--stroke)] bg-white/85 p-8 shadow-[var(--shadow)] backdrop-blur"
      >
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
            Project workspace
          </p>
          <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
            Sign in to Kanban Studio
          </h1>
        </div>
        <label className="flex flex-col gap-2 text-sm font-semibold text-[var(--navy-dark)]">
          Username
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="rounded-xl border border-[var(--stroke)] px-4 py-3 font-normal outline-none focus:border-[var(--primary-blue)]"
            autoComplete="username"
          />
        </label>
        <label className="flex flex-col gap-2 text-sm font-semibold text-[var(--navy-dark)]">
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="rounded-xl border border-[var(--stroke)] px-4 py-3 font-normal outline-none focus:border-[var(--primary-blue)]"
            autoComplete="current-password"
          />
        </label>
        {hasError && (
          <p role="alert" className="text-sm text-[var(--secondary-purple)]">
            Username or password is incorrect.
          </p>
        )}
        <button
          type="submit"
          className="rounded-xl bg-[var(--secondary-purple)] px-4 py-3 font-semibold text-white transition hover:opacity-90"
        >
          Sign in
        </button>
      </form>
    </main>
  );
};

export default function Home() {
  const isAuthenticated = useSyncExternalStore(
    subscribeToSession,
    getSessionAuth,
    getServerSessionAuth
  );
  const [, setAuthRefresh] = useState(false);

  const handleLogout = () => {
    sessionStorage.removeItem(SESSION_KEY);
    notifySessionChange();
    setAuthRefresh((value) => !value);
  };

  return isAuthenticated ? (
    <KanbanBoard onLogout={handleLogout} />
  ) : (
    <LoginForm onLogin={() => setAuthRefresh((value) => !value)} />
  );
}
