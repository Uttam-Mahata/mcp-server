# GitHub-Gemini MCP Server

An advanced Model Context Protocol (MCP) server that integrates GitHub with Google Gemini API for intelligent code assistance and repository management.

## Features

- **Intelligent Code Analysis**: Leverages Gemini's advanced reasoning capabilities to analyze code patterns and suggest improvements
- **Context-Aware Assistance**: Uses GitHub repository context to provide better code suggestions and documentation
- **Function Calling**: Intelligent tool selection for GitHub operations (issues, PRs, code search, etc.)
- **Structured Output**: JSON responses for integration with other tools
- **Code Execution**: Dynamic code analysis and execution for testing suggestions
- **Thinking Mode**: Deep reasoning for complex coding problems
- **Context Caching**: Efficient handling of large repositories with automatic caching

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_personal_access_token
```

## Usage

Run the MCP server:

```bash
python -m github_gemini_mcp
```

## Tools Available

### GitHub Integration
- Repository analysis and navigation
- Issue management and automation
- Pull request operations
- Code search and discovery
- Branch and commit operations

### Gemini AI Features
- Intelligent code suggestions
- Automated documentation generation
- Code review assistance
- Bug detection and fixing
- Architecture recommendations

## Architecture

The server combines:
- GitHub API integration for repository operations
- Gemini 2.5 models for advanced reasoning
- Function calling for intelligent tool selection
- Context caching for performance optimization
- Structured output for reliable integration

## License

MIT License
