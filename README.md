# Strands Agent API

Strands Agent API is a FastAPI-based service that exposes a multi-agent system capable of answering questions using a combination of custom tools, GitHub Copilot, AWS documentation, and Kubernetes MCP integrations. It leverages session management and supports conversational context.

## Features

- Multi-agent orchestration with custom and external tools
- Session-based context management
- Integration with GitHub Copilot MCP, AWS Docs MCP, and Kubernetes MCP
- Extensible toolset (calculator, current time, document retrieval, etc.)
- FastAPI endpoint for question answering
- Streamlit frontend for interactive conversations

## Requirements

- Python 3.8+
- Environment variables:
  - `GEMINI_API_KEY` (for Gemini model)
  - `GITHUB_TOKEN` (for GitHub MCP)
  - Optionally, `KUBECONFIG` for Kubernetes MCP

## Installation

```sh
pip install -r requirements.txt
```

## Running the API Server

Start the FastAPI server:

```sh
python agent.py
```

Or with uvicorn directly:

```sh
uvicorn agent:app --host 0.0.0.0 --port 8000
```

## Running the Streamlit Frontend

To interact with the agent via a web interface, start the Streamlit app (usually in `streamlit_app.py`):

```sh
streamlit run streamlit_app.py
```

- By default, Streamlit runs at [http://localhost:8501](http://localhost:8501).
- The Streamlit app communicates with the FastAPI backend at `http://localhost:8000`.

## Interacting with the Agent

### Using Streamlit

1. Open [http://localhost:8501](http://localhost:8501) in your browser.
2. Enter your question in the chat interface.
3. The agent will respond using its available tools and integrations.

### Using the API Directly

#### POST `/question`

Ask a question to the agent:

**Request Body:**
```json
{
  "question": "What is the current time?",
  "session_id": "your-session-id"
}
```

**Response:**
```json
{
  "message": "The current time is 2024-06-01T12:34:56Z"
}
```

You can use `curl` or any HTTP client:

```sh
curl -X POST http://localhost:8000/question \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the current time?", "session_id": "your-session-id"}'
```

## Tooling

The agent uses the following tools:

- Calculator
- Current time
- Document retrieval
- GitHub Copilot MCP tools
- AWS Docs MCP tools
- Kubernetes MCP tools

## Extending

To add new tools, modify the `tools` list in [`agent.py`](strands-agent-api/agent.py) and implement the tool following the Strands tool interface.

## Development

- See [`agent.py`](strands-agent-api/agent.py) for main entrypoint and agent orchestration.
- See [`tools.py`](strands-agent-api/tools.py) for custom tool examples.

---

For more details, see the code in [`strands-agent-api`](strands-agent-api/agent.py).