import { useState } from "react";
import StepIndicator from "./StepIndicator";
import StepEventName from "./StepEventName";
import StepInspirationImages from "./StepInspirationImages";
import StepClientFiles from "./StepClientFiles";
import StepPrompt from "./StepPrompt";
import StepResult from "./StepResult";
import ProgressBar from "./ProgressBar";
import { submitGeneration } from "../../api";
import type { GenerationResult, ProgressEvent } from "../../types";
import styles from "./GenerationStepper.module.css";

const STEPS = [
  { label: "Événement", icon: "🏆" },
  { label: "Inspiration", icon: "🎨" },
  { label: "Fichiers client", icon: "📁" },
  { label: "Description", icon: "✍️" },
];

function GenerationStepper() {
  const [currentStep, setCurrentStep] = useState(0);
  const [eventName, setEventName] = useState("");
  const [selectedImages, setSelectedImages] = useState<string[]>([]);
  const [clientFiles, setClientFiles] = useState<File[]>([]);
  const [prompt, setPrompt] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<ProgressEvent | null>(null);

  const canGoNext = (): boolean => {
    switch (currentStep) {
      case 0:
        return eventName.trim().length > 0;
      case 1:
        return selectedImages.length > 0 && selectedImages.length <= 3;
      case 2:
        return true; // Les fichiers client sont optionnels
      case 3:
        return prompt.trim().length > 0;
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep((s) => s + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep((s) => s - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    setProgress(null);
    try {
      const res = await submitGeneration(
        {
          eventName,
          inspirationImages: selectedImages,
          clientFiles,
          prompt,
        },
        (event) => setProgress(event),
      );
      setResult(res);
      setCurrentStep(STEPS.length); // Aller à l'écran résultat
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setIsSubmitting(false);
      setProgress(null);
    }
  };

  const handleReset = () => {
    setCurrentStep(0);
    setEventName("");
    setSelectedImages([]);
    setClientFiles([]);
    setPrompt("");
    setResult(null);
    setError(null);
    setProgress(null);
  };

  // Écran de résultat
  if (currentStep === STEPS.length) {
    return (
      <div className={styles.container}>
        <StepResult result={result} onReset={handleReset} />
      </div>
    );
  }

  // Écran de progression pendant la génération
  if (isSubmitting) {
    return (
      <div className={styles.container}>
        <StepIndicator steps={STEPS} currentStep={STEPS.length - 1} />
        <div className={styles.stepContent}>
          <div className={styles.generatingHeader}>
            <h2>🚀 Génération en cours…</h2>
            <p>Veuillez patienter, Gemini travaille sur vos maquettes.</p>
          </div>
          <ProgressBar progress={progress} />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <StepIndicator steps={STEPS} currentStep={currentStep} />

      <div className={styles.stepContent}>
        {currentStep === 0 && (
          <StepEventName value={eventName} onChange={setEventName} />
        )}
        {currentStep === 1 && (
          <StepInspirationImages
            selected={selectedImages}
            onChange={setSelectedImages}
          />
        )}
        {currentStep === 2 && (
          <StepClientFiles files={clientFiles} onChange={setClientFiles} />
        )}
        {currentStep === 3 && (
          <StepPrompt value={prompt} onChange={setPrompt} />
        )}
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <div className={styles.navigation}>
        <button
          className={styles.btnSecondary}
          onClick={handlePrev}
          disabled={currentStep === 0}
        >
          ← Retour
        </button>

        <div className={styles.stepCount}>
          {currentStep + 1} / {STEPS.length}
        </div>

        {currentStep < STEPS.length - 1 ? (
          <button
            className={styles.btnPrimary}
            onClick={handleNext}
            disabled={!canGoNext()}
          >
            Suivant →
          </button>
        ) : (
          <button
            className={styles.btnPrimary}
            onClick={handleSubmit}
            disabled={!canGoNext() || isSubmitting}
          >
            {isSubmitting ? (
              <span className={styles.spinner}>⏳ Génération...</span>
            ) : (
              "🚀 Générer"
            )}
          </button>
        )}
      </div>
    </div>
  );
}

export default GenerationStepper;
