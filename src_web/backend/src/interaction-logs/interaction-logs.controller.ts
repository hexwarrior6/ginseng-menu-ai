import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { InteractionLogsService } from './interaction-logs.service';
import { InteractionLog } from '../models/interaction-log.model';

@Controller('interaction-logs')
export class InteractionLogsController {
  constructor(private readonly interactionLogsService: InteractionLogsService) {}

  @Get()
  async findAll(): Promise<InteractionLog[]> {
    return this.interactionLogsService.findAll();
  }

  @Get(':id')
  async findOne(@Param('id') id: string): Promise<InteractionLog | null> {
    return this.interactionLogsService.findOne(id);
  }

  @Get('user/:userId')
  async findByUserId(@Param('userId') userId: string): Promise<InteractionLog[]> {
    return this.interactionLogsService.findByUserId(userId);
  }

  @Post()
  async create(@Body() createInteractionLogDto: any): Promise<InteractionLog> {
    return this.interactionLogsService.create(createInteractionLogDto);
  }
}