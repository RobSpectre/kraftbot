# MCP Protocol Compliance Fix for sleeper-scraper-mcp

## Issue
The sleeper-scraper-mcp server is missing required MCP protocol methods, causing "Method not found" errors when PydanticAI tries to initialize the MCP connection.

## Required MCP Methods Missing

1. **initialize** - Required for client handshake
2. **notifications/initialized** - Required after successful initialization  
3. **capabilities** - Should be returned in initialize response

## Fix for sleeper-scraper-mcp server.py

Add this code to the `handle_message` method in SleeperMCP class:

```python
def handle_message(self, message):
    """Handle incoming JSON-RPC messages with MCP protocol support"""
    
    # ... existing validation code ...
    
    method = message.get("method")
    if not method:
        # ... existing error handling ...
    
    # Check if this is a notification (no id)
    is_notification = "id" not in message
    
    # MCP Protocol Methods
    if method == "initialize":
        if is_notification:
            return None
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "sleeper-mcp",
                    "version": "1.0.0"
                }
            }
        }
    
    if method == "notifications/initialized":
        # This is always a notification, no response needed
        return None
        
    if method == "tools/list":
        # Handle tools/list (MCP standard) same as listTools
        tool_descriptions = []
        for tool_name in self.tools:
            tool_descriptions.append({
                "name": tool_name,
                "description": getattr(self.tools[tool_name], "__doc__", "").strip(),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            })
            
        if is_notification:
            return None
            
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "tools": tool_descriptions
            }
        }
    
    if method == "tools/call":
        # Handle tools/call (MCP standard)
        params = message.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name in self.tools:
            try:
                result = self.tools[tool_name](arguments)
                if is_notification:
                    return None
                    
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": str(result)
                            }
                        ]
                    }
                }
            except Exception as e:
                logger.error(f"Error executing {tool_name}: {str(e)}")
                if is_notification:
                    return None
                    
                return {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {
                        "code": -32000,
                        "message": "Tool execution error",
                        "data": str(e)
                    }
                }
    
    # Keep existing listTools method for backwards compatibility
    if method == "listTools":
        # ... existing listTools code ...
```

## Alternative: Direct Tool Integration

Instead of fixing the MCP server, you could integrate the Sleeper tools directly into KraftBot:

```python
# Add to kraftbot/core/agent.py _register_tools method
@self.agent.tool
async def sleeper_get_user_info(ctx: RunContext[AgentDependencies], username_or_user_id: str) -> str:
    """Fetch user information from Sleeper by username or user_id"""
    try:
        # Direct API call to Sleeper
        response = requests.get(f"https://api.sleeper.app/v1/user/{username_or_user_id}")
        if response.status_code == 200:
            return str(response.json())
        else:
            return f"Error: Could not fetch user info for {username_or_user_id}"
    except Exception as e:
        return f"Error: {str(e)}"
```

## Recommendation

For immediate resolution, I recommend **Option 3** (keep MCP disabled) since KraftBot is working well with its built-in tools. The sleeper-scraper-mcp server would need significant modifications to be fully MCP-compliant.