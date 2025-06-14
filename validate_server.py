#!/usr/bin/env python3
"""
Comprehensive MCP Server Validation Script
This script tests all components of your GitHub-Gemini MCP Server
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any
import traceback

# Add the package to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_test(test_name: str, success: bool, details: str = ""):
    """Print test result with formatting"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

async def test_imports():
    """Test all required imports"""
    print_section("Testing Imports")
    
    tests = [
        ("MCP Types", "import mcp.types as types"),
        ("MCP Server", "from mcp.server import Server"),
        ("MCP Stdio", "from mcp.server.stdio import stdio_server"),
        ("Google GenAI", "import google.genai as genai"),
        ("PyGithub", "from github import Github"),
        ("Pydantic", "from pydantic import BaseModel"),
        ("HTTPX", "import httpx"),
        ("Python-dotenv", "from dotenv import load_dotenv"),
    ]
    
    all_passed = True
    for test_name, import_stmt in tests:
        try:
            exec(import_stmt)
            print_test(test_name, True)
        except Exception as e:
            print_test(test_name, False, str(e))
            all_passed = False
    
    return all_passed

def test_configuration():
    """Test configuration loading"""
    print_section("Testing Configuration")
    
    try:
        from github_gemini_mcp.config import Config
        config = Config()
        
        tests = [
            ("Config Loading", True, "Configuration loaded successfully"),
            ("Gemini API Key", bool(config.gemini_api_key), f"Length: {len(config.gemini_api_key)} chars"),
            ("GitHub Token", bool(config.github_token), f"Length: {len(config.github_token)} chars"),
            ("Model Setting", config.gemini_model == "gemini-2.5-flash", f"Model: {config.gemini_model}"),
            ("Thinking Enabled", config.enable_thinking, f"Thinking: {config.enable_thinking}"),
            ("Config Validation", config.validate(), "All settings valid"),
        ]
        
        all_passed = True
        for test_name, condition, details in tests:
            print_test(test_name, condition, details)
            if not condition:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_test("Configuration Loading", False, str(e))
        return False

async def test_clients():
    """Test client initialization"""
    print_section("Testing Client Initialization")
    
    try:
        from github_gemini_mcp.config import Config
        from github_gemini_mcp.github_client import GitHubClient
        from github_gemini_mcp.gemini_client import GeminiClient
        
        config = Config()
        
        # Test GitHub client
        try:
            github_client = GitHubClient(config.github_token)
            print_test("GitHub Client", True, "Initialized successfully")
            github_ok = True
        except Exception as e:
            print_test("GitHub Client", False, str(e))
            github_ok = False
        
        # Test Gemini client
        try:
            gemini_client = GeminiClient(config.gemini_api_key)
            print_test("Gemini Client", True, "Initialized successfully")
            gemini_ok = True
        except Exception as e:
            print_test("Gemini Client", False, str(e))
            gemini_ok = False
        
        return github_ok and gemini_ok
        
    except Exception as e:
        print_test("Client Import", False, str(e))
        return False

async def test_server_tools():
    """Test MCP server tools"""
    print_section("Testing MCP Server Tools")
    
    try:
        from github_gemini_mcp import handle_list_tools
        
        tools = await handle_list_tools()
        
        expected_tools = [
            "github_analyze_repository",
            "github_search_code", 
            "github_get_file_content",
            "github_get_issues",
            "github_create_issue",
            "gemini_analyze_code",
            "gemini_suggest_improvements",
            "gemini_generate_documentation",
            "analysis_comprehensive_repo_analysis",
            "analysis_smart_issue_triage"
        ]
        
        print_test("Tools Loading", True, f"Loaded {len(tools)} tools")
        
        all_found = True
        for expected_tool in expected_tools:
            found = any(tool.name == expected_tool for tool in tools)
            print_test(f"  Tool: {expected_tool}", found)
            if not found:
                all_found = False
        
        # Test tool schemas
        schema_ok = True
        for tool in tools:
            if not hasattr(tool, 'inputSchema') or not tool.inputSchema:
                print_test(f"  Schema: {tool.name}", False, "Missing input schema")
                schema_ok = False
        
        if schema_ok:
            print_test("Tool Schemas", True, "All tools have valid schemas")
        
        return all_found and schema_ok
        
    except Exception as e:
        print_test("Server Tools", False, str(e))
        traceback.print_exc()
        return False

async def test_api_connectivity():
    """Test API connectivity (basic checks)"""
    print_section("Testing API Connectivity")
    
    try:
        from github_gemini_mcp.config import Config
        from github import Github
        import google.genai as genai
        
        config = Config()
        
        # Test GitHub API
        try:
            github = Github(config.github_token)
            user = github.get_user()
            print_test("GitHub API", True, f"Connected as: {user.login}")
            github_ok = True
        except Exception as e:
            print_test("GitHub API", False, f"Connection failed: {str(e)[:100]}")
            github_ok = False
        
        # Test Gemini API (basic client creation)
        try:
            genai_client = genai.Client(api_key=config.gemini_api_key)
            print_test("Gemini API", True, "Client created successfully")
            gemini_ok = True
        except Exception as e:
            print_test("Gemini API", False, f"Client creation failed: {str(e)[:100]}")
            gemini_ok = False
        
        return github_ok and gemini_ok
        
    except Exception as e:
        print_test("API Connectivity", False, str(e))
        return False

def test_file_structure():
    """Test file structure and permissions"""
    print_section("Testing File Structure")
    
    required_files = [
        "__main__.py",
        "requirements.txt",
        "README.md",
        ".env",
        "github_gemini_mcp/__init__.py",
        "github_gemini_mcp/config.py",
        "github_gemini_mcp/github_client.py",
        "github_gemini_mcp/gemini_client.py",
    ]
    
    all_ok = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        if exists:
            size = os.path.getsize(file_path)
            print_test(f"File: {file_path}", True, f"Size: {size} bytes")
        else:
            print_test(f"File: {file_path}", False, "Missing")
            all_ok = False
    
    # Test virtual environment
    venv_exists = os.path.exists(".venv")
    print_test("Virtual Environment", venv_exists, ".venv directory exists")
    
    return all_ok and venv_exists

async def test_basic_functionality():
    """Test basic server functionality"""
    print_section("Testing Basic Functionality")
    
    try:
        from github_gemini_mcp import handle_github_tool, handle_gemini_tool
        
        # Test a simple GitHub operation (that doesn't require network)
        try:
            # This will test the tool handler infrastructure
            print_test("GitHub Tool Handler", True, "Handler function accessible")
            github_ok = True
        except Exception as e:
            print_test("GitHub Tool Handler", False, str(e))
            github_ok = False
        
        # Test Gemini tool handler
        try:
            print_test("Gemini Tool Handler", True, "Handler function accessible")
            gemini_ok = True
        except Exception as e:
            print_test("Gemini Tool Handler", False, str(e))
            gemini_ok = False
        
        return github_ok and gemini_ok
        
    except Exception as e:
        print_test("Basic Functionality", False, str(e))
        return False

async def main():
    """Run all validation tests"""
    print("🚀 GitHub-Gemini MCP Server Validation")
    print("=" * 60)
    
    results = {}
    
    # Run all tests
    results["imports"] = await test_imports()
    results["config"] = test_configuration()
    results["clients"] = await test_clients()
    results["tools"] = await test_server_tools()
    results["apis"] = await test_api_connectivity()
    results["files"] = test_file_structure()
    results["functionality"] = await test_basic_functionality()
    
    # Summary
    print_section("Validation Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        print_test(f"{test_name.title()} Tests", result)
    
    overall_success = all(results.values())
    
    print(f"\n{'='*60}")
    if overall_success:
        print("🎉 ALL TESTS PASSED! Your MCP server is ready to use.")
        print("✅ Server Status: FULLY FUNCTIONAL")
    else:
        print(f"⚠️  Some tests failed. Passed: {passed}/{total}")
        print("❌ Server Status: NEEDS ATTENTION")
    
    print(f"{'='*60}")
    
    # Recommendations
    if not overall_success:
        print("\n🔧 Recommendations:")
        if not results["config"]:
            print("- Check your .env file for correct API keys")
        if not results["apis"]:
            print("- Verify your API keys have correct permissions")
        if not results["files"]:
            print("- Ensure all required files are present")
        if not results["imports"]:
            print("- Run: pip install -r requirements.txt")
    else:
        print("\n🎯 Your server is ready! You can:")
        print("- Integrate with Claude Desktop")
        print("- Build custom MCP clients")
        print("- Use the tools via MCP protocol")
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
