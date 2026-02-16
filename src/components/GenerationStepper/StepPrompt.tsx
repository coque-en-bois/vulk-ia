import styles from "./steps.module.css";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function StepPrompt({ value, onChange }: Props) {
  return (
    <div className={styles.step}>
      <h2 className={styles.stepTitle}>✍️ Décrivez votre demande</h2>
      <p className={styles.stepDescription}>
        Précisez le design souhaité : style, motifs, type de bois, textes à
        graver, type de produit (médaille ou trophée)…
      </p>

      <div className={styles.fieldGroup}>
        <label className={styles.label} htmlFor="prompt">
          Description du design
        </label>
        <textarea
          id="prompt"
          className={styles.textarea}
          placeholder={`Ex: "Style moderne et épuré en bois de chêne. Forme hexagonale avec gravure d'un volcan stylisé et des silhouettes de coureurs. Intégrer le nom de l'événement et la distance."`}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={6}
          autoFocus
        />
      </div>

      <div className={styles.tipBox}>
        <strong>💡 Conseil :</strong> Plus votre description est détaillée,
        meilleur sera le résultat. N'hésitez pas à préciser la forme, les
        matériaux, les couleurs et les éléments graphiques souhaités.
      </div>
    </div>
  );
}

export default StepPrompt;
