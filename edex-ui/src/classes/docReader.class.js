import mysql from 'mysql2/promise';
import config from '../config/database.js';

class DocReader {
  constructor() {
    this.pool = mysql.createPool(config);
  }

  async load(docId) {
    const [rows] = await this.pool.execute(`
      SELECT 
        d.id,const mysql = require('mysql2/promise');
        const config = require('../../config/database');
        
        class DocReader {
          constructor() {
            this.pool = mysql.createPool(config);
          }
        
          async getDocument(id) {
            const [rows] = await this.pool.execute(`
              SELECT * FROM documents WHERE id = ?
            `, [id]);
            return rows[0];
          }
        }
        
        module.exports = new DocReader(); // CommonJS for cPanel compatibility
        d.title,
        d.content,
        d.type,
        d.created_at,
        d.location,
        GROUP_CONCAT(t.tag) AS tags
      FROM documents d
      LEFT JOIN document_tags dt ON d.id = dt.document_id
      LEFT JOIN tags t ON dt.tag_id = t.id
      WHERE d.id = ?
      GROUP BY d.id
    `, [docId]);

    if (rows.length === 0) {
      throw new Error('Document not found');
    }

    return this.formatDocument(rows[0]);
  }

  async search(query) {
    const [rows] = await this.pool.execute(`
      SELECT 
        id,
        title,
        type,
        created_at,
        MATCH(title, content) AGAINST(? IN BOOLEAN MODE) AS relevance
      FROM documents
      WHERE MATCH(title, content) AGAINST(? IN BOOLEAN MODE)
      ORDER BY relevance DESC
      LIMIT 50
    `, [query, query]);

    return rows;
  }

  formatDocument(doc) {
    return {
      ...doc,
      tags: doc.tags ? doc.tags.split(',') : [],
      location: doc.location ? JSON.parse(doc.location) : null
    };
  }
}

export default new DocReader();
    constructor(opts) {
        pdfjsLib.GlobalWorkerOptions.workerSrc = './node_modules/pdfjs-dist/build/pdf.worker.js';
        const modalElementId = "modal_" + opts.modalId;
        const path = opts.path;
        const scale = 1;
        const canvas = document.getElementById(modalElementId).querySelector(".pdf_canvas");
        const context = canvas.getContext('2d');
        const loadingTask = pdfjsLib.getDocument(path);
        let pdfDoc = null,
            pageNum = 1,
            pageRendering = false,
            pageNumPending = null,
            zoom = 100

        this.renderPage = (num) => {
            pageRendering = true;
            loadingTask.promise.then(function (pdf) {
                pdfDoc.getPage(num).then(function (page) {
                    const viewport = page.getViewport({ scale: scale });
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;

                    const renderContext = {
                        canvasContext: context,
                        viewport: viewport,
                    };
                    const renderTask = page.render(renderContext);
                    renderTask.promise.then(function () {
                        pageRendering = false;
                        if (pageNumPending !== null) {
                            renderPage(pageNumPending);
                            pageNumPending = null;
                        }
                    });
                });
            });
            document.getElementById(modalElementId).querySelector(".page_num").textContent = num;
        }

        this.queueRenderPage = (num) => {
            if (pageRendering) {
                pageNumPending = num;
            } else {
                this.renderPage(num);
            }
        }

        this.onPrevPage = () => {
            if (pageNum <= 1) {
                return;
            }
            pageNum--;
            this.queueRenderPage(pageNum);
        }

        this.onNextPage = () => {
            if (pageNum >= pdfDoc.numPages) {
                return;
            }
            pageNum++;
            this.queueRenderPage(pageNum);
        }

        this.zoomIn = () => {
            if (zoom >= 200) {
                return;
            }
            zoom = zoom + 10;
            canvas.style.zoom = zoom + "%";
        }

        this.zoomOut = () => {
            if (zoom <= 50) {
                return;
            }
            zoom = zoom - 10;
            canvas.style.zoom = zoom + "%";
        }

        document.getElementById(modalElementId).querySelector(".previous_page").addEventListener('click', this.onPrevPage);
        document.getElementById(modalElementId).querySelector(".next_page").addEventListener('click', this.onNextPage);
        document.getElementById(modalElementId).querySelector(".zoom_in").addEventListener('click', this.zoomIn);
        document.getElementById(modalElementId).querySelector(".zoom_out").addEventListener('click', this.zoomOut);

        pdfjsLib.getDocument(path).promise.then((pdfDoc_) => {
            pdfDoc = pdfDoc_;
            document.getElementById(modalElementId).querySelector(".page_count").textContent = pdfDoc.numPages;
            this.renderPage(pageNum);
        });
    }
}

module.exports = {
    DocReader
};