import streamlit as st
import requests

st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🤖",
    layout="centered"
)

BACKEND_URL = "http://127.0.0.1:8000/chat"
HEALTH_URL = "http://127.0.0.1:8000/health"

st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
        color: #111827;
    }

    .block-container {
        max-width: 850px;
        padding-top: 2rem;
        padding-bottom: 7rem;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    h1 {
        color: #111827 !important;
        text-align: center;
        font-size: 28px !important;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #4b5563 !important;
        font-size: 14px;
        margin-bottom: 30px;
    }

    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 8px 0 !important;
        margin-bottom: 8px !important;
    }

    [data-testid="stChatMessage"] p {
        color: #111827 !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
    }

    [data-testid="stChatMessage"] li {
        color: #111827 !important;
    }

    [data-testid="stChatMessage"] strong {
        color: #111827 !important;
    }

    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
    }

    [data-testid="stChatInput"] > div {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 14px !important;
        box-shadow: none !important;
    }

    [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
        font-size: 15px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #6b7280 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
    }

    [data-testid="stSidebar"] p {
        color: #374151 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #111827 !important;
    }

    .stButton > button {
        width: 100%;
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
    }

    .stButton > button:hover {
        border-color: #2563eb !important;
        color: #2563eb !important;
    }

    .welcome {
        text-align: center;
        margin-top: 70px;
        margin-bottom: 30px;
    }

    .welcome-title {
        color: #111827 !important;
        font-size: 24px;
        font-weight: 600;
    }

    .status {
        background-color: #ecfdf5;
        color: #047857 !important;
        border: 1px solid #a7f3d0;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center;">
            <div style="font-size:40px;">🤖</div>
            <h2 style="color:#111827;">AI Career Assistant</h2>
            <p style="color:#4b5563;">
                Your AI assistant for learning,
                careers and professional development.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        "<h4 style='color:#111827;'>I can help with</h4>",
        unsafe_allow_html=True
    )

    st.write("💼 Career Guidance")
    st.write("🎓 Education")
    st.write("🤖 AI & Machine Learning")
    st.write("📊 Data Science")
    st.write("🐍 Python")
    st.write("📈 Data Analytics")
    st.write("📝 Resume & ATS")
    st.write("🎤 Interview Preparation")
    st.write("🔬 Science")
    st.write("💻 Technology")
    st.write("☤🩺 Medicine")
    st.write("🔍 Research")

    st.divider()

    st.markdown(
        "<h4 style='color:#111827;'>Backend Status</h4>",
        unsafe_allow_html=True
    )

    try:
        response = requests.get(
            HEALTH_URL,
            timeout=5
        )

        if response.status_code == 200:
            st.markdown(
                """
                <div class="status">
                    ● Backend Connected
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.error(
                f"Backend error: {response.status_code}"
            )

    except requests.exceptions.RequestException:
        st.error("Backend offline")

    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

st.markdown(
    "<h1>🤖 AI Career Assistant</h1>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Ask me anything about careers, education,
        AI, technology, science and more...
    </div>
    """,
    unsafe_allow_html=True
)

if len(st.session_state.messages) == 0:
    st.markdown(
        """
        <div class="welcome">
            <div class="welcome-title">
                👋 How can I help you today?
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

for message in st.session_state.messages:

    avatar = "👤" if message["role"] == "user" else "🤖"

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):
        st.markdown(message["content"])

user_input = st.chat_input("Ask anything...")

if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message(
        "user",
        avatar="👤"
    ):
        st.markdown(user_input)

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner("Thinking..."):

            try:

                recent_messages = (
                    st.session_state.messages[-2:]
                )

                response = requests.post(
                    BACKEND_URL,
                    json={
                        "messages": recent_messages
                    },
                    timeout=300
                )

                if response.status_code == 200:

                    data = response.json()

                    answer = data.get("answer")

                    if answer is None:
                        answer = data.get("response")

                    if answer is None:
                        answer = (
                            "Sorry, I couldn't generate "
                            "an answer."
                        )

                    st.markdown(answer)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                else:

                    st.error(
                        f"Backend error: "
                        f"{response.status_code}"
                    )

                    st.code(response.text)

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Cannot connect to FastAPI."
                )

                st.info(
                    "Start the backend using:"
                )

                st.code(
                    "uvicorn main:app --reload"
                )

            except requests.exceptions.Timeout:

                st.error(
                    "⏳ The AI took too long to respond."
                )

            except Exception as e:

                st.error(
                    f"Something went wrong: {str(e)}"
                )