"""Simple chat frontend for AI Career Assistant."""
import os

from groq import Groq, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError
import streamlit as st

st.set_page_config(page_title="AI Career Assistant", page_icon="💬", layout="centered")
SYSTEM_PROMPT = """You are a helpful career assistant. Give practical, balanced advice on
careers, education, skills, resumes and interviews across all fields. Ask clarifying
questions when needed. Do not invent salaries, rankings or course details. Give
clear, complete answers and consider the conversation context."""
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except FileNotFoundError:
        api_key = None
if not api_key:
    st.error("Add GROQ_API_KEY in your app's Secrets settings, then restart the app.")
    st.stop()
client = Groq(api_key=api_key, timeout=60.0, max_retries=0)

st.markdown("""
<style>
.stApp { background: #080c12; color: #d9efff; }
.block-container { max-width: 820px; padding-top: 2.5rem; padding-bottom: 3rem; }
h1 { color: #d9efff !important; font-size: 2rem !important; letter-spacing: -.04em; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li { color: #c4deef; }
[data-testid="stChatMessage"] {
    background: #101923; border: 1px solid #233d52;
    border-radius: 16px; padding: 18px; margin-bottom: 14px;
}
[data-testid="stChatInput"] textarea { background: #101923; color: #d9efff; }
[data-testid="stBottom"] { background: #080c12; }
[data-testid="stHeader"] { background: #080c12; }
[data-testid="stChatInput"] { border: 1px solid #34536b; border-radius: 16px; background: #101923; }
[data-testid="stChatInput"] textarea::placeholder { color: #91b4cc; }
[data-testid="stChatInput"] button { color: #7dd3fc; }
[data-testid="stCaptionContainer"] { color: #91b4cc; }
[data-testid="stChatMessage"] a { color: #7dd3fc; }
[data-testid="stChatMessage"] pre { background: #080c12; color: #d9efff; }
[data-testid="stChatMessage"] code { color: #bae6fd; }
hr { border-color: #233d52 !important; }
.stButton > button {
    border-radius: 10px; background: #101923;
    color: #c4deef; border: 1px solid #34536b;
}
.stButton > button:hover { border-color: #7dd3fc; color: #7dd3fc; }
.welcome { text-align: center; padding: 70px 10px 30px; }
.welcome-icon { font-size: 2.5rem; margin-bottom: 16px; }
.welcome-title { font-size: 1.4rem; font-weight: 600; color: #d9efff; }
.welcome-text { margin-top: 8px; color: #91b4cc; }
@media (max-width: 640px) {
    .block-container { padding-top: 1.5rem; }
    .welcome { padding-top: 40px; }
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []


def clear_chat():
    st.session_state.messages = []


title_column, clear_column = st.columns([4, 1])
with title_column:
    st.title("AI Career Assistant")
    st.caption("Ask a question. Explore your next step.")
with clear_column:
    st.button("Clear chat", on_click=clear_chat, use_container_width=True)
st.divider()

welcome = st.empty()
if not st.session_state.messages:
    welcome.markdown("""
    <div class="welcome">
        <div class="welcome-icon">💬</div>
        <div class="welcome-title">How can I help you today?</div>
        <div class="welcome-text">Type your question below to get started.</div>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Type your message…")
if prompt and prompt.strip():
    welcome.empty()
    prompt = prompt.strip()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking…"):
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}]
                    + st.session_state.messages[-8:],
                    temperature=0.5,
                    max_completion_tokens=800,
                )
                answer = completion.choices[0].message.content
                if not answer or not answer.strip():
                    raise ValueError("Empty answer")
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except AuthenticationError:
            st.error("The API key is invalid. Update GROQ_API_KEY in your app's Secrets settings.")
        except RateLimitError:
            st.error("The free AI usage limit has been reached. Please try again later.")
        except APIConnectionError:
            st.error("Cannot reach the AI service right now. Please try again.")
        except APIStatusError as error:
            status = error.status_code
            if status == 403:
                st.error("Groq denied access (HTTP 403). Check your account and model permissions in Groq Console.")
            elif status == 404:
                st.error("The configured AI model was not found (HTTP 404). Check available models in Groq Console.")
            elif status == 400:
                st.error("Groq rejected the request (HTTP 400). Check the model and request settings.")
            elif status == 413:
                st.error("The conversation is too large (HTTP 413). Clear the chat and send a shorter message.")
            elif status >= 500:
                st.error(f"Groq is experiencing a service error (HTTP {status}). Please try again later.")
            else:
                st.error(f"Groq could not complete the request (HTTP {status}).")
            # Server logs only; never print the API key or request headers.
            body = error.body if isinstance(error.body, dict) else {}
            detail = body.get("error", {})
            code = detail.get("code", "unknown") if isinstance(detail, dict) else "unknown"
            print(f"Groq request failed: HTTP {status}, code={code}")
        except (ValueError, IndexError):
            st.error("The AI returned an empty response. Please try again.")
