import os
from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server
from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel, VisitWebpageTool, ToolCallingAgent, ToolCollection
from mcp import StdioServerParameters
from groq import Groq
from dotenv import load_dotenv 
from smolagents import OpenAIModel
from smolagents import FinalAnswerTool

load_dotenv()

server = Server()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY is not set in environment variables.")

model = OpenAIModel(
    model_id="llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY"),
    api_base="https://api.groq.com/openai/v1",
)


server_parameters = StdioServerParameters(
    command="python",
    args=[os.path.join(os.path.dirname(__file__), "mcpserver.py")],
    env=None
)

@server.agent()
async def health_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    agent = CodeAgent(tools=[DuckDuckGoSearchTool(), VisitWebpageTool()], model=model)
    prompt = input[0].parts[0].content
    print(f"Health Agent Prompt: {prompt}")
    response = await agent.run(prompt)
    yield Message(parts=[MessagePart(content=str(response))])

@server.agent()
async def doctor_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    try:
        with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
            # Create agent with just the necessary tools
            agent = CodeAgent(
                tools=[*tool_collection.tools],
                model=model
            )
            
            prompt = input[0].parts[0].content
            print(f"Doctor Agent Prompt: {prompt}")
            
            enhanced_prompt = f"""
            Please use the list_doctors tool to complete this request:
            {prompt}
            
            Important Instructions:
            1. Always include a state parameter (default to 'GA' if not specified)
            2. Return the raw tool output exactly as received
            3. Don't modify or interpret the results
            """
            
            response = agent.run(enhanced_prompt)
            
            # Handle different response types
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
                
            yield Message(parts=[MessagePart(content=content)])
            
    except Exception as e:
        error_msg = f"Doctor search failed. Please try again later. Error: {str(e)}"
        yield Message(parts=[MessagePart(content=error_msg)])

if __name__ == "__main__":
    server.run(port=8005)
