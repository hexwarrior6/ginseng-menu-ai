import { Controller, Get, Post, Body, Patch, Param, Delete, Query } from '@nestjs/common';
import { UsersService } from './users.service';
import { User } from '../models/user.model';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  async findAll(): Promise<User[]> {
    return this.usersService.findAll();
  }

  @Get(':id')
  async findOne(@Param('id') id: string): Promise<User | null> {
    return this.usersService.findOne(id);
  }

  @Get('uid/:uid')
  async findByUid(@Param('uid') uid: string): Promise<User | null> {
    return this.usersService.findByUid(uid);
  }

  @Post()
  async create(@Body() createUserDto: any): Promise<User> {
    return this.usersService.create(createUserDto);
  }

  @Patch(':id')
  async update(@Param('id') id: string, @Body() updateUserDto: any): Promise<User | null> {
    return this.usersService.update(id, updateUserDto);
  }

  @Patch('uid/:uid')
  async updateByUid(@Param('uid') uid: string, @Body() updateUserDto: any): Promise<User | null> {
    return this.usersService.updateByUid(uid, updateUserDto);
  }

  @Delete(':id')
  async remove(@Param('id') id: string): Promise<any> {
    return this.usersService.remove(id);
  }
}