import styles from "./steps.module.css";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

function StepEventName({ value, onChange }: Props) {
  return (
    <div className={styles.step}>
      <h2 className={styles.stepTitle}>🏆 Nom de l'événement</h2>
      <p className={styles.stepDescription}>
        Renseignez le nom de l'événement sportif pour lequel vous souhaitez
        générer des maquettes de médailles ou trophées en bois.
      </p>

      <div className={styles.fieldGroup}>
        <label className={styles.label} htmlFor="eventName">
          Nom de l'événement
        </label>
        <input
          id="eventName"
          className={styles.input}
          type="text"
          placeholder="Ex: Le Trail des Fous, Les Foulées d'Amboise…"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          autoFocus
        />
      </div>
    </div>
  );
}

export default StepEventName;
