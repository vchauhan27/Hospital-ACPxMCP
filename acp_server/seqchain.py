import asyncio 
import nest_asyncio
from acp_sdk.client import Client
from fastacp import AgentCollection, ACPCallingAgent
from colorama import Fore
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()
nest_asyncio.apply()

async def run_hospital_workflow() -> None:
    try:
        async with Client(base_url="http://localhost:8001") as insurer, \
                Client(base_url="http://localhost:8000") as hospital:
            
            print(Fore.CYAN + "Discovering agents..." + Fore.RESET)
            agent_collection = await AgentCollection.from_acp(insurer, hospital)  
            
            acp_agents = {}
            for client, agent in agent_collection.agents:
                acp_agents[agent.name] = {'agent': agent, 'client': client}
            
            print(Fore.GREEN + "\nDiscovered agents:")
            for name in acp_agents:
                print(f" - {name}")
            print(Fore.RESET)
            
            groq_api_key = os.getenv("GROQ_API_KEY")
            groq_client = Groq(api_key=groq_api_key)
            
            def groq_model(messages, **kwargs):
                groq_messages = []
                for msg in messages:
                    if isinstance(msg, dict):
                        role = msg["role"]
                        content = msg["content"]
                        if isinstance(content, list):
                            text_content = " ".join([part["text"] for part in content if part["type"] == "text"])
                            groq_messages.append({"role": role, "content": text_content})
                        else:
                            groq_messages.append({"role": role, "content": content})
                
                response = groq_client.chat.completions.create(
                    messages=groq_messages,
                    model="llama3-70b-8192",
                    temperature=0.3,
                    **kwargs
                )
                
                return {
                    "content": response.choices[0].message.content,
                    "role": "assistant"
                }
            
            # Create hierarchical agent
            acp_agent = ACPCallingAgent(
                acp_agents=acp_agents,
                model=groq_model,
                prompt_templates=None,  
                planning_interval=None
            )
            
            # Run query
            query = "Do I need rehabilitation after a shoulder reconstruction and what is the waiting period from my insurance?"
            print(Fore.CYAN + f"\nQuery: {query}" + Fore.RESET)
            
            result = await acp_agent.run(query)
            print(Fore.YELLOW + f"\nFinal result: {result}" + Fore.RESET)
            
    except Exception as e:
        print(Fore.RED + f"Error in workflow: {str(e)}" + Fore.RESET)

if __name__ == "__main__":
    try:
        asyncio.run(run_hospital_workflow())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nProcess interrupted by user" + Fore.RESET)