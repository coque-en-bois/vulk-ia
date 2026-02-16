export interface GenerationRequest {
  eventName: string;
  inspirationImages: string[];
  clientFiles: File[];
  prompt: string;
}

export interface InputImage {
  filename: string;
  url: string;
}

export interface ProgressEvent {
  type: "start" | "progress" | "complete" | "error";
  current: number;
  total: number;
  view?: string;
  proposition?: number;
  message: string;
}

export interface GenerationResult {
  success: boolean;
  outputDir: string;
  images: { filename: string; url: string }[];
  message: string;
}
