import {
  Controller,
  Post,
  Body,
  Res,
  UploadedFiles,
  UseInterceptors,
} from "@nestjs/common";
import { FilesInterceptor } from "@nestjs/platform-express";
import { Response } from "express";
import { GenerationService } from "./generation.service";
import type { ProgressEvent } from "./generation.service";

export class GenerateDto {
  eventName: string;
  inspirationImages: string; // JSON stringified array
  prompt: string;
}

@Controller("generate")
export class GenerationController {
  constructor(private readonly generationService: GenerationService) {}

  @Post()
  @UseInterceptors(FilesInterceptor("clientFiles", 10))
  async generate(
    @Body() body: GenerateDto,
    @UploadedFiles() clientFiles: Express.Multer.File[],
    @Res() res: Response,
  ) {
    const inspirationImages: string[] = JSON.parse(
      body.inspirationImages || "[]",
    );

    // Configurer les headers SSE
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.flushHeaders();

    const onProgress = (event: ProgressEvent) => {
      res.write(`data: ${JSON.stringify(event)}\n\n`);
    };

    try {
      const result = await this.generationService.generate({
        eventName: body.eventName,
        inspirationImages,
        clientFiles: clientFiles || [],
        prompt: body.prompt,
        onProgress,
      });

      // Envoyer le résultat final
      res.write(`data: ${JSON.stringify({ type: "result", ...result })}\n\n`);
    } catch (error) {
      res.write(
        `data: ${JSON.stringify({ type: "error", message: error.message })}\n\n`,
      );
    } finally {
      res.end();
    }
  }
}
