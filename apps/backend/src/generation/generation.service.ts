import { Injectable, Logger } from "@nestjs/common";
import { GenerateContentResponse, GoogleGenAI } from "@google/genai";
import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

// Charger .env depuis la racine du projet
dotenv.config({ path: path.join(__dirname, "..", "..", "..", "..", ".env") });

export interface ProgressEvent {
  type: "start" | "progress" | "complete" | "error";
  current: number;
  total: number;
  view?: string;
  proposition?: number;
  message: string;
}

interface GenerateParams {
  eventName: string;
  inspirationImages: string[];
  clientFiles: Express.Multer.File[];
  prompt: string;
  onProgress?: (event: ProgressEvent) => void;
}

// Configuration
const CONFIG = {
  propositionsCount: 3,
  outputDir: path.join(__dirname, "..", "..", "..", "..", "outputs"),
};

@Injectable()
export class GenerationService {
  private readonly logger = new Logger(GenerationService.name);
  private readonly ai: GoogleGenAI;
  private readonly inputsDir = path.join(
    __dirname,
    "..",
    "..",
    "..",
    "..",
    "inputs",
  );

  constructor() {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      this.logger.warn(
        "⚠️ GEMINI_API_KEY non définie — les générations échoueront",
      );
    }
    this.ai = new GoogleGenAI({ apiKey: apiKey || "" });
  }

  async generate(params: GenerateParams) {
    const { eventName, inspirationImages, clientFiles, prompt, onProgress } =
      params;
    const emitProgress = onProgress || (() => {});

    // Créer le slug pour le dossier de sortie
    const eventSlug = eventName
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");

    const eventOutputDir = path.join(CONFIG.outputDir, eventSlug);
    if (!fs.existsSync(eventOutputDir)) {
      fs.mkdirSync(eventOutputDir, { recursive: true });
    }

    // Sauvegarder les fichiers client dans le dossier de sortie
    const clientDir = path.join(eventOutputDir, "client-files");
    if (clientFiles.length > 0) {
      if (!fs.existsSync(clientDir)) {
        fs.mkdirSync(clientDir, { recursive: true });
      }
      for (const file of clientFiles) {
        fs.writeFileSync(path.join(clientDir, file.originalname), file.buffer);
      }
      this.logger.log(
        `📁 ${clientFiles.length} fichier(s) client sauvegardé(s)`,
      );
    }

    // Charger les images d'inspiration sélectionnées
    const exampleImages = this.loadSelectedImages(inspirationImages);

    // Charger les fichiers client comme contexte additionnel
    const clientImageParts = this.loadClientImages(clientFiles);

    // Enrichir le prompt
    const enrichedDescription = `À partir de ces exemples de médailles en bois, crée un design unique pour l'événement "${eventName}": ${prompt}. 
Mets en valeur la texture naturelle du bois. Le design doit rester fonctionnel et esthétique.
${clientFiles.length > 0 ? "IMPORTANT: Intègre les éléments visuels fournis par le client (logos, éléments graphiques) tels quels, sans les modifier." : ""}`;

    const allResults: {
      view: string;
      proposition: number;
      files: string[];
    }[] = [];

    const totalImages = CONFIG.propositionsCount * 2; // flat + 3/4 pour chaque proposition
    let currentImage = 0;

    emitProgress({
      type: "start",
      current: 0,
      total: totalImages,
      message: `Début de la génération de ${totalImages} images…`,
    });

    // Générer les vues flats
    for (let i = 0; i < CONFIG.propositionsCount; i++) {
      currentImage++;
      this.logger.log(
        `🔄 Génération flat — proposition ${i + 1}/${CONFIG.propositionsCount}`,
      );

      emitProgress({
        type: "progress",
        current: currentImage,
        total: totalImages,
        view: "flat",
        proposition: i + 1,
        message: `Génération vue flat — proposition ${i + 1}/${CONFIG.propositionsCount}`,
      });

      const fullPrompt = this.buildPrompt(enrichedDescription, i);

      let responseFlat: GenerateContentResponse | null = null;

      try {
        responseFlat = await this.generateImage(fullPrompt, [
          ...exampleImages,
          ...clientImageParts,
        ]);
        const savedFiles = this.saveResults(
          responseFlat,
          "flat",
          i,
          eventOutputDir,
        );
        allResults.push({
          view: "flat",
          proposition: i + 1,
          files: savedFiles,
        });
      } catch (error) {
        this.logger.error(`❌ Erreur génération: ${error.message}`);
      }

      await new Promise((r) => setTimeout(r, 2000));

      if (!responseFlat) {
        this.logger.warn(
          "⚠️ Pas de résultat pour la vue flat, saut de la génération 3/4 correspondante",
        );
        continue;
      }

      currentImage++;

      emitProgress({
        type: "progress",
        current: currentImage,
        total: totalImages,
        view: "3/4",
        proposition: i + 1,
        message: `Génération vue 3/4 — proposition ${i + 1}/${CONFIG.propositionsCount}`,
      });

      try {
        const response = await this.generateImage(
          `
        Génère une vue en PERSPECTIVE 3/4 (vue isométrique élégante) de l'image passée en paramètre.
        - La médaille doit être inclinée avec un angle de 30-45 degrés
        - Montre l'épaisseur et le volume de la médaille en bois
        - Crée une ombre douce pour accentuer l'effet 3D
        - La texture du bois doit être visible sur la tranche
      `,
          [
            {
              inlineData: {
                mimeType: "image/png",
                data: this.getResponseInlineImageData(responseFlat),
              },
            },
          ],
        );
        const savedFiles = this.saveResults(response, "3_4", i, eventOutputDir);
        allResults.push({
          view: "3/4",
          proposition: i + 1,
          files: savedFiles,
        });
      } catch (error) {
        this.logger.error(`❌ Erreur génération: ${error.message}`);
      }

      // Pause entre les requêtes
      if (i < CONFIG.propositionsCount - 1) {
        await new Promise((r) => setTimeout(r, 2000));
      }
    }

    const generatedImages = allResults.flatMap((r) =>
      r.files.map((f) => ({
        filename: f,
        url: `/api/outputs/${eventSlug}/${f}`,
      })),
    );

    const result = {
      success: allResults.length > 0,
      outputDir: eventSlug,
      images: generatedImages,
      message:
        allResults.length > 0
          ? `✅ ${generatedImages.length} image(s) générée(s) pour "${eventName}"`
          : "Aucune image n'a pu être générée",
    };

    emitProgress({
      type: "complete",
      current: totalImages,
      total: totalImages,
      message: result.message,
    });

    return result;
  }

  private loadSelectedImages(filenames: string[]) {
    return filenames
      .filter((f) => {
        const filePath = path.join(this.inputsDir, path.basename(f));
        return fs.existsSync(filePath);
      })
      .map((f) => {
        const filePath = path.join(this.inputsDir, path.basename(f));
        const base64 = fs.readFileSync(filePath, { encoding: "base64" });
        const ext = path.extname(f).toLowerCase();
        const mimeType =
          ext === ".png"
            ? "image/png"
            : ext === ".svg"
              ? "image/svg+xml"
              : "image/jpeg";
        return {
          inlineData: {
            mimeType,
            data: base64,
          },
        };
      });
  }

  private loadClientImages(files: Express.Multer.File[]) {
    return files
      .filter((f) => f.mimetype.startsWith("image/"))
      .map((f) => ({
        inlineData: {
          mimeType: f.mimetype,
          data: f.buffer.toString("base64"),
        },
      }));
  }

  private buildPrompt(baseDescription: string, propositionIndex: number) {
    const variationSeed = `[Variation créative n°${propositionIndex + 1} - explore une approche différente du design tout en respectant le thème]`;

    return `${baseDescription}

IMPORTANT: Génère une vue PARFAITEMENT À PLAT (vue de dessus/top-down).
        - La médaille doit être vue directement de face, comme posée sur une table et photographiée du dessus
        - Aucune perspective, aucun angle, parfaitement orthogonale
        - Montre tous les détails de la gravure clairement visibles
        - Le fond doit être neutre et non distrayant pour mettre en valeur la médaille
        - Un ruban couleur bleu royal doit être attaché à la médaille, avec une boucle élégante au-dessus

${variationSeed}

Style: Rendu photoréaliste haute qualité, éclairage studio professionnel, fond neutre légèrement texturé.`;
  }

  private async generateImage(
    prompt: string,
    images: { inlineData: { mimeType: string; data: string } }[],
  ) {
    const contents = [{ text: prompt }, ...images];

    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(
        () =>
          reject(new Error("Timeout: la génération a pris plus de 2 minutes")),
        120000,
      );
    });

    const generatePromise = this.ai.models.generateContent({
      model: "gemini-3-pro-image-preview",
      contents: contents,
      config: {
        responseModalities: ["TEXT", "IMAGE"],
      },
    });

    return Promise.race([generatePromise, timeoutPromise]);
  }

  private getResponseInlineImageData(response: any): string {
    const imagePart = response.candidates[0].content.parts.find(
      (p) => p.inlineData,
    );
    return imagePart?.inlineData.data || "";
  }

  private saveResults(
    response: any,
    view: string,
    propositionIndex: number,
    outputDir: string,
  ): string[] {
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const savedFiles: string[] = [];

    for (const part of response.candidates[0].content.parts) {
      if (part.text) {
        this.logger.log(`💬 Gemini: ${part.text}`);
      } else if (part.inlineData) {
        const imageData = part.inlineData.data;
        const buffer = Buffer.from(imageData, "base64");
        const filename = `medaille_${view}_prop${propositionIndex + 1}_${timestamp}.png`;
        const filepath = path.join(outputDir, filename);
        fs.writeFileSync(filepath, buffer);
        savedFiles.push(filename);
        this.logger.log(`✅ Image sauvegardée: ${filename}`);
      }
    }

    return savedFiles;
  }
}
