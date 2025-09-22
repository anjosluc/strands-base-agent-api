import logging
from mcp import stdio_client, StdioServerParameters
from strands.session.file_session_manager import FileSessionManager
from strands_tools import retrieve
from strands_tools.calculator import calculator
from strands_tools.current_time import current_time
from strands_tools.mcp_client import MCPClient
from tools import search_vector_db
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
  model_id="gemini/gemini-2.0-flash",
  params={
    "max_tokens": 10000000,
    "temperature": 0.7,
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
        command="/Users/lucas/.local/bin/uvx", 
        args=["awslabs.aws-documentation-mcp-server@latest"]
    )
  )
)

#eks_mcp = MCPClient(
#  lambda: stdio_client(
#    StdioServerParameters(
#      command="/Users/lucas/.local/bin/uvx", 
#      args=[
#        "awslabs.eks-mcp-server@latest", 
#        "--allow-write", 
#        "--allow-sensitive-data-access"
#      ],
#      env={
#        "AWS_REGION":"us-east-1"
#      }
#    )
#  )
#)

k8s_mcp = MCPClient(
  lambda: stdio_client(
    StdioServerParameters(
      command="/opt/homebrew/bin/npx", 
      args=[
        "-y",
        "kubernetes-mcp-server@latest"
      ]
    )
  )
)

tools = [calculator, current_time, retrieve]

def get_strands_agent(session_id: str):
  session_manager = FileSessionManager(session_id=session_id)
  with copilot_mcp, aws_docs_mcp, k8s_mcp:
    copilot_tools = copilot_mcp.list_tools_sync()
    aws_docs_tools = aws_docs_mcp.list_tools_sync()
    #eks_tools = eks_mcp.list_tools_sync()
    k8s_tools = k8s_mcp.list_tools_sync()
    
    all_tools = tools + copilot_tools + aws_docs_tools + k8s_tools

    # Create a Strands agent
    agent = Agent(
      name="Multi Agent",
      description="An agent to call Github, get datetime, among other ops",
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
def ask_question(question: Question):
  session_id = question.session_id
  agent = get_strands_agent(session_id)
  with copilot_mcp, aws_docs_mcp, k8s_mcp:
    response = agent(question.question)
    return str(response.message)
  

async def main():
  config = uvicorn.Config(app, host="0.0.0.0", port=8000)
  server = uvicorn.Server(config)
  await server.serve()

if __name__ == '__main__':
  asyncio.run(main())