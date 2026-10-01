"""Streamlit frontend for the existing AI Career Assistant backend."""
import os
from datetime import datetime

import requests
import streamlit as st

st.set_page_config(page_title="AI Career Assistant", page_icon="✦", layout="wide")
BASE_URL = os.getenv("CAREER_BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.markdown("""
<style>
.stApp { background: #f6f8fa; color: #172b35; }
.block-container { max-width: 1080px; padding-top: 2.5rem; padding-bottom: 5rem; }
[data-testid="stSidebar"] { background: #edf3f3; border-right: 1px solid #dae5e5; }
h1, h2, h3 { color: #172b35 !important; letter-spacing: -.035em; }
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li { color: #304650; }
.eyebrow { color: #087f78; font-size: .75rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
.hero { padding: 28px 0 22px; }
.hero h1 { font-size: clamp(2rem, 5vw, 3.5rem); line-height: 1.12; margin: 12px 0; }
.hero p { max-width: 650px; color: #60737d; font-size: 1.05rem; line-height: 1.7; }
.brand { font-size: 1.3rem; font-weight: 750; color: #172b35; margin-bottom: 8px; }
.brand span { color: #087f78; }
.note { color: #60737d; font-size: .85rem; line-height: 1.6; }
[data-testid="stChatMessage"] { background: white; border: 1px solid #e0e8eb; border-radius: 16px; padding: 20px; margin: 12px 0; }
[data-testid="stChatInput"] textarea { background: white; color: #172b35; }
[data-testid="stBottom"] { background: #f6f8fa; }
.stButton > button, .stDownloadButton > button { border-radius: 10px; border: 1px solid #cadada; background: white; color: #172b35; min-height: 44px; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color: #087f78; color: #087f78; }
.stButton > button[kind="primary"] { background: #087f78; color: white; border-color: #087f78; }
[data-testid="stVerticalBlockBorderWrapper"] > div { border-radius: 16px; }
@media (max-width: 640px) { .block-container { padding-top: 1.5rem; } .hero { padding-top: 12px; } }
</style>
""", unsafe_allow_html=True)

PROMPTS = [
    ("01 / EXPLORE", "Find your direction", "Compare career paths that fit your interests and strengths.",
     "Help me explore career options. Ask me about my interests, education and strengths first."),
    ("02 / PLAN", "Build a learning roadmap", "Turn a career goal into practical learning steps.",
     "Help me create a learning roadmap for my target career. Ask about my goal, current skills and available study time first."),
    ("03 / PREPARE", "Improve your resume", "Get guidance on clearer bullets and relevant skills.",
     "Help me improve my resume for a target role. Ask me to paste my resume text and describe the role first."),
    ("04 / PRACTICE", "Prepare for interviews", "Practice questions tailored to the role you want.",
     "Help me prepare for an interview. Ask about the role and my experience, then suggest practice questions."),
]

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


@st.cache_data(ttl=15, show_spinner=False)
def backend_available(url):
    try:
        return requests.get(f"{url}/health", timeout=2).status_code == 200
    except requests.exceptions.RequestException:
        return False


def choose_prompt(prompt):
    st.session_state.pending_prompt = prompt


def clear_chat():
    st.session_state.messages = []
    st.session_state.pending_prompt = None


with st.sidebar:
    st.markdown('<div class="brand"><span>✦</span> Career Assistant</div>', unsafe_allow_html=True)
    st.caption("A little clarity for your next big step.")
    st.button("＋  New conversation", type="primary", use_container_width=True, on_click=clear_chat)
    st.divider()
    st.markdown("#### Start with a goal")
    for index, (_, title, _, prompt) in enumerate(PROMPTS):
        st.button(title, key=f"side_{index}", use_container_width=True,
                  on_click=choose_prompt, args=(prompt,))
    st.divider()
    st.markdown("#### Your conversation")
    question_count = sum(message["role"] == "user" for message in st.session_state.messages)
    st.caption(f"{question_count} question{'s' if question_count != 1 else ''} in this session")
    if st.session_state.messages:
        transcript = "\n\n".join(
            f"{'You' if message['role'] == 'user' else 'Career Assistant'}:\n{message['content']}"
            for message in st.session_state.messages
        )
        st.download_button("Download conversation", transcript,
                           file_name=f"career-chat-{datetime.now():%Y%m%d}.txt",
                           mime="text/plain", use_container_width=True)
    st.divider()
    online = backend_available(BASE_URL)
    st.caption("🟢 Assistant connected" if online else "⚪ Assistant unavailable")
    if st.button("Refresh connection", use_container_width=True):
        backend_available.clear()
        st.rerun()
    st.markdown('<div class="note">Answers are based on your latest question. Include relevant background each time. Verify important career and course details.</div>', unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Your next chapter starts here</div>', unsafe_allow_html=True)
if not st.session_state.messages:
    st.markdown("""
    <div class="hero">
      <h1>Big ambitions.<br>A clearer next step.</h1>
      <p>Explore your options, build your skills, and prepare for what comes next.
      Start with a goal below or ask a question of your own.</p>
    </div>
    """, unsafe_allow_html=True)
    for row in range(2):
        columns = st.columns(2)
        for column, index in zip(columns, range(row * 2, row * 2 + 2)):
            label, title, description, prompt = PROMPTS[index]
            with column:
                with st.container(border=True):
                    st.caption(label)
                    st.markdown(f"### {title}")
                    st.write(description)
                    st.button("Let's get started →", key=f"card_{index}",
                              use_container_width=True, on_click=choose_prompt, args=(prompt,))
    st.caption("Tip: share your education, interests, and target role for a more useful answer.")
else:
    st.title("Your career conversation")
    st.caption("Explore possibilities. Leave with a practical next step.")

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="✦" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# A card click and a typed question both enter the same request flow.
typed_prompt = st.chat_input("What would you like to work on today?")
prompt = typed_prompt or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if prompt and prompt.strip():
    prompt = prompt.strip()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="✦"):
        try:
            with st.spinner("Working on your next step…"):
                response = requests.post(
                    f"{BASE_URL}/chat",
                    json={"messages": st.session_state.messages[-2:]},
                    timeout=(5, 300),
                )
                response.raise_for_status()
                data = response.json()
                answer = data.get("answer") or data.get("response")
                if not isinstance(answer, str) or not answer.strip():
                    raise ValueError("The assistant returned an empty or invalid answer.")
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
        except requests.exceptions.ConnectionError:
            st.error("The assistant is unavailable. Start the backend and try again.")
        except requests.exceptions.Timeout:
            st.error("The answer took too long. Please try a shorter question.")
        except requests.exceptions.HTTPError:
            st.error(f"The assistant could not complete this request (HTTP {response.status_code}). Please try again.")
        except (ValueError, requests.exceptions.RequestException):
            st.error("The assistant returned an unexpected response. Please try again.")
