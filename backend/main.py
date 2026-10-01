import time
import torch

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from backend.model_loader import tokenizer, model


app = FastAPI(
    title="AI Career Assistant",
    description="AI Career Assistant powered by Qwen",
    version="1.0"
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "AI Career Assistant Backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    start_time = time.time()

    if not request.messages:
        return {
            "answer": "Please enter a question."
        }

    system_prompt = """
You are a general career guidance assistant.

Your job is to help users with careers, education,
courses, jobs, skills, higher studies, study abroad,
career changes, interviews and future career planning.

Important:

- Give practical and balanced advice.
- Do not assume the user wants a technology career.
- Consider different fields such as technology,
  healthcare, business, finance, education, science,
  engineering, government, law, design and other fields.
- Do not recommend AI, Data Science or Programming
  unless relevant to the question.
- Do not claim that one career is the best for everyone.
- For broad questions, provide useful options with
  a short explanation of each.
- Give approximately 5-8 relevant options when appropriate.
- Explain why each option may be useful.
- For study-abroad questions, discuss countries,
  study options, important factors and career prospects.
- For course questions, discuss major course areas,
  skills gained and possible career paths.
- For roadmap questions, organize the answer into
  clear steps or stages.
- For roadmap questions, include relevant skills,
  tools, projects, experience and job preparation.
- Give enough detail to make the roadmap useful,
  but avoid unnecessary repetition.
- Complete every point before moving to the next point.
- Always finish the current sentence before ending
  the response.
- Do not stop in the middle of a sentence, bullet point,
  numbered point, heading or explanation.
- If the answer is becoming too long, summarize the
  remaining points briefly instead of stopping abruptly.
- Always provide a complete and coherent answer.
- Do not invent statistics, salaries, rankings or
  university information.
- Do not end the answer in the middle of a sentence.
"""

    latest_message = request.messages[-1]

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": latest_message.content
        }
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    device = next(model.parameters()).device

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    print("=" * 50)
    print("Question:", latest_message.content)
    print("Device:", device)
    print(
        "Prompt tokens:",
        inputs["input_ids"].shape[1]
    )

    generation_start = time.time()

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=False,
            repetition_penalty=1.05,
            use_cache=True
    )

    generation_time = time.time() - generation_start

    generated_tokens = outputs[0][
        inputs["input_ids"].shape[1]:
    ]

    answer = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    ).strip()

    if not answer:
        answer = "Sorry, I couldn't generate an answer."

    total_time = time.time() - start_time

    print(
        "Generation time:",
        round(generation_time, 2),
        "seconds"
    )

    print(
        "Total time:",
        round(total_time, 2),
        "seconds"
    )

    print("=" * 50)

    return {
        "answer": answer
    }