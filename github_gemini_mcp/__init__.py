import asyncio
import logging
import os
import json
from typing import Any, Dict, List, Optional, Sequence
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from .config import Config
from .github_client import GitHubClient
from .gemini_client import GeminiClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global clients
config = Config()
github_client = GitHubClient(config.github_token)
gemini_client = GeminiClient(config.gemini_api_key)

# Create the server instance
server = Server("github-gemini-mcp")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available tools"""
    return [
        # GitHub Repository Tools
        types.Tool(
            name="github_analyze_repository",
            description="Comprehensive analysis of a GitHub repository including structure, content, and metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner/organization name"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "include_content": {"type": "boolean", "description": "Whether to include file contents", "default": True}
                },
                "required": ["owner", "repo"]
            }
        ),
        
        types.Tool(
            name="github_search_code",
            description="Search for code across GitHub repositories with advanced filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for code"},
                    "owner": {"type": "string", "description": "Repository owner to limit search"},
                    "repo": {"type": "string", "description": "Repository name to limit search"},
                    "language": {"type": "string", "description": "Programming language filter"},
                    "filename": {"type": "string", "description": "Filename pattern filter"}
                },
                "required": ["query"]
            }
        ),
        
        types.Tool(
            name="github_get_file_content",
            description="Get the content of a specific file from a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "path": {"type": "string", "description": "File path in the repository"},
                    "ref": {"type": "string", "description": "Git reference", "default": "main"}
                },
                "required": ["owner", "repo", "path"]
            }
        ),
        
        types.Tool(
            name="github_get_issues",
            description="Get issues from a repository with filtering options",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "Label filters"}
                },
                "required": ["owner", "repo"]
            }
        ),
        
        types.Tool(
            name="github_create_issue",
            description="Create a new issue in a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "title": {"type": "string", "description": "Issue title"},
                    "body": {"type": "string", "description": "Issue description"},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "Issue labels"},
                    "assignees": {"type": "array", "items": {"type": "string"}, "description": "Issue assignees"}
                },
                "required": ["owner", "repo", "title"]
            }
        ),
        
        # Gemini AI Analysis Tools
        types.Tool(
            name="gemini_analyze_code",
            description="Analyze code using Gemini AI for quality, security, and performance insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Code to analyze"},
                    "language": {"type": "string", "description": "Programming language", "default": "auto"},
                    "analysis_type": {"type": "string", "enum": ["comprehensive", "security", "performance", "maintainability", "style"], "default": "comprehensive"},
                    "context": {"type": "string", "description": "Additional context about the code"}
                },
                "required": ["code"]
            }
        ),
        
        types.Tool(
            name="gemini_suggest_improvements",
            description="Get specific code improvement suggestions from Gemini AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Code to improve"},
                    "language": {"type": "string", "description": "Programming language", "default": "auto"},
                    "focus_areas": {"type": "array", "items": {"type": "string"}, "description": "Areas to focus on"},
                    "context": {"type": "string", "description": "Additional context"}
                },
                "required": ["code"]
            }
        ),
        
        types.Tool(
            name="gemini_generate_documentation",
            description="Generate comprehensive documentation for code using Gemini AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Code to document"},
                    "doc_type": {"type": "string", "enum": ["api", "user_guide", "developer_guide", "comprehensive"], "default": "comprehensive"},
                    "format": {"type": "string", "enum": ["markdown", "rst", "html", "plain"], "default": "markdown"},
                    "context": {"type": "string", "description": "Additional context"}
                },
                "required": ["code"]
            }
        ),
        
        # Combined Analysis Tools
        types.Tool(
            name="analysis_comprehensive_repo_analysis",
            description="Perform comprehensive repository analysis combining GitHub data with Gemini AI insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "focus_areas": {"type": "array", "items": {"type": "string"}, "description": "Areas to focus analysis on"},
                    "depth": {"type": "string", "enum": ["overview", "standard", "comprehensive", "deep"], "default": "comprehensive"}
                },
                "required": ["owner", "repo"]
            }
        ),
        
        types.Tool(
            name="analysis_smart_issue_triage",
            description="Intelligent issue triage and prioritization using Gemini AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "criteria": {"type": "string", "enum": ["default", "business_impact", "technical_debt", "security", "user_experience"], "default": "default"}
                },
                "required": ["owner", "repo"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[types.TextContent]:
    """Execute tool calls"""
    try:
        if name.startswith("github_"):
            result = await handle_github_tool(name, arguments)
        elif name.startswith("gemini_"):
            result = await handle_gemini_tool(name, arguments)
        elif name.startswith("analysis_"):
            result = await handle_analysis_tool(name, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
async def handle_github_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Handle GitHub-specific tools"""
    tool_name = name.replace("github_", "")
    
    if tool_name == "analyze_repository":
        return await github_client.analyze_repository(
            owner=arguments["owner"],
            repo=arguments["repo"],
            include_content=arguments.get("include_content", True)
        )
    
    elif tool_name == "search_code":
        return await github_client.search_code(
            query=arguments["query"],
            owner=arguments.get("owner"),
            repo=arguments.get("repo"),
            language=arguments.get("language"),
            filename=arguments.get("filename")
        )
    
    elif tool_name == "get_file_content":
        return await github_client.get_file_content(
            owner=arguments["owner"],
            repo=arguments["repo"],
            path=arguments["path"],
            ref=arguments.get("ref", "main")
        )
    
    elif tool_name == "get_issues":
        return await github_client.get_issues(
            owner=arguments["owner"],
            repo=arguments["repo"],
            state=arguments.get("state", "open"),
            labels=arguments.get("labels", [])
        )
    
    elif tool_name == "create_issue":
        return await github_client.create_issue(
            owner=arguments["owner"],
            repo=arguments["repo"],
            title=arguments["title"],
            body=arguments.get("body", ""),
            labels=arguments.get("labels", []),
            assignees=arguments.get("assignees", [])
        )
    
    else:
        raise ValueError(f"Unknown GitHub tool: {tool_name}")

async def handle_gemini_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Handle Gemini AI tools"""
    tool_name = name.replace("gemini_", "")
    
    if tool_name == "analyze_code":
        return await gemini_client.analyze_code(
            code=arguments["code"],
            language=arguments.get("language", "auto"),
            analysis_type=arguments.get("analysis_type", "comprehensive"),
            context=arguments.get("context", "")
        )
    
    elif tool_name == "suggest_improvements":
        return await gemini_client.suggest_improvements(
            code=arguments["code"],
            language=arguments.get("language", "auto"),
            focus_areas=arguments.get("focus_areas", []),
            context=arguments.get("context", "")
        )
    
    elif tool_name == "generate_documentation":
        return await gemini_client.generate_documentation(
            code=arguments["code"],
            doc_type=arguments.get("doc_type", "comprehensive"),
            format=arguments.get("format", "markdown"),
            context=arguments.get("context", "")
        )
    
    else:
        raise ValueError(f"Unknown Gemini tool: {tool_name}")

async def handle_analysis_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Handle combined GitHub + Gemini analysis tools"""
    tool_name = name.replace("analysis_", "")
    
    if tool_name == "comprehensive_repo_analysis":
        # Get repository structure and key files
        repo_data = await github_client.analyze_repository(
            owner=arguments["owner"],
            repo=arguments["repo"],
            include_content=True
        )
        
        # Use Gemini to analyze the repository
        analysis = await gemini_client.analyze_repository_structure(
            repo_data=repo_data,
            focus_areas=arguments.get("focus_areas", []),
            depth=arguments.get("depth", "comprehensive")
        )
        
        return {
            "repository_data": repo_data,
            "ai_analysis": analysis
        }
    
    elif tool_name == "smart_issue_triage":
        # Get issues from GitHub
        issues = await github_client.get_issues(
            owner=arguments["owner"],
            repo=arguments["repo"],
            state="open"
        )
        
        # Use Gemini to analyze and prioritize issues
        triage = await gemini_client.triage_issues(
            issues=issues,
            criteria=arguments.get("criteria", "default")
        )
        
        return {
            "issues": issues,
            "triage_analysis": triage
        }
    
    else:
        raise ValueError(f"Unknown analysis tool: {tool_name}")

async def main():
    """Main entry point for the MCP server"""
    logger.info("Starting GitHub-Gemini MCP Server")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, {})

if __name__ == "__main__":
    asyncio.run(main())
