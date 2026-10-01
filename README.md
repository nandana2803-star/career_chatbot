AI Career Assistant

A simple AI chatbot for career guidance, education, learning roadmaps, resumes, and interview preparation. Built with Streamlit, with a black and light blue interface.

The project supports two implementations:

- **Groq version:** the updated Streamlit app calls a hosted model directly. This is the version intended for deployment on Streamlit Community Cloud.
- **Original local version:** the original Streamlit app calls a FastAPI backend that runs Qwen locally using PyTorch and Transformers.

> The Groq app and its deployment requirements must be committed to this repository before following the Groq deployment steps. The original frontend uses a different request flow.

## Features

- Simple chat interface with session history and a clear-chat button.
- Career, course, skill development, resume, and interview guidance.
- Black background with light blue text and accents in the updated frontend.
- Groq version includes recent conversation context and handles connection, authentication, and usage-limit errors.
- Original backend includes health-check and chat endpoints.

## Project structure

```text
career_chatbot/
├── frontend/
│   └── app.py              # Streamlit chatbot UI
├── backend/
│   ├── main.py             # Original FastAPI endpoints and generation logic
│   └── model_loader.py     # Original local Qwen model loader
├── requirements.txt        # Dependencies for the selected implementation
└── README.md
```

## Run the Groq version locally

Requires Python 3.11 or later, a Groq account, and an API key.

### 1. Clone the repository

```bash
git clone https://github.com/nandana2803-star/career_chatbot.git
cd career_chatbot
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

For the Groq version, the root `requirements.txt` should contain:

```text
streamlit
groq
```

Install them:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure your API key

Create an API key at [Groq Console](https://console.groq.com/keys).

Create `.streamlit/secrets.toml` in the project root:

```toml
GROQ_API_KEY = "your-groq-api-key"
```

The updated app also accepts the `GROQ_API_KEY` environment variable. Keep your key private and never commit the secrets file.

### 5. Start the chatbot

```bash
streamlit run frontend/app.py
```

Open the local URL printed in the terminal. No FastAPI process is required for this version.

## Deploy on Streamlit Community Cloud

1. Commit the Groq version of `frontend/app.py` and the two-package `requirements.txt` to GitHub.
2. Sign in at [Streamlit Community Cloud](https://share.streamlit.io) with GitHub.
3. Create an app using these settings:

   | Setting | Value |
   |---|---|
   | Repository | `nandana2803-star/career_chatbot` |
   | Branch | `main` |
   | Main file path | `frontend/app.py` |

4. In **Advanced settings → Secrets**, add:

   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   ```

5. Deploy the app and share the public URL supplied by Streamlit.

Streamlit Community Cloud provides free hosting. Groq offers a free API tier with usage limits; availability and limits depend on the provider and your account. This setup does not require Render.

## How the Groq version works

```text
User → Streamlit app → Groq API → Streamlit chat response
```

The updated app uses `llama-3.3-70b-versatile`, includes a career guidance system prompt, and sends up to the latest eight conversation messages. Messages are stored in Streamlit session state, rather than a database. Clearing the chat removes the history from that session; history is not durably saved.

The `backend/` files can remain in the repository as the original local implementation. The Groq frontend does not import or call them.

## Original local FastAPI/Qwen version

Use this section only with the original frontend, or a frontend configured to call FastAPI. The Groq frontend will continue calling Groq even if you start the local backend.

The original backend uses:

- FastAPI and Uvicorn.
- PyTorch, Transformers, and Accelerate.
- `Qwen/Qwen2.5-1.5B-Instruct`, loaded in float32 on CPU.

Install the original dependencies in a separate environment if desired:

```bash
python -m pip install fastapi uvicorn pydantic torch transformers accelerate streamlit requests
```

From the repository root, start the backend:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

The first start downloads the model and requires an internet connection. Allow time for loading and sufficient RAM: float32 model weights alone require approximately 6 GB, with additional memory needed at runtime.

In another terminal, activate the same environment and start the original frontend:

```bash
streamlit run frontend/app.py
```

The original frontend targets `http://127.0.0.1:8000/chat` and checks `http://127.0.0.1:8000/health`.

### Backend endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Backend status message |
| GET | `/health` | Health check |
| POST | `/chat` | Generate an answer |

Example chat request:

```json
{
  "messages": [
    {"role": "user", "content": "How can I prepare for a job interview?"}
  ]
}
```

Example response shape:

```json
{
  "answer": "Generated career guidance appears here."
}
```

The original backend uses only the latest submitted message when building its model prompt. It does not use the full conversation history.

## Troubleshooting

| Problem | What to check |
|---|---|
| Missing API key | Add `GROQ_API_KEY` to Streamlit Secrets or the environment, then restart the app. |
| Invalid API key | Check the key in Secrets and replace it if needed. |
| Free usage limit reached | Wait and retry; review the limits in your Groq account. |
| Module not found during deployment | Confirm the committed requirements include `streamlit` and `groq`. |
| Cannot connect to FastAPI | You are running the original frontend. Start the local backend or switch to the Groq frontend. |
| Local model fails to load | Check available RAM, internet connectivity, and the backend terminal error. |

## Security and limitations

- Add `.streamlit/secrets.toml`, `.env`, `.venv/`, `venv/`, and `__pycache__/` to `.gitignore`.
- Never upload API keys to GitHub. Revoke and replace a key if it becomes exposed.
- Groq receives the conversation messages sent by the app. Avoid submitting sensitive personal information.
- AI answers can be inaccurate. Verify important course, job, salary, and admission information independently.
- The app does not browse the web or verify current information.
- The project does not currently include durable chat storage, user authentication, resume uploads, or document parsing.

## Documentation

- [Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Groq quickstart](https://console.groq.com/docs/quickstart)
- [Groq API rate limits](https://console.groq.com/docs/rate-limits)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Qwen model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)
