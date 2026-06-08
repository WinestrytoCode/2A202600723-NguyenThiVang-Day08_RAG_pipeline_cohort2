"""
Search Engine — Group Project (Option A)
Giao diện web tìm kiếm hybrid cho thông tin pháp luật và báo chí về ma tuý.
Chạy: streamlit run group_project/search_app.py
"""

import sys
import time
from pathlib import Path

# Thêm project root vào sys.path để import src.*
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DrugLaw Search Engine",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & Base ─────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Background ───────────────────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #12162a 50%, #0d1117 100%);
    min-height: 100vh;
}

/* ── Hide Streamlit default header ───────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

/* ── Hero Header ─────────────────────────────────────────── */
.hero-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    background: linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(16,185,129,0.08) 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1 0%, #10b981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    color: rgba(255,255,255,0.55);
    font-size: 1rem;
    margin: 0;
    font-weight: 400;
}

/* ── Search Box ──────────────────────────────────────────── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(99,102,241,0.35) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-size: 1.05rem !important;
    padding: 0.75rem 1.1rem !important;
    transition: all 0.25s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
}
.stTextInput > div > div > input::placeholder {
    color: rgba(255,255,255,0.3) !important;
}

/* ── Button ──────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.8rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%) !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Stats Bar ────────────────────────────────────────────── */
.stats-bar {
    display: flex;
    gap: 1.2rem;
    padding: 0.75rem 1.2rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    margin-bottom: 1.2rem;
    flex-wrap: wrap;
}
.stat-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: rgba(255,255,255,0.6);
    font-size: 0.82rem;
    font-weight: 500;
}
.stat-value {
    color: #a5b4fc;
    font-weight: 600;
}

/* ── Result Card ──────────────────────────────────────────── */
.result-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}
.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 14px 0 0 14px;
}
.result-card.legal::before { background: linear-gradient(180deg, #10b981, #059669); }
.result-card.news::before  { background: linear-gradient(180deg, #f59e0b, #d97706); }
.result-card.pageindex::before { background: linear-gradient(180deg, #8b5cf6, #7c3aed); }
.result-card:hover {
    border-color: rgba(99,102,241,0.3);
    background: rgba(255,255,255,0.06);
    transform: translateY(-1px);
}

/* ── Card Header ──────────────────────────────────────────── */
.card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.8rem;
    margin-bottom: 0.7rem;
}
.card-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}

/* ── Badges / Chips ──────────────────────────────────────── */
.chip {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
.chip-legal   { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
.chip-news    { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.chip-pageindex { background: rgba(139,92,246,0.15); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.3); }
.chip-hybrid  { background: rgba(99,102,241,0.15); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.3); }

/* ── Score Badge ──────────────────────────────────────────── */
.score-badge {
    min-width: 52px;
    text-align: center;
    padding: 0.3rem 0.65rem;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 700;
    white-space: nowrap;
    flex-shrink: 0;
}
.score-high   { background: rgba(16,185,129,0.18); color: #34d399; border: 1px solid rgba(16,185,129,0.35); }
.score-medium { background: rgba(245,158,11,0.18); color: #fbbf24; border: 1px solid rgba(245,158,11,0.35); }
.score-low    { background: rgba(239,68,68,0.18);  color: #f87171; border: 1px solid rgba(239,68,68,0.35); }

/* ── Source Label ──────────────────────────────────────────── */
.source-label {
    color: rgba(255,255,255,0.5);
    font-size: 0.78rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}
.source-name {
    color: rgba(165,180,252,0.85);
    font-weight: 500;
}

/* ── Content Preview ──────────────────────────────────────── */
.content-text {
    color: rgba(255,255,255,0.75);
    font-size: 0.9rem;
    line-height: 1.65;
    margin: 0;
}
.content-rank {
    position: absolute;
    top: 1.1rem;
    right: 1.3rem;
    color: rgba(255,255,255,0.15);
    font-size: 1.4rem;
    font-weight: 700;
}

/* ── Sidebar ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: rgba(15,15,26,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem !important;
}

/* ── Sidebar Header ─────────────────────────────────────────  */
.sidebar-logo {
    font-size: 1.6rem;
    font-weight: 700;
    color: #a5b4fc;
    margin-bottom: 0.3rem;
}
.sidebar-tagline {
    color: rgba(255,255,255,0.4);
    font-size: 0.78rem;
    margin-bottom: 1.5rem;
}
.sidebar-section-title {
    color: rgba(255,255,255,0.35);
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.6rem;
    margin-top: 1.2rem;
}

/* ── Divider ──────────────────────────────────────────────── */
.custom-divider {
    border: none;
    height: 1px;
    background: rgba(255,255,255,0.07);
    margin: 1.2rem 0;
}

/* ── Empty State ──────────────────────────────────────────── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: rgba(255,255,255,0.3);
}
.empty-icon { font-size: 3.5rem; margin-bottom: 1rem; }
.empty-text { font-size: 1rem; }

/* ── Streamlit radio / selectbox / slider ────────────────── */
.stRadio > div { gap: 0.4rem !important; }
.stRadio label { color: rgba(255,255,255,0.75) !important; font-size: 0.88rem !important; }
.stSelectbox label, .stSlider label, .stCheckbox label {
    color: rgba(255,255,255,0.7) !important;
    font-size: 0.88rem !important;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# LAZY-LOAD BACKEND (cache model loading)
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_retrievers():
    """Load và cache CORPUS + BM25 index (chạy 1 lần)."""
    from src.task5_semantic_search import semantic_search
    from src.task6_lexical_search import lexical_search, build_bm25_index, CORPUS
    from src.task7_reranking import rerank, rerank_rrf
    return semantic_search, lexical_search, build_bm25_index, CORPUS, rerank, rerank_rrf


def do_search(query: str, search_mode: str, top_k: int, use_rerank: bool) -> tuple[list[dict], float]:
    """Thực hiện tìm kiếm và trả về (results, elapsed_time)."""
    semantic_search, lexical_search, build_bm25_index, CORPUS, rerank, rerank_rrf = load_retrievers()

    start = time.perf_counter()

    if search_mode == "🔮 Hybrid (Khuyến nghị)":
        dense = semantic_search(query, top_k=top_k * 2)
        sparse = lexical_search(query, top_k=top_k * 2)
        results = rerank_rrf([dense, sparse], top_k=top_k * 2)
        for r in results:
            r["retrieval_source"] = "hybrid"
    elif search_mode == "🧠 Semantic (Dense)":
        results = semantic_search(query, top_k=top_k)
        for r in results:
            r["retrieval_source"] = "semantic"
    else:  # Lexical BM25
        results = lexical_search(query, top_k=top_k)
        for r in results:
            r["retrieval_source"] = "lexical"

    if use_rerank and results:
        try:
            results = rerank(query, results, top_k=top_k, method="cross_encoder")
        except Exception:
            results = results[:top_k]
    else:
        results = results[:top_k]

    elapsed = time.perf_counter() - start
    return results, elapsed


# ──────────────────────────────────────────────────────────────────────────────
# HELPER RENDERERS
# ──────────────────────────────────────────────────────────────────────────────

def score_class(score: float) -> str:
    if score >= 0.6:   return "score-high"
    if score >= 0.25:  return "score-medium"
    return "score-low"


def format_score(score: float) -> str:
    # Cross-encoder logit có thể > 1 hoặc âm — normalize to 0-1 display
    display = max(0.0, min(score, 1.0)) if score <= 1.0 else 1.0
    return f"{display:.3f}"


def doc_type_chip(doc_type: str) -> str:
    if doc_type == "legal":
        return '<span class="chip chip-legal">⚖️ Pháp luật</span>'
    elif doc_type == "news":
        return '<span class="chip chip-news">📰 Tin tức</span>'
    return '<span class="chip chip-pageindex">🔍 PageIndex</span>'


def retrieval_chip(source: str) -> str:
    label_map = {
        "hybrid": ("chip-hybrid",  "🔀 Hybrid"),
        "semantic": ("chip-hybrid", "🧠 Semantic"),
        "lexical": ("chip-legal",  "🔤 BM25"),
        "pageindex": ("chip-pageindex", "🌐 PageIndex"),
    }
    cls, label = label_map.get(source, ("chip-hybrid", source))
    return f'<span class="chip {cls}">{label}</span>'


def render_result_card(result: dict, rank: int):
    metadata = result.get("metadata", {})
    content  = result.get("content", "")
    score    = result.get("score", 0.0)
    doc_type = metadata.get("type", "unknown")
    source   = metadata.get("source", "Không rõ nguồn")
    ret_src  = result.get("retrieval_source", "hybrid")
    chunk_idx = metadata.get("chunk_index", "?")

    card_cls  = doc_type if doc_type in ("legal", "news") else "pageindex"
    sc_cls    = score_class(score)
    preview   = content[:360] + ("…" if len(content) > 360 else "")

    st.markdown(f"""
    <div class="result-card {card_cls}">
        <span class="content-rank">#{rank}</span>
        <div class="card-header">
            <div class="card-meta">
                {doc_type_chip(doc_type)}
                {retrieval_chip(ret_src)}
            </div>
            <div class="score-badge {sc_cls}">{format_score(score)}</div>
        </div>
        <div class="source-label">
            📄 <span class="source-name">{source}</span>
            &nbsp;·&nbsp; Chunk #{chunk_idx}
        </div>
        <p class="content-text">{preview}</p>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚖️ DrugLaw</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Search Engine · Pháp luật & Tin tức Ma tuý</div>', unsafe_allow_html=True)
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">🔍 Phương thức tìm kiếm</div>', unsafe_allow_html=True)
    search_mode = st.radio(
        "Chế độ",
        ["🔮 Hybrid (Khuyến nghị)", "🧠 Semantic (Dense)", "🔤 Lexical (BM25)"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-section-title">⚙️ Cấu hình</div>', unsafe_allow_html=True)
    top_k = st.slider("Số kết quả (top_k)", min_value=3, max_value=20, value=7, step=1)
    use_rerank = st.checkbox("🎯 Bật Reranking (Cross-Encoder)", value=True)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">💡 Gợi ý truy vấn</div>', unsafe_allow_html=True)

    suggestions = [
        "Hình phạt tàng trữ ma tuý",
        "Chi Dân bị bắt ma tuý",
        "Nghị định 105/2021 điều 12",
        "Cai nghiện bắt buộc",
        "An Tây người mẫu khởi tố",
        "Điều 248 Bộ luật Hình sự",
    ]
    for s in suggestions:
        if st.button(s, key=f"suggest_{s}"):
            st.session_state["search_query"] = s
            st.rerun()

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div style="color:rgba(255,255,255,0.25);font-size:0.73rem;line-height:1.6;">
    <b>Pipeline:</b><br>
    Task 5 · Semantic (ChromaDB)<br>
    Task 6 · Lexical (BM25 Okapi)<br>
    Task 7 · Rerank (CrossEncoder)<br>
    Task 9 · RRF Fusion
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-header">
    <h1 class="hero-title">⚖️ DrugLaw Search Engine</h1>
    <p class="hero-subtitle">Tìm kiếm thông tin pháp luật và báo chí về ma tuý · Hỗ trợ Hybrid Search + AI Reranking</p>
</div>
""", unsafe_allow_html=True)

# Search Input
col_input, col_btn = st.columns([5, 1])
with col_input:
    default_q = st.session_state.get("search_query", "")
    query = st.text_input(
        "Nhập câu truy vấn",
        value=default_q,
        placeholder="VD: Hình phạt cho tội tàng trữ trái phép chất ma tuý ...",
        label_visibility="collapsed",
        key="main_search_input",
    )

with col_btn:
    search_clicked = st.button("🔍 Tìm kiếm", type="primary")

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# SEARCH EXECUTION
# ──────────────────────────────────────────────────────────────────────────────

if search_clicked and query.strip():
    st.session_state["search_query"] = query
    st.session_state["last_results"] = None  # clear cache

    with st.spinner("🔄 Đang tải model và tìm kiếm..."):
        try:
            results, elapsed = do_search(query.strip(), search_mode, top_k, use_rerank)
            st.session_state["last_results"] = results
            st.session_state["last_elapsed"] = elapsed
            st.session_state["last_query"]   = query.strip()
            st.session_state["last_mode"]    = search_mode
        except Exception as e:
            st.error(f"❌ Lỗi khi tìm kiếm: {e}")
            st.stop()


# ──────────────────────────────────────────────────────────────────────────────
# RESULTS DISPLAY
# ──────────────────────────────────────────────────────────────────────────────

results   = st.session_state.get("last_results")
last_q    = st.session_state.get("last_query", "")
elapsed   = st.session_state.get("last_elapsed", 0)
last_mode = st.session_state.get("last_mode", "")

if results is not None:
    if not results:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <p class="empty-text">Không tìm thấy kết quả nào phù hợp.<br>Hãy thử từ khóa khác!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Stats bar
        n_legal = sum(1 for r in results if r.get("metadata", {}).get("type") == "legal")
        n_news  = sum(1 for r in results if r.get("metadata", {}).get("type") == "news")
        rerank_tag = " · 🎯 Reranked" if use_rerank else ""
        mode_short = last_mode.split("(")[0].strip()

        st.markdown(f"""
        <div class="stats-bar">
            <div class="stat-item">🔎 Truy vấn: <span class="stat-value">"{last_q}"</span></div>
            <div class="stat-item">📊 Kết quả: <span class="stat-value">{len(results)}</span></div>
            <div class="stat-item">⚖️ Pháp luật: <span class="stat-value">{n_legal}</span></div>
            <div class="stat-item">📰 Tin tức: <span class="stat-value">{n_news}</span></div>
            <div class="stat-item">⏱ Thời gian: <span class="stat-value">{elapsed:.2f}s</span></div>
            <div class="stat-item">🔀 Mode: <span class="stat-value">{mode_short}{rerank_tag}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # Result cards
        for i, result in enumerate(results, 1):
            render_result_card(result, i)

            # Expandable full content
            with st.expander(f"📖 Xem toàn bộ nội dung #{i}", expanded=False):
                st.markdown(f"""
                <div style="color:rgba(255,255,255,0.8);font-size:0.9rem;
                            line-height:1.7;padding:0.5rem 0;">
                    {result.get('content', '')}
                </div>
                """, unsafe_allow_html=True)
                meta = result.get("metadata", {})
                col1, col2, col3 = st.columns(3)
                col1.metric("Score",     format_score(result.get("score", 0)))
                col2.metric("Loại",      meta.get("type", "?").capitalize())
                col3.metric("Nguồn",     meta.get("source", "?")[:25])

else:
    # Welcome / empty state
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">⚖️</div>
        <p class="empty-text">
            Nhập câu truy vấn và nhấn <b>Tìm kiếm</b> để bắt đầu.<br>
            <span style="font-size:0.85rem;color:rgba(255,255,255,0.2);">
                Hỗ trợ tìm kiếm lai: Semantic + BM25 + AI Reranking
            </span>
        </p>
    </div>
    """, unsafe_allow_html=True)
