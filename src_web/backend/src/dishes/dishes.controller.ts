import { Controller, Get, Post, Body, Patch, Param, Delete } from '@nestjs/common';
import { DishesService } from './dishes.service';
import { Dish } from '../models/dish.model';

@Controller('dishes')
export class DishesController {
  constructor(private readonly dishesService: DishesService) {}

  @Get()
  async findAll(): Promise<Dish[]> {
    return this.dishesService.findAll();
  }

  @Get(':id')
  async findOne(@Param('id') id: string): Promise<Dish | null> {
    return this.dishesService.findOne(id);
  }
}