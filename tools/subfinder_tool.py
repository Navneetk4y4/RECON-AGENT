import asyncio
import shlex

def register_tool():
    """Register a subdomain enumeration tool with fallback options"""
    
    async def subdomain_scan(target: str, kwargs: str = "") -> str:
        """
        Perform subdomain enumeration using multiple methods with fallbacks.

        Args:
            target: Domain to scan for subdomains (e.g., example.com)
            kwargs: Extra flags for advanced users

        Examples:
            - subdomain_scan("example.com")
            - subdomain_scan("example.com", "--threads 50")
        """
        
        if not target:
            return "Error: target parameter is required"
        
        # Try multiple methods with fallbacks
        results = []
        
        # Method 1: Try using Amass if available
        amass_result = await try_amass(target, kwargs)
        if amass_result and "Error" not in amass_result:
            results.append(f"Amass Results:\n{amass_result}")
        
        # Method 2: Try using subfinder if available
        subfinder_result = await try_subfinder(target, kwargs)
        if subfinder_result and "Error" not in subfinder_result:
            results.append(f"Subfinder Results:\n{subfinder_result}")
        
        # Method 3: Try using crt.sh certificate transparency
        crtsh_result = await try_crtsh(target)
        if crtsh_result:
            results.append(f"Certificate Transparency Results:\n{crtsh_result}")
        
        if not results:
            return "No subdomains found using available methods. This could be due to:\n1. Tools not installed\n2. Network restrictions\n3. Domain security measures\n4. Rate limiting\n\nTry manual methods or check tool installation."
        
        return "\n\n".join(results)
    
    async def try_amass(target, kwargs):
        """Try to use Amass for subdomain enumeration"""
        try:
            cmd = ["amass", "enum", "-d", target]
            if kwargs:
                args_list = shlex.split(kwargs)
                cmd.extend(args_list)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            return stdout.decode() if stdout else stderr.decode()
        except Exception:
            return "Amass not available or failed"
    
    async def try_subfinder(target, kwargs):
        """Try to use Subfinder for subdomain enumeration"""
        try:
            cmd = ["subfinder", "-d", target]
            if kwargs:
                args_list = shlex.split(kwargs)
                cmd.extend(args_list)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            return stdout.decode() if stdout else stderr.decode()
        except Exception:
            return "Subfinder not available or failed"
    
    async def try_crtsh(target):
        """Try certificate transparency log search"""
        try:
            # This would use a Python implementation instead of external tool
            import requests
            import json
            
            url = f"https://crt.sh/?q=%.{target}&output=json"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                subdomains = set()
                for entry in data:
                    name = entry.get('name_value', '')
                    if name and target in name:
                        subdomains.add(name)
                
                if subdomains:
                    return "\n".join(sorted(subdomains))
                return "No subdomains found in certificate transparency logs"
            return "Failed to query certificate transparency logs"
        except Exception as e:
            return f"Certificate transparency search failed: {str(e)}"
    
    # MCP schema
    subdomain_scan._mcp_schema = {
        "name": "subdomain_scan",
        "description": "Perform subdomain enumeration using multiple methods with fallback options.",
        "parameters": {
            "target": {
                "type": "string", 
                "description": "Domain to scan for subdomains (e.g., example.com)",
                "required": True
            },
            "kwargs": {
                "type": "string", 
                "description": "Extra flags for advanced users (e.g., '--threads 50')",
                "default": ""
            }
        },
        "examples": [
            {
                "input": {"target": "example.com"},
                "description": "Perform subdomain enumeration on example.com"
            }
        ]
    }
    
    return {"subdomain_scan": subdomain_scan}