#!/usr/bin/env python3
"""
Test LangChain native MCP integration
"""

import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient


async def test_langchain_mcp():
    """Test LangChain's native MCP client"""
    print("=" * 60)
    print("Testing LangChain MCP Adapters")
    print("=" * 60 + "\n")

    try:
        # Create MCP client with tokenbowl server
        print("Connecting to tokenbowl MCP server...")
        client = MultiServerMCPClient({
            "tokenbowl": {
                "transport": "sse",
                "url": "https://tokenbowl-mcp.haihai.ai/sse"
            }
        })

        # Get tools
        print("Discovering tools...")
        tools = await client.get_tools()

        if tools:
            print(f"✓ Discovered {len(tools)} tools:\n")
            for tool in tools:
                print(f"  📦 {tool.name}")
                print(f"     Description: {tool.description[:80]}...")
                print()
        else:
            print("⚠ No tools discovered")

        print("=" * 60)
        print("✅ LangChain MCP integration test completed!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_langchain_mcp())
