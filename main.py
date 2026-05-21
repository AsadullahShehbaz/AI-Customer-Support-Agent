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
import uvicorn

# ── Basic logging setup ──────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Railway uses PORT from environment ───────
PORT = int(os.getenv("PORT", 8080))

chatbot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot
    logger.info("🚀 Starting up — loading RAG chatbot...")
    try:
        chatbot = init_rag_chatbot()
        logger.info("✅ Chatbot ready!")
    except Exception as e:
        logger.error(f"❌ Failed to load chatbot: {e}")
        chatbot = None
    yield
    logger.info("🛑 Shutting down")

app = FastAPI(
    title="Asadullah Portfolio Chatbot API",
    lifespan=lifespan
)

# ── CORS (allow all for Railway) ─────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files mount ──────────────────────
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"✅ Static files mounted from /{static_dir}")
else:
    logger.warning(f"⚠️ {static_dir} folder not found!")
    # Create static directory if it doesn't exist
    os.makedirs(static_dir, exist_ok=True)
    logger.info(f"📁 Created {static_dir} directory")

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
    logger.info("📄 Serving index page")
    
    # Check common paths
    index_paths = [
        "static/index.html",
        "index.html",
        "./static/index.html",
    ]
    
    for path in index_paths:
        if os.path.exists(path):
            logger.info(f"✅ Found index at: {path}")
            return FileResponse(path)
    
    # If no index.html, return simple message
    logger.error("❌ index.html not found")
    return {"message": "Portfolio site is running", "status": "ok", "endpoints": ["/chat", "/health", "/debug"]}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy", 
        "chatbot_ready": chatbot is not None,
        "port": PORT
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint for testing"""
    return {"pong": True}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"💬 Received: {request.message[:50]}...")
    
    if chatbot is None:
        logger.error("❌ Chatbot not ready")
        raise HTTPException(status_code=503, detail="Chatbot is initializing, please try again")
    
    if not request.message.strip():
        logger.warning("⚠️ Empty message received")
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        reply = get_reply(chatbot, request.message)
        logger.info(f"✅ Response sent ({len(reply)} chars)")
        return ChatResponse(response=reply)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug")
async def debug():
    """Debug endpoint"""
    import os
    files = os.listdir(".")
    static_exists = os.path.exists("static")
    static_files = os.listdir("static") if static_exists else []
    index_exists = os.path.exists("static/index.html")
    
    return {
        "cwd": os.getcwd(),
        "port": PORT,
        "chatbot_ready": chatbot is not None,
        "static_exists": static_exists,
        "static_files": static_files[:10],
        "index_exists": index_exists,
        "all_files": files[:20]
    }

# ── Main entry point for Railway ────────────
if __name__ == "__main__":
    logger.info(f"🚀 Starting server on port {PORT}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False  # Important: reload=False for production
    )