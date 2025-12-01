import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document, Types } from 'mongoose';

export type InteractionLogDocument = InteractionLog & Document;

@Schema({ timestamps: true })
export class InteractionLog {
  @Prop({ required: true, type: Types.ObjectId, ref: 'User' })
  userId: Types.ObjectId;

  @Prop({ required: true })
  action: string;

  @Prop()
  actionType: string;

  @Prop()
  dishId?: string;

  @Prop()
  dishName?: string;

  @Prop({ type: Object })
  details?: any;

  @Prop()
  ipAddress?: string;

  @Prop()
  userAgent?: string;
}

export const InteractionLogSchema = SchemaFactory.createForClass(InteractionLog);