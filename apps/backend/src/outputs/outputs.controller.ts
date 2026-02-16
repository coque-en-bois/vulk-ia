import { Controller, Get, Param, Res } from "@nestjs/common";
import { Response } from "express";
import * as fs from "fs";
import * as path from "path";
import * as archiver from "archiver";

@Controller("outputs")
export class OutputsController {
  private readonly outputsDir = path.join(
    __dirname,
    "..",
    "..",
    "..",
    "..",
    "outputs",
  );

  @Get(":eventSlug")
  listImages(@Param("eventSlug") eventSlug: string) {
    const dir = path.join(this.outputsDir, path.basename(eventSlug));

    if (!fs.existsSync(dir)) {
      return [];
    }

    const files = fs
      .readdirSync(dir)
      .filter((f) => /\.(png|jpe?g|webp)$/i.test(f))
      .sort();

    return files.map((filename) => ({
      filename,
      url: `/api/outputs/${eventSlug}/${filename}`,
    }));
  }

  @Get(":eventSlug/download/zip")
  async downloadZip(
    @Param("eventSlug") eventSlug: string,
    @Res() res: Response,
  ) {
    const safeSlug = path.basename(eventSlug);
    const dir = path.join(this.outputsDir, safeSlug);

    if (!fs.existsSync(dir)) {
      return res.status(404).json({ message: "Dossier non trouvé" });
    }

    const images = fs
      .readdirSync(dir)
      .filter((f) => /\.(png|jpe?g|webp)$/i.test(f));

    if (images.length === 0) {
      return res.status(404).json({ message: "Aucune image à télécharger" });
    }

    res.setHeader("Content-Type", "application/zip");
    res.setHeader(
      "Content-Disposition",
      `attachment; filename="${safeSlug}-images.zip"`,
    );

    const archive = archiver.default("zip", { zlib: { level: 6 } });
    archive.pipe(res);

    for (const file of images) {
      archive.file(path.join(dir, file), { name: file });
    }

    await archive.finalize();
  }

  @Get(":eventSlug/:filename")
  getImage(
    @Param("eventSlug") eventSlug: string,
    @Param("filename") filename: string,
    @Res() res: Response,
  ) {
    const safeName = path.basename(filename);
    const safeSlug = path.basename(eventSlug);
    const filePath = path.join(this.outputsDir, safeSlug, safeName);

    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ message: "Image non trouvée" });
    }

    return res.sendFile(filePath);
  }
}
