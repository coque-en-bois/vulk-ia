import { useState, type FormEvent, type ReactNode } from "react";
import styles from "./AuthGate.module.css";

const STORAGE_KEY = "ceb_auth_token";

export function getAuthToken(): string | null {
  return localStorage.getItem(STORAGE_KEY);
}

function setAuthToken(token: string) {
  localStorage.setItem(STORAGE_KEY, token);
}

interface AuthGateProps {
  children: ReactNode;
}

export default function AuthGate({ children }: AuthGateProps) {
  const [token, setToken] = useState<string | null>(getAuthToken());
  const [input, setInput] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) {
      setError("Veuillez renseigner votre token.");
      return;
    }
    setAuthToken(trimmed);
    setToken(trimmed);
  }

  if (token) {
    return <>{children}</>;
  }

  return (
    <div className={styles.overlay}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>🪵</span>
          <h1>VULK-IA</h1>
        </div>
        <p className={styles.subtitle}>Authentification requise</p>

        <label className={styles.label} htmlFor="auth-token">
          Token d'accès
        </label>
        <input
          id="auth-token"
          className={styles.input}
          type="password"
          placeholder="Collez votre token ici…"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setError("");
          }}
          autoFocus
        />
        {error && <p className={styles.error}>{error}</p>}

        <button
          className={styles.button}
          type="submit"
          disabled={!input.trim()}
        >
          Se connecter
        </button>
      </form>
    </div>
  );
}
