import streamlit as st
import time
from dotenv import load_dotenv

# ─── MUST be first Streamlit call ────────────────────────────────────────────
st.set_page_config(
    page_title="VideoMind",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

# ─── deferred imports (after set_page_config) ────────────────────────────────
from utils.audio_processor import process_input
from core.transcriber    import transcribe_all
from core.summarize      import summarize, generate_title
from core.extractor      import extract_action_items, extract_decisions, extract_questions
from core.rag_engine     import build_rag_chain, ask_question


# ══════════════════════════════════════════════════════════════════════════════
# DESIGN TOKENS & GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── tokens ── */
:root {
  --bg:        #0E1117;
  --surface:   #161B25;
  --card:      #1C2333;
  --border:    #252D3D;
  --amber:     #F59E0B;
  --amber-dim: rgba(245,158,11,0.12);
  --amber-glow:rgba(245,158,11,0.30);
  --teal:      #2DD4BF;
  --red:       #F87171;
  --green:     #4ADE80;
  --txt1:      #E2E8F0;
  --txt2:      #8892A4;
  --txt3:      #4A5568;
  --syne:      'Syne', sans-serif;
  --inter:     'Inter', sans-serif;
  --mono:      'JetBrains Mono', monospace;
  --r:         10px;
}

html, body, [class*="css"] { font-family: var(--inter); color: var(--txt1); }
.stApp            { background: var(--bg); }
#MainMenu, footer, header { visibility: hidden; }

/* ── sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--txt1) !important; }

/* ── HERO ── */
.hero { padding: 36px 0 8px; }
.hero-eyebrow {
  font-family: var(--mono);
  font-size: 0.72rem; letter-spacing: 0.18em;
  color: var(--amber); text-transform: uppercase; margin-bottom: 8px;
}
.hero-title {
  font-family: var(--syne);
  font-size: 2.6rem; font-weight: 800; line-height: 1.1;
  color: var(--txt1); margin: 0 0 10px;
}
.hero-title span { color: var(--amber); }
.hero-sub { font-size: 0.92rem; color: var(--txt2); line-height: 1.6; }

/* ── PIPELINE RAIL (signature element) ── */
.rail { display: flex; align-items: flex-start; gap: 0; margin: 28px 0 4px; }
.rail-step { display: flex; flex-direction: column; align-items: center; flex: 1; }
.rail-dot {
  width: 28px; height: 28px; border-radius: 50%;
  border: 2px solid var(--border);
  background: var(--surface);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 600; color: var(--txt3);
  position: relative; z-index: 1; transition: all 0.3s;
}
.rail-dot.done  { border-color: var(--green);  background: rgba(74,222,128,0.12); color: var(--green); }
.rail-dot.active{ border-color: var(--amber);  background: var(--amber-dim);       color: var(--amber);
                  box-shadow: 0 0 12px var(--amber-glow);
                  animation: pulse-dot 1.2s ease-in-out infinite; }
.rail-dot.idle  { border-color: var(--border); }
@keyframes pulse-dot {
  0%,100% { box-shadow: 0 0 8px  var(--amber-glow); }
  50%      { box-shadow: 0 0 20px var(--amber-glow); }
}
.rail-label {
  font-size: 0.68rem; color: var(--txt3); margin-top: 6px;
  text-align: center; font-family: var(--mono); letter-spacing: 0.06em;
}
.rail-label.done   { color: var(--green); }
.rail-label.active { color: var(--amber); }
.rail-connector {
  flex: 1; height: 2px; background: var(--border);
  margin-top: 14px; transition: background 0.4s;
}
.rail-connector.done { background: var(--green); }

/* ── CARDS ── */
.vm-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r); padding: 20px 22px; margin-bottom: 14px;
}
.vm-card-label {
  font-family: var(--mono); font-size: 0.65rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--txt3); margin-bottom: 6px;
}
.vm-card-value { font-size: 1.15rem; font-weight: 600; color: var(--txt1); }

/* ── PILL LIST ── */
.pill-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.pill {
  background: var(--amber-dim); border: 1px solid rgba(245,158,11,0.25);
  border-radius: 20px; padding: 6px 14px;
  font-size: 0.82rem; color: var(--txt1); line-height: 1.4;
}

/* ── TRANSCRIPT ── */
.tx-box {
  font-family: var(--mono); font-size: 0.78rem; line-height: 1.8;
  color: var(--txt2); background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--r);
  padding: 18px 20px; max-height: 320px; overflow-y: auto;
  white-space: pre-wrap; word-break: break-word;
}

/* ── CHAT ── */
.chat-wrap { display: flex; flex-direction: column; gap: 12px; margin: 4px 0 16px; }
.msg-user  { display: flex; justify-content: flex-end; }
.msg-ai    { display: flex; justify-content: flex-start; align-items: flex-start; gap: 10px; }
.bubble-user {
  background: var(--amber); color: #0E1117;
  border-radius: 16px 16px 4px 16px;
  padding: 10px 16px; max-width: 74%;
  font-size: 0.875rem; line-height: 1.55; font-weight: 500;
}
.ai-avatar {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, var(--amber), #D97706);
  display: flex; align-items: center; justify-content: center; font-size: 0.95rem;
}
.bubble-ai {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 4px 16px 16px 16px;
  padding: 10px 16px; max-width: 78%;
  font-size: 0.875rem; line-height: 1.6; color: var(--txt1);
}
.chat-empty {
  text-align: center; padding: 32px 0;
  font-size: 0.85rem; color: var(--txt3); font-family: var(--mono);
}

/* ── SECTION DIVIDER ── */
.sec-div {
  display: flex; align-items: center; gap: 12px;
  margin: 0 0 16px;
}
.sec-div-icon { font-size: 1rem; }
.sec-div-title {
  font-family: var(--syne); font-size: 0.95rem; font-weight: 700;
  color: var(--txt1); margin: 0;
}
.sec-div-line { flex: 1; height: 1px; background: var(--border); }

/* ── WIDGET OVERRIDES ── */
.stTextInput input, .stSelectbox select {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  color: var(--txt1) !important; border-radius: 8px !important;
}
.stTextInput input:focus {
  border-color: var(--amber) !important;
  box-shadow: 0 0 0 2px var(--amber-dim) !important;
}
div[data-testid="stButton"] > button {
  background: var(--amber) !important; color: #0E1117 !important;
  border: none !important; border-radius: 8px !important;
  font-weight: 700 !important; font-family: var(--inter) !important;
  padding: 0.5rem 1.4rem !important; letter-spacing: 0.01em;
  transition: opacity 0.15s;
}
div[data-testid="stButton"] > button:hover { opacity: 0.85; }
.stDownloadButton button {
  background: var(--surface) !important; color: var(--amber) !important;
  border: 1px solid var(--border) !important; border-radius: 8px !important;
}

/* tabs */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important; gap: 2px;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important; color: var(--txt2) !important;
  font-size: 0.84rem !important; font-weight: 500 !important;
  padding: 8px 18px !important; border-radius: 6px 6px 0 0 !important;
}
.stTabs [aria-selected="true"] {
  background: var(--card) !important; color: var(--amber) !important;
  border-bottom: 2px solid var(--amber) !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--txt3); }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
STAGES = [
    ("audio",      "AUDIO"),
    ("transcribe", "TRANSCRIPT"),
    ("analyse",    "ANALYSIS"),
    ("rag",        "RAG INDEX"),
]

def render_rail(current: str):
    order = [s[0] for s in STAGES]
    cur_i = order.index(current) if current in order else -1

    html = '<div class="rail">'
    for i, (sid, label) in enumerate(STAGES):
        if i < cur_i:
            dot_cls = lbl_cls = "done"
            icon = "✓"
        elif i == cur_i:
            dot_cls = lbl_cls = "active"
            icon = str(i + 1)
        else:
            dot_cls = lbl_cls = "idle"
            icon = str(i + 1)

        conn_cls = "done" if i < cur_i else ""
        html += f'<div class="rail-step"><div class="rail-dot {dot_cls}">{icon}</div><div class="rail-label {lbl_cls}">{label}</div></div>'
        if i < len(STAGES) - 1:
            html += f'<div class="rail-connector {conn_cls}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def sec_header(icon: str, title: str):
    st.markdown(
        f'<div class="sec-div">'
        f'<span class="sec-div-icon">{icon}</span>'
        f'<p class="sec-div-title">{title}</p>'
        f'<div class="sec-div-line"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def pill_list(text: str):
    lines = [l.strip().lstrip("-•*0123456789.) ") for l in text.strip().splitlines() if l.strip()]
    if not lines:
        st.markdown('<p style="color:var(--txt3);font-size:0.85rem;">Nothing detected.</p>', unsafe_allow_html=True)
        return
    pills = "".join(f'<div class="pill">{l}</div>' for l in lines)
    st.markdown(f'<div class="pill-grid">{pills}</div>', unsafe_allow_html=True)


def chat_msg(role: str, content: str):
    if role == "user":
        st.markdown(f'<div class="msg-user"><div class="bubble-user">{content}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="msg-ai">'
            f'<div class="ai-avatar">🤖</div>'
            f'<div class="bubble-ai">{content}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, default in [("result", None), ("history", []), ("stage", "idle")]:
    if k not in st.session_state:
        st.session_state[k] = default


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<p style="font-family:\'Syne\',sans-serif;font-size:1.1rem;font-weight:800;'
        'color:#F59E0B;margin:12px 0 20px;">🎙️ VideoMind</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<p style="font-size:0.78rem;color:#8892A4;margin-bottom:4px;">SOURCE</p>', unsafe_allow_html=True)
    source_val = st.text_input("source", label_visibility="collapsed",
                               placeholder="YouTube URL or local file path…")

    st.markdown('<p style="font-size:0.78rem;color:#8892A4;margin:12px 0 4px;">LANGUAGE</p>', unsafe_allow_html=True)
    lang_val = st.selectbox("lang", ["english", "hinglish"], label_visibility="collapsed")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    run_btn = st.button("▶  Analyse", use_container_width=True)

    # live rail in sidebar during processing
    if st.session_state.stage not in ("idle", "done"):
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        render_rail(st.session_state.stage)

    if st.session_state.result:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if st.button("↺  New analysis", use_container_width=True):
            st.session_state.result  = None
            st.session_state.history = []
            st.session_state.stage   = "idle"
            st.rerun()

    st.markdown(
        '<p style="font-size:0.7rem;color:#4A5568;margin-top:auto;padding-top:24px;line-height:1.7;">'
        'Mistral · Whisper · LangChain<br>ChromaDB · Streamlit</p>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="hero">'
    '<div class="hero-eyebrow">AI Video Intelligence</div>'
    '<h1 class="hero-title">Turn any video into<br><span>structured knowledge</span></h1>'
    '<p class="hero-sub">Paste a YouTube link or drop a local file — VideoMind transcribes,<br>'
    'summarises, extracts decisions, and lets you chat with the content.</p>'
    '</div>',
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
if run_btn:
    if not source_val.strip():
        st.error("Enter a YouTube URL or local file path in the sidebar first.")
        st.stop()

    st.session_state.result  = None
    st.session_state.history = []

    pbar    = st.progress(0, text="Starting…")
    msg_box = st.empty()
    rail_box = st.empty()

    try:
        def upd(stage, pct, txt):
            st.session_state.stage = stage
            pbar.progress(pct, text=txt)
            msg_box.info(txt)
            with rail_box.container():
                render_rail(stage)

        upd("audio",      15, "🎵  Extracting audio…")
        chunks = process_input(source_val.strip())

        upd("transcribe", 38, "📝  Transcribing — this may take a moment…")
        transcript = transcribe_all(chunks, language=lang_val)

        upd("analyse",    68, "🧠  Generating title, summary & extractions…")
        title        = generate_title(transcript)
        summary      = summarize(transcript)
        action_items = extract_action_items(transcript)
        decisions    = extract_decisions(transcript)
        questions    = extract_questions(transcript)

        upd("rag",        90, "🔗  Building RAG index…")
        rag_chain = build_rag_chain(transcript)

        pbar.progress(100, text="Done!")
        st.session_state.result = dict(
            title=title, transcript=transcript, summary=summary,
            action_items=action_items, decisions=decisions,
            questions=questions, rag_chain=rag_chain,
        )
        st.session_state.stage = "done"
        time.sleep(0.6)
        pbar.empty(); msg_box.empty(); rail_box.empty()
        st.rerun()

    except Exception as e:
        pbar.empty(); msg_box.empty(); rail_box.empty()
        st.session_state.stage = "idle"
        st.error(f"Pipeline error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.result:
    r = st.session_state.result

    # title card
    st.markdown(
        f'<div class="vm-card" style="border-left:3px solid #F59E0B;">'
        f'<div class="vm-card-label">Detected title</div>'
        f'<div class="vm-card-value">{r["title"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    tab_sum, tab_act, tab_dec, tab_q, tab_tx, tab_chat = st.tabs([
        "📋 Summary", "✅ Actions", "🔑 Decisions", "❓ Questions", "📄 Transcript", "💬 Chat",
    ])

    with tab_sum:
        sec_header("📋", "Summary")
        st.markdown(
            f'<div class="vm-card" style="font-size:0.9rem;line-height:1.8;">{r["summary"]}</div>',
            unsafe_allow_html=True,
        )

    with tab_act:
        sec_header("✅", "Action Items")
        pill_list(r["action_items"])

    with tab_dec:
        sec_header("🔑", "Key Decisions")
        pill_list(r["decisions"])

    with tab_q:
        sec_header("❓", "Open Questions")
        pill_list(r["questions"])

    with tab_tx:
        sec_header("📄", "Full Transcript")
        st.markdown(f'<div class="tx-box">{r["transcript"]}</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.download_button(
            "⬇  Download .txt",
            data=r["transcript"],
            file_name="transcript.txt",
            mime="text/plain",
        )

    with tab_chat:
        sec_header("💬", "Chat with this video")

        if st.session_state.history:
            st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
            for m in st.session_state.history:
                chat_msg(m["role"], m["content"])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="chat-empty">No messages yet — ask anything about the video below.</div>',
                unsafe_allow_html=True,
            )

        col_q, col_send = st.columns([5, 1])
        with col_q:
            user_q = st.text_input("q", placeholder="e.g. What were the main decisions made?",
                                   label_visibility="collapsed", key="chat_q")
        with col_send:
            send = st.button("Send", use_container_width=True)

        if send and user_q.strip():
            st.session_state.history.append({"role": "user", "content": user_q.strip()})
            with st.spinner("Thinking…"):
                ans = ask_question(r["rag_chain"], user_q.strip())
            st.session_state.history.append({"role": "assistant", "content": ans})
            st.rerun()

# ── empty state ───────────────────────────────────────────────────────────────
elif st.session_state.stage == "idle":
    st.markdown(
        '<div style="text-align:center;padding:56px 0 20px;">'
        '<p style="font-size:3rem;margin-bottom:14px;">🎬</p>'
        '<p style="font-size:0.95rem;color:#8892A4;max-width:400px;margin:0 auto;line-height:1.75;">'
        'Enter a source in the sidebar and press <strong style="color:#F59E0B;">Analyse</strong> to begin.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )