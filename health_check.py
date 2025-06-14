#!/usr/bin/env python3
"""
Quick Health Check for MCP Server
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def quick_health_check():
    """Perform a quick health check"""
    print("🏥 MCP Server Quick Health Check")
    print("=" * 40)
    
    checks = []
    
    # 1. Import check
    try:
        from github_gemini_mcp import server
        checks.append(("Server Import", True, "✅"))
    except Exception as e:
        checks.append(("Server Import", False, f"❌ {e}"))
    
    # 2. Config check
    try:
        from github_gemini_mcp.config import Config
        config = Config()
        has_keys = bool(config.gemini_api_key) and bool(config.github_token)
        checks.append(("API Keys", has_keys, "✅" if has_keys else "❌"))
    except Exception as e:
        checks.append(("API Keys", False, f"❌ {e}"))
    
    # 3. Tools check
    try:
        import asyncio
        from github_gemini_mcp import handle_list_tools
        
        async def get_tools():
            return await handle_list_tools()
        
        tools = asyncio.run(get_tools())
        tool_count = len(tools)
        checks.append(("Tools Available", tool_count > 0, f"✅ {tool_count} tools"))
    except Exception as e:
        checks.append(("Tools Available", False, f"❌ {e}"))
    
    # 4. Process check
    import subprocess
    try:
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        is_running = "__main__.py" in result.stdout
        checks.append(("Server Process", is_running, "✅ Running" if is_running else "❌ Not running"))
    except Exception:
        checks.append(("Server Process", False, "❌ Can't check"))
    
    # Print results
    all_good = True
    for check_name, success, status in checks:
        print(f"{status} {check_name}")
        if not success:
            all_good = False
    
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 SERVER IS HEALTHY!")
        print("✅ Ready for use")
    else:
        print("⚠️ SERVER NEEDS ATTENTION")
        print("❌ Check failed items above")
    
    return all_good

if __name__ == "__main__":
    quick_health_check()
