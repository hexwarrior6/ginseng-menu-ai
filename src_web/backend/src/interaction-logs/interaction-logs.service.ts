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
    return this.interactionLogModel
      .find()
      .populate('userId', 'name email')
      .exec();
  }

  async findOne(id: string): Promise<InteractionLog | null> {
    return this.interactionLogModel
      .findById(id)
      .populate('userId', 'name email')
      .exec();
  }

  async findByUserId(userId: string): Promise<InteractionLog[]> {
    return this.interactionLogModel
      .find({ userId })
      .populate('userId', 'name email')
      .exec();
  }

  async create(createInteractionLogDto: any): Promise<InteractionLog> {
    const createdInteractionLog = new this.interactionLogModel(createInteractionLogDto);
    return createdInteractionLog.save();
  }

  async remove(id: string): Promise<any> {
    return this.interactionLogModel.findByIdAndDelete(id).exec();
  }
}