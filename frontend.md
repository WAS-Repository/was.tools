Below is a mapping of each UI pane in your multi‐pane EDEX-inspired frontend to the backend services, data models and API patterns you’ll need in Node.js + MySQL to make it all work as a cohesive system.

---

## 1. Current Time

* **Frontend:** simple clock component
* **Backend:** none (pure client-side).
* **Integration tip:** Use the browser’s `Intl.DateTimeFormat` or a small utility (e.g. `new Date()`) and keep it in sync with `setInterval`. No round-trip needed.

---

## 2. Project Metadata

* **Data model:**

  ```sql
  CREATE TABLE project_metadata (
    key   VARCHAR(64) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP
  );
  ```
* **Service:** `metadata-service` (Express/Koa)
* **Endpoint:**

  ```http
  GET /api/metadata
  ```

  returns JSON `{ "uptime":"2 days, 07:45:44", "power":"WIRED", … }`
* **Frontend:** fetch on page load (or WebSocket for live updates) and render.

---

## 3. Document Correlation Strength

* **Data model:** store precomputed edge‐weights

  ```sql
  CREATE TABLE correlations (
    from_doc INT,
    to_doc   INT,
    score    FLOAT,
    PRIMARY KEY (from_doc, to_doc)
  );
  ```
* **Service:** `correlation-service`
* **Endpoint:**

  ```http
  GET /api/docs/:id/correlations?limit=5
  ```

  returns top N correlated documents
* **Frontend:** bar chart component; call on node selection.

---

## 4. Time-Series Heatmap of Event Dates

* **Data model:**

  ```sql
  CREATE TABLE events (
    doc_id   INT,
    event_ts DATE,
    count    INT
  );
  ```
* **Service:** `timeline-service`
* **Endpoint:**

  ```http
  GET /api/docs/:id/events?from=YYYY-MM-DD&to=YYYY-MM-DD
  ```

  returns an array of `{ date, count }`
* **Frontend:** turn into a heatmap grid (e.g. CSS grid + colored cells).

---

## 5. Node Key Role-Players List

* **Data model:**

  ```sql
  CREATE TABLE actors (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(128),
    role    VARCHAR(64)
  );
  CREATE TABLE doc_actors (
    doc_id INT,
    actor_id INT,
    involvement_score FLOAT
  );
  ```
* **Service:** `actors-service`
* **Endpoint:**

  ```http
  GET /api/docs/:id/actors?sort=score&limit=5
  ```

  returns top actors with their involvement percentages.
* **Frontend:** list with name + percent bar.

---

## 6a/6b. File Explorer / Terminal Toggle

* **Data model:**

  * *Files* live in the database (e.g. `files` table with `id, name, mime, content_url`).
* **Service:**

  * `files-service` exposing REST + streaming endpoints.
  * `terminal-service` exposing a secure PTY back end (e.g. via \[node-pty]).
* **Endpoints:**

  ```http
  GET    /api/files?path=/home/user/...
  GET    /api/files/:id/download
  POST   /api/terminal/:sessionId/input  { text }
  GET    /api/terminal/:sessionId/output  (Server-Sent Events or WebSocket)
  ```
* **Frontend:**

  * File explorer pane: tree view calling `/api/files`.
  * Terminal pane: a `<canvas>` or `<pre>` that speaks to a WebSocket, rendering pty output; send key events into `/api/terminal`.

---

## 7. Document Selection Tabs

* **Service:** built into `files-service` + `docs-service`.
* **Data model:** your `documents` table.
* **Endpoint:**

  ```http
  GET /api/docs?filter=…&page=…
  ```

  populates the tabs.
* **Frontend:** render each selected doc as its own tab, fetch content on activate.

---

## 8a/8b. Document Node Location of Origin & Primary Impact

* **Data model:** extend `documents` with geo fields

  ```sql
  ALTER TABLE documents
    ADD origin_lat  DECIMAL(9,6),
    ADD origin_lon  DECIMAL(9,6),
    ADD impact_lat  DECIMAL(9,6),
    ADD impact_lon  DECIMAL(9,6);
  ```
* **Service:** `docs-service`
* **Endpoint:**

  ```http
  GET /api/docs/:id/locations
  ```

  returns `{ origin:{lat,lon}, impact:{lat,lon} }`

---

## 9. Leaflet.js Map of Locality & Documents

* **Frontend:** use Leaflet, load base-tiles (e.g. OpenStreetMap).
* **Endpoint (reuse above):**

  * `GET /api/docs/:id/locations` for single doc
  * `GET /api/docs?bbox=…` to fetch multiple near a bounding box
* **Integration:** on map move/zoom, call `/api/docs?bbox=` to re-plot nearby doc markers.

---

## 10. Knowledge Graph Highlight of Connected Documents

* **Endpoint:**

  ```http
  GET /api/graph/subgraph?centerId=123&depth=1
  ```

  returns `{ nodes: […], edges: […] }` JSON.
* **Frontend:** feed into your graph-viz library (Cytoscape.js/Sigma.js) to render and highlight neighbors.

---

## 11. Document Viewer

* **Service:** `docs-service`
* **Endpoint:**

  ```http
  GET /api/docs/:id/content
  ```

  streams PDF or HTML from your proxy.
* **Frontend:**

  * PDFs → use PDF.js (or React-PDF, pdfvuer).
  * HTML → fetch via the same endpoint, sanitize, and `innerHTML` or render in a sandboxed `<iframe>` from your origin.

---

## 12a/12b/12c. On-Screen Keyboard & Terminal Behavior

* **Frontend logic:**

  * Detect viewport width or touch-capable devices → show on-screen keyboard component.
  * Detect physical keyboard events (`keydown`) → hide on-screen keyboard.
* **Integration:**

  * When on-screen keyboard active, route key events into the terminal pane’s WebSocket.
  * When a real keyboard is plugged in, listen for any `keydown` within 30 s of load → hide on-screen keyboard and show full terminal.

---

### General API Patterns

* **REST vs. GraphQL:**

  * Restful endpoints above are straightforward.
  * Consider GraphQL for one-call fetch of metadata + graph + events for a selected node.
* **Real-time updates:**

  * Use WebSockets (e.g. Socket.io) for live terminal I/O, metadata updates (uptime, network status), or push new events/correlations as they are computed.
* **Authentication & CORS:**

  * If fully public, no auth; otherwise JWT middleware on your Express routes.
  * Proxy all external PDF/HTML through your domain to avoid CORS/`X-Frame-Options`.

---

### Putting It All Together

1. **Node.js Monorepo** (or separate packages) for each service:

   ```
   /services
     /metadata-service
     /docs-service
     /files-service
     /correlation-service
     /actors-service
     /timeline-service
     /terminal-service
   /frontend
     /pwa-app (Svelte/Vue/React)
   ```
2. **Docker Compose** to bring up MySQL, Redis (for dedupe sets), and each Node service.
3. **API Gateway** (e.g. Kong, or simply NGINX/Express) routes `/api/*` to the correct service.
4. **CI/CD** spins up new containers, runs migrations, and deploys.

With this mapping, your frontend tabs and widgets each have a clear backend contract. As you build, document each endpoint in OpenAPI (Swagger) and share the TypeScript types with the PWA to keep everything in sync. Good luck!
