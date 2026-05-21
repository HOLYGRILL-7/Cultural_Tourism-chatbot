import os
from pathlib import Path
import json
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

load_dotenv()

# ── 1. Load knowledge base ─────────────────────────────────────
with open("ghana_knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)
knowledge_text = json.dumps(knowledge, indent=2)

# ── 2. Config ──────────────────────────────────────────────────
API_KEY    = os.getenv("GEMINI_API_KEY")
MODEL      = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
SKILL_PATH = Path.home() / ".config/opencode/skills/culturalbot/SKILL.md"
SYSTEM_PROMPT  = SKILL_PATH.read_text().strip()
SYSTEM_PROMPT += f"\n\n=== GHANA KNOWLEDGE BASE ===\n{knowledge_text}"
SYSTEM_PROMPT += "\n\n=== FORMATTING RULE ===\nAlways write special characters and diacritics directly as real characters (e.g. ɛ, ɔ, ŋ) — never as Unicode escape codes like \\u025b or \\u0254."

# ── Configure Gemini ───────────────────────────────────────────
genai.configure(api_key=API_KEY)

# ── FIXED INTRO — always the same, no API call ─────────────────
KOFI_INTRO = "Akwaaba! 🇬🇭 I'm Kofi, your friendly Ghanaian cultural guide. Whether you're curious about our vibrant festivals, breathtaking tourist sites, local languages, or rich traditions — I'm here to help. What would you like to explore today? ✨"

# ── 3. Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="Kofi – Ghana Cultural Guide",
    page_icon="🇬🇭",
    layout="wide"
)

# ── 4. Dark-mode-only styles ───────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --gold:        #D4AF37;
    --gold-dim:    rgba(212, 175, 55, 0.35);
    --gold-glow:   rgba(212, 175, 55, 0.12);
    --bg:          #0a0905;
    --surface:     rgba(18, 15, 6, 0.95);
    --text:        #f0e6c8;
    --subtext:     rgba(240, 230, 200, 0.5);
    --border:      rgba(212, 175, 55, 0.28);
    --user-bubble: rgba(212, 175, 55, 0.10);
    --kofi-bubble: rgba(22, 18, 8, 0.90);
    --input-bg:    rgba(12, 10, 4, 0.97);
    --hatch:       rgba(212, 175, 55, 0.06);
    --red:         #CE1126;
    --green:       #006B3F;
}

/* ── Reset & base ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text) !important;
}

/* ── Kill Streamlit default blue bottom strip ── */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section[data-testid="stSidebar"] {
    background-color: #0a0905 !important;
    background: #0a0905 !important;
}

/* ── Crosshatch background ── */
[data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    background-image:
        repeating-linear-gradient(0deg,  transparent, transparent 32px, var(--hatch) 32px, var(--hatch) 33px),
        repeating-linear-gradient(90deg, transparent, transparent 32px, var(--hatch) 32px, var(--hatch) 33px) !important;
}

/* ── Kente top bar ── */
.kente-bar {
    position: fixed;
    top: 0; left: 0;
    width: 100%;
    height: 8px;
    background: repeating-linear-gradient(
        90deg,
        #D4AF37  0px,  #D4AF37  20px,
        #0e0e0e  20px, #0e0e0e  40px,
        #CE1126  40px, #CE1126  60px,
        #006B3F  60px, #006B3F  80px,
        #D4AF37  80px, #D4AF37 100px,
        #0e0e0e 100px, #0e0e0e 120px
    );
    z-index: 9999;
    box-shadow: 0 2px 20px rgba(212, 175, 55, 0.3);
}

/* ── Corner ornaments ── */
.ornament {
    position: fixed;
    width: 64px;
    height: 64px;
    opacity: 0.22;
    z-index: 2;
    pointer-events: none;
}

/* ── Header ── */
.ghana-header {
    text-align: center;
    padding: 3rem 1rem 0.8rem;
}

.ghana-header h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.4rem;
    font-weight: 700;
    color: var(--gold);
    margin: 0;
    letter-spacing: 3px;
    text-shadow: 0 0 40px rgba(212, 175, 55, 0.25), 0 2px 4px rgba(0,0,0,0.5);
}

.ghana-header .subtitle {
    color: var(--subtext);
    font-size: 0.88rem;
    font-weight: 300;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ── Kente divider ── */
.kente-divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    margin: 0.7rem auto;
    width: fit-content;
}

.kente-block {
    width: 20px;
    height: 5px;
    border-radius: 1px;
}

/* ── Gold rule ── */
hr.gold-rule, .gold-rule {
    border: none !important;
    border-top: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--gold-dim), transparent) !important;
    margin: 0.5rem auto 1.5rem !important;
    max-width: 600px !important;
    width: 100% !important;
    display: block !important;
}

/* ── Constrain chat to readable width (like Claude) ── */
[data-testid="stMainBlockContainer"] {
    max-width: 760px !important;
    margin: 0 auto !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    padding-bottom: 8rem !important;  /* clears the floating input bar */
    background: transparent !important;
}

/* ── Chat bubbles ── */
[data-testid="stChatMessage"] {
    background: var(--kofi-bubble) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1rem 1.3rem !important;
    margin-bottom: 0.8rem !important;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(212,175,55,0.08);
    transition: box-shadow 0.2s ease;
}

[data-testid="stChatMessage"]:hover {
    box-shadow: 0 4px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(212,175,55,0.15);
}

[data-testid="stChatMessage"] p {
    color: var(--text) !important;
    font-size: 0.97rem;
    line-height: 1.8;
}

/* User bubble — warmer gold tint */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--user-bubble) !important;
    border-color: rgba(212, 175, 55, 0.45) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(212,175,55,0.15) !important;
}

/* ── Input bar — constrained width + margin bottom ── */
[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 1.2rem;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: calc(100% - 3rem) !important;
    max-width: 760px !important;
    z-index: 100;
    background: var(--input-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 0.9rem 1.2rem !important;
    backdrop-filter: blur(24px);
    box-shadow: 0 -4px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(212,175,55,0.1);
}

[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.04) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: var(--gold-dim) !important;
    box-shadow: 0 0 0 3px var(--gold-glow) !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: var(--subtext) !important;
}

/* ── Hide default spinner, use gold dots ── */
.stSpinner { display: none !important; }

/* ── Typing dots loader ── */
.kofi-typing {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0.4rem;
}

.kofi-typing span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--gold);
    opacity: 0.3;
    animation: kofi-bounce 1.2s ease-in-out infinite;
}

.kofi-typing span:nth-child(1) { animation-delay: 0s; }
.kofi-typing span:nth-child(2) { animation-delay: 0.2s; }
.kofi-typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes kofi-bounce {
    0%, 80%, 100% { opacity: 0.2; transform: scale(0.85); }
    40%            { opacity: 1;   transform: scale(1.2); }
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
</style>

<!-- Kente bar -->
<div class="kente-bar"></div>

<!-- Adinkra corner ornaments -->
<svg class="ornament" style="top:16px;left:12px" viewBox="0 0 60 60">
    <circle cx="30" cy="30" r="26" fill="none" stroke="#D4AF37" stroke-width="1.5"/>
    <circle cx="30" cy="30" r="16" fill="none" stroke="#D4AF37" stroke-width="1"/>
    <circle cx="30" cy="30" r="6"  fill="none" stroke="#D4AF37" stroke-width="1"/>
    <line x1="4"  y1="30" x2="56" y2="30" stroke="#D4AF37" stroke-width="1"/>
    <line x1="30" y1="4"  x2="30" y2="56" stroke="#D4AF37" stroke-width="1"/>
    <line x1="11" y1="11" x2="49" y2="49" stroke="#D4AF37" stroke-width="0.75"/>
    <line x1="49" y1="11" x2="11" y2="49" stroke="#D4AF37" stroke-width="0.75"/>
</svg>
<svg class="ornament" style="top:16px;right:12px" viewBox="0 0 60 60">
    <circle cx="30" cy="30" r="26" fill="none" stroke="#D4AF37" stroke-width="1.5"/>
    <circle cx="30" cy="30" r="16" fill="none" stroke="#D4AF37" stroke-width="1"/>
    <circle cx="30" cy="30" r="6"  fill="none" stroke="#D4AF37" stroke-width="1"/>
    <line x1="4"  y1="30" x2="56" y2="30" stroke="#D4AF37" stroke-width="1"/>
    <line x1="30" y1="4"  x2="30" y2="56" stroke="#D4AF37" stroke-width="1"/>
    <line x1="11" y1="11" x2="49" y2="49" stroke="#D4AF37" stroke-width="0.75"/>
    <line x1="49" y1="11" x2="11" y2="49" stroke="#D4AF37" stroke-width="0.75"/>
</svg>

<!-- Header -->
<div class="ghana-header">
    <h1>🇬🇭 Ghana Cultural Companion</h1>
    <div class="kente-divider">
        <div class="kente-block" style="background:#D4AF37"></div>
        <div class="kente-block" style="background:#1a1a1a"></div>
        <div class="kente-block" style="background:#CE1126"></div>
        <div class="kente-block" style="background:#006B3F"></div>
        <div class="kente-block" style="background:#D4AF37"></div>
        <div class="kente-block" style="background:#1a1a1a"></div>
        <div class="kente-block" style="background:#CE1126"></div>
        <div class="kente-block" style="background:#006B3F"></div>
        <div class="kente-block" style="background:#D4AF37"></div>
    </div>
    <p class="subtitle">Ask Kofi about festivals · tourist sites · languages · culture</p>
</div>
<hr class="gold-rule">
""", unsafe_allow_html=True)

# ── 5. Session state ───────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=SYSTEM_PROMPT
    )

# -- 6. Kofi fixed intro on first load --------------------------------
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🇬🇭"):
        st.markdown(KOFI_INTRO)
    # Save to messages for display only — NOT to history so Gemini doesn't copy the pattern
    st.session_state.messages.append({"role": "assistant", "content": KOFI_INTRO})

# ── 7. Display messages (skip first since shown above) ─────────
for msg in st.session_state.messages[1:]:
    avatar = "🇬🇭" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# -- 8. Chat input ------------------------------------------------------------
user_input = st.chat_input("Ask Kofi anything about Ghana...")

if user_input:
    # Show user message immediately
    with st.chat_message("user", avatar="🇬🇭"):
        st.markdown(user_input)

    st.session_state.history.append({"role": "user", "parts": user_input})
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Dots render OUTSIDE the bubble so Streamlit paints them instantly
    thinking = st.empty()
    thinking.markdown('<div class="kofi-typing"><span></span><span></span><span></span></div>', unsafe_allow_html=True)

    try:
        import time
        chat = st.session_state.model.start_chat(history=st.session_state.history[:-1])
        stream = chat.send_message(user_input, stream=True)
        # Collect full reply while dots are showing
        full_reply = "".join(chunk.text or "" for chunk in stream)

        # Dots gone — now show the assistant bubble with word-by-word reveal
        thinking.empty()
        with st.chat_message("assistant", avatar="🇬🇭"):
            placeholder = st.empty()
            buffer = []
            words = full_reply.split(" ")
            for i, word in enumerate(words):
                buffer.append(word + (" " if i < len(words) - 1 else ""))
                placeholder.markdown("".join(buffer))
                time.sleep(0.03)

        st.session_state.messages.append({"role": "assistant", "content": full_reply})
        st.session_state.history.append({"role": "model", "parts": full_reply})

    except Exception as e:
        thinking.empty()
        if "429" in str(e):
            st.warning("⚠️ Rate limit reached. Please wait a moment and try again.")
        else:
            st.error(f"Something went wrong: {e}")