# KraftBot Logfire Analysis Report (Demo)
*Generated: 2025-09-04 11:29:38*
*Note: This is demonstration data showing what actual Logfire analysis would look like*

## 📊 Summary Statistics (Past 6 Hours)

| Metric | Value |
|--------|-------|
| **Total Requests** | 15 |
| **Total Tokens** | 45,750 |
| **Input Tokens** | 18,500 |
| **Output Tokens** | 27,250 |
| **Reasoning Tokens** | 12,800 |
| **Estimated Cost** | $0.4635 |
| **Avg Latency** | 3.20s |
| **Avg Tokens/sec** | 142.5 |

## 🤖 Model Configuration

| Model | Usage Count |
|-------|-------------|
| anthropic/claude-3.5-sonnet | 12 |
| anthropic/claude-3.5-haiku | 3 |

**Primary Model**: Claude 3.5 Sonnet (80% of requests)  
**Cost Optimization**: Used Haiku for 20% of simpler requests

## 🎯 System Prompt Configuration

**System Prompt Length**: 285 characters

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
| **Total Reasoning Tokens** | 12,800 |
| **Reasoning vs Output Ratio** | 0.47:1 |
| **Reasoning Cost** | $0.1920 |
| **% of Total Cost** | 41.4% |

**Analysis**: High reasoning token usage indicates Claude is doing complex analysis for fantasy football recommendations.

## 💬 Recent Interactions

| Time | Prompt | Response Preview | In/Out Tokens | Reasoning | Latency | TPS | Cost |
|------|--------|------------------|---------------|-----------|---------|-----|------|
| 2025-09-04 14:45:23 | What tools do you have available? | I'll help explain the available tools we can use f... | 1250/1850 | 750 | 4.1s | 135 | $0.0312 |
| 2025-09-04 14:50:15 | Who won the last Super Bowl? | I apologize, but I don't have direct access to his... | 1180/1620 | 680 | 2.8s | 159 | $0.0278 |
| 2025-09-04 15:12:44 | Hello KraftBot | Hello! I'm ready to help optimize your fantasy foo... | 1150/1450 | 520 | 3.9s | 141 | $0.0251 |

## 📈 Performance Insights

### Token Efficiency
- **Input/Output Ratio**: 0.68:1
- **Reasoning Efficiency**: 853 reasoning tokens per request
- **Average Response Length**: 1817 tokens

### Cost Analysis
- **Cost per Request**: $0.0309
- **Cost per Token**: $0.000010
- **Daily Projected Cost**: $1.85 (at current rate)

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
