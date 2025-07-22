from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server
from groq import Groq
import os
import nest_asyncio
from dotenv import load_dotenv  

load_dotenv()

nest_asyncio.apply()

server = Server()

groq_api_key = os.getenv("GROQ_API_KEY")

groq = Groq(api_key=groq_api_key)

@server.agent()
async def health_agent(input: list[Message]) -> AsyncGenerator[Message, None]:
    """Direct health questions to Groq without CodeAgent complexity"""
    if not input or not input[0].parts:
        yield Message(parts=[MessagePart(content="No input provided")])
        return
        
    question = input[0].parts[0].content
    
    try:
        response = groq.chat.completions.create(
            messages=[{"role": "user", "content": question}],
            model="llama3-8b-8192",
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        yield Message(parts=[MessagePart(content=answer)])
        
    except Exception as e:
        error_msg = f"Error processing your request: {str(e)}"
        yield Message(parts=[MessagePart(content=error_msg)])

if __name__ == "__main__":
    print("Starting Health Agent Server on port 8000...")
    server.run(port=8000)