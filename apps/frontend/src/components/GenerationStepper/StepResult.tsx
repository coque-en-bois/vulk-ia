import type { GenerationResult } from "../../types";
import { getZipDownloadUrl } from "../../api";
import styles from "./steps.module.css";

interface Props {
  result: GenerationResult | null;
  onReset: () => void;
}

function StepResult({ result, onReset }: Props) {
  if (!result) {
    return (
      <div className={styles.step}>
        <p className={styles.errorText}>Aucun résultat reçu.</p>
        <button className={styles.resetButton} onClick={onReset}>
          🔄 Recommencer
        </button>
      </div>
    );
  }

  return (
    <div className={styles.step}>
      <h2 className={styles.stepTitle}>
        {result.success ? "🎉 Génération terminée !" : "❌ Erreur"}
      </h2>

      <p className={styles.stepDescription}>{result.message}</p>

      {result.success && result.images.length > 0 && (
        <>
          <div className={styles.resultGrid}>
            {result.images.map((img) => (
              <div key={img.filename} className={styles.resultCard}>
                <img
                  src={img.url}
                  alt={img.filename}
                  className={styles.resultImage}
                />
                <span className={styles.resultFilename}>{img.filename}</span>
              </div>
            ))}
          </div>

          <a
            href={getZipDownloadUrl(result.outputDir)}
            download
            className={styles.downloadButton}
          >
            📦 Télécharger toutes les images (ZIP)
          </a>
        </>
      )}

      <button className={styles.resetButton} onClick={onReset}>
        🔄 Nouvelle génération
      </button>
    </div>
  );
}

export default StepResult;
