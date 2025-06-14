from typing import List
from mcp.types import Tool
import mcp.types as types

def get_available_tools() -> List[Tool]:
    """Get all available MCP tools"""
    
    return [
        # GitHub Repository Tools
        Tool(
            name="github_analyze_repository",
            description="Comprehensive analysis of a GitHub repository including structure, content, and metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner/organization name"
                    },
                    "repo": {
                        "type": "string", 
                        "description": "Repository name"
                    },
                    "include_content": {
                        "type": "boolean",
                        "description": "Whether to include file contents in analysis",
                        "default": True
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        
        Tool(
            name="github_search_code",
            description="Search for code across GitHub repositories with advanced filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for code"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Repository owner to limit search"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name to limit search"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language filter"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Filename pattern filter"
                    }
                },
                "required": ["query"]
            }
        ),
        
        Tool(
            name="github_get_file_content",
            description="Get the content of a specific file from a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "path": {
                        "type": "string",
                        "description": "File path in the repository"
                    },
                    "ref": {
                        "type": "string",
                        "description": "Git reference (branch, tag, or commit SHA)",
                        "default": "main"
                    }
                },
                "required": ["owner", "repo", "path"]
            }
        ),
        
        Tool(
            name="github_update_file",
            description="Update or create a file in a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "path": {
                        "type": "string",
                        "description": "File path in the repository"
                    },
                    "content": {
                        "type": "string",
                        "description": "New file content"
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message"
                    },
                    "sha": {
                        "type": "string",
                        "description": "Current file SHA (for updates)"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Target branch",
                        "default": "main"
                    }
                },
                "required": ["owner", "repo", "path", "content", "message"]
            }
        ),
        
        # GitHub Issues Tools
        Tool(
            name="github_get_issues",
            description="Get issues from a repository with filtering options",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "state": {
                        "type": "string",
                        "enum": ["open", "closed", "all"],
                        "description": "Issue state filter",
                        "default": "open"
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Label filters"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        
        Tool(
            name="github_create_issue",
            description="Create a new issue in a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "title": {
                        "type": "string",
                        "description": "Issue title"
                    },
                    "body": {
                        "type": "string",
                        "description": "Issue description"
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Issue labels"
                    },
                    "assignees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Issue assignees"
                    }
                },
                "required": ["owner", "repo", "title"]
            }
        ),
        
        # GitHub Pull Request Tools
        Tool(
            name="github_get_pull_requests",
            description="Get pull requests from a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "state": {
                        "type": "string",
                        "enum": ["open", "closed", "all"],
                        "description": "Pull request state",
                        "default": "open"
                    },
                    "base": {
                        "type": "string",
                        "description": "Base branch filter"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        
        Tool(
            name="github_create_pull_request",
            description="Create a new pull request",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "title": {
                        "type": "string",
                        "description": "Pull request title"
                    },
                    "body": {
                        "type": "string",
                        "description": "Pull request description"
                    },
                    "head": {
                        "type": "string",
                        "description": "Head branch (source)"
                    },
                    "base": {
                        "type": "string",
                        "description": "Base branch (target)",
                        "default": "main"
                    }
                },
                "required": ["owner", "repo", "title", "head"]
            }
        ),
        
        # Gemini AI Analysis Tools
        Tool(
            name="gemini_analyze_code",
            description="Analyze code using Gemini AI for quality, security, and performance insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to analyze"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                        "default": "auto"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["comprehensive", "security", "performance", "maintainability", "style"],
                        "description": "Type of analysis to perform",
                        "default": "comprehensive"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context about the code"
                    }
                },
                "required": ["code"]
            }
        ),
        
        Tool(
            name="gemini_suggest_improvements",
            description="Get specific code improvement suggestions from Gemini AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to improve"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                        "default": "auto"
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Areas to focus on (e.g., performance, readability, security)"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context"
                    }
                },
                "required": ["code"]
            }
        ),
        
        Tool(
            name="gemini_generate_documentation",
            description="Generate comprehensive documentation for code using Gemini AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to document"
                    },
                    "doc_type": {
                        "type": "string",
                        "enum": ["api", "user_guide", "developer_guide", "comprehensive"],
                        "description": "Type of documentation",
                        "default": "comprehensive"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["markdown", "rst", "html", "plain"],
                        "description": "Documentation format",
                        "default": "markdown"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context"
                    }
                },
                "required": ["code"]
            }
        ),
        
        Tool(
            name="gemini_explain_code",
            description="Get detailed code explanations from Gemini AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to explain"
                    },
                    "level": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"],
                        "description": "Explanation level",
                        "default": "intermediate"
                    },
                    "focus": {
                        "type": "string",
                        "enum": ["functionality", "algorithm", "architecture", "patterns"],
                        "description": "Focus area for explanation",
                        "default": "functionality"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context"
                    }
                },
                "required": ["code"]
            }
        ),
        
        Tool(
            name="gemini_review_pull_request",
            description="Perform AI-powered code review of a pull request diff",
            inputSchema={
                "type": "object",
                "properties": {
                    "diff": {
                        "type": "string",
                        "description": "Pull request diff content"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context about the changes"
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Areas to focus on in the review"
                    }
                },
                "required": ["diff"]
            }
        ),
        
        Tool(
            name="gemini_generate_tests",
            description="Generate comprehensive test cases for code using Gemini AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to generate tests for"
                    },
                    "test_framework": {
                        "type": "string",
                        "description": "Testing framework to use",
                        "default": "auto"
                    },
                    "coverage_level": {
                        "type": "string",
                        "enum": ["basic", "standard", "comprehensive", "exhaustive"],
                        "description": "Test coverage level",
                        "default": "comprehensive"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context"
                    }
                },
                "required": ["code"]
            }
        ),
        
        # Combined Analysis Tools
        Tool(
            name="analysis_comprehensive_repo_analysis",
            description="Perform comprehensive repository analysis combining GitHub data with Gemini AI insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Areas to focus analysis on"
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["overview", "standard", "comprehensive", "deep"],
                        "description": "Analysis depth",
                        "default": "comprehensive"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        
        Tool(
            name="analysis_smart_issue_triage",
            description="Intelligent issue triage and prioritization using Gemini AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "criteria": {
                        "type": "string",
                        "enum": ["default", "business_impact", "technical_debt", "security", "user_experience"],
                        "description": "Triage criteria",
                        "default": "default"
                    }
                },
                "required": ["owner", "repo"]
            }
        ),
        
        Tool(
            name="analysis_automated_code_review",
            description="Automated comprehensive code review of pull requests using Gemini AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "Repository owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "pr_number": {
                        "type": "integer",
                        "description": "Pull request number"
                    },
                    "review_level": {
                        "type": "string",
                        "enum": ["quick", "standard", "thorough", "exhaustive"],
                        "description": "Review thoroughness level",
                        "default": "thorough"
                    }
                },
                "required": ["owner", "repo", "pr_number"]
            }
        )
    ]
