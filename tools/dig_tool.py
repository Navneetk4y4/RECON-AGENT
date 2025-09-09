import asyncio
import shlex
import shutil
from typing import Dict, Any

def register_tool():
    """Register the dig tool with its schema"""
    
    async def dig_query(target: str, kwargs: str = "") -> str:
        """
        Perform DNS queries using dig.

        Args:
            target: Domain or hostname to query (e.g., example.com)
            kwargs: Extra dig flags (e.g., "A", "MX", "TXT +short @8.8.8.8")

        Examples:
            - dig_query("example.com", "A")
            - dig_query("example.com", "MX +short")
            - dig_query("example.com", "TXT @1.1.1.1")
        """
        if not target:
            return "Error: target parameter is required"

        # Base command
        cmd = ["dig", target]

        # Add extra args if provided
        if kwargs:
            try:
                args_list = shlex.split(kwargs)
                cmd.extend(args_list)
            except Exception as e:
                return f"Error parsing arguments: {str(e)}"

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            result = stdout.decode() if stdout else stderr.decode()

            return f"Dig query for {target}:\n\n{result}"

        except Exception as e:
            return f"Error executing dig: {str(e)}"

    # MCP schema (normalized)
    dig_query._mcp_schema = {
        "name": "dig_query",
        "description": "Run DNS queries with dig for any record type (A, AAAA, MX, TXT, etc.).",
        "parameters": {
            "target": {
                "type": "string",
                "description": "Domain or hostname to query (e.g., example.com)",
                "required": True
            },
            "kwargs": {
                "type": "string",
                "description": "Additional dig flags (e.g., 'A', 'MX +short', 'TXT @8.8.8.8')",
                "default": ""
            }
        },
        "examples": [
            {
                "input": {"target": "example.com", "kwargs": "A"},
                "description": "Query A record for example.com"
            },
            {
                "input": {"target": "example.com", "kwargs": "MX +short"},
                "description": "Get MX records for example.com in short format"
            },
            {
                "input": {"target": "example.com", "kwargs": "TXT @8.8.8.8"},
                "description": "Query TXT records for example.com using 8.8.8.8 DNS server"
            }
        ]
    }
    
    return {"dig_query": dig_query}
