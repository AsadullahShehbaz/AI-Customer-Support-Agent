# ─────────────────────────────────────────────
#  main.py  —  FastAPI server for Railway deployment
# ─────────────────────────────────────────────

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from rag_agent import init_rag_chatbot, get_reply
import os
import logging

# ── Basic logging setup ──────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Railway uses PORT 8080, not 8000 ─────────
PORT = int(os.getenv("PORT", 8080))

chatbot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot
    logger.info("🚀 Starting up — loading RAG chatbot...")
    chatbot = init_rag_chatbot()
    logger.info("✅ Chatbot ready!")
    yield
    logger.info("🛑 Shutting down")

app = FastAPI(
    title="Asadullah Portfolio Chatbot API",
    lifespan=lifespan
)

# ── CORS (relaxed for Railway) ──────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files mount ──────────────────────
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("✅ Static files mounted from /static")
else:
    logger.warning("⚠️ static folder not found!")

# ── Models ──────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str = "portfolio_visitor"

class ChatResponse(BaseModel):
    response: str
    status: str = "ok"

# ── Routes ──────────────────────────────────

@app.get("/")
async def serve_index():
    """Serve the portfolio HTML"""
    possible_paths = [
        "static/index.html",
        "index.html",
        "./static/index.html",
        "../static/index.html"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"✅ Serving index from: {path}")
            return FileResponse(path)
    
    logger.error("❌ index.html not found in any location!")
    return {"error": "Index file not found", "paths_checked": possible_paths}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "chatbot_ready": chatbot is not None}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if chatbot is None:
        logger.error("Chatbot not ready")
        raise HTTPException(status_code=503, detail="Chatbot not ready")
    
    if not request.message.strip():
        logger.warning("Empty message received")
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        logger.info(f"💬 Chat request: {request.message[:50]}...")
        reply = get_reply(chatbot, request.message)
        logger.info(f"✅ Response sent ({len(reply)} chars)")
        return ChatResponse(response=reply)
    except Exception as e:
        logger.error(f"❌ Error in /chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ── Debug endpoint (optional) ────────────────
@app.get("/debug")
async def debug():
    """Debug endpoint to see what files exist"""
    files = os.listdir(".")
    static_files = os.listdir("static") if os.path.exists("static") else []
    
    return {
        "current_directory": os.getcwd(),
        "files": files[:20],
        "static_folder_exists": os.path.exists("static"),
        "static_files": static_files[:10],
        "index_exists": os.path.exists("static/index.html")
    }