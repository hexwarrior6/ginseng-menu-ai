import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { UserDish, UserDishSchema } from './user-dish.model';
import { UserDishesService } from './user-dishes.service';
import { UserDishesController } from './user-dishes.controller';

@Module({
  imports: [
    MongooseModule.forFeature([{ name: UserDish.name, schema: UserDishSchema, collection: 'user_dishes' }]),
  ],
  controllers: [UserDishesController],
  providers: [UserDishesService],
  exports: [UserDishesService],
})
export class UserDishesModule {}