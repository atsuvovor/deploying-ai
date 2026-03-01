# main.py

from langgraph.graph import StateGraph, MessagesState, START
from langchain.chat_models import init_chat_model
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
import os
from pathlib import Path
from utils.logger import get_logger

# -----------------------------
# Load environment secrets
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / ".secrets")

_logs = get_logger(__name__)

# -----------------------------
# Initialize chat model with explicit API key
# -----------------------------
api_key = os.getenv("API_GATEWAY_KEY")
if not api_key:
    raise RuntimeError(
        "API_GATEWAY_KEY not found in environment. Make sure it is in .secrets"
    )

chat_agent = init_chat_model(
    "gpt-4o-mini",
    model_provider="openai",
    base_url="https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
    default_headers={"x-api-key": api_key},
)

# -----------------------------
# Import tools safely
# -----------------------------
try:
    from assignment_chat.tools_animals import get_cat_facts, get_dog_facts
except Exception:
    get_cat_facts = get_dog_facts = lambda *args, **kwargs: "Animal tool unavailable"

try:
    from assignment_chat.tools_horoscope import get_horoscope
except Exception:
    get_horoscope = lambda *args, **kwargs: "Horoscope tool unavailable"

try:
    from assignment_chat.tools_music import recommend_albums
except Exception:
    recommend_albums = lambda *args, **kwargs: "Music tool unavailable"

try:
    from assignment_chat.tools_service3 import risk_calculator
except Exception:
    risk_calculator = lambda *args, **kwargs: "Risk tool unavailable"

try:
    from assignment_chat.prompts import return_instructions
    instructions = return_instructions()
except Exception:
    instructions = "You are an AI assistant. Respond concisely."

try:
    from assignment_chat.guardrails import guardrails
except Exception:
    guardrails = lambda state: state  # no-op fallback

# -----------------------------
# CHROMA_MODE
# -----------------------------
chroma_mode = "local"  # Using local embeddings with music_reviews collection
_logs.info(f"CHROMA_MODE={chroma_mode}")

# -----------------------------
# Tools list
# -----------------------------
tools = [get_cat_facts, get_dog_facts, recommend_albums, get_horoscope, risk_calculator]

# -----------------------------
# LLM call node
# -----------------------------
def call_model(state: MessagesState):
    """LLM decides whether to call a tool or not"""
    try:
        response = chat_agent.bind_tools(tools).invoke(
            [SystemMessage(content=instructions)] + state["messages"]
        )
        return {"messages": [response]}
    except Exception as e:
        _logs.error(f"LLM call failed: {e}")
        return {"messages": [{"content": "Error: LLM call failed."}]}

# -----------------------------
# Build graph
# -----------------------------
def get_graph():
    builder = StateGraph(MessagesState)

    # Add nodes
    builder.add_node("guardrails", guardrails)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))

    # Edges
    builder.add_edge(START, "guardrails")
    builder.add_edge("guardrails", "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")

    graph = builder.compile()
    return graph