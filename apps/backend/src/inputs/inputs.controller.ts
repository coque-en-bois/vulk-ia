import { Controller, Get, Param, Res } from "@nestjs/common";
import { Response } from "express";
import * as fs from "fs";
import * as path from "path";

@Controller("inputs")
export class InputsController {
  private readonly inputsDir = path.join(
    __dirname,
    "..",
    "..",
    "..",
    "..",
    "inputs",
  );

  @Get()
  listImages() {
    if (!fs.existsSync(this.inputsDir)) {
      return [];
    }

    const files = fs
      .readdirSync(this.inputsDir)
      .filter((f) => /\.(png|jpe?g|svg|webp)$/i.test(f))
      .sort();

    return files.map((filename) => ({
      filename,
      url: `/api/inputs/${filename}`,
    }));
  }

  @Get(":filename")
  getImage(@Param("filename") filename: string, @Res() res: Response) {
    // Sécurité : empêcher la traversée de répertoire
    const safeName = path.basename(filename);
    const filePath = path.join(this.inputsDir, safeName);

    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ message: "Image non trouvée" });
    }

    return res.sendFile(filePath);
  }
}
