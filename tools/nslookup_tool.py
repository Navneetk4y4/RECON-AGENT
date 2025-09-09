import asyncio
import shlex

def register_tool():
    """Register the NSLOOKUP tool with a normalized schema"""
    
    async def nslookup_query(target: str, kwargs: str = "") -> str:
        """
        Perform DNS lookups using nslookup.

        Args:
            target: Domain or IP to look up (e.g., example.com or 8.8.8.8)
            kwargs: Extra nslookup flags (e.g., '-type=MX 8.8.8.8')

        Examples:
            - nslookup_query("example.com", "-type=MX")
            - nslookup_query("8.8.8.8", "")
            - nslookup_query("openai.com", "-type=TXT 1.1.1.1")
        """
        
        if not target:
            return "Error: target parameter is required"
        
        # Build command
        cmd = ["nslookup"]
        
        # Add kwargs if provided
        if kwargs:
            try:
                args_list = shlex.split(kwargs)
                cmd.extend(args_list)
            except ValueError as e:
                return f"Error parsing nslookup flags: {str(e)}"
        
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
            
            return f"NSLOOKUP for {target} with args [{kwargs or 'default'}]:\n\n{result}"
            
        except Exception as e:
            return f"Error executing nslookup: {str(e)}"
    
    # MCP schema (normalized)
    nslookup_query._mcp_schema = {
        "name": "nslookup_query",
        "description": "Resolve domain names or IPs with nslookup (supports custom record types and DNS servers).",
        "parameters": {
            "target": {
                "type": "string", 
                "description": "Domain or IP to look up (e.g., example.com or 8.8.8.8)",
                "required": True
            },
            "kwargs": {
                "type": "string", 
                "description": "Extra nslookup flags (e.g., '-type=MX 8.8.8.8' or '-type=TXT 1.1.1.1')",
                "default": ""
            }
        },
        "examples": [
            {
                "input": {"target": "example.com", "kwargs": "-type=MX"},
                "description": "Look up MX records for example.com"
            },
            {
                "input": {"target": "openai.com", "kwargs": "-type=TXT 1.1.1.1"},
                "description": "Look up TXT records for openai.com using Cloudflare DNS"
            }
        ]
    }
    
    return {"nslookup_query": nslookup_query}
