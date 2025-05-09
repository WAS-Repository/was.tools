import DocReader from './src/classes/docReader.class.js';
import axios from 'axios';
import cheerio from 'cheerio';

class WebSearchAgent {
  constructor() {
    this.sources = [
      'https://hampton.gov/docconst axios = require('axios');
      const mysql = require('mysql2/promise');
      const cheerio = require('cheerio');
      
      // cPanel connection pool
      const pool = mysql.createPool({
        host: 'localhost',
        user: 'jo_hruser',
        password: process.env.DB_PASSWORD,
        database: 'jo_hrdocs',
        waitForConnections: true
      });
      
      async function crawl() {
        try {
          const sources = [
            'https://hampton.gov/document-center',
            'https://norfolk.gov/documents'
          ];
      
          for (const url of sources) {
            const { data } = await axios.get(url);
            const $ = cheerio.load(data);
            
            const documents = [];
            $('.document-item').each((i, el) => {
              documents.push({
                title: $(el).find('h3').text().trim(),
                url: new URL($(el).find('a').attr('href'), url).toString(),
                type: 'document'
              });
            });
      
            await saveDocuments(documents);
          }
        } catch (error) {
          console.error('Crawl failed:', error);
        }
      }
      
      async function saveDocuments(docs) {
        const conn = await pool.getConnection();
        try {
          await conn.beginTransaction();
          
          for (const doc of docs) {
            const [res] = await conn.execute(
              `INSERT INTO documents (title, content, type) 
               VALUES (?, ?, ?)
               ON DUPLICATE KEY UPDATE content=VALUES(content)`,
              [doc.title, doc.url, doc.type]
            );
          }
          
          await conn.commit();
        } finally {
          conn.release();
        }
      }
      
      // Run daily at 2 AM
      require('node-cron').schedule('0 2 * * *', crawl);ument-center',
      'https://norfolk.gov/documents'
    ];
  }

  async crawl() {
    for (const url of this.sources) {
      const response = await axios.get(url);
      const $ = cheerio.load(response.data);
      
      $('.document-item').each(async (i, el) => {
        const title = $(el).find('.doc-title').text().trim();
        const link = $(el).find('a').attr('href');
        
        if (title && link) {
          await DocReader.saveDocument({
            title,
            type: 'document',
            content: await this.extractContent(link),
            source: url
          });
        }
      });
    }
  }

  async extractContent(url) {
    // Implementation for content extraction
  }
}

const agent = new WebSearchAgent();
agent.crawl();