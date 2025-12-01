import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type InteractionLogDocument = InteractionLog & Document;

// Define the extra field structure with different possible shapes
export class InteractionLogExtra {
  @Prop()
  uid?: string;

  @Prop()
  action?: string;

  @Prop()
  module_name?: string;

  @Prop({ type: Object })
  details?: any;

  @Prop({ type: Object })
  input_data?: any;

  @Prop({ type: Object })
  output_data?: any;

  @Prop({ type: Boolean })
  success?: boolean;

  @Prop()
  image_path?: string;

  @Prop({ type: Object })
  analysis_result?: any;

  @Prop()
  speech_input?: string;

  @Prop()
  suggestion_result?: string;

  @Prop({ type: Object })
  error?: any;

  @Prop({ type: Object })
  function?: string;

  @Prop({ type: Number })
  args_length?: number;

  @Prop({ type: [String] })
  kwargs_keys?: string[];

  @Prop({ type: String })
  result_type?: string;

  @Prop({ type: Number })
  result_length?: number;
}

@Schema({ timestamps: false, collection: 'user_interactions' }) // Don't use timestamps since we have timestamp field from logs, and set collection name to user_interactions
export class InteractionLog {
  @Prop({ required: true })
  timestamp: Date;

  @Prop({ required: true, default: 'INFO' })
  level: string;

  @Prop({ required: true })
  message: string;

  @Prop()
  module: string;

  @Prop()
  function: string;

  @Prop({ type: Number })
  line_number?: number;

  @Prop()
  logger_name?: string;

  @Prop({ type: Number })
  process_id?: number;

  @Prop()
  thread_id?: string;

  @Prop()
  thread_name?: string;

  @Prop({ type: InteractionLogExtra })
  extra?: InteractionLogExtra;

  // For backward compatibility
  @Prop()
  userId?: string;

  @Prop()
  action?: string;

  @Prop()
  actionType?: string;

  @Prop()
  dishName?: string;

  @Prop()
  dishId?: string;

  @Prop({ type: Object })
  details?: any;

  @Prop()
  ipAddress?: string;

  @Prop()
  userAgent?: string;
}

export const InteractionLogSchema = SchemaFactory.createForClass(InteractionLog);