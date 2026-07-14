import streamlit as st
import os
import sys
import subprocess
import random

APP_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, ".."))
WAREHOUSE_PATH = os.path.join(PROJECT_ROOT, "warehouse.duckdb")

sys.path.insert(0, APP_DIR)


@st.cache_resource(show_spinner=False)
def bootstrap_pipeline():
    """
    Self-bootstrapping pipeline: if the warehouse doesn't exist yet (e.g. fresh
    deploy on Streamlit Cloud), generate data, load it, and run dbt - once per
    app instance. This is the same DAG run_pipeline.sh runs locally; here it's
    triggered automatically so the deployed app works with zero manual setup.
    """
    if os.path.exists(WAREHOUSE_PATH):
        return "already built"
    env = os.environ.copy()
    env["MELT_RISK_DB_PATH"] = WAREHOUSE_PATH
    env["DBT_PROFILES_DIR"] = os.path.join(PROJECT_ROOT, "dbt_project")

    # Use the exact same Python interpreter running this Streamlit app (sys.executable),
    # not a bare "python3" command - on some hosts (like Streamlit Cloud) "python3" can
    # resolve to a different interpreter than the one with our pip-installed packages.
    python_exe = sys.executable
    dbt_exe = os.path.join(os.path.dirname(python_exe), "dbt")
    if not os.path.exists(dbt_exe):
        dbt_exe = "dbt"  # fall back to PATH if not found alongside the interpreter

    steps = [
        ([python_exe, "generate_data.py"], os.path.join(PROJECT_ROOT, "data")),
        ([python_exe, "load_to_duckdb.py"], os.path.join(PROJECT_ROOT, "data")),
        ([dbt_exe, "run"], os.path.join(PROJECT_ROOT, "dbt_project")),
    ]
    for cmd, cwd in steps:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            raise RuntimeError(f"Pipeline step failed: {' '.join(cmd)}\n{result.stderr}")
    return "built fresh"


with st.spinner("🍦 Scooping intelligence..."):
    bootstrap_pipeline()

from agent import run_agent

st.set_page_config(page_title="Melt Risk Agent", page_icon="🍦", layout="centered")

# ============================================================================
# THEME / CSS  -  premium ice-cream-boutique visual system
# ============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Quicksand:wght@500;600;700;800&display=swap');

/* ---------------------------------------------------------------------- */
/* 1. DESIGN TOKENS                                                        */
/* ---------------------------------------------------------------------- */
:root {
    --cream:        #FFF9F0;
    --vanilla:      #FFF1DC;
    --plum:         #2B1735;
    --plum-2:       #3C2149;
    --raspberry:    #FF4D8D;
    --raspberry-dk: #D6266A;
    --mint:         #3DE0C0;
    --mint-dk:      #1FA98D;
    --lemon:        #FFD866;
    --grape:        #B47CFF;
    --sky:          #7FD7F5;
    --choco:        #4A2E1F;
    --text-light:   #F3E8FF;
    --glass:        rgba(255,255,255,0.08);
    --glass-brd:    rgba(255,255,255,0.20);
}

html, body, [class*="css"] { font-family: 'Quicksand', sans-serif; }

/* ---------------------------------------------------------------------- */
/* 2. BACKGROUND - layered gradient + drifting blurred blobs + sprinkles   */
/* ---------------------------------------------------------------------- */
.stApp {
    background:
        radial-gradient(circle at 4px 4px, rgba(255,77,141,.35) 1.5px, transparent 1.5px),
        radial-gradient(circle at 24px 34px, rgba(61,224,192,.28) 1.5px, transparent 1.5px),
        radial-gradient(circle at 44px 14px, rgba(255,216,102,.26) 1.5px, transparent 1.5px),
        linear-gradient(180deg, var(--plum) 0%, var(--plum-2) 100%);
    background-size: 60px 60px, 60px 60px, 60px 60px, auto;
    background-attachment: fixed;
    position: relative;
    overflow-x: hidden;
}

.mr-blobs { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
.mr-blob {
    position: absolute; border-radius: 50%; filter: blur(50px); opacity: 0.55;
    animation: blobDrift 16s ease-in-out infinite;
}
.mr-blob.b1 { width: 340px; height: 340px; top: -80px; left: -60px; background: var(--raspberry); animation-delay: 0s; }
.mr-blob.b2 { width: 300px; height: 300px; top: 10%; right: -80px; background: var(--mint); animation-delay: -5s; }
.mr-blob.b3 { width: 260px; height: 260px; bottom: -60px; left: 20%; background: var(--grape); animation-delay: -9s; }
.mr-blob.b4 { width: 220px; height: 220px; bottom: 10%; right: 10%; background: var(--lemon); opacity: 0.35; animation-delay: -3s; }
@keyframes blobDrift {
    0%, 100% { transform: translate(0,0) scale(1); }
    33%      { transform: translate(24px,-30px) scale(1.08); }
    66%      { transform: translate(-18px,18px) scale(0.95); }
}

/* Floating decorative emojis - purely cosmetic, ignore clicks */
.mr-float-emoji {
    position: fixed; font-size: 1.8rem; opacity: 0.35; pointer-events: none; z-index: 0;
    animation: floatY 6s ease-in-out infinite;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.25));
}
@keyframes floatY {
    0%, 100% { transform: translateY(0) rotate(-4deg); }
    50%      { transform: translateY(-18px) rotate(4deg); }
}

/* Make sure real content sits above the decorative layer */
[data-testid="stAppViewContainer"] > .main { position: relative; z-index: 1; }

/* ---------------------------------------------------------------------- */
/* 3. HERO HEADER                                                          */
/* ---------------------------------------------------------------------- */
.mr-header { padding: 2.4rem 1.8rem 3.4rem 1.8rem; text-align: center; position: relative; }
.mr-logo {
    font-size: 4rem; display: inline-block;
    animation: logoPulse 3.2s ease-in-out infinite;
    filter: drop-shadow(0 10px 20px rgba(255,77,141,0.45));
}
@keyframes logoPulse {
    0%, 100% { transform: scale(1) rotate(0deg); }
    50%      { transform: scale(1.08) rotate(-3deg); }
}
.mr-title {
    font-family: 'Fredoka', sans-serif;
    font-weight: 700;
    font-size: 3.4rem;
    line-height: 1.05;
    margin: 0.3rem 0 0 0;
    background: linear-gradient(90deg, var(--raspberry) 0%, var(--lemon) 33%, var(--mint) 66%, var(--grape) 100%);
    background-size: 280% auto;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: shimmer 8s ease-in-out infinite;
}
@keyframes shimmer {
    0%   { background-position: 0% center; }
    50%  { background-position: 100% center; }
    100% { background-position: 0% center; }
}
.mr-subtitle {
    font-weight: 600;
    color: #E4D6F7;
    max-width: 620px;
    margin: 0.9rem auto 0 auto;
    font-size: 1.05rem;
    line-height: 1.6;
}
/* Melting drip divider under the header */
.mr-drip {
    height: 38px;
    margin-top: -1px;
    background-image: radial-gradient(circle at 22px -12px, transparent 20px, var(--cream) 21px);
    background-size: 44px 44px;
    background-repeat: repeat-x;
    background-position: bottom;
    animation: dripWiggle 5s ease-in-out infinite;
}
@keyframes dripWiggle { 0%,100% { background-position-x: 0; } 50% { background-position-x: 6px; } }

.mr-badges { display: flex; gap: 0.55rem; justify-content: center; flex-wrap: wrap; margin-top: 1.3rem; }
.mr-badge {
    background: var(--glass);
    border: 1px solid var(--glass-brd);
    backdrop-filter: blur(8px);
    color: var(--text-light);
    padding: 0.36rem 0.95rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.mr-badge:hover { transform: translateY(-3px); box-shadow: 0 8px 18px rgba(0,0,0,0.25); }

/* ---------------------------------------------------------------------- */
/* 4. GLASS CARD + GRADIENT BORDER (reusable pattern)                      */
/* ---------------------------------------------------------------------- */
.gradient-border-fx { position: relative; }
.gradient-border-fx::before {
    content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 2px;
    background: linear-gradient(135deg, var(--raspberry), var(--lemon), var(--mint), var(--grape));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor; mask-composite: exclude;
    pointer-events: none; opacity: 0.85;
}

/* ---------------------------------------------------------------------- */
/* 5. SIDEBAR                                                              */
/* ---------------------------------------------------------------------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1D0F26 0%, #2B1735 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family: 'Fredoka', sans-serif;
    color: var(--mint) !important;
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
    color: #E4D6F7;
}
[data-testid="stSidebar"] .stButton button {
    width: 100%; text-align: left;
    background: var(--glass);
    border: 1px solid var(--glass-brd);
    color: var(--text-light);
    border-radius: 14px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.5rem;
    font-weight: 700;
    font-size: 0.85rem;
    transition: all 0.22s cubic-bezier(.2,.8,.2,1);
}
[data-testid="stSidebar"] .stButton button:nth-of-type(5n+1):hover { border-color: var(--raspberry); box-shadow: 0 6px 18px rgba(255,77,141,0.4); }
[data-testid="stSidebar"] .stButton button:nth-of-type(5n+2):hover { border-color: var(--mint); box-shadow: 0 6px 18px rgba(61,224,192,0.4); }
[data-testid="stSidebar"] .stButton button:nth-of-type(5n+3):hover { border-color: var(--lemon); box-shadow: 0 6px 18px rgba(255,216,102,0.4); }
[data-testid="stSidebar"] .stButton button:nth-of-type(5n+4):hover { border-color: var(--grape); box-shadow: 0 6px 18px rgba(180,124,255,0.4); }
[data-testid="stSidebar"] .stButton button:hover { transform: translateY(-2px) scale(1.015); }
[data-testid="stSidebar"] .stButton button:active { transform: scale(0.97); }

/* ---------------------------------------------------------------------- */
/* 6. CHAT MESSAGES                                                        */
/* ---------------------------------------------------------------------- */
[data-testid="stChatMessage"] {
    background: rgba(255, 249, 240, 0.98) !important;
    border-radius: 20px !important;
    box-shadow: 0 10px 26px rgba(0,0,0,0.25);
    padding: 0.55rem 0.35rem;
    margin-bottom: 0.85rem;
    border-left: 5px solid var(--mint);
    animation: messageIn 0.45s cubic-bezier(.2,.8,.2,1) both;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stChatMessage"]:hover { transform: translateY(-2px); box-shadow: 0 14px 30px rgba(0,0,0,0.3); }
@keyframes messageIn {
    from { opacity: 0; transform: translateY(16px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
/* Messages alternate user/assistant in DOM order - color-code by position */
[data-testid="stChatMessage"]:nth-of-type(odd)  { border-left-color: var(--raspberry); }
[data-testid="stChatMessage"]:nth-of-type(even) { border-left-color: var(--mint-dk); }
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {
    color: var(--choco) !important; font-weight: 600;
}
[data-testid="stChatMessage"] strong { color: var(--raspberry-dk) !important; }

/* Chat input */
[data-testid="stChatInput"] {
    background: rgba(255, 249, 240, 0.97);
    border-radius: 999px;
    border: 2px solid var(--grape);
    transition: box-shadow 0.25s ease, border-color 0.25s ease;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--raspberry);
    box-shadow: 0 0 0 5px rgba(255,77,141,0.22), 0 10px 26px rgba(180,124,255,0.35);
}
[data-testid="stChatInput"] textarea { color: var(--choco) !important; font-weight: 600; }

/* ---------------------------------------------------------------------- */
/* 7. BUTTONS (global)                                                     */
/* ---------------------------------------------------------------------- */
.stButton button {
    border-radius: 12px;
    font-weight: 700;
    transition: all 0.22s cubic-bezier(.2,.8,.2,1);
}
.stButton button:hover { transform: translateY(-2px) scale(1.02); }
.stButton button:active { transform: translateY(0) scale(0.97); }

/* ---------------------------------------------------------------------- */
/* 8. API KEY FORM CARD                                                    */
/* ---------------------------------------------------------------------- */
[data-testid="stForm"] {
    background: var(--glass);
    border: 1px solid var(--glass-brd);
    border-radius: 22px;
    padding: 1.6rem;
    backdrop-filter: blur(10px);
    position: relative;
}

/* ---------------------------------------------------------------------- */
/* 9. CUSTOM SCROLLBAR                                                     */
/* ---------------------------------------------------------------------- */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--raspberry), var(--mint));
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, var(--raspberry-dk), var(--mint-dk)); }

/* Hide default Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
</style>

<div class="mr-blobs">
    <div class="mr-blob b1"></div>
    <div class="mr-blob b2"></div>
    <div class="mr-blob b3"></div>
    <div class="mr-blob b4"></div>
</div>
<div class="mr-float-emoji" style="top:8%; left:6%; animation-delay:0s;">🍓</div>
<div class="mr-float-emoji" style="top:14%; right:8%; animation-delay:-2s;">🍫</div>
<div class="mr-float-emoji" style="bottom:18%; left:10%; animation-delay:-4s;">✨</div>
<div class="mr-float-emoji" style="bottom:10%; right:12%; animation-delay:-1s;">🧊</div>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="mr-header">
    <div class="mr-logo">🍦</div>
    <h1 class="mr-title">Melt Risk Agent</h1>
    <p class="mr-subtitle">
        An agentic AI analyst for ice cream cold-chain distribution. Ask about melt risk,
        stock levels, or demand — it queries a real dbt + DuckDB warehouse and reasons over
        the results using Groq's Llama 3.3 70B with tool calling.
    </p>
    <div class="mr-badges">
        <span class="mr-badge">🧊 DuckDB</span>
        <span class="mr-badge">🔧 dbt</span>
        <span class="mr-badge">🤖 Groq · Llama 3.3 70B</span>
        <span class="mr-badge">⚡ Agentic tool-calling</span>
    </div>
</div>
<div class="mr-drip"></div>
""", unsafe_allow_html=True)

# --- API key handling: Streamlit secrets (deployed) or manual entry (local) ---
try:
    api_key = st.secrets.get("GROQ_API_KEY", None)
except Exception:
    api_key = None
if not api_key:
    api_key = st.session_state.get("groq_api_key")

if not api_key:
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    with st.form("api_key_form"):
        st.markdown("##### 🔑 Enter your free Groq API key to start")
        st.caption("Get one at console.groq.com/keys — it's free, takes 30 seconds, and is never stored anywhere.")
        key_input = st.text_input("Groq API Key", type="password", label_visibility="collapsed")
        submitted = st.form_submit_button("Let's go 🍨")
        if submitted and key_input:
            st.session_state["groq_api_key"] = key_input
            st.rerun()
    st.stop()

os.environ["GROQ_API_KEY"] = api_key

if "history" not in st.session_state:
    st.session_state.history = []
if "queued_prompt" not in st.session_state:
    st.session_state.queued_prompt = None

SUGGESTIONS = [
    "🚨 Which shipments are at critical melt risk?",
    "📦 What products are understocked?",
    "📈 Forecast demand for IC001 at CW01",
    "🌡️ Which warehouse has the worst cold-chain issues?",
    "📋 Summarize overall risk across the network",
]

# Playful, rotating loading messages for the "thinking" spinner - cosmetic only,
# does not touch the agent logic itself.
THINKING_MESSAGES = [
    "🍦 Scooping intelligence...",
    "🍨 Checking frozen inventory...",
    "❄️ Keeping things cool...",
    "🧊 Calculating melt risk...",
    "🍓 Chasing the right data...",
]

with st.sidebar:
    st.markdown("### 🍨 Try asking")
    for s in SUGGESTIONS:
        if st.button(s, key=f"sugg_{s}", use_container_width=True):
            st.session_state.queued_prompt = s.split(" ", 1)[1]  # strip emoji
            st.rerun()

    st.divider()
    st.markdown("### 🏗️ Architecture")
    st.markdown(
        "Synthetic data → **DuckDB** → **dbt** "
        "(staging + marts) → **Groq agent** (tool-calling loop) → **Streamlit**"
    )

    st.divider()
    if st.button("🔄 Reset conversation", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ============================================================================
# CHAT
# ============================================================================
for msg in st.session_state.history:
    avatar = "🍦" if msg["role"] == "assistant" else "🙋"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


def handle_prompt(prompt: str):
    with st.chat_message("user", avatar="🙋"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🍦"):
        with st.spinner(random.choice(THINKING_MESSAGES)):
            try:
                answer, updated_history = run_agent(prompt, st.session_state.history)
                st.markdown(answer)
                st.session_state.history = updated_history
            except Exception as e:
                st.error(f"Error: {e}")


if st.session_state.queued_prompt:
    p = st.session_state.queued_prompt
    st.session_state.queued_prompt = None
    handle_prompt(p)

if prompt := st.chat_input("Ask about melt risk, inventory, or demand... 🍨"):
    handle_prompt(prompt)