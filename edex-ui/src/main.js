// Web-based version of eDEX-UI
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const port = process.env.PORT || 3000;

// MIME types for serving different file types
const mimeTypes = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.wav': 'audio/wav',
  '.mp3': 'audio/mpeg',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.eot': 'application/vnd.ms-fontobject',
  '.otf': 'font/otf'
};

// Create a simple HTTP server
const server = http.createServer((req, res) => {
  console.log(`Request: ${req.url}`);
  
  // Parse the URL and get the pathname
  const parsedUrl = url.parse(req.url);
  let pathname = parsedUrl.pathname;
  
  // If the path is '/', serve the Svelte UI
  if (pathname === '/') {
    pathname = '/ui_svelte.html';
  }
  
  // Get the file path
  const filePath = path.join(__dirname, pathname);
  
  // Get the file extension
  const extname = path.extname(filePath);
  
  // Default content type
  let contentType = mimeTypes[extname] || 'application/octet-stream';
  
  // Read the file
  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        // Page not found
        fs.readFile(path.join(__dirname, '404.html'), (err, content) => {
          res.writeHead(404, { 'Content-Type': 'text/html' });
          res.end(content, 'utf-8');
        });
      } else {
        // Server error
        res.writeHead(500);
        res.end(`Server Error: ${err.code}`);
      }
    } else {
      // Success - return the content
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

// Start the server
server.listen(port, () => {
  console.log(`eDEX-UI is running on http://localhost:${port}`);
  console.log('Press Ctrl+C to quit');
});

// Create a 404 page if it doesn't exist
const notFoundPath = path.join(__dirname, '404.html');
if (!fs.existsSync(notFoundPath)) {
  const notFoundContent = `
<!DOCTYPE html>
<html>
<head>
  <title>404 - Not Found</title>
  <style>
    body {
      background-color: #000;
      color: #0f0;
      font-family: monospace;
      text-align: center;
      padding-top: 50px;
    }
    h1 {
      font-size: 36px;
    }
  </style>
</head>
<body>
  <h1>404 - File Not Found</h1>
  <p>The resource you are looking for does not exist.</p>
  <a href="/">Return Home</a>
</body>
</html>
  `;
  fs.writeFileSync(notFoundPath, notFoundContent);
} 