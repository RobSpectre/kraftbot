# Fantasy-Football Week-Setting Prompt for MCP-Agent  
(Re-written for tool-driven, not endpoint-driven, interaction)

## 1. Establish MCP session  
Connect to the MCP server that fronts your fantasy league.  
Your client already knows the list of available tools—don’t guess their names.  
Use the built-in `list_tools` call (or equivalent) to discover what is offered.  
Keep that list in context; you will map each need below to the closest-matching tool.

------------------------------------------------
## 2. Collect the state of the universe  
You must obtain seven **classes** of information.  
Pick whichever tools give you each class; if none exist, SAY SO and abort rather than invent.

| Class of data | How you will use it |
|---------------|---------------------|
| League rules & roster slots | Know how many players you must start at each position and what scoring system applies. |
| Current week & lock time | Know the deadline after which no lineup changes are allowed. |
| Your full roster | Get every player you own, their positions, bye weeks, and current injury tags. |
| Point projections | Fetch forecasted fantasy points for the upcoming scoring period. |
| News / injury report | Convert tags like “Out”, “Doubtful”, “Questionable” into a go/no-go decision. |
| Opponent strength vs. position | See how generous each player’s upcoming NFL opponent has been to that position. |
| Any already-locked spots | Prevent you from moving players whose games have kicked off. |

Query only the tools that provide the above.  
Cache the returned JSON under human-readable keys (`league_rules`, `proj_map`, etc.).

------------------------------------------------
## 3. Filter & Rank  
For every player you control, build a simple record:  
`{ id, pos, pts, floor, ceil, injury, opp_rank, locked?, bye? }`

**Hard filters**  
- Drop “Out” players.  
- Drop players on a bye.  
- Honor locked slots—do not touch them.

**Scoring slot fill order**  
1. Fill required positions first (QB, RB, WR, TE, D/ST, K).  
2. Then FLEX (RB/WR/TE) using best remaining eligible player.  
3. If super-flex or IDP slots exist, fill them last.

**Tie-breaker stack (apply in order)**  
a. Highest expected points.  
b. Lowest injury risk.  
c. Highest floor when expected points differ by ≤ 1.  
d. Softer opponent rank (lower number = easier matchup).  

------------------------------------------------
## 4. Commit the lineup  
Locate the tool whose description contains phrases like “set starters”, “submit lineup”, or “update roster”.  
Construct its required payload—usually an array mapping slot names to player IDs.  
Call the validation flavour first if one exists; fix any rejected slots and retry (max 3 times).  
On success, log the server’s confirmation token and print a short summary to stdout:
