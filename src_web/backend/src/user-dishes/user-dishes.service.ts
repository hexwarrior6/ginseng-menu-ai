import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { UserDish, UserDishDocument } from './user-dish.model';

@Injectable()
export class UserDishesService {
  constructor(@InjectModel(UserDish.name) private userDishModel: Model<UserDishDocument>) {}

  async findAll(): Promise<UserDish[]> {
    return this.userDishModel.find().exec();
  }

  async findByUid(uid: string): Promise<UserDish[]> {
    return this.userDishModel.find({ uid }).exec();
  }

  async findOne(id: string): Promise<UserDish | null> {
    return this.userDishModel.findById(id).exec();
  }

  async create(createUserDishDto: any): Promise<UserDish> {
    const createdUserDish = new this.userDishModel({
      ...createUserDishDto,
      timestamp: createUserDishDto.timestamp || new Date(),
    });
    return createdUserDish.save();
  }

  async remove(id: string): Promise<any> {
    return this.userDishModel.findByIdAndDelete(id).exec();
  }

  async removeByUidAndDishName(uid: string, dishName: string): Promise<any> {
    return this.userDishModel.deleteMany({ uid, dish_name: dishName }).exec();
  }
}