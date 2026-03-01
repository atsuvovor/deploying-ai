# Assignment 2 – Conversational AI System

## Overview

This implementation provides a conversational AI system built using LangGraph and tool-based architecture. The assistant supports three core services:

1. API-based services (facts + astrology)
2. Semantic search over music reviews
3. Custom risk analysis service

The system is implemented entirely in the assignment_chat folder as required.



## Architecture

The system uses LangGraph with the following flow:

START → Guardrails → LLM → Tools (conditional) → LLM

### Guardrails

Guardrails execute before model invocation and:

* Block restricted topics (cats, dogs, horoscopes, zodiac signs, Taylor Swift)
* Prevent prompt injection
* Prevent system prompt exposure


If a violation is detected, the system returns a safe response without calling the LLM.



## Services

### Service 1: API Tools

Implemented in:

* tools_animals.py
* tools_horoscope.py

These tools call external APIs using requests and return structured responses.



### Service 2: Semantic Music Search

Implemented in:

* tools_music.py

This service:

* Uses ChromaDB running via Docker
* Uses OpenAI embeddings
* Retrieves album reviews
* Fetches additional metadata from PostgreSQL

The LLM generates recommendations using retrieved results.



### Service 3: Risk Calculator

Implemented in:

* tools_service3.py

This tool calculates expected loss:

Expected Loss = Loss × Probability

This demonstrates custom tool integration.



## User Interface

The chat interface is implemented using Gradio.

The app:

* Converts Gradio messages into LangChain message objects
* Maintains conversation history
* Tracks LLM call count
* Returns the final assistant message



## Design Decisions

* Guardrails are executed before model invocation for safety.
* Tools are routed using LangGraph’s ToolNode.
* System prompt instructions enforce tone and formatting.
* The system is modular to allow additional services.


## How to Run

### 1. Start Docker

Open Docker Desktop.

### 2. Start Chroma + PostgreSQL

From the folder containing docker-compose.yml:


docker compose up -d


### 3. Set Environment Variable

In 05_src:


$env:CHROMA_MODE="local"


### 4. Run the App


python -m assignment_chat.app


The Gradio interface will open in the browser.



## Testing Examples

General chat:

* “Hello, course chat!”

Animals:

* “Tell me a cat fact.”

Horoscope:

* “What’s the horoscope for Leo?”

Music:

* “Recommend me an album.”

Risk:

* “Calculate risk for loan amount $10,000.”

Conversation memory:

* Ask a question, then request a follow-up.



## Challenges & Workarounds

**1. Chat returned “Error” for all prompts**
Cause: API key not properly loaded.
Fix: Ensure .deploying-ai-env and .secrets are loaded with load_dotenv() and the key is available via `os.getenv().

**2. Chroma not working**
Cause: CHROMA_MODE not set.
Fix: Set:


$env:CHROMA_MODE="local"


**3. Docker services not running**
Music search fails if containers are down.
Fix: Always run docker compose up -d before launching the app.

**4. DummyCollection behavior**
If embeddings are unavailable, music search returns placeholder results.
This is expected in development mode.



## Requirements

* Docker running
* ChromaDB container active
* PostgreSQL active
* .env and .secrets configured
* Valid API_GATEWAY_KEY
* CHROMA_MODE="local"

