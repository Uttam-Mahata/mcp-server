# GitHub-Gemini MCP Server - Usage Guide

## 🎉 Server Status: RUNNING

Your GitHub-Gemini MCP Server is now running successfully!

### Process Information
- **Process ID**: Running in background
- **Location**: `/home/uttammahata/mcp-server`
- **Status**: ✅ Active and listening

### Available Features

#### 🐙 GitHub Integration Tools
- `github_analyze_repository` - Comprehensive repository analysis
- `github_search_code` - Advanced code search across repositories
- `github_get_file_content` - Retrieve specific file contents
- `github_get_issues` - Fetch repository issues with filtering
- `github_create_issue` - Create new issues

#### 🤖 Gemini AI Tools
- `gemini_analyze_code` - AI-powered code analysis
- `gemini_suggest_improvements` - Code improvement suggestions
- `gemini_generate_documentation` - Auto-generate documentation

#### 🔍 Advanced Analysis Tools
- `analysis_comprehensive_repo_analysis` - Full repo analysis with AI insights
- `analysis_smart_issue_triage` - Intelligent issue prioritization

### How to Use

#### Option 1: Via MCP Client
Connect to the server using any MCP-compatible client:
```bash
# The server is listening on stdio for MCP protocol messages
# Use process ID or direct stdio communication
```

#### Option 2: Integration with Claude Desktop
Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "github-gemini": {
      "command": "python",
      "args": ["__main__.py"],
      "cwd": "/home/uttammahata/mcp-server"
    }
  }
}
```

#### Option 3: VS Code Extension
Create a VS Code extension that communicates with the MCP server.

### Configuration
- ✅ **Gemini API**: Configured and ready
- ✅ **GitHub Token**: Configured and ready
- ✅ **Model**: gemini-2.5-flash
- ✅ **Thinking Mode**: Enabled
- ✅ **Caching**: Enabled

### Example Usage Scenarios

1. **Repository Analysis**
   ```json
   {
     "tool": "analysis_comprehensive_repo_analysis",
     "arguments": {
       "owner": "microsoft",
       "repo": "vscode",
       "depth": "comprehensive"
     }
   }
   ```

2. **Code Review**
   ```json
   {
     "tool": "gemini_analyze_code",
     "arguments": {
       "code": "your code here",
       "analysis_type": "security"
     }
   }
   ```

3. **Issue Triage**
   ```json
   {
     "tool": "analysis_smart_issue_triage",
     "arguments": {
       "owner": "your-org",
       "repo": "your-repo"
     }
   }
   ```

### Server Management

- **Stop Server**: Find the process and kill it
- **Restart**: Run `python __main__.py` again
- **Logs**: Check terminal output where server was started

### Troubleshooting

1. **Server Not Responding**: Check if process is still running
2. **API Errors**: Verify API keys in `.env` file
3. **Rate Limits**: Server automatically handles GitHub rate limiting

---

🚀 **Your GitHub-Gemini MCP Server is ready for action!**

The server combines the power of GitHub's comprehensive API with Gemini's advanced AI capabilities to provide intelligent code assistance, repository management, and automated analysis tools.
