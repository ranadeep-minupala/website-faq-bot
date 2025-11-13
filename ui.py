import time
import streamlit as st
from bot import build_knowledge_base, answer_question

# ---------- Page config ----------
st.set_page_config(
    page_title="Website FAQ Bot",
    page_icon="🌐",
    layout="wide"
)

# ---------- Simple styling ----------
st.markdown(
    """
    <style>
    .user-bubble {
        background-color: #e6f0ff;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin-bottom: 0.3rem;
        max-width: 90%;
    }
    .bot-bubble {
        background-color: #f5f5f5;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin-bottom: 0.3rem;
        max-width: 90%;
    }
    .user-label {
        font-size: 0.75rem;
        color: #3366ff;
        margin-bottom: 0.1rem;
    }
    .bot-label {
        font-size: 0.75rem;
        color: #555555;
        margin-bottom: 0.1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Session state ----------
if "chunks" not in st.session_state:
    st.session_state.chunks = None
if "embeddings" not in st.session_state:
    st.session_state.embeddings = None
if "current_url" not in st.session_state:
    st.session_state.current_url = None
if "chat_history" not in st.session_state:
    # list of {"role": "user" / "bot", "content": "..."}
    st.session_state.chat_history = []
if "last_stats" not in st.session_state:
    st.session_state.last_stats = None  # (num_chunks, elapsed_seconds)


# ---------- Sidebar: controls ----------
with st.sidebar:
    st.header("Step 1: Website URL")

    url = st.text_input(
        "Enter website URL",
        value=st.session_state.current_url or "",
        placeholder="https://example.com",
    )

    top_k = st.slider(
        "Context depth (how many chunks to use)",
        min_value=1,
        max_value=5,
        value=3,
        help="Higher values use more of the website text for each answer.",
    )

    process_btn = st.button("Process Website", use_container_width=True)

    st.markdown("---")
    if st.button("Clear chat history", use_container_width=True):
        st.session_state.chat_history = []
        st.toast("Chat history cleared.", icon="🧹")

# ---------- Main layout ----------
col_left, col_right = st.columns([1, 2])

with col_left:
    st.title("🌐 Website FAQ Bot")
    st.write(
        "Ask questions about any website’s content.\n\n"
        "1. Enter a URL in the sidebar and click **Process Website**.\n"
        "2. Then ask questions in the chat on the right."
    )

    # Show last processing stats if available
    if st.session_state.chunks is not None and st.session_state.last_stats is not None:
        num_chunks, elapsed = st.session_state.last_stats
        st.success(
            f"Website loaded from **{st.session_state.current_url}**\n\n"
            f"- Text chunks: **{num_chunks}**\n"
            f"- Processing time: **{elapsed:.1f} seconds**"
        )

with col_right:
    st.subheader("Step 2: Chat with the website")

    chat_container = st.container()

    # ---------- Process website when button clicked ----------
    if process_btn:
        if not url.strip():
            st.error("Please enter a URL in the sidebar first.")
        else:
            with st.spinner("Fetching and processing website content..."):
                try:
                    start = time.time()
                    chunks, embeddings = build_knowledge_base(url.strip())
                    elapsed = time.time() - start

                    st.session_state.chunks = chunks
                    st.session_state.embeddings = embeddings
                    st.session_state.current_url = url.strip()
                    st.session_state.last_stats = (len(chunks), elapsed)

                    st.session_state.chat_history = []  # reset chat for new site
                    st.success("Website processed successfully. You can start asking questions.")
                except Exception as e:
                    st.error(f"Error while processing website: {e}")

    # ---------- Show chat history ----------
    with chat_container:
        if not st.session_state.chat_history:
            st.info("No questions yet. Ask something about the website once it’s processed.")
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown('<div class="user-label">You</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="bot-label">Bot</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="bot-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

    # ---------- Question input (form so Enter works nicely) ----------
    st.markdown("---")
    with st.form("question_form", clear_on_submit=True):
        question = st.text_input(
            "Type your question",
            placeholder="e.g. What graduate programs does this university offer?",
        )
        submitted = st.form_submit_button("Send")

    if submitted:
        if st.session_state.chunks is None or st.session_state.embeddings is None:
            st.warning("First process a website from the sidebar.")
        elif not question.strip():
            st.warning("Please type a question before sending.")
        else:
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": question.strip()})

            with st.spinner("Thinking..."):
                try:
                    answer = answer_question(
                        question.strip(),
                        st.session_state.chunks,
                        st.session_state.embeddings,
                        top_k=top_k,
                    )
                except Exception as e:
                    answer = f"Error while generating answer: {e}"

            # Add bot message
            st.session_state.chat_history.append({"role": "bot", "content": answer})

            # Rerun to display updated chat nicely
            st.experimental_rerun()
