import asyncio
import shlex

def register_tool():
    """Register the WHOIS tool with a normalized schema"""
    
    async def whois_lookup(target: str, kwargs: str = "") -> str:
        """
        Perform WHOIS lookup on a domain.

        Args:
            target: Domain name to look up (e.g., example.com)
            kwargs: Extra WHOIS flags (optional, e.g., '-h whois.verisign-grs.com')

        Examples:
            - whois_lookup("example.com")
            - whois_lookup("example.com", "-h whois.verisign-grs.com")
        """
        
        if not target:
            return "Error: target parameter is required"
        
        # Build command
        cmd = ["whois"]
        
        # Add kwargs if provided
        if kwargs:
            try:
                args_list = shlex.split(kwargs)
                cmd.extend(args_list)
            except ValueError as e:
                return f"Error parsing WHOIS flags: {str(e)}"
        
        # Add target at the end
        cmd.append(target)
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            result = stdout.decode() if stdout else stderr.decode()
            
            return f"WHOIS lookup for {target} with args [{kwargs or 'default'}]:\n\n{result}"
            
        except Exception as e:
            return f"Error executing WHOIS lookup: {str(e)}"
    
    # MCP schema (normalized)
    whois_lookup._mcp_schema = {
        "name": "whois_lookup",
        "description": "Perform WHOIS lookup to get domain registration info (registrar, contacts, expiration, etc.).",
        "parameters": {
            "target": {
                "type": "string", 
                "description": "Domain name to look up (e.g., example.com)",
                "required": True
            },
            "kwargs": {
                "type": "string", 
                "description": "Extra WHOIS flags (e.g., '-h whois.verisign-grs.com')",
                "default": ""
            }
        },
        "examples": [
            {
                "input": {"target": "example.com"},
                "description": "Perform a default WHOIS lookup for example.com"
            },
            {
                "input": {"target": "example.com", "kwargs": "-h whois.verisign-grs.com"},
                "description": "Perform WHOIS lookup using a specific WHOIS server"
            }
        ]
    }
    
    return {"whois_lookup": whois_lookup}
