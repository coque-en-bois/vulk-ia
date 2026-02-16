import styles from "./StepIndicator.module.css";

interface Step {
  label: string;
  icon: string;
}

interface Props {
  steps: Step[];
  currentStep: number;
}

function StepIndicator({ steps, currentStep }: Props) {
  return (
    <div className={styles.indicator}>
      {steps.map((step, index) => (
        <div key={index} className={styles.stepItem}>
          <div
            className={`${styles.stepCircle} ${
              index < currentStep
                ? styles.completed
                : index === currentStep
                  ? styles.active
                  : styles.upcoming
            }`}
          >
            {index < currentStep ? "✓" : step.icon}
          </div>
          <span
            className={`${styles.stepLabel} ${
              index === currentStep ? styles.labelActive : ""
            }`}
          >
            {step.label}
          </span>
          {index < steps.length - 1 && (
            <div
              className={`${styles.connector} ${
                index < currentStep ? styles.connectorDone : ""
              }`}
            />
          )}
        </div>
      ))}
    </div>
  );
}

export default StepIndicator;
