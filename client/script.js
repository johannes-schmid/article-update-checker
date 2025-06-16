async function loadArticles() {
  const res = await fetch('/articles/with-suggestions');
  const articles = await res.json();
  const tbody = document.querySelector('#articles-table tbody');
  tbody.innerHTML = '';
  articles.forEach(article => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${article.title}</td><td>${article.suggestion_count}</td>`;
    tr.addEventListener('click', () => loadSuggestions(article));
    tbody.appendChild(tr);
  });
}

async function loadSuggestions(article) {
  const res = await fetch(`/articles/${article.id}/suggestions`);
  const suggestions = await res.json();
  const tbody = document.querySelector('#suggestions-table tbody');
  tbody.innerHTML = '';
  suggestions.forEach(s => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${s.suggestion}</td>`;
    tbody.appendChild(tr);
  });
  document.querySelector('#article-title').textContent = article.title;
  document.getElementById('suggestions-section').style.display = 'block';
}

loadArticles();
