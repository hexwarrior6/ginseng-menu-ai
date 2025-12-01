import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { User, UserSchema } from '../models/user.model';
import { Dish, DishSchema } from '../models/dish.model';
import { InteractionLog, InteractionLogSchema } from '../models/interaction-log.model';
import { UserDish, UserDishSchema } from '../user-dishes/user-dish.model';
import { DataInsightController } from './data-insight.controller';
import { DataInsightService } from './data-insight.service';

@Module({
  imports: [
    MongooseModule.forFeature([
      { name: User.name, schema: UserSchema },
      { name: Dish.name, schema: DishSchema },
      { name: InteractionLog.name, schema: InteractionLogSchema },
      { name: UserDish.name, schema: UserDishSchema }
    ]),
  ],
  controllers: [DataInsightController],
  providers: [DataInsightService],
})
export class DataInsightModule { }