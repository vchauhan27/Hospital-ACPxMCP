from typing import Optional
import json
import requests
from mcp.server.fastmcp import FastMCP
from colorama import Fore

mcp = FastMCP("doctorserver")

@mcp.tool()
def list_doctors(state: str, specialty: Optional[str] = "") -> str:
    """
    This tool returns a list of doctors filtered by state and optionally by specialty.
     Args:
        state: The two-letter state code (e.g., "CA")
        specialty: Optional doctor specialty to filter
    Returns:
        JSON string of doctors list or error message.
    """
    print(f"Tool called with state={state}, specialty={specialty}")
    url = 'https://raw.githubusercontent.com/nicknochnack/ACPWalkthrough/refs/heads/main/doctors.json'

    try:
        response = requests.get(url)
        response.raise_for_status()
        doctors = response.json()
    except Exception as e:
        return json.dumps({"message": f"Failed to fetch doctor data: {str(e)}"})

    matches = [
        doctor for doctor in doctors.values()
        if doctor["address"]["state"].lower() == state.lower() and
           (not specialty or doctor["specialty"].lower() == specialty.lower())
    ]

    if not matches:
        return json.dumps({"message": f"No doctors found in {state} with specialty '{specialty}'."})

    # Limit to 5 doctors to avoid flooding the model
    doctor_summaries = [
        f"{d['name']} ({d['specialty']}) - {d['address']['city']}, {d['address']['state']}"
        for d in matches[:5]
    ]

    return json.dumps({"message": "Here are some doctors:\n" + "\n".join(doctor_summaries)})

if __name__ == "__main__":
    print(f"{Fore.GREEN}MCP Doctor Server Running...{Fore.RESET}")
    mcp.run(transport="stdio")
