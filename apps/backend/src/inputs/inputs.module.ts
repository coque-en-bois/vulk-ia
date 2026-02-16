import { Module } from "@nestjs/common";
import { InputsController } from "./inputs.controller";

@Module({
  controllers: [InputsController],
})
export class InputsModule {}
