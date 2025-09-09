import asyncio
import shlex
import shutil
from typing import AsyncGenerator, Dict, Any

def register_tool():
    """Register the Amass tool with its schema"""

    async def amass_enum(target: str, kwargs: str = "") -> str:
        """
        Perform subdomain enumeration using Amass.

        Args:
            target: The domain to scan (e.g., "example.com")
            kwargs: Extra Amass arguments (e.g., "--passive", "--brute", "-timeout 30")

        Examples:
            - amass_enum("tesla.com")
            - amass_enum("tesla.com", "--passive")
            - amass_enum("google.com", "--active -timeout 30")
        """
        # Check if Amass is installed
        if not shutil.which("amass"):
            return "Error: Amass is not installed or not in PATH. Please install Amass first."

        # Warn about placeholder domains
        if target.lower() in ["example.com", "example.org", "example.net"]:
            return ("Note: example.com is a reserved domain for documentation. "
                    "Amass typically finds limited or no subdomains for this domain. "
                    "Try a real domain like tesla.com or google.com.")

        # Collect all output from streaming run
        output_lines = []
        async for line in stream_amass_enum(target, kwargs):
            output_lines.append(line)

        result = "\n".join(output_lines)
        if not result.strip():
            return (f"No subdomains found for {target}. Try:\n\n"
                    "- A different domain\n"
                    "- Different Amass flags (--passive, --active, --brute)\n"
                    "- Verify Amass is installed/configured correctly")
        return result

    async def stream_amass_enum(target: str, kwargs: str = "") -> AsyncGenerator[str, None]:
        """Run Amass and stream output line by line (no timeout)."""
        if not target:
            yield "Error: target parameter is required."
            return

        # Base command
        cmd = ["amass", "enum", "-d", target]

        # Add extra flags if provided
        if kwargs:
            try:
                args_list = shlex.split(kwargs)
                cmd.extend(args_list)
            except Exception as e:
                yield f"Error parsing arguments: {str(e)}"
                return

        yield f"Running Amass command: {' '.join(cmd)}\n"

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Stream stdout
            async for line in process.stdout:
                decoded_line = line.decode().rstrip()
                if decoded_line:
                    yield decoded_line

            # Stream stderr
            async for line in process.stderr:
                decoded_line = line.decode().rstrip()
                if decoded_line:
                    yield "[stderr] " + decoded_line

            # Wait for exit
            return_code = await process.wait()
            if return_code != 0:
                yield f"Amass exited with code: {return_code}"

        except Exception as e:
            yield f"Error executing Amass: {str(e)}"

    # MCP schema (normalized: target + kwargs)
    amass_enum._mcp_schema = {
        "name": "amass_enum",
        "description": "Perform subdomain enumeration using Amass (passive, active, or brute modes).",
        "parameters": {
            "target": {
                "type": "string",
                "description": "The target domain to scan (e.g., 'example.com').",
                "required": True
            },
            "kwargs": {
                "type": "string",
                "description": "Additional Amass flags (e.g., '--passive', '--active', '--brute', '-timeout 30').",
                "default": ""
            }
        },
        "examples": [
            {
                "input": {"target": "tesla.com", "kwargs": "--passive"},
                "description": "Passive enumeration of tesla.com using public sources"
            },
            {
                "input": {"target": "tesla.com", "kwargs": "--active"},
                "description": "Active scan of tesla.com with direct requests"
            },
            {
                "input": {"target": "small-company.com", "kwargs": "--brute -src"},
                "description": "Brute force scan of small-company.com showing data sources"
            }
        ]
    }

    return {"amass_enum": amass_enum}
