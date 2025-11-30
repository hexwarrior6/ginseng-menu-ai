import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document, Types } from 'mongoose';

export type UserDocument = User & Document;

@Schema({ timestamps: true })
export class User {
  @Prop({ required: true })
  name: string;

  @Prop({ required: true, unique: true })
  email: string;

  @Prop()
  preferences?: string[];

  @Prop()
  dietaryRestrictions?: string[];

  @Prop({ type: Object })
  interactionHistory?: any;

  @Prop()
  lastLogin?: Date;

  @Prop({ default: true })
  isActive?: boolean;
}

export const UserSchema = SchemaFactory.createForClass(User);