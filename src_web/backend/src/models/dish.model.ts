import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type DishDocument = Dish & Document;

@Schema({ timestamps: true })
export class Dish {
  @Prop({ required: true })
  name: string;

  @Prop()
  description?: string;

  @Prop()
  category?: string;

  @Prop([String])
  ingredients?: string[];

  @Prop({ type: Object })
  nutritionalInfo?: {
    calories?: number;
    protein?: number;
    carbs?: number;
    fat?: number;
  };

  @Prop()
  image?: string;

  @Prop({ default: true })
  isAvailable?: boolean;

  @Prop()
  preparationTime?: number;

  @Prop({ type: Object })
  additionalInfo?: any;
}

export const DishSchema = SchemaFactory.createForClass(Dish);