import {
  GenerationRequest,
  GenerationResult,
  InputImage,
  ProgressEvent,
} from "./types";
import { getAuthToken } from "./components/AuthGate/AuthGate";

const API_BASE = import.meta.env.VITE_BACKEND_API;

if (!API_BASE) {
  throw new Error("VITE_BACKEND_API environment variable is not set");
}

function authHeaders(): Record<string, string> {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchInputImages(): Promise<InputImage[]> {
  const res = await fetch(`${API_BASE}/inputs`, {
    headers: authHeaders(),
  });
  if (!res.ok)
    throw new Error("Impossible de charger les images d'inspiration");
  return res.json();
}

export async function submitGeneration(
  data: GenerationRequest,
  onProgress?: (event: ProgressEvent) => void,
): Promise<GenerationResult> {
  const formData = new FormData();
  formData.append("eventName", data.eventName);
  formData.append("prompt", data.prompt);
  formData.append("inspirationImages", JSON.stringify(data.inspirationImages));

  for (const file of data.clientFiles) {
    formData.append("clientFiles", file);
  }

  const res = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: "Erreur serveur" }));
    throw new Error(err.message || "Erreur lors de la génération");
  }

  // Lire le stream SSE
  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalResult: GenerationResult | null = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Extraire les messages SSE du buffer
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const parsed = JSON.parse(line.slice(6));

          if (parsed.type === "result") {
            finalResult = {
              success: parsed.success,
              outputDir: parsed.outputDir,
              images: parsed.images,
              message: parsed.message,
            };
          } else if (parsed.type === "error") {
            throw new Error(parsed.message);
          } else if (onProgress) {
            onProgress(parsed as ProgressEvent);
          }
        } catch (e) {
          if (e instanceof Error && e.message !== "Erreur serveur") {
            throw e;
          }
        }
      }
    }
  }

  if (!finalResult) {
    throw new Error("Aucun résultat reçu du serveur");
  }

  return finalResult;
}

export function getZipDownloadUrl(outputDir: string): string {
  return `${API_BASE}/outputs/${outputDir}/download/zip`;
}
