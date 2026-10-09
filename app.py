import html

import streamlit as st

from chatbot import Chatbot
from config import (
    APP_NAME,
    APP_TAGLINE,
    AVATAR_URL,
    PROVIDERS,
    available_providers,
)
from providers import ProviderError


USER_AVATAR = "🧑‍💻"
BOT_AVATAR = AVATAR_URL or "💠"

# This must be the first Streamlit command.
st.set_page_config(
    page_title=f"{APP_NAME} | AI Assistant",
    page_icon="💠",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------
# Styling  (dark "midnight" theme with violet -> cyan accent)
# ---------------------------------------------------------------
STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, .stApp, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
    }

    /* Soft glow behind the page */
    .stApp {
        background:
            radial-gradient(900px 420px at 85% -10%, rgba(124, 92, 255, 0.16), transparent 60%),
            radial-gradient(700px 380px at -10% 0%, rgba(34, 211, 238, 0.10), transparent 60%),
            #0A0E1A !important;
    }

    /* Hide Streamlit chrome we do not need */
    #MainMenu, footer, [data-testid="stDecoration"] { visibility: hidden; }

    .block-container {
        max-width: 860px;
        padding-top: 1.6rem;
        padding-bottom: 7rem;
    }

    /* ---------- Top brand bar ---------- */
    .brand-bar {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        padding: 0.9rem 1.1rem;
        margin-bottom: 1.4rem;
        border: 1px solid #232C48;
        border-radius: 18px;
        background: rgba(17, 23, 41, 0.75);
        backdrop-filter: blur(6px);
    }

    .logo {
        display: grid;
        place-items: center;
        flex: 0 0 auto;
        width: 44px;
        height: 44px;
        border-radius: 13px;
        color: #fff;
        font-weight: 800;
        font-size: 1.35rem;
        background: linear-gradient(135deg, #7C5CFF, #22D3EE);
        box-shadow: 0 6px 22px rgba(124, 92, 255, 0.45);
    }

    .brand-name {
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }

    .brand-tag {
        color: #8A94B5;
        font-size: 0.82rem;
    }

    .chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        margin-left: auto;
        justify-content: flex-end;
    }

    .chip {
        padding: 0.22rem 0.65rem;
        color: #B9C2E0;
        font-size: 0.72rem;
        font-weight: 600;
        border: 1px solid #2A3557;
        border-radius: 999px;
        background: #141B30;
        white-space: nowrap;
    }

    .chip.live { color: #4ADE80; border-color: rgba(74, 222, 128, 0.35); }

    /* ---------- Welcome section ---------- */
    .welcome { text-align: center; padding: 1.8rem 0 1.2rem; }

    .welcome h1 {
        margin: 0 0 0.5rem;
        font-size: clamp(1.9rem, 5vw, 2.7rem);
        font-weight: 800;
        letter-spacing: -0.04em;
        background: linear-gradient(90deg, #C4B5FD, #67E8F9);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .welcome p { margin: 0; color: #8A94B5; font-size: 1rem; }

    /* Suggestion cards (main-area buttons) */
    [data-testid="stMain"] .stButton > button {
        min-height: 4.2rem;
        padding: 0.9rem 1rem;
        text-align: left;
        color: #E8ECF8;
        font-weight: 600;
        border: 1px solid #232C48;
        border-radius: 16px;
        background: #111729;
        transition: border-color .15s ease, transform .15s ease, box-shadow .15s ease;
    }

    [data-testid="stMain"] .stButton > button:hover {
        border-color: #7C5CFF;
        transform: translateY(-2px);
        box-shadow: 0 10px 26px rgba(124, 92, 255, 0.18);
    }

    /* ---------- Chat messages ---------- */
    [data-testid="stChatMessage"] {
        padding: 1rem 1.1rem;
        margin: 0.7rem 0;
        border: 1px solid #232C48;
        border-radius: 18px;
        background: #111729;
    }

    /* Your messages get a violet tint */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        border-color: rgba(124, 92, 255, 0.45);
        background: linear-gradient(135deg, rgba(124, 92, 255, 0.16), rgba(124, 92, 255, 0.05));
    }

    [data-testid="stChatMessage"] a { color: #67E8F9 !important; font-weight: 600; }

    /* ---------- Chat input ---------- */
    [data-testid="stChatInput"] {
        border: 1px solid #2A3557 !important;
        border-radius: 18px;
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.35);
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #7C5CFF !important;
        box-shadow: 0 0 0 3px rgba(124, 92, 255, 0.22);
    }

    [data-testid="stBottom"] > div { background: transparent !important; }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] { border-right: 1px solid #232C48; }

    .side-brand { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.2rem; }
    .side-brand .logo { width: 34px; height: 34px; font-size: 1.05rem; border-radius: 10px; }
    .side-brand span { font-size: 1.1rem; font-weight: 800; letter-spacing: -0.02em; }

    .side-label {
        margin: 1rem 0 0.35rem;
        color: #8A94B5;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    /* Primary button = gradient */
    button[kind="primary"] {
        border: none !important;
        color: #fff !important;
        font-weight: 700;
        background: linear-gradient(135deg, #7C5CFF, #22D3EE) !important;
    }

    /* ---------- Setup screen ---------- */
    .setup-card {
        padding: 1.4rem 1.5rem;
        margin: 1rem 0;
        border: 1px solid #232C48;
        border-radius: 18px;
        background: #111729;
    }

    .setup-card h3 { margin-top: 0; }

    @media (max-width: 640px) {
        .brand-bar { flex-wrap: wrap; }
        .chips { margin-left: 0; justify-content: flex-start; }
    }
</style>
"""

st.markdown(STYLE, unsafe_allow_html=True)


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def brand_logo_letter() -> str:
    return html.escape((APP_NAME[:1] or "N").upper())


def render_setup_screen() -> None:
    """Friendly first-run screen shown when no API key exists."""
    st.markdown(
        f"""
        <div class="brand-bar">
            <div class="logo">{brand_logo_letter()}</div>
            <div>
                <div class="brand-name">{html.escape(APP_NAME)}</div>
                <div class="brand-tag">{html.escape(APP_TAGLINE)}</div>
            </div>
        </div>
        <div class="setup-card">
            <h3>One quick step: add an API key</h3>
            <p>
                Create a file named <code>.env</code> in the project folder
                (copy <code>.env.example</code>) and paste <b>at least one</b>
                key. Then restart the app.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for settings in PROVIDERS.values():
        st.markdown(
            f"**{settings['label']}** &nbsp;→&nbsp; "
            f"`{settings['api_key_env']}=` &nbsp;·&nbsp; "
            f"[get a key]({settings['key_url']})"
        )

    st.caption("Keys stay on your computer inside .env and are never uploaded.")


def conversation_markdown(messages: list[dict]) -> str:
    """Format the chat as a Markdown document for download."""
    lines = [f"# {APP_NAME} conversation", ""]

    for message in messages:
        speaker = "You" if message["role"] == "user" else APP_NAME
        lines += [f"**{speaker}:**", "", message["content"], ""]

    return "\n".join(lines)


def initialize_chatbot() -> bool:
    """Create the chatbot once per browser session. Returns False on failure."""
    if "bot" in st.session_state:
        return True

    try:
        st.session_state.bot = Chatbot()
    except ProviderError as error:
        st.error(str(error))
        return False

    return True


def on_provider_change() -> None:
    try:
        st.session_state.bot.set_provider(st.session_state.provider_select)
        st.session_state.pop("last_error", None)
    except ProviderError as error:
        st.session_state.last_error = str(error)


# ---------------------------------------------------------------
# Start-up checks
# ---------------------------------------------------------------
providers = available_providers()

if not providers:
    render_setup_screen()
    st.stop()

if not initialize_chatbot():
    st.stop()

bot = st.session_state.bot


# ---------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------
visible_messages = [m for m in bot.messages if m["role"] != "system"]

with st.sidebar:
    st.markdown(
        f"""
        <div class="side-brand">
            <div class="logo">{brand_logo_letter()}</div>
            <span>{html.escape(APP_NAME)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(APP_TAGLINE)

    st.markdown('<div class="side-label">Model provider</div>', unsafe_allow_html=True)
    st.selectbox(
        "Model provider",
        options=providers,
        index=providers.index(bot.provider_name)
        if bot.provider_name in providers
        else 0,
        format_func=lambda name: PROVIDERS[name]["label"],
        key="provider_select",
        on_change=on_provider_change,
        label_visibility="collapsed",
    )
    st.code(bot.provider.model, language=None)

    st.markdown('<div class="side-label">Tools</div>', unsafe_allow_html=True)
    st.success("Live web search enabled", icon="🔎")

    st.markdown('<div class="side-label">Conversation</div>', unsafe_allow_html=True)
    st.metric("Messages", len(visible_messages))

    if st.button("＋  New chat", use_container_width=True, type="primary"):
        bot.reset()
        st.session_state.pop("last_error", None)
        st.rerun()

    if visible_messages:
        st.download_button(
            "⬇  Export chat (.md)",
            data=conversation_markdown(visible_messages),
            file_name=f"{APP_NAME.lower()}-chat.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.divider()
    st.caption(
        "History lasts for this browser session only. "
        "Add more providers any time in your .env file."
    )


# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.markdown(
    f"""
    <div class="brand-bar">
        <div class="logo">{brand_logo_letter()}</div>
        <div>
            <div class="brand-name">{html.escape(APP_NAME)}</div>
            <div class="brand-tag">{html.escape(APP_TAGLINE)}</div>
        </div>
        <div class="chips">
            <span class="chip">{html.escape(bot.provider.label)}</span>
            <span class="chip live">● Web search on</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------
# Welcome screen with example prompts
# ---------------------------------------------------------------
if not visible_messages:
    st.markdown(
        """
        <div class="welcome">
            <h1>What would you like to explore?</h1>
            <p>Ask anything. I can research the web, explain ideas,
            write, and help with code.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    suggestions = [
        (
            "🔎  Latest tech news",
            "What are the most important technology news stories today? Cite your sources.",
        ),
        (
            "🧠  Explain simply",
            "Explain how large language models work in simple terms, with an analogy.",
        ),
        (
            "💻  Python best practices",
            "What is a clean, professional folder structure for a Python project?",
        ),
        (
            "✉️  Write an email",
            "Draft a concise, professional email asking for a project deadline extension.",
        ),
    ]

    for row_start in range(0, len(suggestions), 2):
        columns = st.columns(2)

        for column, (label, prompt_text) in zip(
            columns, suggestions[row_start:row_start + 2]
        ):
            with column:
                if st.button(label, use_container_width=True, key=f"sug_{label}"):
                    st.session_state.pending_prompt = prompt_text
                    st.rerun()


# ---------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------
for message in visible_messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if "last_error" in st.session_state:
    st.error(st.session_state.last_error, icon="⚠️")


prompt = st.chat_input(
    f"Message {APP_NAME}...",
    max_chars=4000,
)

# A clicked example prompt is used as if the user had typed it.
if not prompt and "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")


if prompt:
    st.session_state.pop("last_error", None)

    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        with st.spinner("Researching and thinking..."):
            try:
                bot.reply(prompt)
            except Exception as error:
                st.session_state.last_error = str(error)

    # Rerun so the sidebar counter and export button refresh too.
    st.rerun()
