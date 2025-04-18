# mcp_server.py
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from pyats.topology import loader
from genie.conf import Genie
from typing import List
import time, json

# Create FastMCP server
mcp = FastMCP("PyATS MCP Server")

@mcp.tool()
def get_config(
    device_name: str = Field(description="Name of the device in the testbed"),
    interface_name: str = Field(description="Name of the interface in the testbed"),
    testbed_file: str = "testbed.yaml",
) -> str:
    """Retrieves the running configuration of an interface from a network device.

    Args:
        device_name (str): Name of the device in the testbed.
        interface_name (str): Name of the interface to retrieve the configuration for.
        testbed_file (str): Path to the testbed YAML file (default: 'testbed.yaml').

    Returns:
        str: The device's running configuration or an error message in string.
    """
    try:
        testbed = loader.load(testbed_file)
        print("loaded testbed")
        device = testbed.devices[device_name]
        device.connect()
        print("connected to device")
        config = device.execute("show run interface %s" % interface_name)
        print("got config")
        device.disconnect()
        print("disconnected")
        time.sleep(2)
        return config
    except Exception as e:
        device.disconnect()
        return f"Error getting config: {str(e)}"

@mcp.tool()
def run_show_command(
    device_name: str = Field(description="Name of the device in the testbed"),
    command: str = Field(description="Show command to execute (e.g., 'show interfaces')"),
    testbed_file: str = "testbed.yaml"
) -> str:
    """Runs a show command on a network device and returns the output in dictionary format.

    Args:
        device_name (str): Name of the device in the testbed.
        command (str): Show command to execute.
        testbed_file (str): Path to the testbed YAML file (default: 'testbed.yaml').

    Returns:
        str: The command output or an error message in string.
    """
    try:
        testbed = loader.load(testbed_file)
        device = testbed.devices[device_name]
        device.connect()
        if "uac" in command or "meraki" in command:
            output = device.execute(command)
        else:
            output = device.parse(command)
        device.disconnect()
        return json.dumps(output)
    except Exception as e:
        device.disconnect()
        return f"Error running command: {str(e)}"


@mcp.tool()
def ping(
    device_name: str = Field(description="Name of the device in the testbed"),
    target: str = Field(description="Domain name or IP address to ping"),
    ipv6: bool = Field(default=False, description="Set to True to use IPv6 stack"),
    testbed_file: str = "testbed.yaml"
) -> str:
    """Performs a ping operation on a device to a given target.

    Args:
        device_name (str): Name of the device in the testbed.
        target (str): Domain name or IP address to ping.
        ipv6 (bool): Use IPv6 stack if True, otherwise use IPv4 (default: False).
        testbed_file (str): Path to the testbed YAML file (default: 'testbed.yaml').

    Returns:
        str: The ping result or an error message. If there is no connectivity to the given target, then error message is returned.
    """
    try:
        testbed = loader.load(testbed_file)
        device = testbed.devices[device_name]
        device.connect()
        command = f"ping {'ipv6 ' if ipv6 else 'ip '}{target}"
        output = device.execute(command)
        device.disconnect()
        return output
    except Exception as e:
        return f"Error performing ping: {str(e)}"

@mcp.tool()
def apply_config(
    device_name: str = Field(description="Name of the device in the testbed"),
    config_commands: List[str] = Field(description="List of configuration commands to apply"),
    testbed_file: str = "testbed.yaml"
) -> str:
    """Applies configuration commands to a network device.

    Args:
        device_name (str): Name of the device in the testbed.
        config_commands (list[str]): List of configuration commands to apply.
        testbed_file (str): Path to the testbed YAML file (default: 'testbed.yaml').

    Returns:
        str: Confirmation of applied configuration or an error message.
    """
    try:
        testbed = loader.load(testbed_file)
        device = testbed.devices[device_name]
        device.connect()
        output = device.configure(config_commands)
        device.disconnect()
        return f"Configuration applied: {output}"
    except Exception as e:
        return f"Error applying config: {str(e)}"


if __name__ == "__main__":
    import sys
    print("Starting echo MCP server ", file=sys.stderr)
    mcp.run(transport="stdio")
    print("PyATS MCP server ended", file=sys.stderr)