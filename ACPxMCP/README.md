# Doctor Finder Agent System

This project implements an asynchronous multi-agent system for searching doctors by location and specialty. The design leverages the ACP (Agent Composability Protocol) framework with tools from SmolAgents, the Groq API, and a minimal MCP server.

## Features

- Search for doctors by US state and specialty.
- Agents communicate using `acp_sdk` with tool-calling support.
- Integrates with:
  - DuckDuckGo search
  - Webpage visits
  - Final Answer tool
- Uses Groq's `llama3-8b-8192` model through an OpenAI-compatible API.
- Contains two specialized agents: `health_agent` and `doctor_agent`.

## Project Files

### `acpxmcp.py`
- Main entry point for running the agent server.
- Sets up `health_agent` and `doctor_agent`.
- Loads the Groq API key from environment variables.
- Connects to the backend MCP tool server.
- Listens on port 8005.

### `mcpserver.py`
- Implements the MCP tool backend.
- Defines the `list_doctors(state, specialty)` tool:
  - Fetches doctor data from a static JSON file hosted on GitHub.
  - Filters doctors based on state and optional specialty.
  - Returns up to 5 formatted doctor entries.

### `testacpxmcp.py`
- Test script to verify the `doctor_agent` and MCP tool integration.
- Sends a sample query and displays the tool’s response.

## How MCP Server was Integrated into ACP

The **MCP (Model Context Protocol) server** was integrated into ACP to allow agents to both **expose tools** and **invoke tools** across different agent systems in a modular and composable fashion. This enables agents to communicate and delegate tasks dynamically.

### Integration Details:

- The MCP tool server (`mcpserver.py`) runs independently and exposes tool functions using the MCP protocol.
- In the `acpxmcp.py` agent script:
  - The MCP tool URL is provided as input to `RemoteCommandTool`, allowing agents to call tools defined externally via MCP.
  - The tools exposed by the MCP server (`list_doctors`) can now be dynamically called from within agent reasoning flows.
- Communication between the agent and the MCP server happens over standard IO streams or HTTP (depending on the implementation), allowing seamless plug-and-play extensibility.
- This design makes it easy to add new functionalities—just run an MCP-compatible tool server and update the agent's tool loading configuration.

### Benefits:

- **Standardized tool access** via schemas and structured inputs/outputs.
- **Tool discovery & composition** across agent systems without tightly coupling logic.
- **Extensible architecture**, perfect for building large multi-agent systems or plug-in style AI tools.

## Requirements

- Python 3.10 or higher
- `.env` file with `GROQ_API_KEY`

### Required Python Packages

- `acp_sdk`
- `smolagents`
- `requests`
- `colorama`
- `python-dotenv`
- `nest_asyncio`

## Usage

1. Start the agent server  
   Run `acpxmcp.py`

2. Run the test client  
   Run `testacpxmcp.py`

## Example Output

```
Doctor Agent Prompt:
I'm based in Atlanta,GA. Are there any Cardiologists near me?

Tool called with state=GA, specialty=Cardiologist
Here are some doctors:
Dr. Jane Smith (Cardiologist) - Atlanta, GA
...
```

## Notes

- If the state parameter is not provided, the system defaults to "GA".
- The tool fetches doctor data from a static JSON; internet access is required.
- The architecture is extendable—simply plug in new MCP tool servers to enhance agent capabilities.

