import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { User } from '../models/user.model';
import { Dish } from '../models/dish.model';
import { InteractionLog } from '../models/interaction-log.model';

@Injectable()
export class DataInsightService {
  constructor(
    @InjectModel(User.name) private userModel: Model<User>,
    @InjectModel(Dish.name) private dishModel: Model<Dish>,
    @InjectModel(InteractionLog.name) private interactionLogModel: Model<InteractionLog>,
  ) {}

  async getDashboardStats() {
    const totalUsers = await this.userModel.countDocuments();
    const totalInteractions = await this.interactionLogModel.countDocuments();

    // Get today's date for daily stats
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    // Count dishes created today (daily dishes) instead of total dishes
    const dailyDishes = await this.dishModel.countDocuments({
      createdAt: { $gte: today, $lt: tomorrow }
    });

    const dailyInteractions = await this.interactionLogModel.countDocuments({
      createdAt: { $gte: today, $lt: tomorrow }
    });

    const dailyUsers = await this.interactionLogModel.distinct('userId', {
      createdAt: { $gte: today, $lt: tomorrow }
    });

    return {
      totalUsers,
      totalDishes: dailyDishes, // Changed to return daily dishes instead of total dishes
      totalInteractions,
      dailyInteractions,
      dailyActiveUsers: dailyUsers.length,
    };
  }

  async getUserPreferences(userId: string) {
    const user = await this.userModel.findById(userId);
    return user?.preferences || [];
  }

  async getPopularDishes(limit: number = 10) {
    // This would aggregate interaction logs to find popular dishes
    // For now, returning all dishes as a placeholder
    return await this.dishModel.find({ isAvailable: true }).limit(limit);
  }

  async getRecentActivity(limit: number = 20) {
    return await this.interactionLogModel
      .find()
      .populate('userId', 'name email')
      .sort({ createdAt: -1 })
      .limit(limit);
  }
}