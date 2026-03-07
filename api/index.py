from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from engine import evaluate_task

app = FastAPI(title="AI Automation Responsibility Engine")

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        response = JSONResponse(content={})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

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

@app.options("/analyze")
def analyze_options():
    return JSONResponse(content={}, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    })
