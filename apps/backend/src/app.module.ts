import { Module } from "@nestjs/common";
import { ServeStaticModule } from "@nestjs/serve-static";
import { join } from "path";
import { GenerationModule } from "./generation/generation.module";
import { InputsModule } from "./inputs/inputs.module";
import { OutputsModule } from "./outputs/outputs.module";

@Module({
  imports: [
    ServeStaticModule.forRoot({
      rootPath: join(__dirname, "..", "..", "frontend", "dist"),
      exclude: ["/api/(.*)"],
    }),
    GenerationModule,
    InputsModule,
    OutputsModule,
  ],
})
export class AppModule {}
