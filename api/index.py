from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import evaluate_task

app = FastAPI(title="AI Automation Responsibility Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskInput(BaseModel):
    text: str


class TaskOutput(BaseModel):
    decision: str
    responsibility: str
    explanation: str


@app.get("/")
def root():
    return {"status": "AIRE backend is running"}


@app.post("/analyze", response_model=TaskOutput)
def analyze_task(data: TaskInput):
    decision, role, explanation = evaluate_task(data.text)
    return {
        "decision": decision,
        "responsibility": role,
        "explanation": explanation
    }
