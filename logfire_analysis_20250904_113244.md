# KraftBot Logfire Analysis Report

## Summary
No traces found. Make sure LOGFIRE_WRITE_TOKEN is set and KraftBot is logging data.

## Setup Instructions

To get Logfire traces:

1. **Set LOGFIRE_WRITE_TOKEN**: Get your token from [Logfire Console](https://logfire.pydantic.dev/)
2. **Run KraftBot**: Use `python main.py chat` and have some conversations
3. **Re-run this script**: `python analyze_logfire.py`

The enhanced logging will capture:
- Token usage (input/output/reasoning)
- Response times and tokens per second
- Cost estimates
- System prompts
- Model configurations
