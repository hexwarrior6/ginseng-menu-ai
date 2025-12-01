import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { User, UserDocument } from '../models/user.model';

@Injectable()
export class UsersService {
  constructor(@InjectModel(User.name) private userModel: Model<UserDocument>) {}

  async findAll(): Promise<User[]> {
    return this.userModel.find().exec();
  }

  async findOne(id: string): Promise<User | null> {
    return this.userModel.findById(id).exec();
  }

  async findByUid(uid: string): Promise<User | null> {
    return this.userModel.findOne({ uid }).exec();
  }

  async create(createUserDto: any): Promise<User> {
    const createdUser = new this.userModel({
      ...createUserDto,
      created_at: new Date(),
      last_active: new Date(),
    });
    return createdUser.save();
  }

  async update(id: string, updateUserDto: any): Promise<User | null> {
    return this.userModel.findByIdAndUpdate(id, {
      ...updateUserDto,
      last_active: new Date()
    }, { new: true }).exec();
  }

  async updateByUid(uid: string, updateUserDto: any): Promise<User | null> {
    return this.userModel.findOneAndUpdate(
      { uid },
      { ...updateUserDto, last_active: new Date() },
      { new: true }
    ).exec();
  }

  async remove(id: string): Promise<any> {
    return this.userModel.findByIdAndDelete(id).exec();
  }
}