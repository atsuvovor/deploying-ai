#guardrails.py
from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState

FORBIDDEN_TOPICS = [
    "cat",
    "dog",
    "horoscope",
    "zodiac",
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
    "taylor swift",
    "taylor",
    "swift"
]

FORBIDDEN_META = [
    "system prompt",
    "ignore previous instructions",
    "reveal instructions",
]


def guardrails(state: MessagesState):
    """Blocks restricted topics before LLM is called."""

    last_message = state["messages"][-1].content.lower()

    # Topic blocking
    for word in FORBIDDEN_TOPICS:
        if word in last_message:
            return {
                "messages": [
                    AIMessage(content="This topic is restricted and cannot be discussed.")
                ]
            }

    # Prompt injection protection
    for word in FORBIDDEN_META:
        if word in last_message:
            return {
                "messages": [
                    AIMessage(content="Access to system-level instructions is denied.")
                ]
            }

    # If safe → pass state forward unchanged
    return state