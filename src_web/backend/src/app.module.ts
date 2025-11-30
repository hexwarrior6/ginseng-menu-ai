import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { ConfigModule } from '@nestjs/config';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { DishesModule } from './dishes/dishes.module';
import { UsersModule } from './users/users.module';
import { InteractionLogsModule } from './interaction-logs/interaction-logs.module';
import { DataInsightModule } from './data-insight/data-insight.module';
import { UserDishesModule } from './user-dishes/user-dishes.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    MongooseModule.forRoot(process.env.DATABASE_URL || '', {
      autoCreate: true,
      autoIndex: true,
    }),
    DishesModule,
    UsersModule,
    InteractionLogsModule,
    DataInsightModule,
    UserDishesModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
