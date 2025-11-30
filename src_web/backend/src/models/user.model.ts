import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type UserDocument = User & Document;

@Schema({ timestamps: true })
export class User {
  @Prop({ required: true, unique: true })
  uid: string;

  @Prop()
  name?: string;

  @Prop({
    type: {
      dietary_restrictions: [String],
      favorite_cuisines: [String],
      allergies: [String],
    },
  })
  preferences?: {
    dietary_restrictions?: string[];
    favorite_cuisines?: string[];
    allergies?: string[];
  };

  @Prop()
  created_at?: Date;

  @Prop()
  last_active?: Date;
}

export const UserSchema = SchemaFactory.createForClass(User);