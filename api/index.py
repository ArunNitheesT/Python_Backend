from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from engine import evaluate_task

app = FastAPI(title="AI Automation Responsibility Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class TaskInput(BaseModel):
    text: str


class TaskOutput(BaseModel):
    decision: str
    responsibility: str
    explanation: str


@app.get("/")
def serve_home():
    return FileResponse("static/index.html")


@app.get("/audit")
def serve_audit():
    return FileResponse("static/audit.html")


@app.post("/analyze", response_model=TaskOutput)
def analyze_task(data: TaskInput):
    decision, role, explanation = evaluate_task(data.text)
    return {
        "decision": decision,
        "responsibility": role,
        "explanation": explanation
    }
