# ACP Hospital Insurance Agents

This repository provides a set of AI agent systems for **insurance and hospital automation**, using Retrieval-Augmented Generation (RAG) and large language models (LLMs) via Groq. It includes components for policy question-answering, hierarchical agent orchestration, and a simple health Q&A agent.

## File Overview

| File            | Description                                                                                     |
|-----------------|------------------------------------------------------------------------------------------------|
| `rag_system.py` | RAG-based server for answering insurance policy questions with LLMs and FAISS vector store.     |
| `seqchain.py`   | Hierarchical agent workflow client, orchestrating queries among hospital and insurer agents.    |
| `smolagent.py`  | Minimal health-question agent server powered directly by Groq's language models.                |

## 1. rag_system.py

**Purpose:**  
Creates a **Policy RAG System** that answers insurance policy questions using Retriever-Augmented Generation with PDF-based document retrieval and Groq-powered LLM responses.

**Main Features:**
- Loads hospital policy PDF, splits it, and creates a FAISS vectorstore for semantic search.
- Uses HuggingFace embeddings and Groq (llama3-8b-8192) for answer synthesis.
- Runs as an `acp_sdk.server.Server` agent on port *8001*.
- API accepts user questions and returns contextified policy answers.

**Key dependencies:**
- `faiss`, `langchain`, `acp_sdk`, `groq`, `dotenv`, `nest_asyncio`, `PyPDFLoader`, `sentence-transformers`

**Setup & Run:**
1. Place `hospital.pdf` at the configured path or set a new path in the `PolicyRAGSystem` init.
2. Set environment variables, especially `GROQ_API_KEY`.
3. Start the server:
   ```bash
   python rag_system.py
   ```
   The Policy Agent Server will listen on **port 8001**.

## 2. seqchain.py

**Purpose:**  
Orchestrates **multi-agent workflows** between insurance and hospital agents via the ACP protocol.

**Main Features:**
- Discovers and coordinates agents running on local ports (expects `rag_system.py` and a compatible hospital agent running).
- Adapts user queries into Groq LLM prompts (llama3-70b-8192).
- Produces dialog output with agent discovery, query, and final answer.
- Example workflow question included: rehabilitation and waiting period after shoulder reconstruction.

**Key dependencies:**
- `fastacp`, `acp_sdk`, `colorama`, `groq`, `dotenv`, `nest_asyncio`

**Setup & Run:**
1. Ensure both `rag_system.py` and a hospital agent are running.
2. Start the workflow orchestrator:
   ```bash
   python seqchain.py
   ```
   Output includes agent discovery and final result.

## 3. smolagent.py

**Purpose:**  
A **lightweight agent server** that sends user health questions directly to Groq LLM for answers.

**Main Features:**
- Minimal logic; no document retrieval or vector search.
- Serves as a simple health Q&A server (llama3-8b-8192).
- Error handling for empty inputs and exceptions.

**Key dependencies:**
- `acp_sdk`, `groq`, `dotenv`, `nest_asyncio`

**Setup & Run:**
1. Set `GROQ_API_KEY` in environment variables.
2. Start the server:
   ```bash
   python smolagent.py
   ```
   The server listens on **port 8000**.

## Environment Variables

- `GROQ_API_KEY`: **Required** for using Groq LLM APIs.

## Installation

```bash
pip install faiss-cpu langchain sentence-transformers groq acp_sdk fastacp python-dotenv colorama nest_asyncio
```

## Example Workflow

1. Run `smolagent.py` (port 8000).
2. Run `rag_system.py` (port 8001).
3. Execute `seqchain.py` to test hierarchical querying and agent collaboration.

## Notes

- PDF file location and port values can be modified to fit deployment needs.
- Vector store for RAG is cached locally for fast restarts.
- For production, update paths and environment variable management as required.

