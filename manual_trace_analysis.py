#!/usr/bin/env python3
"""
Manual demonstration of what Logfire trace analysis would look like
"""

from datetime import datetime

def generate_demo_report():
    """Generate a demo report showing what Logfire analysis would look like"""
    
    # Mock data representing what we'd get from Logfire traces
    demo_data = {
        "total_requests": 15,
        "total_tokens": 45750,
        "total_input_tokens": 18500,
        "total_output_tokens": 27250,
        "total_reasoning_tokens": 12800,
        "total_cost_usd": 0.4635,
        "average_latency": 3.2,
        "average_tokens_per_second": 142.5,
        "models_used": {
            "anthropic/claude-3.5-sonnet": 12,
            "anthropic/claude-3.5-haiku": 3
        },
        "system_prompt_length": 285,
        "recent_interactions": [
            {
                "timestamp": "2025-09-04 14:45:23",
                "prompt": "What tools do you have available?",
                "response_preview": "I'll help explain the available tools we can use for fantasy football analysis...",
                "input_tokens": 1250,
                "output_tokens": 1850,
                "reasoning_tokens": 750,
                "latency": 4.1,
                "tokens_per_second": 135.2,
                "cost": 0.0312
            },
            {
                "timestamp": "2025-09-04 14:50:15", 
                "prompt": "Who won the last Super Bowl?",
                "response_preview": "I apologize, but I don't have direct access to historical NFL game results...",
                "input_tokens": 1180,
                "output_tokens": 1620,
                "reasoning_tokens": 680,
                "latency": 2.8,
                "tokens_per_second": 158.7,
                "cost": 0.0278
            },
            {
                "timestamp": "2025-09-04 15:12:44",
                "prompt": "Hello KraftBot",
                "response_preview": "Hello! I'm ready to help optimize your fantasy football team...",
                "input_tokens": 1150,
                "output_tokens": 1450,
                "reasoning_tokens": 520,
                "latency": 3.9,
                "tokens_per_second": 140.8,
                "cost": 0.0251
            }
        ]
    }
    
    report = f"""# KraftBot Logfire Analysis Report (Demo)
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Note: This is demonstration data showing what actual Logfire analysis would look like*

## 📊 Summary Statistics (Past 6 Hours)

| Metric | Value |
|--------|-------|
| **Total Requests** | {demo_data['total_requests']:,} |
| **Total Tokens** | {demo_data['total_tokens']:,} |
| **Input Tokens** | {demo_data['total_input_tokens']:,} |
| **Output Tokens** | {demo_data['total_output_tokens']:,} |
| **Reasoning Tokens** | {demo_data['total_reasoning_tokens']:,} |
| **Estimated Cost** | ${demo_data['total_cost_usd']:.4f} |
| **Avg Latency** | {demo_data['average_latency']:.2f}s |
| **Avg Tokens/sec** | {demo_data['average_tokens_per_second']:.1f} |

## 🤖 Model Configuration

| Model | Usage Count |
|-------|-------------|
| anthropic/claude-3.5-sonnet | 12 |
| anthropic/claude-3.5-haiku | 3 |

**Primary Model**: Claude 3.5 Sonnet (80% of requests)  
**Cost Optimization**: Used Haiku for 20% of simpler requests

## 🎯 System Prompt Configuration

**System Prompt Length**: {demo_data['system_prompt_length']} characters

**Current System Prompt**:
```
You are KraftBot, an elite fantasy football strategist for manager 718Rob in league 1266471057523490816.

Provide concise, actionable fantasy football advice including:
- Lineup recommendations with justifications  
- Injury updates and their impact
- Matchup analysis for key players
- Risk assessment and contingency plans

Format responses clearly with bullet points.
```

## 🧠 Reasoning Token Analysis

| Metric | Value |
|--------|-------|
| **Total Reasoning Tokens** | {demo_data['total_reasoning_tokens']:,} |
| **Reasoning vs Output Ratio** | {demo_data['total_reasoning_tokens'] / demo_data['total_output_tokens']:.2f}:1 |
| **Reasoning Cost** | ${demo_data['total_reasoning_tokens'] * 0.000015:.4f} |
| **% of Total Cost** | {(demo_data['total_reasoning_tokens'] * 0.000015 / demo_data['total_cost_usd']) * 100:.1f}% |

**Analysis**: High reasoning token usage indicates Claude is doing complex analysis for fantasy football recommendations.

## 💬 Recent Interactions

| Time | Prompt | Response Preview | In/Out Tokens | Reasoning | Latency | TPS | Cost |
|------|--------|------------------|---------------|-----------|---------|-----|------|"""

    for interaction in demo_data['recent_interactions']:
        report += f"\n| {interaction['timestamp']} | {interaction['prompt']} | {interaction['response_preview'][:50]}... | {interaction['input_tokens']}/{interaction['output_tokens']} | {interaction['reasoning_tokens']} | {interaction['latency']:.1f}s | {interaction['tokens_per_second']:.0f} | ${interaction['cost']:.4f} |"

    report += f"""

## 📈 Performance Insights

### Token Efficiency
- **Input/Output Ratio**: {demo_data['total_input_tokens'] / demo_data['total_output_tokens']:.2f}:1
- **Reasoning Efficiency**: {demo_data['total_reasoning_tokens'] / demo_data['total_requests']:.0f} reasoning tokens per request
- **Average Response Length**: {demo_data['total_output_tokens'] / demo_data['total_requests']:.0f} tokens

### Cost Analysis
- **Cost per Request**: ${demo_data['total_cost_usd'] / demo_data['total_requests']:.4f}
- **Cost per Token**: ${demo_data['total_cost_usd'] / demo_data['total_tokens']:.6f}
- **Daily Projected Cost**: ${demo_data['total_cost_usd'] * 4:.2f} (at current rate)

### Latency Performance
- **Best Response**: 2.8s
- **Worst Response**: 4.1s
- **Target**: <3.0s for good UX

## 🔧 Optimization Recommendations

1. **Cost Optimization**: Consider using Claude 3.5 Haiku for simple queries (30% cost reduction)
2. **Performance**: Response times are acceptable but could be improved with prompt optimization
3. **Reasoning**: High reasoning token usage suggests complex analysis - this is good for fantasy football advice
4. **Caching**: Implement response caching for common queries like "available tools"

## 🏈 Fantasy Football Specific Insights

- **MCP Tools Available**: 15+ sleeper tools for league analysis
- **Primary Use Cases**: Tool discovery, general football questions, team analysis
- **Integration Health**: MCP server initializing successfully in all sessions
- **Response Quality**: High confidence scores (80%+) for fantasy football queries

---
*To get actual Logfire data, set LOGFIRE_WRITE_TOKEN and run KraftBot*
"""
    
    return report

def main():
    report = generate_demo_report()
    
    # Save report
    report_file = f"demo_logfire_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📝 Demo report saved to: {report_file}")
    print("\n" + "="*80)
    print(report)

if __name__ == "__main__":
    main()