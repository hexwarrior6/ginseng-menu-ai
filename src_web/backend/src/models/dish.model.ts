import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type DishDocument = Dish & Document;

@Schema({ timestamps: true })
export class Dish {
  @Prop({ required: true })
  name: string;

  @Prop()
  category?: string;

  @Prop()
  timestamp?: Date;

  @Prop()
  calories?: number;

  @Prop({ type: Object })
  nutrition?: {
    protein_g?: number;
    carbs_g?: number;
    fat_g?: number;
    fiber_g?: number;
  };
}

export const DishSchema = SchemaFactory.createForClass(Dish);