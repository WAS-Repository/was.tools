-- Enable full-text search
ALTER TABLE documents 
ADD FULLTEXT INDEX `ft_search` (title, content);

-- Sample document table
CREATE TABLE IF NOT EXISTS documents (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  content TEXT,
  type ENUM('document', 'permit', 'project') DEFAULT 'document',
  location JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tags for advanced filtering
CREATE TABLE IF NOT EXISTS tags (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tag VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS document_tags (
  document_id INT,
  tag_id INT,
  PRIMARY KEY (document_id, tag_id),
  FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);