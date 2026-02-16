import GenerationStepper from "./components/GenerationStepper/GenerationStepper";
import styles from "./App.module.css";

function App() {
  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>🪵</span>
          <h1>VULK-IA</h1>
        </div>
        <p className={styles.subtitle}>Générateur de maquettes en bois</p>
      </header>

      <main className={styles.main}>
        <GenerationStepper />
      </main>
    </div>
  );
}

export default App;
