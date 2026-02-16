import { Module } from "@nestjs/common";
import { OutputsController } from "./outputs.controller";

@Module({
  controllers: [OutputsController],
})
export class OutputsModule {}
