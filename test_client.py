#!/usr/bin/env python3
"""
Simple test client for the GitHub-Gemini MCP Server
"""

import asyncio
import json
import sys
from mcp.client.stdio import stdio_client
from mcp.types import StdioServerParameters

async def test_mcp_server():
    """Test the MCP server by listing available tools"""
    
    try:
        print("🚀 Starting MCP server test...")
        
        # Create server parameters
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["__main__.py"],
            cwd="/home/uttammahata/mcp-server"
        )
        
        # Connect to the server via stdio
        async with stdio_client(server_params) as (read, write):
            # Initialize the client
            result = await write.request(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            )
            print(f"✅ Server initialized: {result.get('serverInfo', {}).get('name', 'Unknown')}")
            
            # List available tools
            tools_result = await write.request("tools/list", {})
            tools = tools_result.get("tools", [])
            
            print(f"\n📋 Available tools ({len(tools)}):")
            for tool in tools[:5]:  # Show first 5 tools
                print(f"  • {tool['name']}: {tool['description'][:60]}...")
            
            if len(tools) > 5:
                print(f"  ... and {len(tools) - 5} more tools")
            
            print(f"\n✅ MCP Server is working correctly!")
            print(f"🔧 Total tools available: {len(tools)}")
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
