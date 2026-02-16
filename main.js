import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import * as readline from "node:readline";
import dotenv from "dotenv";

dotenv.config();

// Obtenir le répertoire courant en ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const CONFIG = {
  // Nombre de propositions à générer par vue
  propositionsCount: 3,
  // Types de vues à générer
  views: ["flat", "3_4"],
  // Résolution et format
  aspectRatio: "1:1",
  resolution: "2K",
  // Dossier de sortie
  outputDir: path.join(__dirname, "outputs"),
};

// Charger toutes les images d'exemple depuis le dossier inputs
function loadExampleImages() {
  const inputsDir = path.join(__dirname, "inputs");
  const files = fs.readdirSync(inputsDir).filter((f) => f.endsWith(".png"));

  return files
    .splice(0, 3) // Limiter à 3 images pour la génération
    .map((file) => {
      const base64 = fs.readFileSync(path.join(inputsDir, file), {
        encoding: "base64",
      });
      return {
        inlineData: {
          mimeType: "image/png",
          data: base64,
        },
      };
    });
}

// Générer le prompt selon la vue demandée
function buildPrompt(baseDescription, view, propositionIndex) {
  const viewInstructions = {
    flat: `
      IMPORTANT: Génère une vue PARFAITEMENT À PLAT (vue de dessus/top-down).
      - La médaille doit être vue directement de face, comme posée sur une table et photographiée du dessus
      - Aucune perspective, aucun angle, parfaitement orthogonale
      - Montre tous les détails de la gravure clairement visibles
    `,
    "3_4": `
      IMPORTANT: Génère une vue en PERSPECTIVE 3/4 (vue isométrique élégante).
      - La médaille doit être inclinée avec un angle de 30-45 degrés
      - Montre l'épaisseur et le volume de la médaille en bois
      - Crée une ombre douce pour accentuer l'effet 3D
      - La texture du bois doit être visible sur la tranche
    `,
  };

  const variationSeed = `[Variation créative n°${propositionIndex + 1} - explore une approche différente du design tout en respectant le thème]`;

  return `${baseDescription}

${viewInstructions[view]}

${variationSeed}

Style: Rendu photoréaliste haute qualité, éclairage studio professionnel, fond neutre légèrement texturé.`;
}

// Générer une image avec Gemini
async function generateImage(ai, prompt, exampleImages) {
  const contents = [{ text: prompt }, ...exampleImages];

  console.log("  🔄 Envoi de la requête à Gemini...");
  const startTime = Date.now();

  // Timeout de 2 minutes pour la génération d'image
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(
      () =>
        reject(new Error("Timeout: la génération a pris plus de 2 minutes")),
      120000,
    );
  });

  const generatePromise = ai.models.generateContent({
    model: "gemini-3-pro-image-preview",
    contents: contents,
    config: {
      responseModalities: ["TEXT", "IMAGE"],
    },
  });

  const response = await Promise.race([generatePromise, timeoutPromise]);

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`  ⏱️  Réponse reçue en ${elapsed}s`);

  return response;
}

// Sauvegarder les résultats
function saveResults(response, view, propositionIndex, outputDir, productType) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const savedFiles = [];

  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(`  💬 Gemini: ${part.text}`);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      const filename = `${productType}_${view}_prop${propositionIndex + 1}_${timestamp}.png`;
      const filepath = path.join(outputDir, filename);
      fs.writeFileSync(filepath, buffer);
      savedFiles.push(filename);
      console.log(`  ✅ Image sauvegardée: ${filename}`);
    }
  }

  return savedFiles;
}

// Demander une entrée utilisateur
function askQuestion(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer);
    });
  });
}

async function main() {
  const ai = new GoogleGenAI({
    apiKey: process.env.GEMINI_API_KEY,
  });

  // Demander les informations au client
  console.log(
    "\n🎨 ═══════════════════════════════════════════════════════════",
  );
  console.log("   VULK-IA - Générateur de maquettes en bois");
  console.log(
    "═══════════════════════════════════════════════════════════════\n",
  );

  // Question 1: Nom de l'événement
  const eventName = await askQuestion("🏆 Nom de l'événement sportif: ");

  if (!eventName.trim()) {
    console.log("\n❌ Aucun nom d'événement fourni. Abandon.");
    process.exit(1);
  }

  // Créer un slug pour le dossier (sans accents ni caractères spéciaux)
  const eventSlug = eventName
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

  // Question 2: Type de produit
  console.log("\n📦 Quel type de produit souhaitez-vous générer?");
  console.log("   1. Médaille");
  console.log("   2. Trophée");
  const productChoice = await askQuestion("\n🔢 Votre choix (1 ou 2): ");

  const productType = productChoice.trim() === "2" ? "trophee" : "medaille";
  const productLabel = productType === "trophee" ? "trophée" : "médaille";

  console.log(`\n✅ Génération de ${productLabel}s pour: ${eventName}\n`);

  // Question 3: Description du design
  console.log(`📝 Décrivez le design de la ${productLabel} souhaitée.`);
  console.log(
    "   Incluez: le style, les motifs, le type de bois, les textes à graver...",
  );

  console.log("\n💡 Exemple de description complète:");
  console.log("   ─────────────────────────────────────────────────────────");
  if (productType === "medaille") {
    console.log(
      '   "Style moderne et épuré en bois de chêne. Forme hexagonale',
    );
    console.log("   avec gravure d'un volcan stylisé et des silhouettes de");
    console.log(
      "   coureurs. Intégrer le nom de l'événement et la distance.\"",
    );
  } else {
    console.log(
      '   "Trophée élégant en bois de noyer avec socle rectangulaire.',
    );
    console.log(
      "   Forme verticale avec découpe laser représentant un coureur",
    );
    console.log(
      "   franchissant la ligne d'arrivée. Plaque gravée pour le nom.\"",
    );
  }
  console.log("   ─────────────────────────────────────────────────────────\n");

  const baseDescription = await askQuestion("🖊️  Votre description: ");

  if (!baseDescription.trim()) {
    console.log("\n❌ Aucune description fournie. Abandon.");
    process.exit(1);
  }

  // Enrichir automatiquement le prompt avec le contexte métier
  const enrichedDescription = `À partir de ces exemples de ${productLabel}s en bois, crée un design unique pour l'événement "${eventName}": ${baseDescription}. 
Mets en valeur la texture naturelle du bois. Le design doit rester fonctionnel et esthétique.`;

  // Définir le dossier de sortie pour cet événement
  const eventOutputDir = path.join(CONFIG.outputDir, eventSlug);

  console.log("\n✨ Description enrichie et prête pour la génération!\n");

  // Créer le dossier de sortie s'il n'existe pas
  if (!fs.existsSync(eventOutputDir)) {
    fs.mkdirSync(eventOutputDir, { recursive: true });
  }

  // Charger les images d'exemple
  console.log("📂 Chargement des images d'exemple...");
  const exampleImages = loadExampleImages();
  console.log(`  ${exampleImages.length} images chargées\n`);

  const allResults = [];

  // Générer pour chaque vue
  for (const view of CONFIG.views) {
    console.log(`\n🎨 === Génération vue ${view.toUpperCase()} ===`);

    // Générer plusieurs propositions
    for (let i = 0; i < CONFIG.propositionsCount; i++) {
      console.log(
        `\n📌 Proposition ${i + 1}/${CONFIG.propositionsCount} (${view})...`,
      );

      const prompt = buildPrompt(enrichedDescription, view, i);

      console.log("prompt généré:");
      console.log("─────────────────────────────────────────────────────────");
      console.log(prompt);
      console.log(
        "─────────────────────────────────────────────────────────\n",
      );

      try {
        const response = await generateImage(ai, prompt, exampleImages);
        const savedFiles = saveResults(
          response,
          view,
          i,
          eventOutputDir,
          productType,
        );
        allResults.push({ view, proposition: i + 1, files: savedFiles });
      } catch (error) {
        console.error(`  ❌ Erreur: ${error.message}`);
      }

      // Petite pause entre les requêtes pour éviter le rate limiting
      if (
        i < CONFIG.propositionsCount - 1 ||
        view !== CONFIG.views[CONFIG.views.length - 1]
      ) {
        console.log("  ⏳ Pause de 2 secondes...");
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
    }
  }

  // Résumé final
  console.log("\n\n🏆 === GÉNÉRATION TERMINÉE ===");
  console.log(`📁 Dossier de sortie: ${eventOutputDir}`);
  console.log(`📊 Résumé:`);
  for (const view of CONFIG.views) {
    const count = allResults.filter((r) => r.view === view).length;
    console.log(`   - Vue ${view}: ${count} propositions générées`);
  }
  console.log(`\n🎉 Total: ${allResults.length} images générées!`);

  process.exit(0);
}

main();
