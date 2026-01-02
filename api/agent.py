import logging
from mcp import stdio_client, StdioServerParameters
from strands.session.file_session_manager import FileSessionManager
from strands_tools import retrieve
from strands_tools.calculator import calculator
from strands_tools.current_time import current_time
from strands_tools.mcp_client import MCPClient
from strands_tools.a2a_client import A2AClientToolProvider
#from tools import search_vector_db
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
import uvicorn
import asyncio
from pydantic import BaseModel
from fastapi import FastAPI
from strands.models.litellm import LiteLLMModel
import os

logging.basicConfig(level=logging.INFO)

app = FastAPI()

model = LiteLLMModel(
  client_args={
    "api_key": os.environ["GEMINI_API_KEY"],
  },
  # **model_config
  model_id="gemini/gemini-2.5-flash",
  params={
    "max_tokens": 10000000,
    "temperature": 0.7,
    "no-cache": True
  }
)

copilot_mcp = MCPClient(
    lambda: streamablehttp_client(
        url="https://api.githubcopilot.com/mcp/", 
        # Get pat token from here: https://github.com/settings/personal-access-tokens
        headers={"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
    )
)

aws_docs_mcp = MCPClient(
  lambda: stdio_client(
    StdioServerParameters(
        command="uvx", 
        args=["awslabs.aws-documentation-mcp-server@latest"]
    )
  )
)

eks_mcp_envs = {}

if len(os.getenv("AWS_PROFILE", "")) > 0:
  eks_mcp_envs["AWS_PROFILE"] = os.environ["AWS_PROFILE"]
if len(os.getenv("AWS_REGION", "")) > 0:
  eks_mcp_envs["AWS_REGION"] = os.environ["AWS_REGION"]

eks_mcp = MCPClient(
  lambda: stdio_client(
    StdioServerParameters(
      command="uvx", 
      args=[
        "awslabs.eks-mcp-server@latest", 
        "--allow-write", 
        "--allow-sensitive-data-access"
      ],
      env=eks_mcp_envs
    )
  )
)

#k8s_mcp = MCPClient(
#  lambda: stdio_client(
#    StdioServerParameters(
#      command="python3", 
#      args=[
#        "-m",
#        "kubectl_mcp_tool"
#      ],
#      env={
#        "KUBECONFIG":"/Users/lucas/.kube/config"
#      }
#    )
#  )
#)

a2a_agent_urls = os.getenv("A2A_AGENT_URLS", "http://127.0.0.1:8083/api/a2a/default/platform-engineering-bot")

platform_engineering_agent_tool = A2AClientToolProvider(
  known_agent_urls=[a2a_agent_urls],
  timeout=300000000,  # Increased timeout to prevent premature connection closure
)

tools = [calculator, current_time, retrieve] 
tools = tools + platform_engineering_agent_tool.tools

def get_strands_agent(session_id: str):
  session_manager = FileSessionManager(session_id=session_id)
  with copilot_mcp, aws_docs_mcp:
    #copilot_tools = copilot_mcp.list_tools_sync()
    #aws_docs_tools = aws_docs_mcp.list_tools_sync()
    #eks_tools = eks_mcp.list_tools_sync()
    #k8s_tools = k8s_mcp.list_tools_sync()

    all_tools = tools #+ copilot_tools + aws_docs_tools + k8s_tools

    # Create a Strands agent
    agent = Agent(
      name="Multi Agent",
      description="An agent to integrate multiple cloud-native MCP agents and tools.",
      system_prompt='''
      You are a helpful AI assistant that integrates multiple cloud-native MCP agents and tools to answer user questions effectively.

      ALWAYS forward requests to A2A agents discovered as tools on platform_engineering_agent_tool.tools to delegate platform engineering questions or tasks related to AWS EKS, Kubernetes, and cloud-native technologies.

      Discover A2A agents to delegate platform engineering questions or tasks related to AWS EKS, Kubernetes, and cloud-native technologies.

      Use the available tools to gather information, perform calculations, and provide accurate responses to user queries.

      Always think step-by-step about which tools to use and in what order to best answer the user's question.

      Be sure to cite your sources when providing information from external documents or tools.
      ''',
      tools=all_tools,
      callback_handler=None,
      session_manager=session_manager,
      model=model
    )
    return agent

class Question(BaseModel):
  question: str
  session_id: str

@app.post("/question")
async def ask_question(question: Question):
  session_id = question.session_id
  agent = get_strands_agent(session_id)
  with copilot_mcp, aws_docs_mcp:
    try:
      response = agent(question.question)
      return response.message
    except RuntimeError as e:
      # Handle closed transport errors gracefully
      if "handler is closed" in str(e):
        logging.warning(f"Connection cleanup error (non-fatal): {e}")
        return {"error": "Request completed but cleanup failed", "status": "partial"}
      raise
  

async def main():
  config = uvicorn.Config(app, host="0.0.0.0", port=8000)
  server = uvicorn.Server(config)
  await server.serve()

if __name__ == '__main__':
  asyncio.run(main())