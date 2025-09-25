#!/usr/bin/env python3
"""
MCP Server for Recon Agent - Uses dynamic tool registration with robust parameter handling
"""

import logging
import shlex
import inspect
import sys
import shutil
import platform
import subprocess
from inspect import Parameter
from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("recon-agent")


mcp = FastMCP("recon-agent")


try:
    from tool_registry import ToolRegistry
    tool_registry = ToolRegistry()
except ImportError as e:
    logger.error(f"Failed to import tool registry: {e}")
    class DummyToolRegistry:
        def list_tools(self):
            return {}
    tool_registry = DummyToolRegistry()


type_map = {
    "string": str,
    "array": list,
    "integer": int,
    "boolean": bool,
}

def parse_kwargs_string(kwargs_string):
    """
    Parse a kwargs string like 'domain=example.com' or 'target=127.0.0.1 args=-sS'
    into a proper dictionary.
    """
    if not kwargs_string:
        return {}
    try:
        if "=" in kwargs_string:
            params = {}
            parts = shlex.split(kwargs_string)
            for part in parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    params[key.strip()] = value.strip()
            return params
        else:
            
            return {"target": kwargs_string}
    except Exception as e:
        logger.error(f"Error parsing kwargs string: {kwargs_string}, error: {e}")
        return {}

def check_tool_installation(tool_name):
    """Check if a tool is installed and available in PATH"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["where", tool_name],
                capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        else:
            return shutil.which(tool_name) is not None
    except Exception:
        return False


for tool_name, tool_info in tool_registry.list_tools().items():
    tool_func = tool_info["function"]
    schema = tool_info["schema"]
    parameters = schema.get("parameters", {})

    # Check if the tool is available
    if hasattr(tool_func, "_required_tool"):
        if not check_tool_installation(tool_func._required_tool):
            logger.warning(
                f"Tool {tool_name} requires {tool_func._required_tool} which is not installed"
            )
            continue

    # Create parameters for the signature
    params = []
    for param_name, param_info in parameters.items():
        param_type = type_map.get(param_info["type"], str)
        default = param_info.get("default", Parameter.empty)
        if default is not Parameter.empty:
            param = Parameter(
                param_name,
                Parameter.KEYWORD_ONLY,
                default=default,
                annotation=param_type,
            )
        else:
            param = Parameter(
                param_name, Parameter.KEYWORD_ONLY, annotation=param_type
            )
        params.append(param)

    signature = inspect.Signature(params)

    # Fix late-binding issue by capturing values in default args
    async def tool_wrapper(*args, __tool_func=tool_func, __signature=signature, **kwargs):
        bound = __signature.bind(*args, **kwargs)
        bound.apply_defaults()

        if hasattr(__tool_func, "_required_tool") and not check_tool_installation(
            __tool_func._required_tool
        ):
            return f"Error: {__tool_func._required_tool} is not installed. Please install it to use this tool."

        try:
            return await __tool_func(**bound.arguments)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return f"Error executing tool: {str(e)}"

    # Set the function attributes
    tool_wrapper.__signature__ = signature
    tool_wrapper.__annotations__ = {param.name: param.annotation for param in params}
    tool_wrapper.__name__ = tool_name
    tool_wrapper.__doc__ = schema.get("description", "")

    # Register the tool with MCP
    mcp.tool()(tool_wrapper)
    logger.info(f"Registered tool: {tool_name}")

if __name__ == "__main__":
    logger.info("Starting MCP server for Recon Agent...")
    available_tools = list(tool_registry.list_tools().keys())
    logger.info(f"Available tools: {', '.join(available_tools)}")

    missing_tools = []
    for tool_name, tool_info in tool_registry.list_tools().items():
        if hasattr(tool_info["function"], "_required_tool"):
            tool = tool_info["function"]._required_tool
            if not check_tool_installation(tool):
                missing_tools.append(tool)

    if missing_tools:
        logger.warning(f"The following tools are not installed: {', '.join(missing_tools)}")
        logger.warning("Some functionality may be limited")

    mcp.run(transport="stdio")
