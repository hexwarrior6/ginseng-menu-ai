import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type UserDishDocument = UserDish & Document;

@Schema({
  timestamps: true,
  collection: 'user_dishes' // Explicitly specify the collection name
})
export class UserDish {
  @Prop({ required: true })
  uid: string;

  @Prop({ required: true })
  dish_name: string;

  @Prop()
  timestamp?: Date;
}

export const UserDishSchema = SchemaFactory.createForClass(UserDish);