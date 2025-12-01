import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Dish, DishDocument } from '../models/dish.model';

@Injectable()
export class DishesService {
  constructor(@InjectModel(Dish.name) private dishModel: Model<DishDocument>) {}

  async findAll(): Promise<Dish[]> {
    return this.dishModel.find().exec();
  }

  async findOne(id: string): Promise<Dish | null> {
    return this.dishModel.findById(id).exec();
  }

  async create(createDishDto: any): Promise<Dish> {
    const createdDish = new this.dishModel({
      ...createDishDto,
      timestamp: createDishDto.timestamp || new Date(),
    });
    return createdDish.save();
  }

  async update(id: string, updateDishDto: any): Promise<Dish | null> {
    return this.dishModel.findByIdAndUpdate(id, {
      ...updateDishDto,
      timestamp: updateDishDto.timestamp || new Date(),
    }, { new: true }).exec();
  }

  async remove(id: string): Promise<any> {
    return this.dishModel.findByIdAndDelete(id).exec();
  }
}