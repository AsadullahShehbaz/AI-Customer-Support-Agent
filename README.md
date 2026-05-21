# Asadullah Shehbaz · AI-Customer-Support-RAG-Agent
**AI-powered portfolio with agentic rag chatbot** using FastAPI, LangGraph, Groq LLM, and FAISS vector search.\
![Try Now](https://asadullahshehbaz.up.railway.app/)
[![Hero Section](hero-section.png)](https://asadullahshehbaz.up.railway.app/ "target=_blank")
[![About Section](about-section.png)](https://asadullahshehbaz.up.railway.app/ "target=_blank")
[![AI Assistant](ai-assistant.png)](https://asadullahshehbaz.up.railway.app/ "target=_blank")

---

## 📦 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Uvicorn |
| AI Agent | LangGraph |
| LLM | Groq (GPT-OSS-120B) |
| Embeddings | HuggingFace `all-mpnet-base-v2` |
| Vector DB | FAISS |
| Frontend | HTML, CSS, JavaScript |

---

## 🚀 Quick Start

```bash
# 1. Clone & enter
git clone https://github.com/AsadullahShehbaz/AI-Customer-Support-RAG-Agent.git.git
cd portfolio-rag

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variable
# Create .env file with:
GROQ_API_KEY=your_api_key_here

# 5. Run server
uvicorn main:app --reload
```

Visit `http://localhost:8000`

---

## 📁 Project Structure

```
├── main.py              # FastAPI server + routes
├── rag_agent.py         # LangGraph RAG agent
├── static/              # Frontend assets
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── images/
├── resume.pdf           # Source for RAG (your resume)
├── requirements.txt
└── .env                 # API keys (gitignored)
```

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves portfolio HTML |
| POST | `/chat` | Chatbot endpoint |

**POST `/chat` example:**
```json
// Request
{ "message": "What are your skills?" }

// Response
{ "response": "I specialize in...", "status": "ok" }
```

---

## 🧠 How It Works

1. **Startup** — Loads `resume.pdf`, chunks it, builds FAISS vector store
2. **User asks** → Frontend sends POST to `/chat`
3. **LangGraph agent** decides to call `rag_tool`
4. **FAISS retrieves** top 4 relevant chunks
5. **Groq LLM** generates answer from context
6. **Response** returned to chat widget

---

## ☁️ Deployment (Railway)

```bash
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Push to GitHub, then deploy on Railway
```

Add `GROQ_API_KEY` in Railway dashboard → Variables.

---

## 📄 License

MIT — free to use and modify.

---

## 🤝 Connect

- **Email:** asadullahcreative@gmail.com
- **GitHub:** [@AsadullahShehbaz](https://github.com/AsadullahShehbaz)
- **Kaggle:** [#26 Global Dataset Grandmaster](https://www.kaggle.com/asadullahshehbaz)

---

*Built with FastAPI + LangGraph + Groq + FAISS* 🚀
