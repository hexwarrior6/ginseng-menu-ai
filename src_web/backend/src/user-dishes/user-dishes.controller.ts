import { Controller, Get, Post, Body, Param, Delete, Query } from '@nestjs/common';
import { UserDishesService } from './user-dishes.service';
import { UserDish } from './user-dish.model';

@Controller('user-dishes')
export class UserDishesController {
  constructor(private readonly userDishesService: UserDishesService) {}

  @Get()
  async findAll(): Promise<UserDish[]> {
    return this.userDishesService.findAll();
  }

  @Get('uid/:uid')
  async findByUid(@Param('uid') uid: string): Promise<UserDish[]> {
    return this.userDishesService.findByUid(uid);
  }

  @Get(':id')
  async findOne(@Param('id') id: string): Promise<UserDish | null> {
    return this.userDishesService.findOne(id);
  }

  @Post()
  async create(@Body() createUserDishDto: any): Promise<UserDish> {
    return this.userDishesService.create(createUserDishDto);
  }

  @Delete(':id')
  async remove(@Param('id') id: string) {
    return this.userDishesService.remove(id);
  }

  @Delete('uid/:uid/dish/:dishName')
  async removeByUidAndDishName(
    @Param('uid') uid: string,
    @Param('dishName') dishName: string,
  ) {
    return this.userDishesService.removeByUidAndDishName(uid, dishName);
  }
}