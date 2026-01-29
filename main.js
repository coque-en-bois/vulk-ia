import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

import exemple1 from "./inputs/1.png";
import exemple2 from "./inputs/2.png";
import exemple3 from "./inputs/3.png";
import exemple4 from "./inputs/4.png";
import exemple5 from "./inputs/5.png";
import exemple6 from "./inputs/6.png";
import exemple7 from "./inputs/7.png";
import exemple8 from "./inputs/8.png";
import exemple9 from "./inputs/9.png";

const base64ImageFile1 = fs.readFileSync(exemple1, {
  encoding: "base64",
});
const base64ImageFile2 = fs.readFileSync(exemple2, {
  encoding: "base64",
});
const base64ImageFile3 = fs.readFileSync(exemple3, {
  encoding: "base64",
});
const base64ImageFile4 = fs.readFileSync(exemple4, {
  encoding: "base64",
});
const base64ImageFile5 = fs.readFileSync(exemple5, {
  encoding: "base64",
});
const base64ImageFile6 = fs.readFileSync(exemple6, {
  encoding: "base64",
});
const base64ImageFile7 = fs.readFileSync(exemple7, {
  encoding: "base64",
});
const base64ImageFile8 = fs.readFileSync(exemple8, {
  encoding: "base64",
});
const base64ImageFile9 = fs.readFileSync(exemple9, {
  encoding: "base64",
});

async function main() {
  const ai = new GoogleGenAI({});

  const prompt =
    "An office group photo of these people, they are making funny faces.";
  const aspectRatio = "5:4";
  const resolution = "2K";

  const contents = [
    { text: prompt },
    {
      inlineData: {
        mimeType: "image/png",
        data: base64ImageFile1,
      },
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: base64ImageFile2,
      },
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: base64ImageFile3,
      },
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: base64ImageFile4,
      },
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: base64ImageFile5,
      },
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: base64ImageFile6,
      },
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: base64ImageFile7,
      },
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: base64ImageFile8,
      },
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: base64ImageFile9,
      },
    },
  ];

  const response = await ai.models.generateContent({
    model: "gemini-3-pro-image-preview",
    contents: contents,
    config: {
      responseModalities: ["TEXT", "IMAGE"],
      imageConfig: {
        aspectRatio: aspectRatio,
        imageSize: resolution,
      },
    },
  });

  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      console.log(part.text);
    } else if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync("image.png", buffer);
      console.log("Image saved as image.png");
    }
  }
}

main();
