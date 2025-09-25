from typing import Dict, Any, Callable
import importlib
import os
import sys

class ToolRegistry:
    def __init__(self):
        self.tools = {}
       
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        self.load_all_tools()
    
    def load_all_tools(self):
        """Dynamically load all tools from the tools directory"""
      
        sys.stderr.write("Loading tools dynamically from tools directory...\n")
        
       
        tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools')
        
        
        if not os.path.exists(tools_dir):
            sys.stderr.write(f"Tools directory not found: {tools_dir}\n")
            return
        
        
        for filename in os.listdir(tools_dir):
           
            if filename.endswith('_tool.py'):
                tool_name = filename[:-3]  
                
                try:
                   
                    module = importlib.import_module(f"tools.{tool_name}")
                    if hasattr(module, 'register_tool'):
                        registered_tools = module.register_tool()
                        self.tools.update(registered_tools)
                        sys.stderr.write(f"Successfully loaded {tool_name}: {list(registered_tools.keys())}\n")
                    else:
                        sys.stderr.write(f"{tool_name} doesn't have a register_tool function\n")
                except ImportError as e:
                    sys.stderr.write(f"Failed to load {tool_name}: {e}\n")
                except Exception as e:
                    sys.stderr.write(f"Error loading {tool_name}: {e}\n")
    
    def get_tool(self, name: str) -> Callable:
        """Get a tool function by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> Dict[str, Any]:
        """Return all available tools with their schemas"""
        return {
            name: {
                "function": func,
                "schema": getattr(func, '_mcp_schema', {})
            }
            for name, func in self.tools.items()
        }
