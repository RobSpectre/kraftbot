"""
Kraftbot agent implementation with streaming support
"""

import time
import asyncio
from datetime import datetime
from typing import Optional, AsyncGenerator, List, Dict, Any
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.callbacks import get_openai_callback

from kraftbot.core.models import TokenCounter, AgentResponse

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    HAS_MCP_ADAPTERS = True
except ImportError:
    HAS_MCP_ADAPTERS = False


class KraftbotAgent:
    """
    Main Kraftbot agent with memory, MCP awareness, and streaming support
    """

    def __init__(
        self,
        model_name: str,
        api_key: str,
        system_prompt: str,
        mcp_enabled: bool = True,
        verbose: bool = False
    ):
        """
        Initialize Kraftbot agent

        Args:
            model_name: OpenRouter model name
            api_key: OpenRouter API key
            system_prompt: System prompt for the agent
            mcp_enabled: Enable MCP server integration
            verbose: Enable verbose logging
        """
        self.model_name = model_name
        self.base_system_prompt = system_prompt
        self.system_prompt = system_prompt
        self.memory = ConversationBufferMemory(return_messages=True)
        self.token_counter = TokenCounter()
        self.mcp_enabled = mcp_enabled
        self.verbose = verbose

        # Initialize MCP tools
        self.mcp_client = None
        self.mcp_tools = []
        self.agent_executor = None
        self.tool_calls = []  # Track tool calls for display

        # Initialize OpenRouter-compatible LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7,
            streaming=False,
            max_tokens=16000,
            default_headers={
                "HTTP-Referer": "https://github.com/RobSpectre/kraftbot",
                "X-Title": "Kraftbot Fantasy Football Assistant"
            }
        )

        # LLM for streaming (separate instance to avoid conflicts)
        self.streaming_llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7,
            streaming=True,
            max_tokens=16000,
            default_headers={
                "HTTP-Referer": "https://github.com/RobSpectre/kraftbot",
                "X-Title": "Kraftbot Fantasy Football Assistant"
            }
        )

    async def initialize(self):
        """Initialize the agent (must be called before use)"""
        if self.mcp_enabled and HAS_MCP_ADAPTERS:
            try:
                if self.verbose:
                    print("Connecting to MCP servers via LangChain...")

                # Use LangChain's native MCP support
                self.mcp_client = MultiServerMCPClient({
                    "tokenbowl": {
                        "transport": "sse",
                        "url": "https://tokenbowl-mcp.haihai.ai/sse"
                    }
                })

                # Get all tools from MCP servers
                self.mcp_tools = await self.mcp_client.get_tools()

                if self.mcp_tools:
                    # Use tool calling agent for OpenAI models, ReAct for others
                    is_openai_model = self.model_name.startswith('openai/')

                    if is_openai_model:
                        if self.verbose:
                            print("Using tool calling agent for OpenAI model")
                        # OpenAI models work best with native tool calling
                        prompt = ChatPromptTemplate.from_messages([
                            ("system", self.base_system_prompt),
                            MessagesPlaceholder("chat_history", optional=True),
                            ("human", "{input}"),
                            MessagesPlaceholder("agent_scratchpad"),
                        ])
                        agent = create_tool_calling_agent(self.llm, self.mcp_tools, prompt)
                    else:
                        if self.verbose:
                            print("Using structured chat agent for non-OpenAI model")
                        # Non-OpenAI models work better with structured chat (handles JSON tool inputs)
                        from langchain import hub
                        try:
                            # Try to load the standard structured chat prompt
                            structured_prompt = hub.pull("hwchase17/structured-chat-agent")
                            # Prepend our system prompt
                            structured_prompt.messages[0].prompt.template = self.base_system_prompt + "\n\n" + structured_prompt.messages[0].prompt.template
                        except:
                            # Fallback to manual structured chat prompt if hub is unavailable
                            structured_prompt = ChatPromptTemplate.from_messages([
                                ("system", self.base_system_prompt + """

Respond to the human as helpfully and accurately as possible. You have access to the following tools:

{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Follow this format:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}
```"""),
                                MessagesPlaceholder("chat_history", optional=True),
                                ("human", "{input}\n\n{agent_scratchpad}"),
                            ])
                        agent = create_structured_chat_agent(self.llm, self.mcp_tools, structured_prompt)

                    self.agent_executor = AgentExecutor(
                        agent=agent,
                        tools=self.mcp_tools,
                        verbose=self.verbose,
                        return_intermediate_steps=True,
                        handle_parsing_errors=True,
                        max_iterations=50,
                        max_execution_time=900
                    )

                    if self.verbose:
                        print(f"✓ Initialized agent with {len(self.mcp_tools)} MCP tools")
                        for tool in self.mcp_tools:
                            print(f"  - {tool.name}")
                else:
                    if self.verbose:
                        print("⚠ No tools discovered from MCP server")

            except Exception as e:
                if self.verbose:
                    print(f"⚠ Failed to connect to MCP server: {e}")
                self.mcp_tools = []
                self.agent_executor = None
        elif self.mcp_enabled and not HAS_MCP_ADAPTERS:
            if self.verbose:
                print("⚠ MCP enabled but langchain-mcp-adapters not installed")
                print("  Install with: pip install langchain-mcp-adapters")

    def get_current_week(self) -> str:
        """Estimate current fantasy football week"""
        month = datetime.now().month
        day = datetime.now().day

        if month < 9:
            return "Pre-Season"
        elif month == 9:
            if day < 10:
                return "Week 1"
            elif day < 17:
                return "Week 2"
            elif day < 24:
                return "Week 3"
            else:
                return "Week 4"
        elif month == 10:
            week = 4 + ((day - 1) // 7) + 1
            return f"Week {week}"
        elif month == 11:
            week = 8 + ((day - 1) // 7) + 1
            return f"Week {week}"
        elif month == 12:
            week = 13 + ((day - 1) // 7)
            return f"Week {week}"
        elif month == 1:
            return "Playoffs"
        else:
            return "Off-Season"

    def _build_messages(self, user_input: str) -> list:
        """Build messages list for LLM"""
        messages = [SystemMessage(content=self.system_prompt)]

        # Add conversation history
        history = self.memory.chat_memory.messages
        messages.extend(history)

        # Add current user message
        messages.append(HumanMessage(content=user_input))

        return messages

    async def chat(self, user_input: str) -> AgentResponse:
        """
        Process a single chat interaction (non-streaming)

        Args:
            user_input: User's input message

        Returns:
            AgentResponse with formatted output
        """
        start_time = time.time()
        self.tool_calls = []  # Reset tool calls tracking

        try:
            # Use agent executor if tools are available, otherwise use standard chat
            if self.agent_executor and self.mcp_tools:
                # Reset token counter for this request
                self.token_counter.reset()

                # Get chat history for context
                chat_history = self.memory.chat_memory.messages

                if self.verbose:
                    print(f"\n[DEBUG] Starting agent executor with {len(self.mcp_tools)} tools")

                # Use get_openai_callback to track token usage
                with get_openai_callback() as cb:
                    # Invoke agent with tools
                    if self.verbose:
                        print("[DEBUG] Calling agent_executor.ainvoke()...")
                    result = await self.agent_executor.ainvoke(
                        {
                            "input": user_input,
                            "chat_history": chat_history
                        }
                    )

                    if self.verbose:
                        print(f"[DEBUG] Agent executor returned, tokens used: {cb.total_tokens}")

                    # Update token counter from callback
                    self.token_counter.input_tokens = cb.prompt_tokens
                    self.token_counter.output_tokens = cb.completion_tokens
                    self.token_counter.total_tokens = cb.total_tokens

                # Extract response and intermediate steps
                if self.verbose:
                    print(f"[DEBUG] Extracting response, result keys: {result.keys()}")
                response_content = result.get("output", "")
                if self.verbose:
                    print(f"[DEBUG] Response content length: {len(response_content) if response_content else 0}")

                # Check if we got an empty response
                if not response_content:
                    if self.verbose:
                        print("[DEBUG] WARNING: Agent returned empty output!")
                    # Check if the agent hit max iterations or other limits
                    if "intermediate_steps" in result:
                        step_count = len(result.get("intermediate_steps", []))
                        if step_count >= 50:
                            response_content = "I gathered a lot of information but hit the maximum number of tool calls. Please try asking a more specific question."
                        else:
                            response_content = "I was unable to generate a response. Please try rephrasing your question."

                intermediate_steps = result.get("intermediate_steps", [])

                # Track tool calls
                if self.verbose:
                    print(f"[DEBUG] Processing {len(intermediate_steps)} intermediate steps")
                for step in intermediate_steps:
                    if len(step) >= 2:
                        action, observation = step
                        self.tool_calls.append({
                            "tool": action.tool,
                            "input": action.tool_input,
                            "output": observation
                        })

                # Update memory
                if self.verbose:
                    print("[DEBUG] Updating memory...")
                self.memory.chat_memory.add_user_message(user_input)
                self.memory.chat_memory.add_ai_message(response_content)

                # Calculate response time
                response_time = time.time() - start_time

                if self.verbose:
                    print(f"[DEBUG] Creating response object (time: {response_time:.2f}s)")

                # Create response object with tool calls
                mcp_status = f"Connected ({len(self.mcp_tools)} tools)" if self.mcp_tools else "Disabled"
                agent_response = AgentResponse(
                    content=response_content,
                    response_time=response_time,
                    tokens=self.token_counter.get_summary(),
                    week=self.get_current_week(),
                    model_name=self.model_name,
                    system_prompt=self.system_prompt,
                    user_prompt=user_input,
                    mcp_status=mcp_status,
                    tool_calls=self.tool_calls
                )

                if self.verbose:
                    print(f"[DEBUG] Returning response object")

                return agent_response

            else:
                # Standard chat without tools
                messages = self._build_messages(user_input)

                # Get response from model
                response = await asyncio.to_thread(self.llm.invoke, messages)

                # Update token counter
                self.token_counter.update(response)

                # Extract reasoning if available
                reasoning = None
                if hasattr(response, 'additional_kwargs'):
                    reasoning = response.additional_kwargs.get('reasoning', None)

                # Update memory
                self.memory.chat_memory.add_user_message(user_input)
                self.memory.chat_memory.add_ai_message(response.content)

                # Calculate response time
                response_time = time.time() - start_time

                # Create response object
                mcp_status = f"Connected ({len(self.mcp_tools)} tools)" if self.mcp_tools else "Disabled"
                agent_response = AgentResponse(
                    content=response.content,
                    response_time=response_time,
                    tokens=self.token_counter.get_summary(),
                    week=self.get_current_week(),
                    model_name=self.model_name,
                    system_prompt=self.system_prompt,
                    user_prompt=user_input,
                    reasoning=reasoning,
                    mcp_status=mcp_status
                )

                return agent_response

        except Exception as e:
            mcp_status = f"Connected ({len(self.mcp_tools)} tools)" if self.mcp_tools else "Disabled"
            return AgentResponse(
                content=f"Error processing request: {str(e)}",
                response_time=time.time() - start_time,
                tokens=self.token_counter.get_summary(),
                week=self.get_current_week(),
                model_name=self.model_name,
                system_prompt=self.system_prompt,
                user_prompt=user_input,
                mcp_status=mcp_status,
                error=str(e)
            )

    async def chat_stream(self, user_input: str) -> AsyncGenerator[str, None]:
        """
        Process a single chat interaction with streaming output

        Args:
            user_input: User's input message

        Yields:
            Chunks of the response as they arrive
        """
        messages = self._build_messages(user_input)
        full_response = ""

        try:
            # Stream the response
            async for chunk in self.streaming_llm.astream(messages):
                if chunk.content:
                    full_response += chunk.content
                    yield chunk.content

            # Update memory after streaming is complete
            self.memory.chat_memory.add_user_message(user_input)
            self.memory.chat_memory.add_ai_message(full_response)

        except Exception as e:
            error_msg = f"\n\n[Error: {str(e)}]"
            yield error_msg
            # Still update memory even on error
            if full_response:
                self.memory.chat_memory.add_user_message(user_input)
                self.memory.chat_memory.add_ai_message(full_response + error_msg)

    def clear_memory(self):
        """Clear conversation history"""
        self.memory.clear()
        self.token_counter.reset()

    def get_mcp_status_info(self) -> dict:
        """Get MCP server status information"""
        return {
            'enabled': self.mcp_enabled,
            'connected': self.mcp_client is not None,
            'tools_count': len(self.mcp_tools),
            'tools': [tool.name for tool in self.mcp_tools] if self.mcp_tools else []
        }
