import uuid
import os
import logging
import requests
from smolagents import CodeAgent, LiteLLMModel, DuckDuckGoSearchTool
from smolagents.tools import ToolCollection
from mcp import StdioServerParameters

# Enable basic logging
logging.basicConfig(level=logging.INFO)

# Set API key via environment variable "GEMINI_API_KEY"
model = LiteLLMModel(model_id="gemini/gemini-1.5-flash")

# Read content from system_prompt.txt and store in system_prompt variable
system_prompt_path = os.path.abspath("system_prompt.txt")
if not os.path.exists(system_prompt_path):
    raise FileNotFoundError(f"system_prompt.txt not found at {system_prompt_path}")
with open(system_prompt_path, "r") as file:
    system_prompt = file.read().strip()

# Function to call company’s LLM API (unused but retained)
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
testbed_path = os.path.abspath("testbed.yaml")
if not os.path.exists(testbed_path):
    raise FileNotFoundError(f"testbed.yaml not found at {testbed_path}")

server_parameters = [StdioServerParameters(
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
        "mcp_server_pyats",
    ],
    env={"PATH": os.environ.get("PATH"), "PYTHONPATH": "/app"},
    ), StdioServerParameters(
    command="docker",
    args=[
        "run",
        "-i",
        "--rm",
        "mcp/sequentialthinking",
    ],
    ), 
    ]

# Load tools from PyATS MCP server
try:
    print("Loading MCP tools...")
    with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
        print("Available MCP Tools:", [tool.name for tool in tool_collection.tools])

        # Create a CodeAgent
        mcp_context_id = str(uuid.uuid4())
        agent = CodeAgent(
            tools=[DuckDuckGoSearchTool(), *tool_collection.tools],
           # prompt_templates={"system_prompt": system_prompt},
            model=model,
            add_base_tools=True,
            # verbosity_level=2,
            # max_steps=10,
            additional_authorized_imports=['*'],
        )
        print("Initialized agent")

        # Interactive chat loop
        print("\nEnter your prompt (press Ctrl+C to exit):")
        while True:
            try:
               # print(agent.prompt_templates["system_prompt"])
                user_prompt = input("> ")
                if user_prompt.strip():
                    print(f"\nProcessing Prompt: {user_prompt}")
                    logging.info(f"Running task: {user_prompt}")
                    result = agent.run(user_prompt + "\nMake sure to understand the tool input, output data types and code correctly for parsing.")
                    print("Result:", result)
                    logging.info(f"Result: {result}")
                else:
                    print("Please enter a non-empty prompt.")
            except KeyboardInterrupt:
                print("\nExiting chat. Goodbye!")
                logging.info("Chat session terminated by user")
                break
            except Exception as e:
                print(f"Error processing prompt: {str(e)}")
                logging.error(f"Error processing prompt: {str(e)}")

except Exception as e:
    print(f"Failed to load MCP tools: {str(e)}")
    logging.error(f"Failed to load MCP tools: {str(e)}")
    # docker_cmd = ["docker", "run", "-i", "--rm", "-v", f"{testbed_path}:/app/testbed.yaml", "pyats-mcp", "python", "-m", "mcp_server_pyats"]
    # try:
    #     result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=30)
    #     print("Docker stdout:", result.stdout)
    #     print("Docker stderr:", result.stderr)
    #     logging.debug(f"Docker stdout: {result.stdout}")
    #     logging.debug(f"Docker stderr: {result.stderr}")
    # except subprocess.TimeoutExpired as te:
    #     print("Docker command timed out:", str(te))
    #     logging.error(f"Docker command timed out: {str(te)}")
    # except subprocess.CalledProcessError as cpe:
    #     print("Docker command failed:", cpe.output)
    #     logging.error(f"Docker command failed: {cpe.output}")