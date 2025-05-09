import dotenv from 'dotenv';
dotenv.config();

export default {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'hr_docs',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};