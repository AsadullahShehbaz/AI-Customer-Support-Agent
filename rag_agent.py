# ── 1. Imports ──────────────────────────────
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated, TypedDict, List
from prompt import SYSTEM_PROMPT
from dotenv import load_dotenv
import os
import logging
from google import genai
from langchain.embeddings.base import Embeddings

# ── 2. Setup ────────────────────────────────
load_dotenv()

logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ── 3. Google Embeddings Class ──────────────
class GoogleGenAIEmbeddings(Embeddings):
    """Google Gemini embeddings wrapper for LangChain"""
    
    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        embeddings = []
        for text in texts:
            # Truncate to 2048 tokens max (Google's limit)
            text = text[:8000]  # Roughly 2000 tokens
            result = self.client.models.embed_content(
                model=self.model,
                contents=text
            )
            embeddings.append(result.embeddings[0].values)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        result = self.client.models.embed_content(
            model=self.model,
            contents=text
        )
        return result.embeddings[0].values

# ── 4. LLM setup ────────────────────────────
llm = ChatGroq(model="openai/gpt-oss-120b")

# ── 5. Configuration ────────────────────────
PDF_PATH = "./resume.pdf"
VECTOR_STORE_PATH = "./faiss_index"

# Initialize Google embeddings (no local model = minimal memory!)
embeddings = GoogleGenAIEmbeddings(
    api_key=os.getenv("GOOGLE_API_KEY")  # You need this in .env
)

# ── 6. Load or create vector store ──────────
def get_vector_store():
    """Load existing FAISS index or create new one from PDF"""
    
    if os.path.exists(VECTOR_STORE_PATH):
        print(f"📂 Loading existing vector store from {VECTOR_STORE_PATH}")
        vector_store = FAISS.load_local(
            VECTOR_STORE_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        print("✅ Vector store loaded from disk")
    else:
        print(f"📄 Creating new vector store from {PDF_PATH}")
        print("📡 Using Google Embeddings API (no local model needed)")
        
        loader = PyPDFLoader(PDF_PATH)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        print(f"✅ Loaded {len(docs)} pages → {len(chunks)} chunks")
        
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(VECTOR_STORE_PATH)
        print(f"✅ Vector store saved to {VECTOR_STORE_PATH}")
    
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )
    return retriever

# ── 7. RAG tool ─────────────────────────────
def make_rag_tool(retriever):
    @tool
    def rag_tool(query: str) -> dict:
        """Retrieve relevant information about Asadullah from his resume PDF."""
        results = retriever.invoke(query)
        context = [doc.page_content for doc in results]
        return {"query": query, "context": context}
    return rag_tool

# ── 8. LangGraph state ──────────────────────
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ── 9. Build the LangGraph chatbot ──────────
def build_chatbot(rag_tool):
    tools = [rag_tool]
    llm_with_tools = llm.bind_tools(tools)

    def chat_node(state: ChatState):
        from langchain_core.messages import SystemMessage
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(ChatState)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")

    chatbot = graph.compile()
    print("✅ LangGraph chatbot compiled")
    return chatbot

# ── 10. Get reply ───────────────────────────
def get_reply(chatbot, user_message: str) -> str:
    response = chatbot.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    return response["messages"][-1].content

# ── 11. One-time initialization ─────────────
def init_rag_chatbot():
    retriever = get_vector_store()
    rag_tool = make_rag_tool(retriever)
    chatbot = build_chatbot(rag_tool)
    return chatbot

# ── 12. CLI test ────────────────────────────
if __name__ == "__main__":
    retriever = get_vector_store()
    rag_tool = make_rag_tool(retriever)
    chatbot = build_chatbot(rag_tool)
    print("Chatbot ready! Type 'quit' to exit.")
    
    while True:
        user_message = input("You: ")
        if user_message.lower() == 'quit':
            break
        reply = get_reply(chatbot, user_message)
        print("AI:", reply)