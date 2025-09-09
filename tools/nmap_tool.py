import asyncio
import shlex

def register_tool():
    """Register the Nmap tool with a normalized schema"""
    
    async def nmap_scan(target: str, kwargs: str = "") -> str:
        """
        Perform a network scan using Nmap.

        Args:
            target: Host or network to scan (e.g., 192.168.1.1, example.com, 10.0.0.0/24)
            kwargs: Extra Nmap flags (e.g., '-sS -T4 -p 80,443 -A')

        Examples:
            - nmap_scan("scanme.nmap.org", "-sV -p 80,443")
            - nmap_scan("192.168.1.0/24", "-sS -T4")
        """
        
        if not target:
            return "Error: target parameter is required"
        
        # Build command
        cmd = ["sudo", "nmap"]
        
        # Add any provided flags
        if kwargs:
            try:
                args_list = shlex.split(kwargs)
                cmd.extend(args_list)
            except ValueError as e:
                return f"Error parsing Nmap flags: {str(e)}"
        
        # Add target last
        cmd.append(target)
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            result = stdout.decode() if stdout else stderr.decode()
            
            return f"Nmap scan on {target} with args [{kwargs}]:\n\n{result}"
            
        except Exception as e:
            return f"Error executing Nmap: {str(e)}"
    
    # MCP schema (normalized)
    nmap_scan._mcp_schema = {
        "name": "nmap_scan",
        "description": "Run an Nmap scan on a host or network with optional flags.",
        "parameters": {
            "target": {
                "type": "string",
                "description": "Host or network to scan (e.g., 192.168.1.1, example.com, 10.0.0.0/24)",
                "required": True
            },
            "kwargs": {
                "type": "string",
                "description": "Extra Nmap flags (e.g., '-sS -T4 -p 80,443 -A')",
                "default": ""
            }
        },
        "examples": [
            {
                "input": {"target": "scanme.nmap.org", "kwargs": "-sV -p 80,443"},
                "description": "Service/version detection on ports 80 and 443"
            },
            {
                "input": {"target": "192.168.1.0/24", "kwargs": "-sS -T4"},
                "description": "Stealth scan of a subnet with aggressive timing"
            }
        ]
    }
    
    return {"nmap_scan": nmap_scan}
