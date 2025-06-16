const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const cors = require("cors");
const path = require("path");

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.static(path.join(__dirname, "client")));

const db = new sqlite3.Database("./articles.db");
const reviewDb = new sqlite3.Database("./article_reviews.db");

// Get raw articles
app.get("/articles", (req, res) => {
  const query = `SELECT id, title, content FROM articles`;
  db.all(query, [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    const safeRows = rows.map(row => ({
      ...row,
      title: String(row.title)
    }));
    res.json(safeRows);
  });
});

// Get articles with suggestion counts
app.get("/articles/with-suggestions", (req, res) => {
  const query = `SELECT a.id, a.title, COUNT(r.id) as suggestion_count
                 FROM articles a
                 LEFT JOIN article_reviews r ON a.id = r.article_id
                 GROUP BY a.id`;
  db.all(query, [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

// Get suggestions for a specific article
app.get("/articles/:id/suggestions", (req, res) => {
  const query = `SELECT suggestion FROM article_reviews WHERE article_id = ?`;
  reviewDb.all(query, [req.params.id], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
