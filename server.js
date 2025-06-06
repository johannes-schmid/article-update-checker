const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const cors = require("cors");

const app = express();
const PORT = 3001;

app.use(cors());

const db = new sqlite3.Database("./articles.db");

// Get all articles with their update status
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

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});