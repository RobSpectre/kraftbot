"""
Observability and logging configuration using Logfire.
"""

import os
from typing import Optional

import logfire


class LogfireConfig:
    """Configuration and management for Logfire observability"""

    def __init__(
        self,
        token: Optional[str] = None,
        service_name: str = "kraftbot",
        service_version: str = "1.0.0",
        auto_configure: bool = True,
    ):
        """
        Initialize Logfire configuration

        Args:
            token: Logfire write token (defaults to LOGFIRE_WRITE_TOKEN env var)
            service_name: Name of the service for logging
            service_version: Version of the service
            auto_configure: Whether to automatically configure Logfire
        """
        self.token = token or os.getenv("LOGFIRE_WRITE_TOKEN")
        self.service_name = service_name
        self.service_version = service_version
        self.configured = False

        if auto_configure and self.token:
            self.configure()

    def configure(self) -> bool:
        """
        Configure Logfire with the provided settings

        Returns:
            bool: True if configuration was successful, False otherwise
        """
        if not self.token:
            return False

        try:
            logfire.configure(
                token=self.token,
                service_name=self.service_name,
                service_version=self.service_version,
            )

            # Enable automatic instrumentation for token tracking
            try:
                logfire.instrument_pydantic_ai()
                logfire.instrument_mcp()
            except Exception as inst_error:
                print(f"⚠️  Instrumentation failed: {inst_error}")
                # Continue without instrumentation

            self.configured = True

            logfire.info(
                "Logfire configured successfully",
                extra={"service": self.service_name, "version": self.service_version},
            )

            return True

        except Exception as e:
            print(f"⚠️  Failed to configure Logfire: {e}")
            return False

    def log_agent_interaction(
        self,
        prompt: str,
        user_id: str,
        session_id: str,
        model_name: str,
        response_data: dict,
        system_prompt: Optional[str] = None,
        usage_data: Optional[dict] = None,
    ):
        """Log a detailed agent interaction with token usage and costs"""
        if not self.configured:
            return

        log_data = {
            "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            "prompt_length": len(prompt),
            "user_id": user_id,
            "session_id": session_id,
            "model": model_name,
            "system_prompt_length": len(system_prompt) if system_prompt else 0,
            **response_data,
        }

        # Add usage data if available
        if usage_data:
            log_data.update(
                {
                    "input_tokens": usage_data.get("input_tokens", 0),
                    "output_tokens": usage_data.get("output_tokens", 0),
                    "total_tokens": usage_data.get("total_tokens", 0),
                    "reasoning_tokens": usage_data.get("reasoning_tokens", 0),
                    "tokens_per_second": usage_data.get("tokens_per_second", 0),
                    "estimated_cost_usd": usage_data.get("estimated_cost", 0),
                    "cache_creation_input_tokens": usage_data.get(
                        "cache_creation_input_tokens", 0
                    ),
                    "cache_read_input_tokens": usage_data.get(
                        "cache_read_input_tokens", 0
                    ),
                }
            )

        logfire.info("Agent interaction", extra=log_data)

    def log_error(self, error: Exception, context: dict = None):
        """Log an error with context"""
        if not self.configured:
            return

        logfire.error(f"Error occurred: {str(error)}", extra=context or {})

    def create_span(self, name: str, **kwargs):
        """Create a Logfire span for tracking operations"""
        if not self.configured:
            return logfire.no_auto_trace()

        return logfire.span(name, **kwargs)
