# Strands Agent API

Strands Agent API is a FastAPI-based service that exposes a multi-agent system capable of answering questions using a combination of custom tools, MCP (Model Context Protocol) integrations, and Agent-to-Agent (A2A) delegation. It leverages session management, conversational context, and intelligent task routing to specialized agents.

## Features

- **Multi-Agent Orchestration**: Coordinates multiple specialized agents for different domains
- **Agent-to-Agent (A2A) Integration**: Delegates platform engineering and cloud-native tasks to specialized agents
- **MCP Integrations**: 
  - GitHub Copilot MCP for code assistance and documentation
  - AWS Documentation MCP for AWS service information
- **Session-Based Context Management**: Maintains conversation history and state across requests
- **Built-in Tools**: Calculator, current time, document retrieval, and more
- **FastAPI Backend**: RESTful API with async support
- **Streamlit Frontend**: Interactive web interface for conversations

## Requirements

- Python 3.8+
- `strands-agents` package with A2A support
- `strands-agents-tools` and tools extras
- Environment variables:
  - `GEMINI_API_KEY` (for Gemini 2.5 Flash model)
  - `GITHUB_TOKEN` (for GitHub Copilot MCP access; get one [here](https://github.com/settings/personal-access-tokens))
  - `A2A_AGENT_URLS` (optional; comma-separated list of A2A agent endpoints; defaults to `http://127.0.0.1:8083/api/a2a/default/platform-engineering-bot`)

## Installation

```sh
pip install -r api/requirements.txt
```

**API Requirements:**
- `strands-agents[a2a]` - Core agent framework with A2A support
- `strands-agents-tools` - Tool utilities and helpers
- `strands-agents[litellm]` - LiteLLM model provider
- `strands-agents-tools[a2a_client]` - A2A client tool provider
- `kubectl-mcp-tool` - Kubernetes MCP integration

## Running the API Server

### Quick Start

Set required environment variables:

```sh
export GEMINI_API_KEY="your-gemini-api-key"
export GITHUB_TOKEN="your-github-personal-access-token"
# Optional - configure A2A agent URLs
export A2A_AGENT_URLS="http://127.0.0.1:8083/api/a2a/default/platform-engineering-bot"
```

Start the FastAPI server:

```sh
cd api
python agent.py
```

Or with uvicorn directly:

```sh
uvicorn agent:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

## Running the Streamlit Frontend

To interact with the agent via a web interface, start the Streamlit app:

```sh
cd streamlit-frontend
pip install -r requirements.txt
streamlit run main.py
```

- By default, Streamlit runs at [http://localhost:8501](http://localhost:8501).
- The Streamlit app communicates with the FastAPI backend at `http://localhost:8000`.
- Enter your name and start chatting with the agent.

## Interacting with the Agent

### Using Streamlit

1. Open [http://localhost:8501](http://localhost:8501) in your browser.
2. Enter your name (used as session ID).
3. Type your question in the chat input.
4. The agent will respond, potentially delegating to specialized agents for platform engineering questions.

### Using the API Directly

#### POST `/question`

Ask a question to the agent and maintain session context:

**Request Body:**
```json
{
  "question": "What is the current time?",
  "session_id": "user-session-id"
}
```

**Response:**
```json
"The current time is 2024-06-01T12:34:56Z"
```

**Example with curl:**

```sh
curl -X POST http://localhost:8000/question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the current time?",
    "session_id": "my-session-id"
  }'
```

The response includes the agent's answer, which may utilize:
- Built-in tools (calculator, current time)
- MCP integrations (GitHub Copilot, AWS Docs)
- A2A delegation to specialized agents

## Tooling & Integrations

The agent is equipped with multiple tools and integrations:

### Built-in Tools
- **Calculator** - Perform mathematical operations
- **Current Time** - Get the current date and time
- **Document Retrieval** - Retrieve relevant documents

### MCP (Model Context Protocol) Integrations
- **GitHub Copilot MCP** - Access code assistance and GitHub documentation
- **AWS Documentation MCP** - Query AWS service documentation and best practices

### Agent-to-Agent (A2A) Integration
The agent can delegate tasks to specialized agents through A2A communication:
- **Platform Engineering Bot** - Handles Kubernetes, AWS EKS, and cloud-native infrastructure questions
- Configurable via `A2A_AGENT_URLS` environment variable
- Automatic delegation based on question context

## Extending

### Adding New Tools

To add new tools to the agent, modify the `tools` list in [`api/agent.py`](api/agent.py):

```python
from strands import tool

@tool
def my_custom_tool(param: str) -> str:
    """Description of what the tool does."""
    return f"Result: {param}"

tools = [calculator, current_time, retrieve, my_custom_tool]
```

### Configuring A2A Agents

Set the `A2A_AGENT_URLS` environment variable to point to your A2A agents:

```sh
export A2A_AGENT_URLS="http://agent-host:8083/api/a2a/default/agent-name"
```

Multiple agents can be configured as a comma-separated list.

### Using Different Models

The agent currently uses Gemini 2.5 Flash via LiteLLM. To use a different model, modify the `model_id` in [`api/agent.py`](api/agent.py):

```python
model = LiteLLMModel(
    model_id="your-provider/your-model",
    ...
)

## Development

- **Main Agent Logic**: [`api/agent.py`](api/agent.py) - Agent orchestration, tool registration, and request handling
- **Custom Tools**: [`api/tools.py`](api/tools.py) - Custom tool implementations
- **Frontend**: [`streamlit-frontend/main.py`](streamlit-frontend/main.py) - Interactive Streamlit interface
- **Session Management**: File-based session storage for maintaining conversation context across requests

### System Prompt

The agent operates under a system prompt that instructs it to:
- Use available tools intelligently to answer questions
- Delegate platform engineering and cloud-native questions to A2A agents
- Cite sources when providing information from external documents
- Think step-by-step when solving problems

## Architecture

```
┌─────────────────────────┐
│   Streamlit Frontend    │
│  (Port 8501)            │
└────────────┬────────────┘
             │ HTTP
             ▼
┌─────────────────────────┐
│   FastAPI Backend       │
│   (Port 8000)           │
│  ┌──────────────────┐   │
│  │  Strands Agent   │   │
│  └────────┬─────────┘   │
└───────────┼─────────────┘
            │
      ┌─────┴─────┬──────────┬──────────────┐
      ▼           ▼          ▼              ▼
  ┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
  │ Tools  │ │GitHub  │ │   AWS    │ │   A2A    │
  │(Calc,  │ │Copilot │ │   Docs   │ │ Agents   │
  │ Time)  │ │  MCP   │ │   MCP    │ │          │
  └────────┘ └────────┘ └──────────┘ └──────────┘
```

---

For more details, see the code files in the [`api/`](api/) and [`streamlit-frontend/`](streamlit-frontend/) directories.