# Backend Architecture (Node.js + MySQL)

* **Microservices:** Split the system into small services (e.g. link scraper, content crawler, API server, GNN processor) that communicate via lightweight APIs or events. Node.js is well-suited for async microservices. For example, use Express/Koa for HTTP APIs and a message broker (RabbitMQ, Kafka, or Redis Streams) for event-driven tasks. This decouples agents and lets each scale independently (failure in one won’t take down others).
* **Data Model:** In MySQL, store one table for *Nodes* and one for *Edges*, where each edge row references its source and target node IDs. Index the node and edge tables carefully (e.g. composite indexes on predicates) to speed graph queries. As the graph grows, you may partition or sharding the tables. If extreme scalability is needed, consider a dedicated graph database (e.g. Neo4j, ArangoDB) or an analytics engine as a future addition.
* **Scraping & Crawling:** Use Node.js libraries like [Crawlee](https://crawlee.dev) or [Puppeteer](https://pptr.dev/) for crawling. Crawlee’s `RequestList` automatically deduplicates URLs by a unique key, which prevents revisiting the same link. Schedule crawlers with a job queue or cron. Use lightweight headless browsers or HTML parsers (Cheerio) to fetch content.
* **Graph Neural Network (GNN):** Offload heavy ML to a separate service. For example, export subgraphs from MySQL and train GNNs in Python (e.g. PyTorch Geometric, DGL), then store embeddings or inference results back in MySQL. Alternatively, use [TensorFlow.js](https://www.tensorflow.org/js) for small on-node inference, but large GNN training is usually done offline in Python.

*Tools & Practices:* Use Docker to containerize services. Employ connection pooling (e.g. [mysql2](https://github.com/sidorares/node-mysql2) with pool) and graceful shutdown. Use environment variables and logging (e.g. `winston`). Because Node.js is single-threaded, run multiple instances (PM2 or Kubernetes) behind a load balancer for concurrency.

# Deduplication (Scraped Data)

* **URL-level deduplication:** Before crawling, remove duplicate URLs. Frameworks like Crawlee’s `RequestList` do this by default. Store each visited URL’s hash or unique ID in a “visited” set (in MySQL or Redis) to avoid re-enqueueing the same link. Use canonicalization (normalize URLs) to catch small variations.
* **Content-level deduplication:** After scraping a page, compute a fingerprint (e.g. MD5/SHA1 of the text) and check against a “seen content” store. If an identical or near-duplicate (using fuzzy hashing like SimHash) exists, skip adding it. This catches cases where different URLs serve the same document. For large text dedup, open-source tools like [Dedupe](https://github.com/dedupeio/dedupe) (Python) can be used for fuzzy matching.
* **Database deduplication:** Define uniqueness constraints or use `INSERT ... ON DUPLICATE KEY` on nodes/edges. For example, if an “entity” node has a unique URI or title, enforce a unique index to prevent repeats. After scraping runs, run cleanup jobs or use SQL `SELECT DISTINCT` inserts to merge duplicates.
* **Tooling:** Consider data-processing frameworks. For instance, Apify’s actors include a “Merge, Dedup & Transform” tool to clean scraping datasets. (This open-source platform shows how to pipeline scraping and deduplication.) Even if not using Apify’s service, their approach illustrates combining actors (scraper ➔ deduper).

# Frontend Stack (PWA Compatibility & Performance)

| Framework / Library         | Bundle Size & Render Speed                                                                                                                                                                        | PWA Support                                      | Ecosystem & Tradeoffs                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| **React**                   | Larger bundle; virtual-DOM can slow initial render. Mature tooling (Create React App, Next.js for SSR) and vast ecosystem. PWA support via Workbox and CRA’s service worker.                      | Excellent (CRA/Next have PWA templates)          | Very popular; lots of libraries. Can feel “heavy” for simple UIs.                              |
| **Vue.js**                  | Moderate bundle; faster startup than React (smaller runtime). Supports templates or JSX. PWA support via Vue CLI plugin and Nuxt.js.                                                              | Good (Vue CLI PWA plugin, Nuxt)                  | Balance of performance and ease-of-use. Strong documentation. Fewer mobile options than React. |
| **Angular**                 | Large bundle (full framework); incremental DOM in v9+ improves speed, but still generally slower than React. Built-in tools (CLI, RxJS). PWA support built into Angular CLI with a PWA generator. | Good (Angular Service Worker, CLI scaffolding)   | Heavy weight; full MVC framework. Less flexible but batteries-included (forms, router, i18n).  |
| **Svelte / SvelteKit**      | Smallest bundle; compiles to vanilla JS with no runtime, yielding **very fast** initial loads and updates. PWA support via service worker plugin.                                                 | Good (community templates and Vite integrations) | Newer ecosystem (fewer component libraries). Ideal if top performance is critical.             |
| **Others:** *(e.g. Preact)* | Similar to React but smaller.                                                                                                                                                                     | Varies                                           | Preact: drop-in React alternative, smaller bundle.                                             |

* **Rendering:** According to benchmarks, *Svelte* produces the smallest bundles and fastest initial render (no virtual DOM). *Vue* apps typically load faster than comparable React apps due to smaller overhead. *React* offers the largest ecosystem but comes with more runtime cost. *Angular* is feature-rich but has higher upfront weight; React has a slight performance edge over Angular.

* **PWA Features:** All major frameworks can be PWAs. Tools like Workbox (by Google) or framework CLI plugins generate the `manifest.json` and service workers for offline caching. For 1920×1080 desktop PWA, ensure responsive design (or lock UI to that resolution via CSS) and use service workers to cache critical assets/documents for fast load.

* **Stack Choices:** If you need the absolute fastest front-end, *Svelte* (or *Preact*) is best. If you prefer maturity and a huge ecosystem, *React* is solid. *Vue* is a good middle ground. Whichever you pick, use modern bundlers (Webpack, Vite/Rollup) to code-split and minimize bundle size, and enable tree-shaking.

# In-App Document Viewing (PDF/HTML)

* **PDF.js:** Mozilla’s [PDF.js](https://mozilla.github.io/pdf.js/) is the de-facto open-source library for rendering PDFs in-browser. It renders onto HTML5 `<canvas>`, allowing text search/selection. You can integrate the default PDF.js viewer or use it headlessly in your UI. For React/Vue/Angular, there are wrappers like **React-PDF** and **pdfvuer**.

* **Framework-specific viewers:** For React, [react-pdf](https://github.com/wojtekmaj/react-pdf) leverages PDF.js to render PDFs. For Vue, [pdfvuer](https://github.com/arkokoley/pdfvuer) does similarly. For Angular, [ngx-extended-pdf-viewer](https://github.com/stephanrauh/ngx-extended-pdf-viewer) (Apache-2.0) is a full-featured PDF viewer component. All are open-source and support zooming, pagination, etc.

* **HTML content:** If documents are HTML, you can either display the raw HTML in a safe container (e.g. using `v-html` in Vue or `dangerouslySetInnerHTML` in React after sanitizing with DOMPurify) or embed them via an `<iframe>`. **Important:** Many government sites set `X-Frame-Options: DENY`, so external HTML won’t load in an iframe. To handle this, either fetch the HTML server-side (Node) and serve it (so it’s same-origin), or use a headless browser (Puppeteer) to snapshot/convert it. Another option is to convert HTML to PDF (e.g. with `wkhtmltopdf`) and then use PDF.js.

* **ViewerJS:** [ViewerJS](https://viewerjs.org/) is an open-source web-based document viewer (GPL) built on PDF.js and WebODF. It can display PDFs and ODF (LibreOffice formats) out of the box. It requires no server conversion and runs entirely in the browser. It’s lightweight and offline-capable, making it a good fallback if your data includes OpenDocument formats.

* **Security:** Always sanitize or CORS-proxy external content. For example, use Node.js (express middleware) to fetch a PDF or HTML and pipe it to the frontend. This avoids mixed-content and CORS issues. Disable `X-Frame-Options` by proxying through your domain.

# Graph Visualization Optimization

* **Use WebGL or Canvas:** For large graphs, prefer libraries that use GPU. *Sigma.js* (WebGL) can smoothly render tens of thousands of nodes. *Ogma* (commercial) also uses WebGL for 100k+ nodes. *Vis.js* uses HTML5 Canvas and supports built-in clustering for large data. *Cytoscape.js* is pure JS (Canvas/SVG) and handles very large networks (100k+ nodes) with efficient layout and a headless mode.

* **Simplify and Cluster:** Avoid drawing the entire graph at once. Use clustering or abstraction: group related nodes into a single cluster node until the user zooms in. Allow expanding clusters on demand. Simplify styles (use simple circles/lines, avoid heavy shadows or transparencies).

* **Lazy Loading:** Fetch and render graph data on demand. Start with a small subgraph, then load neighbors as needed (infinite scroll graph). This reduces initial rendering load.

* **Efficient Layouts:** Pre-compute layouts server-side if possible, or use fast algorithms (force-directed, but only run once). Use Web Worker to avoid blocking the UI thread on layouts. Many graph libraries (Cytoscape, D3) support async layouts.

* **Hardware Acceleration:** Enable WebGL shaders if available. For example, Sigma can use WebGL to render in “WebGL renderer” mode. This offloads drawing from the CPU.

* **Interactivity:** Limit real-time updates; batch changes or throttle interactions. Use features like fisheye zoom or focus+context to highlight parts of the graph without showing all edges.

* **Library Choices:** Recommended open-source libraries:

  * **Cytoscape.js:** MIT-licensed, very powerful (built-in algorithms, 100k+ nodes). Good for most use cases.
  * **Sigma.js:** MIT, WebGL-based for large graphs (tens of thousands of nodes).
  * **Vis.js (vis-network):** MIT, easy setup, HTML5 Canvas, good for thousands of nodes.
  * **D3.js:** General-purpose (force-directed), but more coding required; suitable for custom needs.
  * **ECharts (Apache):** Has a graph/chart module with WebGL support for large graphs.
  * **Graphology + React/Canvas:** A flexible combination for custom visualizations.

Each has trade-offs in features vs. performance. In general, prefer WebGL-based rendering (Sigma/Ogma) for largest graphs, and use interactivity (pan/zoom) wisely.

**Sources:** Architecture and microservice patterns; URL de-dup in Crawlee; deduplication tools; front-end benchmarks; PDF.js and viewers; graph viz libraries.
