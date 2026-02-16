import type { ProgressEvent } from "../../types";
import styles from "./ProgressBar.module.css";

interface Props {
  progress: ProgressEvent | null;
}

function ProgressBar({ progress }: Props) {
  if (!progress) return null;

  const percentage =
    progress.total > 0
      ? Math.round((progress.current / progress.total) * 100)
      : 0;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.label}>
          {progress.type === "start" && "⏳ Préparation…"}
          {progress.type === "progress" && (
            <>
              🎨 Vue <strong>{progress.view}</strong> — Proposition{" "}
              {progress.proposition}
            </>
          )}
          {progress.type === "complete" && "✅ Terminé !"}
        </span>
        <span className={styles.count}>
          {progress.current}/{progress.total} — {percentage}%
        </span>
      </div>

      <div className={styles.trackOuter}>
        <div
          className={`${styles.trackInner} ${progress.type === "complete" ? styles.complete : ""}`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <p className={styles.message}>{progress.message}</p>
    </div>
  );
}

export default ProgressBar;
