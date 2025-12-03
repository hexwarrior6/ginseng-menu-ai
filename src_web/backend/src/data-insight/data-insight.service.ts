import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { User } from '../models/user.model';
import { Dish } from '../models/dish.model';
import { InteractionLog } from '../models/interaction-log.model';
import { UserDish } from '../user-dishes/user-dish.model';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class DataInsightService {
  constructor(
    @InjectModel(User.name) private userModel: Model<User>,
    @InjectModel(Dish.name) private dishModel: Model<Dish>,
    @InjectModel(InteractionLog.name) private interactionLogModel: Model<InteractionLog>,
    @InjectModel(UserDish.name) private userDishModel: Model<UserDish>,
    private configService: ConfigService,
  ) { }

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
      $or: [
        { timestamp: { $gte: today, $lt: tomorrow } },
        { createdAt: { $gte: today, $lt: tomorrow } }
      ]
    });

    // For daily interactions, use timestamp field
    const dailyInteractions = await this.interactionLogModel.countDocuments({
      timestamp: { $gte: today, $lt: tomorrow }
    });

    // For dailyUsers, we need to check both userId field and extra.uid
    const dailyUsersFromUserId = await this.interactionLogModel.distinct('userId', {
      timestamp: { $gte: today, $lt: tomorrow }
    });

    const dailyUsersFromExtra = await this.interactionLogModel.distinct('extra.uid', {
      timestamp: { $gte: today, $lt: tomorrow }
    });

    // Combine both arrays and remove duplicates
    const allDailyUsers = [...new Set([...dailyUsersFromUserId, ...dailyUsersFromExtra])];

    return {
      totalUsers,
      totalDishes: dailyDishes, // Changed to return daily dishes instead of total dishes
      totalInteractions,
      dailyInteractions,
      dailyActiveUsers: allDailyUsers.length,
    };
  }

  async getUserPreferences(userId: string) {
    const user = await this.userModel.findById(userId);
    return user?.preferences || [];
  }

  async getPopularDishes(
    limit: number = 10,
    timeRange: string = 'history',
    startDate?: string,
    endDate?: string,
  ) {
    const pipeline: any[] = [];

    if (timeRange === 'today' && startDate && endDate) {
      pipeline.push({
        $match: {
          timestamp: {
            $gte: new Date(startDate),
            $lt: new Date(endDate),
          },
        },
      });
    } else if (timeRange === 'today') {
      // Fallback to server time if no dates provided (backward compatibility)
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);

      pipeline.push({
        $match: {
          timestamp: { $gte: today, $lt: tomorrow },
        },
      });
    }

    pipeline.push(
      {
        $group: {
          _id: '$dish_name',
          count: { $sum: 1 }
        }
      },
      { $sort: { count: -1 } },
      { $limit: limit },
      {
        $project: {
          _id: 0,
          name: '$_id',
          count: 1
        }
      }
    );

    return await this.userDishModel.aggregate(pipeline);
  }

  async getRecentActivity(limit: number = 20) {
    return await this.interactionLogModel
      .find()
      .sort({ timestamp: -1 })  // Changed from createdAt to timestamp
      .limit(limit);
  }

  async getAiAnalysis() {
    // 1. Gather Data
    const stats = await this.getDashboardStats();
    const popularDishes = await this.getPopularDishes(5, 'today');

    // 2. Construct Prompt
    const prompt = `
      Analyze the following restaurant data for today:
      - Daily Active Users: ${stats.dailyActiveUsers}
      - Daily Dishes Ordered: ${stats.totalDishes}
      - Daily Interactions: ${stats.dailyInteractions}
      - Top Popular Dishes Today: ${popularDishes.map(d => `${d.name} (${d.count})`).join(', ')}
      
      Please provide a brief business analysis and suggestions (max 150 words). Focus on sales performance and user engagement.
    `;

    // 3. Call DeepSeek API
    const apiKey = this.configService.get<string>('DEEPSEEK_API_KEY');
    const apiUrl = 'https://api.deepseek.com/chat/completions'; // Verify this URL

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: "deepseek-chat",
          messages: [
            { role: "system", content: "You are a helpful business analyst for a restaurant." },
            { role: "user", content: prompt }
          ],
          stream: false
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('DeepSeek API Error Status:', response.status);
        console.error('DeepSeek API Error Text:', errorText);
        throw new Error(`API Error: ${response.status} ${response.statusText} - ${errorText}`);
      }

      const data = await response.json();
      return {
        analysis: data.choices[0].message.content
      };
    } catch (error) {
      console.error('AI Analysis failed details:', error);
      return {
        analysis: "AI analysis is currently unavailable. Please try again later."
      };
    }
  }
}