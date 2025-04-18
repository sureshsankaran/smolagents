# client.py
import requests
import uuid
import os
from smolagents import CodeAgent, ToolCollection
from mcp import StdioServerParameters

# Function to call company’s LLM API
def company_llm_completion(
    prompt,
    api_key=os.getenv("LLM_API_KEY", "your-llm-api-key-here"),
    api_base="https://your-company-api.com/v1/completions",
    mcp_context_id=None
):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-MCP-Context-ID": mcp_context_id or str(uuid.uuid4()),
    }
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an assistant that generates Python code to call tools provided by an MCP server. "
                    "The tools are dynamically loaded, and their names and parameters are unknown. "
                    "Based on the task, generate code to call the appropriate tool with the given inputs. "
                    "If tool names are unclear, make reasonable assumptions or return a list of available tools."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0.7,
    }
    try:
        response = requests.post(api_base, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["content"]
    except Exception as e:
        raise Exception(f"LLM API call failed: {str(e)}")

# Configure MCP server parameters to implicitly start the server
testbed_path = os.path.abspath("testbed.yaml")  # Path to testbed.yaml on the host
server_parameters = StdioServerParameters(
    command="docker",
    args=[
        "run",
        "-i",
        "--rm",
        "-v",
        f"{testbed_path}:/app/testbed.yaml",
        "pyats-mcp",
        "python",
        "-m",
        "mcp_server",
    ],
    env={"PATH": os.environ.get("PATH"), "PYTHONPATH": "/app"},
)

# Load tools from PyATS MCP server
try:
    with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
        print("Available MCP Tools:", [tool.__name__ for tool in tool_collection.tools])

        # Create a CodeAgent
        mcp_context_id = str(uuid.uuid4())
        agent = CodeAgent(
            tools=[*tool_collection.tools],
            llm=company_llm_completion,
            max_iterations=3,
            verbose=True,
            llm_kwargs={"mcp_context_id": mcp_context_id},
            add_base_tools=True,
        )

        # Example tasks
        tasks = [
            "Retrieve the running configuration for device 'switch1' using the appropriate MCP tool.",
            "Run the 'show interfaces' command on device 'switch1' using the appropriate MCP tool.",
            "Apply the configuration commands ['interface GigabitEthernet0/0', 'description TEST'] to device 'switch1' using the appropriate MCP tool.",
        ]

        # Run each task
        for task in tasks:
            print(f"\nRunning Task: {task}")
            result = agent.run(task)
            print("Result:", result)
except Exception as e:
    print(f"Failed to load MCP tools: {str(e)}")
