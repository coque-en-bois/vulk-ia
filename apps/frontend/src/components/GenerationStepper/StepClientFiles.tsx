import { useRef } from "react";
import styles from "./steps.module.css";

interface Props {
  files: File[];
  onChange: (files: File[]) => void;
}

function StepClientFiles({ files, onChange }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      onChange([...files, ...newFiles]);
    }
    // Reset input pour permettre re-sélection du même fichier
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const removeFile = (index: number) => {
    onChange(files.filter((_, i) => i !== index));
  };

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} o`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
  };

  return (
    <div className={styles.step}>
      <h2 className={styles.stepTitle}>📁 Fichiers du client</h2>
      <p className={styles.stepDescription}>
        Uploadez les fichiers fournis par le client qui devront être intégrés
        tels quels dans les visuels (logo, éléments graphiques…).
        <br />
        <em>Cette étape est optionnelle.</em>
      </p>

      <div
        className={styles.dropZone}
        onClick={() => fileInputRef.current?.click()}
      >
        <span className={styles.dropIcon}>📤</span>
        <p>Cliquez ou glissez vos fichiers ici</p>
        <span className={styles.dropHint}>PNG, SVG, PDF — Max 10 Mo</span>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,.pdf,.svg"
          onChange={handleFileChange}
          className={styles.hiddenInput}
        />
      </div>

      {files.length > 0 && (
        <div className={styles.fileList}>
          {files.map((file, index) => (
            <div key={`${file.name}-${index}`} className={styles.fileItem}>
              <div className={styles.fileInfo}>
                <span className={styles.fileName}>{file.name}</span>
                <span className={styles.fileSize}>{formatSize(file.size)}</span>
              </div>
              <button
                className={styles.fileRemove}
                onClick={() => removeFile(index)}
                type="button"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default StepClientFiles;
