import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { InteractionLog, InteractionLogDocument } from '../models/interaction-log.model';

@Injectable()
export class InteractionLogsService {
  constructor(
    @InjectModel(InteractionLog.name)
    private interactionLogModel: Model<InteractionLogDocument>
  ) {}

  async findAll(): Promise<InteractionLog[]> {
    return this.interactionLogModel.find().exec();
  }

  async findOne(id: string): Promise<InteractionLog | null> {
    return this.interactionLogModel.findById(id).exec();
  }

  async findByUserId(userId: string): Promise<InteractionLog[]> {
    // Search in both the userId field and the extra.uid field for backward compatibility
    return this.interactionLogModel.find({
      $or: [
        { userId: userId },
        { 'extra.uid': userId }
      ]
    }).exec();
  }

  async create(createInteractionLogDto: any): Promise<InteractionLog> {
    const createdInteractionLog = new this.interactionLogModel({
      ...createInteractionLogDto,
      timestamp: createInteractionLogDto.timestamp || new Date()
    });
    return createdInteractionLog.save();
  }

  async remove(id: string): Promise<any> {
    return this.interactionLogModel.findByIdAndDelete(id).exec();
  }
}