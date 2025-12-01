import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Enable CORS to allow requests from the frontend
  app.enableCors({
    origin: [
      'http://localhost:5173',  // Vite default port
      'http://localhost:3000',  // Your current API base URL
      'http://localhost:3001',  // Common Vite port
      'http://localhost:3002',  // Another common port
      'http://localhost:8080',  // Common dev server port
      'http://localhost:8000',  // Another common port
      'http://localhost:4200',  // Angular default port
      'http://localhost:4173',  // Vite build server port
      'https://ginseng-menu-ai.vercel.app',
      'https://ginseng-menu-ai.hexwarrior6.top',
    ],
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS',
    credentials: true,
    allowedHeaders: 'Origin, X-Requested-With, Content-Type, Accept, Authorization',
  });

  await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
