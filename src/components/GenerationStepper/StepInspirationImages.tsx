import styles from "./steps.module.css";

const images = [
  { filename: "1.png", url: "./images/1.png" },
  { filename: "2.png", url: "./images/2.png" },
  { filename: "3.png", url: "./images/3.png" },
  { filename: "4.png", url: "./images/4.png" },
  { filename: "5.png", url: "./images/5.png" },
  { filename: "6.png", url: "./images/6.png" },
  { filename: "7.png", url: "./images/7.png" },
  { filename: "8.png", url: "./images/8.png" },
  { filename: "9.png", url: "./images/9.png" },
];

interface Props {
  selected: string[];
  onChange: (selected: string[]) => void;
}

function StepInspirationImages({ selected, onChange }: Props) {
  const toggleImage = (filename: string) => {
    if (selected.includes(filename)) {
      onChange(selected.filter((f) => f !== filename));
    } else if (selected.length < 3) {
      onChange([...selected, filename]);
    }
  };

  return (
    <div className={styles.step}>
      <h2 className={styles.stepTitle}>🎨 Images d'inspiration</h2>
      <p className={styles.stepDescription}>
        Sélectionnez jusqu'à <strong>3 images</strong> qui serviront
        d'inspiration pour la génération. ({selected.length}/3 sélectionnées)
      </p>

      <div className={styles.imageGrid}>
        {images.map((img) => {
          const isSelected = selected.includes(img.filename);
          const isDisabled = !isSelected && selected.length >= 3;

          return (
            <button
              key={img.filename}
              className={`${styles.imageCard} ${isSelected ? styles.imageSelected : ""} ${isDisabled ? styles.imageDisabled : ""}`}
              onClick={() => toggleImage(img.filename)}
              disabled={isDisabled}
              type="button"
            >
              <img src={img.url} alt={img.filename} className={styles.image} />
              {isSelected && (
                <div className={styles.selectedBadge}>
                  ✓ {selected.indexOf(img.filename) + 1}
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default StepInspirationImages;
