const analyzeBtn = document.getElementById('analyze-btn');
const suggestBtn = document.getElementById('suggest-btn');
const inputEl = document.getElementById('task-input');
const resultsEl = document.getElementById('results');
const saveCheckbox = document.getElementById('save-checkbox');

const BACKEND_BASE_URL = window.BACKEND_BASE_URL || '';
const ANALYZE_URL = `${BACKEND_BASE_URL}/api/tasks/analyze/`;
const SUGGEST_URL = `${BACKEND_BASE_URL}/api/tasks/suggest/`;

function showError(message) {
  resultsEl.innerHTML = `<div class="card low"><div class="title">Error</div><div class="meta">${escapeHtml(message)}</div></div>`;
}

function escapeHtml(unsafe) {
    if (!unsafe && unsafe !== 0) return '';
    return String(unsafe)
         .replaceAll('&','&amp;')
         .replaceAll('<','&lt;')
         .replaceAll('>','&gt;')
         .replaceAll('"','&quot;')
         .replaceAll("'",'&#039;');
}

function renderTasks(tasks) {
  if (!Array.isArray(tasks) || tasks.length === 0) {
    resultsEl.innerHTML = `<div class="card low"><div class="title">No tasks found</div><div class="meta">Provide at least one task in JSON and click Analyze.</div></div>`;
    return;
  }
  resultsEl.innerHTML = '';
  tasks.forEach((t, idx) => {
    const score = Number(t.score || 0);
    let level = 'low';
    if (score >= 50) level = 'high';
    else if (score >= 15) level = 'medium';
    else level = 'low';

    const due = t.due_date ? `Due: ${escapeHtml(t.due_date)}` : 'No due date';
    const deps = (t.dependencies && t.dependencies.length) ? `Deps: ${escapeHtml(JSON.stringify(t.dependencies))}` : '';
    const importance = `Importance: ${escapeHtml(t.importance)}`;

    const card = document.createElement('div');
    card.className = `card ${level}`;
    card.innerHTML = `
      <div>
        <span class="title">${escapeHtml(t.title)}</span>
        <span class="score">${score}</span>
      </div>
      <div class="meta">${due} &nbsp; ${importance} &nbsp; ${deps}</div>
    `;
    resultsEl.appendChild(card);
  });
}

async function postAnalyze(tasks) {
  const payload = { tasks: tasks, save: saveCheckbox.checked };
  try {
    const resp = await fetch(ANALYZE_URL, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (!resp.ok) {
      showError(data.error || (data.details && data.details.join(', ')) || JSON.stringify(data));
      return;
    }
    renderTasks(data.tasks);
    } catch (err) {
    showError('Network error: ' + err.message + '. Make sure the Django server is running at http://127.0.0.1:8000');
  }
}

async function postSuggest(tasks) {
  const payload = { tasks: tasks };
  try {
    const resp = await fetch(SUGGEST_URL, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (!resp.ok) {
      showError(data.error || JSON.stringify(data));
      return;
    }
    // Show suggestions with explanation
    const combined = data.suggestions || [];
    resultsEl.innerHTML = `<div class="card"><div class="title">Top Suggestions</div><div class="meta">${escapeHtml(data.explanation || '')}</div></div>`;
    renderTasks(combined);
  } catch (err) {
    showError('Network error: ' + err.message + '. Make sure the Django server is running.');
  }
}

analyzeBtn.addEventListener('click', () => {
  let parsed;
  try {
    parsed = JSON.parse(inputEl.value);
  } catch (err) {
    showError('Invalid JSON input. Please provide a JSON array of task objects.');
    return;
  }
  if (!Array.isArray(parsed)) {
    showError('Input must be a JSON array of tasks.');
    return;
  }
  postAnalyze(parsed);
});

suggestBtn.addEventListener('click', () => {
  let parsed;
  try {
    parsed = JSON.parse(inputEl.value);
  } catch (err) {
    showError('Invalid JSON input. Please provide a JSON array of task objects.');
    return;
  }
  if (!Array.isArray(parsed)) {
    showError('Input must be a JSON array of tasks.');
    return;
  }
  postSuggest(parsed);
});
