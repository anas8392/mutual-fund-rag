from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
import os

# Import the generator from Phase 4
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phase4_generation')))
from generator import RAGGenerator

app = FastAPI(title="Mutual Fund RAG API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize generator once on startup to load model
try:
    generator = RAGGenerator()
except Exception as e:
    print(f"Failed to initialize generator: {e}")
    generator = None

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if generator is None:
        return ChatResponse(answer="Error: RAG Generator not initialized. Check API keys and DB.")
        
    try:
        answer = generator.generate_answer(request.query)
        return ChatResponse(answer=answer)
    except Exception as e:
        return ChatResponse(answer=f"Error generating answer: {str(e)}")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Mount the Phase 6 Frontend static directory
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phase6_frontend'))
app.mount("/assets", StaticFiles(directory=frontend_dir), name="assets")

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(frontend_dir, "index.html"))
