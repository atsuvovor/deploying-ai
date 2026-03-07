"""
guardrails.py

This module defines a guardrails node for the LangGraph workflow.
It blocks:
1. Restricted content topics (e.g., animals, zodiac, celebrities)
2. Prompt injection attempts targeting system instructions

If a violation is detected, it appends a safe AI response and stops
the unsafe content from reaching the LLM.
"""

from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState


# Topics that are not allowed to be discussed
FORBIDDEN_TOPICS = [
    "cat", "dog",
    "horoscope", "zodiac",
    "aries", "taurus", "gemini", "cancer", "leo",
    "virgo", "libra", "scorpio", "sagittarius",
    "capricorn", "aquarius", "pisces",
    "taylor swift", "taylor", "swift"
]

# Phrases commonly used in prompt injection attempts
FORBIDDEN_META = [
    "system prompt",
    "ignore previous instructions",
    "reveal instructions",
]


def guardrails(state: MessagesState):
    """
    Guardrails node that runs BEFORE the LLM.
    It inspects the most recent user message and:
    - Blocks restricted topics
    - Blocks attempts to access system-level instructions
    If blocked, it appends a safe AI response to the message history.
    If safe, it returns the state unchanged.
    """

    # Get the most recent user message and normalize it
    last_message = state["messages"][-1].content.lower()

    # ---- Topic Blocking ----
    for word in FORBIDDEN_TOPICS:
        if word in last_message:
            return {
                # Preserve full conversation history
                "messages": state["messages"] + [
                    AIMessage(
                        content="This topic is restricted and cannot be discussed."
                    )
                ]
            }

    # ---- Prompt Injection Protection ----
    for word in FORBIDDEN_META:
        if word in last_message:
            return {
                # Preserve full conversation history
                "messages": state["messages"] + [
                    AIMessage(
                        content="Access to system-level instructions is denied."
                    )
                ]
            }

    # If no violations are found, pass state forward unchanged
    return state