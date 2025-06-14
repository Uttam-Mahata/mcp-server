import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for the GitHub-Gemini MCP Server"""
    
    def __init__(self):
        self.gemini_api_key = self._get_required_env("GEMINI_API_KEY")
        self.github_token = self._get_required_env("GITHUB_TOKEN")
        
        # Optional configurations
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.thinking_budget = int(os.getenv("THINKING_BUDGET", "1000"))
        self.enable_caching = os.getenv("ENABLE_CACHING", "true").lower() == "true"
        self.cache_ttl = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "1048576"))  # 1MB default
        self.github_base_url = os.getenv("GITHUB_BASE_URL", "https://api.github.com")
        
        # Gemini configuration
        self.enable_structured_output = os.getenv("ENABLE_STRUCTURED_OUTPUT", "true").lower() == "true"
        self.enable_function_calling = os.getenv("ENABLE_FUNCTION_CALLING", "true").lower() == "true"
        self.enable_code_execution = os.getenv("ENABLE_CODE_EXECUTION", "true").lower() == "true"
        self.enable_thinking = os.getenv("ENABLE_THINKING", "true").lower() == "true"
        
        # Server configuration
        self.server_host = os.getenv("SERVER_HOST", "localhost")
        self.server_port = int(os.getenv("SERVER_PORT", "8000"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise an error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def validate(self) -> bool:
        """Validate configuration"""
        try:
            # Validate API keys are present
            if not self.gemini_api_key or not self.github_token:
                return False
            
            # Validate numeric values
            if self.thinking_budget < 0 or self.cache_ttl < 0:
                return False
            
            if self.max_file_size < 1024:  # Minimum 1KB
                return False
            
            return True
        except Exception:
            return False
    
    def get_gemini_config(self) -> dict:
        """Get Gemini-specific configuration"""
        return {
            "api_key": self.gemini_api_key,
            "model": self.gemini_model,
            "thinking_budget": self.thinking_budget if self.enable_thinking else 0,
            "enable_caching": self.enable_caching,
            "cache_ttl": self.cache_ttl,
            "enable_structured_output": self.enable_structured_output,
            "enable_function_calling": self.enable_function_calling,
            "enable_code_execution": self.enable_code_execution
        }
    
    def get_github_config(self) -> dict:
        """Get GitHub-specific configuration"""
        return {
            "token": self.github_token,
            "base_url": self.github_base_url,
            "max_file_size": self.max_file_size
        }
