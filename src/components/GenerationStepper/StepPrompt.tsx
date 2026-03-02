import { useState, useEffect, useCallback } from "react";
import styles from "./steps.module.css";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

interface PromptSelections {
  style: string;
  woodType: string;
  shape: string;
  cutouts: string;
  technique: string;
}

const STYLE_OPTIONS = [
  { value: "moderne", label: "Moderne & épuré", icon: "✨" },
  { value: "rustique", label: "Rustique & naturel", icon: "🌿" },
  { value: "classique", label: "Classique & élégant", icon: "👑" },
  { value: "sportif", label: "Sportif & dynamique", icon: "⚡" },
  { value: "minimaliste", label: "Minimaliste", icon: "◻️" },
  { value: "artistique", label: "Artistique & créatif", icon: "🎨" },
];

const WOOD_OPTIONS = [
  { value: "contre-plaqué", label: "Contre-plaqué", icon: "📐" },
  { value: "chêne", label: "Chêne", icon: "🟫" },
  { value: "hêtre", label: "Hêtre", icon: "🟨" },
  { value: "noyer", label: "Noyer", icon: "🟤" },
];

const SHAPE_OPTIONS = [
  { value: "ronde", label: "Ronde", icon: "⭕" },
  { value: "hexagonale", label: "Hexagonale", icon: "⬡" },
  { value: "octogonale", label: "Octogonale", icon: "🛑" },
  { value: "en étoile", label: "En étoile", icon: "⭐" },
];

const CUTOUT_OPTIONS = [
  { value: "sans évidé", label: "Sans évidé (plein)", icon: "◼️" },
  { value: "avec évidés", label: "Avec évidés", icon: "◻️" },
];

const TECHNIQUE_OPTIONS = [
  { value: "gravure", label: "Gravure", icon: "🔥" },
  { value: "impression UV", label: "Impression UV", icon: "☀️" },
];

function buildPrompt(selections: PromptSelections): string {
  const parts: string[] = [];

  parts.push("Médaille");

  if (selections.style) {
    parts.push(`au style ${selections.style}`);
  }
  if (selections.woodType) {
    parts.push(
      `en bois ${selections.woodType === "contre-plaqué" ? selections.woodType : `de ${selections.woodType}`}`,
    );
  }
  if (selections.shape) {
    parts.push(`de forme ${selections.shape}`);
  }
  if (selections.cutouts) {
    parts.push(selections.cutouts);
  }
  if (selections.technique) {
    parts.push(`technique ${selections.technique}`);
  }

  return parts.join(", ") + ".";
}

function parsePrompt(prompt: string): PromptSelections {
  const selections: PromptSelections = {
    style: "",
    woodType: "",
    shape: "",
    cutouts: "",
    technique: "",
  };

  if (!prompt) return selections;

  for (const opt of STYLE_OPTIONS) {
    if (prompt.includes(opt.value)) {
      selections.style = opt.value;
      break;
    }
  }
  for (const opt of WOOD_OPTIONS) {
    if (prompt.includes(opt.value)) {
      selections.woodType = opt.value;
      break;
    }
  }
  for (const opt of SHAPE_OPTIONS) {
    if (prompt.includes(opt.value)) {
      selections.shape = opt.value;
      break;
    }
  }
  for (const opt of CUTOUT_OPTIONS) {
    if (prompt.includes(opt.value)) {
      selections.cutouts = opt.value;
      break;
    }
  }
  for (const opt of TECHNIQUE_OPTIONS) {
    if (prompt.includes(opt.value)) {
      selections.technique = opt.value;
      break;
    }
  }

  return selections;
}

function OptionChip({
  option,
  selected,
  onSelect,
}: {
  option: { value: string; label: string; icon: string };
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      className={`${styles.chip} ${selected ? styles.chipSelected : ""}`}
      onClick={onSelect}
    >
      <span className={styles.chipIcon}>{option.icon}</span>
      <span className={styles.chipLabel}>{option.label}</span>
    </button>
  );
}

function StepPrompt({ value, onChange }: Props) {
  const [selections, setSelections] = useState<PromptSelections>(() =>
    parsePrompt(value),
  );
  const [freeText, setFreeText] = useState("");

  const updatePrompt = useCallback(
    (newSelections: PromptSelections, extraText: string) => {
      const allFilled =
        newSelections.style &&
        newSelections.woodType &&
        newSelections.shape &&
        newSelections.cutouts &&
        newSelections.technique;
      if (!allFilled) {
        onChange("");
        return;
      }
      const base = buildPrompt(newSelections);
      const trimmed = extraText.trim();
      onChange(trimmed ? `${base} ${trimmed}` : base);
    },
    [onChange],
  );

  useEffect(() => {
    // Sync on mount if there's already a value
    if (
      value &&
      !selections.style &&
      !selections.woodType &&
      !selections.shape &&
      !selections.cutouts &&
      !selections.technique
    ) {
      const parsed = parsePrompt(value);
      setSelections(parsed);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSelect = (field: keyof PromptSelections, optionValue: string) => {
    const newSelections = {
      ...selections,
      [field]: selections[field] === optionValue ? "" : optionValue,
    };
    setSelections(newSelections);
    updatePrompt(newSelections, freeText);
  };

  const handleFreeTextChange = (text: string) => {
    setFreeText(text);
    updatePrompt(selections, text);
  };

  const allSelected =
    selections.style &&
    selections.woodType &&
    selections.shape &&
    selections.cutouts &&
    selections.technique;

  return (
    <div className={styles.step}>
      <h2 className={styles.stepTitle}>✍️ Décrivez votre médaille</h2>
      <p className={styles.stepDescription}>
        Configurez les caractéristiques de votre médaille en sélectionnant une
        option dans chaque catégorie.
      </p>

      {/* Style */}
      <div className={styles.promptSection}>
        <label className={styles.label}>Style</label>
        <div className={styles.chipGrid}>
          {STYLE_OPTIONS.map((opt) => (
            <OptionChip
              key={opt.value}
              option={opt}
              selected={selections.style === opt.value}
              onSelect={() => handleSelect("style", opt.value)}
            />
          ))}
        </div>
      </div>

      {/* Technique */}
      <div className={styles.promptSection}>
        <label className={styles.label}>Technique</label>
        <div className={styles.chipGrid}>
          {TECHNIQUE_OPTIONS.map((opt) => (
            <OptionChip
              key={opt.value}
              option={opt}
              selected={selections.technique === opt.value}
              onSelect={() => handleSelect("technique", opt.value)}
            />
          ))}
        </div>
      </div>

      {/* Type de bois */}
      <div className={styles.promptSection}>
        <label className={styles.label}>Type de bois</label>
        <div className={styles.chipGrid}>
          {WOOD_OPTIONS.map((opt) => (
            <OptionChip
              key={opt.value}
              option={opt}
              selected={selections.woodType === opt.value}
              onSelect={() => handleSelect("woodType", opt.value)}
            />
          ))}
        </div>
      </div>

      {/* Forme */}
      <div className={styles.promptSection}>
        <label className={styles.label}>Forme</label>
        <div className={styles.chipGrid}>
          {SHAPE_OPTIONS.map((opt) => (
            <OptionChip
              key={opt.value}
              option={opt}
              selected={selections.shape === opt.value}
              onSelect={() => handleSelect("shape", opt.value)}
            />
          ))}
        </div>
      </div>

      {/* Évidés */}
      <div className={styles.promptSection}>
        <label className={styles.label}>Évidés</label>
        <div className={styles.chipGrid}>
          {CUTOUT_OPTIONS.map((opt) => (
            <OptionChip
              key={opt.value}
              option={opt}
              selected={selections.cutouts === opt.value}
              onSelect={() => handleSelect("cutouts", opt.value)}
            />
          ))}
        </div>
      </div>

      {/* Texte libre facultatif */}
      <div className={styles.promptSection}>
        <label className={styles.label}>
          Précisions supplémentaires (facultatif)
        </label>
        <textarea
          className={styles.textarea}
          placeholder={
            "Ex: \"Gravure d'un volcan stylisé avec des silhouettes de coureurs. Intégrer le nom de l'événement et la distance.\""
          }
          value={freeText}
          onChange={(e) => handleFreeTextChange(e.target.value)}
          rows={3}
        />
      </div>

      {/* Aperçu du prompt */}
      {allSelected && (
        <div className={styles.promptPreview}>
          <label className={styles.label}>Aperçu du prompt généré</label>
          <div className={styles.promptPreviewText}>{value}</div>
        </div>
      )}

      <div className={styles.tipBox}>
        <strong>💡 Conseil :</strong> Sélectionnez une option dans chaque
        catégorie pour que le prompt soit complet. Vous pouvez ajouter des
        précisions libres pour affiner le résultat.
      </div>
    </div>
  );
}

export default StepPrompt;
