/* ─────────────────────────────────────────────────────────────────────────────
   DrugLaw Search Engine — Frontend JavaScript
   ─────────────────────────────────────────────────────────────────────────── */

const API_BASE = window.location.origin;

// ── State ────────────────────────────────────────────────────────────────────
const state = {
  query: '',
  mode: 'hybrid',
  topK: 7,
  useRerank: true,
  loading: false,
  lastQuery: '',
};

// ── DOM Refs ─────────────────────────────────────────────────────────────────
const $searchInput  = document.getElementById('search-input');
const $searchBtn    = document.getElementById('search-btn');
const $resultsList  = document.getElementById('results-list');
const $emptyState   = document.getElementById('empty-state');
const $loadingState = document.getElementById('loading-state');
const $errorState   = document.getElementById('error-state');
const $errorMsg     = document.getElementById('error-message');
const $statsbar     = document.getElementById('statsbar');
const $topKSlider   = document.getElementById('top-k-slider');
const $topKValue    = document.getElementById('top-k-value');
const $rerankToggle = document.getElementById('rerank-toggle');
const $retryBtn     = document.getElementById('retry-btn');
const $sidebar      = document.getElementById('sidebar');
const $sidebarToggle= document.getElementById('sidebar-toggle');
const $main         = document.querySelector('.main');
const $modeOptions  = document.querySelectorAll('.mode-option');
const $suggestions  = document.querySelectorAll('.suggestion-pill');
const cardTemplate  = document.getElementById('card-template');

// ── Sidebar Toggle ────────────────────────────────────────────────────────────
$sidebarToggle.addEventListener('click', () => {
  const isCollapsed = $sidebar.classList.toggle('collapsed');
  $main.classList.toggle('sidebar-hidden', isCollapsed);
});

// Mobile: click outside sidebar to close
document.addEventListener('click', (e) => {
  if (window.innerWidth <= 768 &&
      $sidebar.classList.contains('open') &&
      !$sidebar.contains(e.target) &&
      e.target !== $sidebarToggle) {
    $sidebar.classList.remove('open');
  }
});

// ── Mode Radio ────────────────────────────────────────────────────────────────
$modeOptions.forEach(opt => {
  opt.addEventListener('click', () => {
    $modeOptions.forEach(o => o.classList.remove('active'));
    opt.classList.add('active');
    const radio = opt.querySelector('input[type=radio]');
    radio.checked = true;
    state.mode = radio.value;
  });
});

// ── Top-K Slider ──────────────────────────────────────────────────────────────
function updateSliderTrack(slider) {
  const pct = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
  slider.style.background = `linear-gradient(to right, var(--accent) 0%, var(--accent) ${pct}%, var(--bg-elevated) ${pct}%)`;
}

$topKSlider.addEventListener('input', () => {
  state.topK = parseInt($topKSlider.value);
  $topKValue.textContent = state.topK;
  updateSliderTrack($topKSlider);
});
updateSliderTrack($topKSlider);

// ── Rerank Toggle ─────────────────────────────────────────────────────────────
$rerankToggle.addEventListener('change', () => {
  state.useRerank = $rerankToggle.checked;
});

// ── Suggestion Pills ──────────────────────────────────────────────────────────
$suggestions.forEach(pill => {
  pill.addEventListener('click', () => {
    const q = pill.dataset.q;
    $searchInput.value = q;
    state.query = q;
    runSearch(q);
  });
});

// ── Search Input ──────────────────────────────────────────────────────────────
$searchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && $searchInput.value.trim()) {
    runSearch($searchInput.value.trim());
  }
});
$searchBtn.addEventListener('click', () => {
  if ($searchInput.value.trim()) {
    runSearch($searchInput.value.trim());
  }
});

// ── Retry ─────────────────────────────────────────────────────────────────────
$retryBtn.addEventListener('click', () => {
  if (state.lastQuery) runSearch(state.lastQuery);
});

// ── Show / Hide States ─────────────────────────────────────────────────────────
function showState(which) {
  $emptyState.hidden   = which !== 'empty';
  $loadingState.hidden = which !== 'loading';
  $errorState.hidden   = which !== 'error';
  $resultsList.hidden  = which !== 'results';
  $statsbar.hidden     = which !== 'results';
}
showState('empty');

// ── Score Helpers ─────────────────────────────────────────────────────────────
function normalizeScore(score) {
  // Cross-encoder scores can be > 1 or negative; clamp for display
  return Math.min(1, Math.max(0, score));
}

function scoreColor(score) {
  const s = normalizeScore(score);
  if (s >= 0.6) return { stroke: '#10b981', text: '#34d399' };
  if (s >= 0.3) return { stroke: '#f59e0b', text: '#fbbf24' };
  return           { stroke: '#ef4444', text: '#f87171' };
}

// ── Badge Helpers ─────────────────────────────────────────────────────────────
const DOC_TYPE_LABELS = {
  legal:     ['⚖️ Pháp luật', 'badge-legal'],
  news:      ['📰 Tin tức',   'badge-news'],
  pageindex: ['🌐 PageIndex', 'badge-pageindex'],
};
const RETRIEVAL_LABELS = {
  hybrid:   ['🔀 Hybrid',   'badge-hybrid'],
  semantic: ['🧠 Semantic', 'badge-semantic'],
  lexical:  ['🔤 BM25',     'badge-lexical'],
  pageindex:['🌐 PageIndex','badge-pageindex'],
};

// ── Render One Card ───────────────────────────────────────────────────────────
function renderCard(result, delay = 0) {
  const clone = cardTemplate.content.cloneNode(true);
  const card  = clone.querySelector('.result-card');

  // Doc type class on card
  card.classList.add(result.doc_type || 'unknown');

  // Animate with stagger
  card.style.animationDelay = `${delay}ms`;

  // Type Badge
  const [typeLabel, typeCls] = DOC_TYPE_LABELS[result.doc_type] || ['❓ Unknown', 'badge-unknown'];
  const typeBadge = card.querySelector('.badge-type');
  typeBadge.textContent = typeLabel;
  typeBadge.classList.add(typeCls);

  // Retrieval Source Badge
  const [retLabel, retCls] = RETRIEVAL_LABELS[result.retrieval_source] || ['Hybrid', 'badge-hybrid'];
  const retBadge = card.querySelector('.badge-source-type');
  retBadge.textContent = retLabel;
  retBadge.classList.add(retCls);

  // Score Ring
  const norm = normalizeScore(result.score);
  const { stroke, text } = scoreColor(result.score);
  const circumference = 94.2;
  const offset = circumference - norm * circumference;
  const fill = card.querySelector('.score-fill');
  fill.style.strokeDashoffset = offset;
  fill.style.stroke = stroke;
  const scoreText = card.querySelector('.score-text');
  scoreText.textContent = norm.toFixed(2);
  scoreText.style.color = text;

  // Source
  const srcName  = card.querySelector('.source-name');
  const srcChunk = card.querySelector('.source-chunk');
  srcName.textContent  = result.source || 'Không rõ';
  srcChunk.textContent = `· Chunk #${result.chunk_index}`;

  // Content preview
  const preview = result.content.length > 380
    ? result.content.slice(0, 380) + '…'
    : result.content;
  card.querySelector('.card-content').textContent = preview;

  // Rank badge
  card.querySelector('.rank-badge').textContent = `#${result.rank}`;

  // Expanded content
  card.querySelector('.expanded-content').textContent = result.content;
  card.querySelector('.score-val').textContent  = result.score.toFixed(4);
  card.querySelector('.type-val').textContent   = result.doc_type;
  card.querySelector('.source-val').textContent = result.source;
  card.querySelector('.chunk-val').textContent  = result.chunk_index;
  card.querySelector('.method-val').textContent = result.retrieval_source;

  // Expand toggle
  const expandBtn  = card.querySelector('.expand-btn');
  const expandedEl = card.querySelector('.card-expanded');
  expandBtn.addEventListener('click', () => {
    const open = expandedEl.hidden;
    expandedEl.hidden = !open;
    expandBtn.textContent = open ? 'Thu gọn ↑' : 'Xem đầy đủ ↓';
    expandBtn.classList.toggle('expanded', open);
  });

  return card;
}

// ── Run Search ────────────────────────────────────────────────────────────────
async function runSearch(query) {
  if (state.loading) return;
  state.loading  = true;
  state.lastQuery = query;

  showState('loading');
  $searchBtn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        mode:       state.mode,
        top_k:      state.topK,
        use_rerank: state.useRerank,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    renderResults(data);

  } catch (err) {
    $errorMsg.textContent = err.message;
    showState('error');
  } finally {
    state.loading  = false;
    $searchBtn.disabled = false;
  }
}

// ── Render Results ─────────────────────────────────────────────────────────────
function renderResults(data) {
  $resultsList.innerHTML = '';

  if (!data.results || data.results.length === 0) {
    showState('empty');
    return;
  }

  // Stats bar
  const nLegal = data.results.filter(r => r.doc_type === 'legal').length;
  const nNews  = data.results.filter(r => r.doc_type === 'news').length;
  const modeLabel = { hybrid: '🔀 Hybrid', semantic: '🧠 Semantic', lexical: '🔤 BM25' }[data.mode] || data.mode;
  const reranked  = data.reranked ? ' + 🎯 Reranked' : '';

  document.getElementById('stat-query').innerHTML = `🔎 <strong>"${data.query}"</strong>`;
  document.getElementById('stat-count').innerHTML = `📊 <strong>${data.total}</strong> kết quả`;
  document.getElementById('stat-time').innerHTML  = `⏱ <strong>${data.elapsed_ms.toFixed(0)}ms</strong>`;
  document.getElementById('stat-mode').innerHTML  = `${modeLabel}${reranked}`;

  // Render cards with stagger
  data.results.forEach((result, i) => {
    const card = renderCard(result, i * 60);
    $resultsList.appendChild(card);
  });

  showState('results');
}

// ── Keyboard Shortcut (/) to focus search ─────────────────────────────────────
document.addEventListener('keydown', (e) => {
  if (e.key === '/' && document.activeElement !== $searchInput) {
    e.preventDefault();
    $searchInput.focus();
  }
  if (e.key === 'Escape') {
    $searchInput.blur();
  }
});
