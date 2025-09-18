#!/usr/bin/env python3
"""
Script to analyze Logfire traces for KraftBot usage analytics.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
import json

def get_logfire_data(hours_back: int = 6) -> List[Dict[str, Any]]:
    """
    Fetch Logfire traces for the past N hours.
    
    Note: This requires the Logfire API endpoint and authentication.
    You'll need to replace with actual Logfire API details.
    """
    
    # This is a placeholder - you'll need to implement actual Logfire API calls
    # The Logfire Python SDK might have query capabilities, or you can use their REST API
    
    print(f"📊 Fetching Logfire traces from the past {hours_back} hours...")
    print("⚠️  This script needs to be configured with your Logfire API details.")
    print("📖 Check https://docs.pydantic.dev/logfire/ for API documentation.")
    
    return []

def analyze_traces(traces: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze traces and generate summary statistics."""
    
    if not traces:
        return {
            "total_requests": 0,
            "message": "No traces found. Make sure LOGFIRE_WRITE_TOKEN is set and KraftBot is logging data."
        }
    
    analysis = {
        "total_requests": len(traces),
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_tokens": 0,
        "total_reasoning_tokens": 0,
        "total_cost_usd": 0.0,
        "average_latency": 0.0,
        "average_tokens_per_second": 0.0,
        "models_used": {},
        "system_prompts": set(),
        "interactions": []
    }
    
    for trace in traces:
        extra = trace.get("extra", {})
        
        # Token analysis
        analysis["total_input_tokens"] += extra.get("input_tokens", 0)
        analysis["total_output_tokens"] += extra.get("output_tokens", 0)
        analysis["total_tokens"] += extra.get("total_tokens", 0)
        analysis["total_reasoning_tokens"] += extra.get("reasoning_tokens", 0)
        analysis["total_cost_usd"] += extra.get("estimated_cost_usd", 0.0)
        
        # Performance analysis
        latency = extra.get("response_time", 0)
        tps = extra.get("tokens_per_second", 0)
        analysis["average_latency"] += latency
        analysis["average_tokens_per_second"] += tps
        
        # Model usage
        model = extra.get("model", "unknown")
        analysis["models_used"][model] = analysis["models_used"].get(model, 0) + 1
        
        # System prompts
        if "system_prompt_length" in extra:
            analysis["system_prompts"].add(extra.get("system_prompt_length", 0))
        
        # Store interaction for detailed output
        analysis["interactions"].append({
            "timestamp": trace.get("timestamp", "unknown"),
            "prompt": extra.get("prompt", "")[:100] + "...",
            "response_length": extra.get("response_length", 0),
            "input_tokens": extra.get("input_tokens", 0),
            "output_tokens": extra.get("output_tokens", 0),
            "reasoning_tokens": extra.get("reasoning_tokens", 0),
            "latency": latency,
            "tokens_per_second": tps,
            "cost": extra.get("estimated_cost_usd", 0.0)
        })
    
    # Calculate averages
    if analysis["total_requests"] > 0:
        analysis["average_latency"] /= analysis["total_requests"]
        analysis["average_tokens_per_second"] /= analysis["total_requests"]
    
    analysis["system_prompts"] = list(analysis["system_prompts"])
    
    return analysis

def generate_markdown_report(analysis: Dict[str, Any]) -> str:
    """Generate a markdown report from the analysis."""
    
    if analysis["total_requests"] == 0:
        return f"""# KraftBot Logfire Analysis Report

## Summary
{analysis.get("message", "No data available")}

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
"""

    report = f"""# KraftBot Logfire Analysis Report
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📊 Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Requests** | {analysis['total_requests']:,} |
| **Total Tokens** | {analysis['total_tokens']:,} |
| **Input Tokens** | {analysis['total_input_tokens']:,} |
| **Output Tokens** | {analysis['total_output_tokens']:,} |
| **Reasoning Tokens** | {analysis['total_reasoning_tokens']:,} |
| **Estimated Cost** | ${analysis['total_cost_usd']:.4f} |
| **Avg Latency** | {analysis['average_latency']:.2f}s |
| **Avg Tokens/sec** | {analysis['average_tokens_per_second']:.1f} |

## 🤖 Model Configuration

| Model | Usage Count |
|-------|-------------|
"""
    
    for model, count in analysis['models_used'].items():
        report += f"| {model} | {count} |\n"
    
    report += f"""
## 🎯 System Prompt Configuration

System prompt lengths used: {', '.join(map(str, analysis['system_prompts']))} characters

## 💬 Recent Interactions

| Time | Prompt Preview | Tokens In/Out | Reasoning | Latency | TPS | Cost |
|------|----------------|---------------|-----------|---------|-----|------|
"""
    
    for interaction in analysis['interactions'][-10:]:  # Show last 10
        report += f"| {interaction['timestamp']} | {interaction['prompt']} | {interaction['input_tokens']}/{interaction['output_tokens']} | {interaction['reasoning_tokens']} | {interaction['latency']:.2f}s | {interaction['tokens_per_second']:.1f} | ${interaction['cost']:.4f} |\n"
    
    if analysis['total_reasoning_tokens'] > 0:
        report += f"""
## 🧠 Reasoning Analysis

- **Total Reasoning Tokens**: {analysis['total_reasoning_tokens']:,}
- **Reasoning vs Output Ratio**: {analysis['total_reasoning_tokens'] / analysis['total_output_tokens']:.2f}:1
- **Reasoning Cost**: ${analysis['total_reasoning_tokens'] * 0.000015:.4f}
"""
    
    return report

def main():
    """Main execution function."""
    
    # Check if Logfire token is configured
    logfire_token = os.getenv("LOGFIRE_WRITE_TOKEN")
    if not logfire_token:
        print("❌ LOGFIRE_WRITE_TOKEN environment variable not found!")
        print("💡 Get your token from: https://logfire.pydantic.dev/")
        print("💡 Then set it: export LOGFIRE_WRITE_TOKEN=your_token_here")
        sys.exit(1)
    
    # Fetch and analyze data
    traces = get_logfire_data(hours_back=6)
    analysis = analyze_traces(traces)
    
    # Generate report
    report = generate_markdown_report(analysis)
    
    # Save report
    report_file = f"logfire_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📝 Report saved to: {report_file}")
    print("\n" + "="*60)
    print(report)

if __name__ == "__main__":
    main()