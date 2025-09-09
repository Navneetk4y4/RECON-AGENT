import asyncio
import shlex

def register_tool():
    """Register the WhatWeb tool with a normalized schema"""
    
    async def whatweb_scan(target: str, kwargs: str = "") -> str:
        """
        Perform web technology detection using WhatWeb.

        Args:
            target: URL or domain to scan (e.g., example.com)
            kwargs: Extra WhatWeb flags (optional, e.g., '--color=never --aggression=3')

        Examples:
            - whatweb_scan("example.com")
            - whatweb_scan("https://example.com", "--color=never --aggression=3")
        """
        
        if not target:
            return "Error: target parameter is required"
        
        # Build command
        cmd = ["whatweb"]
        
        # Add kwargs if provided
        if kwargs:
            try:
                args_list = shlex.split(kwargs)
                cmd.extend(args_list)
            except ValueError as e:
                return f"Error parsing WhatWeb flags: {str(e)}"
        
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
            
            # Check if WhatWeb is installed
            if "command not found" in result or "not found" in result.lower():
                return "Error: WhatWeb is not installed. Please install it using:\n\n- macOS: `brew install whatweb`\n- Linux: `sudo apt install whatweb` or from https://github.com/urbanadventurer/WhatWeb\n- Windows: Download from https://github.com/urbanadventurer/WhatWeb"
            
            return f"WhatWeb scan for {target} with args [{kwargs or 'default'}]:\n\n{result}"
            
        except Exception as e:
            return f"Error executing WhatWeb scan: {str(e)}"
    
    # MCP schema (normalized)
    whatweb_scan._mcp_schema = {
        "name": "whatweb_scan",
        "description": "Perform web technology detection using WhatWeb to identify websites, CMS, JavaScript libraries, and other technologies.",
        "parameters": {
            "target": {
                "type": "string", 
                "description": "URL or domain to scan (e.g., example.com or https://example.com)",
                "required": True
            },
            "kwargs": {
                "type": "string", 
                "description": "Extra WhatWeb flags (e.g., '--color=never', '--aggression=3', '--log-json=-')",
                "default": ""
            }
        },
        "examples": [
            {
                "input": {"target": "example.com"},
                "description": "Perform a default WhatWeb scan for example.com"
            },
            {
                "input": {"target": "https://example.com", "kwargs": "--color=never --aggression=3"},
                "description": "Perform WhatWeb scan with specific aggression level and no color output"
            },
            {
                "input": {"target": "example.com", "kwargs": "--log-json=-"},
                "description": "Perform WhatWeb scan with JSON output format"
            }
        ]
    }
    
    return {"whatweb_scan": whatweb_scan}