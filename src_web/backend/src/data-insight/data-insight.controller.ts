import { Controller, Get, Param, Query } from '@nestjs/common';
import { DataInsightService } from './data-insight.service';

@Controller('data-insight')
export class DataInsightController {
  constructor(private readonly dataInsightService: DataInsightService) { }

  @Get('dashboard-stats')
  async getDashboardStats() {
    return this.dataInsightService.getDashboardStats();
  }

  @Get('user-preferences/:userId')
  async getUserPreferences(@Param('userId') userId: string) {
    return this.dataInsightService.getUserPreferences(userId);
  }

  @Get('popular-dishes')
  async getPopularDishes(@Query('limit') limit?: string, @Query('timeRange') timeRange?: string) {
    const parsedLimit = limit ? parseInt(limit, 10) : 10;
    return this.dataInsightService.getPopularDishes(parsedLimit, timeRange);
  }

  @Get('recent-activity')
  async getRecentActivity(@Query('limit') limit?: string) {
    const parsedLimit = limit ? parseInt(limit, 10) : 20;
    return this.dataInsightService.getRecentActivity(parsedLimit);
  }
}