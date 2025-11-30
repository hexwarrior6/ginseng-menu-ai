import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { InteractionLog, InteractionLogSchema } from '../models/interaction-log.model';
import { InteractionLogsController } from './interaction-logs.controller';
import { InteractionLogsService } from './interaction-logs.service';

@Module({
  imports: [
    MongooseModule.forFeature([{ name: InteractionLog.name, schema: InteractionLogSchema }]),
  ],
  controllers: [InteractionLogsController],
  providers: [InteractionLogsService],
  exports: [InteractionLogsService],
})
export class InteractionLogsModule {}