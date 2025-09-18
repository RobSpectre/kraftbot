"""
Configuration settings for KraftBot application.
"""

import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ModelConfig(BaseModel):
    """Configuration for a specific model"""

    name: str = Field(description="Model name (e.g., anthropic/claude-3.5-sonnet)")
    provider: str = Field(description="Model provider")
    description: Optional[str] = Field(None, description="Model description")
    strengths: List[str] = Field(default_factory=list, description="Model strengths")
    speed: str = Field("medium", description="Model speed rating")
    cost: str = Field("medium", description="Model cost rating")
    context_length: Optional[int] = Field(None, description="Maximum context length")

    class Config:
        """Pydantic configuration"""

        extra = "allow"


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Keys
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    logfire_write_token: Optional[str] = Field(None, env="LOGFIRE_WRITE_TOKEN")

    # Default Configuration
    default_model: str = Field("anthropic/claude-3.5-sonnet", env="DEFAULT_MODEL")
    default_user_id: str = Field("cli_user", env="DEFAULT_USER_ID")

    # Observability
    enable_logfire: bool = Field(True, env="ENABLE_LOGFIRE")
    verbose_logging: bool = Field(False, env="VERBOSE")

    # CLI Configuration
    cli_width: int = Field(120, env="CLI_WIDTH")
    cli_color: bool = Field(True, env="CLI_COLOR")
    cli_animations: bool = Field(True, env="CLI_ANIMATIONS")

    # Agent Configuration
    default_confidence_threshold: float = Field(0.7, env="CONFIDENCE_THRESHOLD")
    max_response_tokens: int = Field(2000, env="MAX_RESPONSE_TOKENS")
    request_timeout: int = Field(60, env="REQUEST_TIMEOUT")

    # System Prompt Configuration
    prompts_dir: Optional[str] = Field(None, env="PROMPTS_DIR")
    default_system_prompt_file: Optional[str] = Field(
        None, env="DEFAULT_SYSTEM_PROMPT_FILE"
    )

    # MCP Server Configuration
    mcp_server_command: str = Field("python", env="MCP_SERVER_COMMAND")
    mcp_server_args: str = Field("-m sleeper_mcp_server", env="MCP_SERVER_ARGS")
    enable_mcp_server: bool = Field(
        True, env="ENABLE_MCP_SERVER"
    )  # Enabled for Sleeper fantasy football functionality

    # Available Models Configuration
    available_models: Dict[str, ModelConfig] = Field(
        default_factory=lambda: {
            "anthropic/claude-3.5-sonnet": ModelConfig(
                name="anthropic/claude-3.5-sonnet",
                provider="Anthropic",
                description="Advanced reasoning and code generation",
                strengths=["Code", "Analysis", "Writing", "Reasoning"],
                speed="fast",
                cost="medium",
                context_length=200000,
            ),
            "openai/gpt-4": ModelConfig(
                name="openai/gpt-4",
                provider="OpenAI",
                description="General purpose large language model",
                strengths=["General Purpose", "Creative Writing", "Problem Solving"],
                speed="medium",
                cost="high",
                context_length=128000,
            ),
            "openai/gpt-4-turbo": ModelConfig(
                name="openai/gpt-4-turbo",
                provider="OpenAI",
                description="Faster version of GPT-4 with improved efficiency",
                strengths=["Speed", "Efficiency", "General Purpose"],
                speed="fast",
                cost="medium",
                context_length=128000,
            ),
            "meta-llama/llama-3.1-70b-instruct": ModelConfig(
                name="meta-llama/llama-3.1-70b-instruct",
                provider="Meta",
                description="Open source large language model",
                strengths=["Open Source", "Reasoning", "Code"],
                speed="medium",
                cost="low",
                context_length=32000,
            ),
            "google/gemini-pro": ModelConfig(
                name="google/gemini-pro",
                provider="Google",
                description="Multimodal AI with large context window",
                strengths=["Multimodal", "Large Context", "Analysis"],
                speed="fast",
                cost="low",
                context_length=1048576,
            ),
        }
    )

    class Config:
        """Pydantic settings configuration"""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"

    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""
        return self.available_models.get(model_name)

    def get_available_model_names(self) -> List[str]:
        """Get list of available model names"""
        return list(self.available_models.keys())

    def is_api_key_configured(self) -> bool:
        """Check if OpenRouter API key is configured"""
        return bool(self.openrouter_api_key)

    def is_logfire_configured(self) -> bool:
        """Check if Logfire is configured"""
        return bool(self.logfire_write_token and self.enable_logfire)

    def validate_environment(self) -> Dict[str, Any]:
        """Validate environment configuration and return status"""
        status = {
            "openrouter_api_key": {
                "configured": self.is_api_key_configured(),
                "status": "✅ Ready" if self.is_api_key_configured() else "❌ Missing",
                "required": True,
            },
            "logfire_token": {
                "configured": bool(self.logfire_write_token),
                "status": "✅ Enabled" if self.logfire_write_token else "⚠️  Disabled",
                "required": False,
            },
            "default_model": {
                "configured": self.default_model in self.available_models,
                "status": (
                    "✅ Valid"
                    if self.default_model in self.available_models
                    else "⚠️  Invalid"
                ),
                "value": self.default_model,
                "required": True,
            },
        }
        return status


# Global settings instance
settings = Settings()
