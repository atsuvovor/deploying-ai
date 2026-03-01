#tools_service3.py
from langchain.tools import tool
import math

@tool
def risk_calculator(loss: float, probability: float):
    """
    Calculates expected loss.
    """
    expected_loss = loss * probability
    return f"Expected loss is {expected_loss}"