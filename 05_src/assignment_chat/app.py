# app.py
import sys
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from assignment_chat.main import get_graph
from langchain_core.messages import HumanMessage, AIMessage
import gradio as gr
from dotenv import load_dotenv
from utils.logger import get_logger

_logs = get_logger(__name__)

# -----------------------------
# Load environment secrets
# -----------------------------
load_dotenv(BASE_DIR / ".secrets")
load_dotenv(BASE_DIR / ".env")

# -----------------------------
# Initialize LLM graph
# -----------------------------
try:
    llm = get_graph()
except Exception as e:
    _logs.error(f"Failed to initialize LLM graph: {e}")
    llm = None  # fallback to prevent crashes

# -----------------------------
# Chat callback for Gradio
# -----------------------------
def course_chat(message: str, history: list[dict] = None) -> str:
    if history is None:
        history = []

    langchain_messages = []
    n = 0
    _logs.debug(f"History: {history}")

    for msg in history:
        if msg.get('role') == 'user':
            langchain_messages.append(HumanMessage(content=msg['content']))
        elif msg.get('role') == 'assistant':
            langchain_messages.append(AIMessage(content=msg['content']))
            n += 1

    langchain_messages.append(HumanMessage(content=message))
    state = {"messages": langchain_messages, "llm_calls": n}

    try:
        if llm:
            response = llm.invoke(state)
            return response['messages'][-1].content
        else:
            return "LLM not initialized. Cannot generate a response."
    except Exception as e:
        _logs.error(f"LLM invocation failed: {e}")
        return "Error: could not generate a response."

# -----------------------------
# Launch Gradio chat interface
# -----------------------------
chat = gr.ChatInterface(fn=course_chat)

if __name__ == "__main__":
    _logs.info(f"Starting Course Chat App with CHROMA_MODE={os.getenv('CHROMA_MODE', 'undefined')}")
    chat.launch()