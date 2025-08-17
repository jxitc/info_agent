"""
Memory Agent using LangGraph with ReAct Architecture

Improved version that addresses TODOs and FIXMEs:
1. Removes unnecessary classify_query step  
2. Implements ReAct loop (agent_reasoning ↔ execute_tools)
3. Supports extensible multi-step operations (create/dedup/update)
"""

import json
import logging
from typing import Dict, List, Any, TypedDict, Annotated, Optional, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START, add_messages

# Try relative imports first, fall back to absolute imports for LangGraph Studio
try:
    from ..tools.memory_tools import get_all_memory_tools, get_search_tools
    from ..utils.langsmith_config import (
        setup_langsmith_tracing, 
        trace_agent_operation, 
        create_run_context,
        log_tool_execution
    )
except ImportError:
    # Fallback for LangGraph Studio - use absolute imports
    import sys
    import os
    from pathlib import Path
    
    # Add project root to path
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from info_agent.tools.memory_tools import get_all_memory_tools, get_search_tools
    from info_agent.utils.langsmith_config import (
        setup_langsmith_tracing, 
        trace_agent_operation, 
        create_run_context,
        log_tool_execution
    )

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Enhanced state for the memory agent workflow with ReAct support"""
    messages: Annotated[List[BaseMessage], add_messages]
    user_query: str
    operation_type: Optional[str]  # 'search', 'create', 'update', 'delete'
    iteration_count: int
    max_iterations: int
    search_results: Optional[Dict[str, Any]]
    final_response: Optional[str]
    next_action: Optional[str]  # For ReAct loop control


class MemoryAgent:
    """
    Memory Agent with ReAct architecture and extensible operations.
    
    Features:
    1. Direct agent reasoning (no unnecessary classification)
    2. ReAct loop for multi-step operations
    3. Support for complex workflows (search → analyze → act)
    4. Extensible for future operations (create, dedup, update)
    """
    
    def __init__(self, model: str = "gpt-4o-mini", tools: List[BaseTool] = None, max_iterations: int = 5):
        """
        Initialize Memory Agent
        
        Args:
            model: OpenAI model to use for reasoning
            tools: List of tools (defaults to all memory tools)
            max_iterations: Maximum ReAct iterations to prevent infinite loops
        """
        self.model = model
        self.tools = tools or get_all_memory_tools()
        self.max_iterations = max_iterations
        
        # Setup LangSmith tracing if configured
        self.langsmith_enabled = setup_langsmith_tracing("info-agent-memory")
        if self.langsmith_enabled:
            logger.info("✅ LangSmith tracing enabled for Memory Agent")
        else:
            logger.info("ℹ️ LangSmith tracing not configured or disabled")
        
        # Initialize LLM with tools
        self.llm = ChatOpenAI(model=model, temperature=0).bind_tools(self.tools)
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        
        logger.info(f"Memory Agent initialized with {len(self.tools)} tools, max_iterations: {max_iterations}")
    
    def _build_workflow(self) -> StateGraph:
        """Build the enhanced LangGraph workflow with ReAct pattern"""
        
        # Create workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for ReAct architecture
        workflow.add_node("agent_reasoning", self._agent_reasoning)
        workflow.add_node("execute_tools", self._execute_tools)
        workflow.add_node("should_continue", self._should_continue)
        workflow.add_node("format_response", self._format_response)
        
        # Add edges for ReAct loop
        workflow.add_edge(START, "agent_reasoning")
        workflow.add_edge("agent_reasoning", "execute_tools")
        workflow.add_edge("execute_tools", "should_continue")
        
        # Conditional edges for ReAct loop
        workflow.add_conditional_edges(
            "should_continue",
            self._route_next_action,
            {
                "continue": "agent_reasoning",  # Continue ReAct loop
                "finish": "format_response"     # End workflow
            }
        )
        
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    @trace_agent_operation("agent_reasoning", {"component": "memory_agent", "step": "reasoning"})
    def _agent_reasoning(self, state: AgentState) -> Dict[str, Any]:
        """Enhanced reasoning step that handles various operation types"""
        
        # Extract user query from state or messages
        user_query = state.get("user_query")
        if not user_query and state.get("messages"):
            # Extract from the first human message if user_query is not provided
            for msg in state["messages"]:
                if hasattr(msg, 'content') and msg.content:
                    user_query = msg.content
                    break
        
        if not user_query:
            user_query = "Show me my recent memories"  # Default fallback
            
        iteration = state.get("iteration_count", 0)
        search_results = state.get("search_results", {})
        
        # Determine operation type if not set
        operation_type = state.get("operation_type")
        if not operation_type:
            operation_type = self._detect_operation_type(user_query)
        
        # Create context-aware reasoning prompt
        if iteration == 0:
            # First iteration - initial reasoning
            reasoning_prompt = f"""
            User Query: "{user_query}"
            Operation Type: {operation_type}
            
            Available tools: {[tool.name for tool in self.tools]}
            
            You are a personal memory assistant. Based on the user's query, determine the best approach to help them.
            
            For search operations: Use the most appropriate search tool (hybrid is usually best for complex queries).
            For future memory creation: You would search for similar memories first to avoid duplicates.
            For memory updates: You would retrieve the specific memory and related ones.
            
            Start by using the appropriate tools to help the user.
            """
        else:
            # Subsequent iterations - analyze previous results and decide next action
            reasoning_prompt = f"""
            User Query: "{user_query}"
            Operation Type: {operation_type}
            Iteration: {iteration}
            
            Previous search results: {json.dumps(search_results, indent=2)}
            
            Available tools: {[tool.name for tool in self.tools]}
            
            Based on the previous results, determine if you need to:
            1. Use additional tools to get more information
            2. Search with different parameters
            3. You have enough information to provide a final response
            
            If you have sufficient information, don't call any tools and I'll format the final response.
            Otherwise, use the appropriate tools to gather more information.
            """
        
        # Get LLM response with potential tool calls
        messages = state["messages"] + [HumanMessage(content=reasoning_prompt)]
        response = self.llm.invoke(messages)
        
        logger.info(f"Agent reasoning iteration {iteration}, tool calls: {len(response.tool_calls) if response.tool_calls else 0}")
        
        return {
            "messages": state["messages"] + [response],
            "user_query": user_query,
            "operation_type": operation_type,
            "iteration_count": iteration + 1
        }
    
    @trace_agent_operation("execute_tools", {"component": "memory_agent", "step": "tool_execution"})
    def _execute_tools(self, state: AgentState) -> Dict[str, Any]:
        """Execute tool calls and update search results"""
        
        last_message = state["messages"][-1]
        current_results = state.get("search_results", {})
        
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            logger.info("No tool calls to execute in this iteration")
            return {
                "search_results": current_results,
                "next_action": "finish"  # No tools called, ready to finish
            }
        
        # Execute tool calls
        tool_messages = []
        new_results = {}
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
            
            # Find and execute the tool
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if tool:
                try:
                    result = tool.invoke(tool_args)
                    tool_messages.append(ToolMessage(
                        content=result,
                        tool_call_id=tool_call["id"]
                    ))
                    new_results[tool_name] = json.loads(result) if result.startswith('{') else result
                    logger.info(f"Tool {tool_name} executed successfully")
                    
                    # Log tool execution to LangSmith
                    log_tool_execution(tool_name, tool_args, result)
                    
                except Exception as e:
                    error_msg = f"Error executing {tool_name}: {str(e)}"
                    tool_messages.append(ToolMessage(
                        content=error_msg,
                        tool_call_id=tool_call["id"]
                    ))
                    new_results[tool_name] = {"error": str(e)}
                    logger.error(error_msg)
                    
                    # Log tool execution error to LangSmith
                    log_tool_execution(tool_name, tool_args, None, error_msg)
            else:
                error_msg = f"Tool {tool_name} not found"
                tool_messages.append(ToolMessage(
                    content=error_msg,
                    tool_call_id=tool_call["id"]
                ))
                new_results[tool_name] = {"error": "Tool not found"}
                logger.error(error_msg)
        
        # Merge new results with existing results
        merged_results = {**current_results, **new_results}
        
        return {
            "messages": state["messages"] + tool_messages,
            "search_results": merged_results,
            "next_action": "continue"  # Tools were executed, continue reasoning
        }
    
    def _should_continue(self, state: AgentState) -> Dict[str, Any]:
        """Determine if the ReAct loop should continue or finish"""
        
        iteration_count = state["iteration_count"]
        max_iterations = state.get("max_iterations", self.max_iterations)
        next_action = state.get("next_action", "continue")
        
        # Stop if max iterations reached
        if iteration_count >= max_iterations:
            logger.info(f"Reached max iterations ({max_iterations}), finishing")
            next_action = "finish"
        
        # Stop if previous step indicated we should finish
        if next_action == "finish":
            logger.info(f"Finishing after {iteration_count} iterations")
        
        return {"next_action": next_action}
    
    def _route_next_action(self, state: AgentState) -> Literal["continue", "finish"]:
        """Route the workflow based on next_action"""
        next_action = state.get("next_action", "finish")
        return "continue" if next_action == "continue" else "finish"
    
    @trace_agent_operation("format_response", {"component": "memory_agent", "step": "response_formatting"})
    def _format_response(self, state: AgentState) -> Dict[str, Any]:
        """Format the final response based on all search results"""
        
        search_results = state.get("search_results", {})
        user_query = state["user_query"]
        operation_type = state.get("operation_type", "search")
        iteration_count = state["iteration_count"]
        
        if not search_results:
            final_response = "I wasn't able to find information to help with your request. Please try rephrasing your query."
        else:
            # Let LLM format the response based on all accumulated results
            format_prompt = f"""
            User asked: "{user_query}"
            Operation type: {operation_type}
            Processing iterations: {iteration_count}
            
            All search results gathered: {json.dumps(search_results, indent=2)}
            
            Please provide a helpful, conversational response based on these search results.
            
            Guidelines:
            - If memories were found, summarize the key information clearly
            - If no memories were found, suggest alternative search terms or approaches
            - If multiple tools were used, synthesize information from all sources
            - Keep it concise but informative
            - Be conversational and helpful
            """
            
            messages = [HumanMessage(content=format_prompt)]
            response = self.llm.invoke(messages)
            final_response = response.content
        
        logger.info(f"Final response formatted after {iteration_count} iterations: {len(final_response)} characters")
        
        return {
            "final_response": final_response,
            "messages": state["messages"] + [AIMessage(content=final_response)]
        }
    
    def _detect_operation_type(self, query: str) -> str:
        """Detect the type of operation from the user query"""
        
        query_lower = query.lower()
        
        # Future extensibility: detect different operation types
        if any(word in query_lower for word in ["add", "create", "save", "remember", "store"]):
            return "create"
        elif any(word in query_lower for word in ["update", "change", "modify", "edit"]):
            return "update"
        elif any(word in query_lower for word in ["delete", "remove", "forget"]):
            return "delete"
        elif any(word in query_lower for word in ["stats", "statistics", "count", "how many"]):
            return "statistics"
        else:
            return "search"  # Default to search operations
    
    @trace_agent_operation("process_query", {"component": "memory_agent", "step": "full_workflow"})
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query through the enhanced agent workflow
        
        Args:
            query: User's natural language query
            
        Returns:
            Dict with final response and workflow results
        """
        logger.info(f"Processing query: '{query}'")
        
        # Create LangSmith run context
        operation_type = self._detect_operation_type(query)
        run_context = create_run_context(query, operation_type)
        
        # Initialize state with tracing context
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "user_query": query,
            "operation_type": None,
            "iteration_count": 0,
            "max_iterations": self.max_iterations,
            "search_results": {},
            "final_response": None,
            "next_action": "continue"
        }
        
        try:
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            result = {
                "query": query,
                "operation_type": final_state.get("operation_type"),
                "iterations": final_state.get("iteration_count"),
                "search_results": final_state.get("search_results"),
                "final_response": final_state.get("final_response"),
                "success": True,
                "tracing_context": run_context if self.langsmith_enabled else None
            }
            
            logger.info(f"Query processing completed successfully in {result['iterations']} iterations")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}")
            return {
                "query": query,
                "operation_type": operation_type,
                "iterations": 0,
                "search_results": {},
                "final_response": f"I encountered an error processing your request: {str(e)}",
                "success": False,
                "error": str(e),
                "tracing_context": run_context if self.langsmith_enabled else None
            }


def create_memory_agent(model: str = "gpt-4o-mini", tools: List[BaseTool] = None, max_iterations: int = 5) -> MemoryAgent:
    """
    Factory function to create a Memory Agent
    
    Args:
        model: OpenAI model to use
        tools: Custom tools list (optional)
        max_iterations: Maximum ReAct iterations
        
    Returns:
        Configured MemoryAgent instance
    """
    return MemoryAgent(model=model, tools=tools, max_iterations=max_iterations)


def create_search_agent(model: str = "gpt-4o-mini", max_iterations: int = 3) -> MemoryAgent:
    """
    Create a focused search agent with only search tools and fewer iterations
    
    Args:
        model: OpenAI model to use
        max_iterations: Maximum iterations (lower for focused search)
        
    Returns:
        MemoryAgent configured for search operations only
    """
    search_tools = get_search_tools()
    return MemoryAgent(model=model, tools=search_tools, max_iterations=max_iterations)


# LangGraph Studio Entry Point
# This allows Studio to load the agent workflow directly from this file
if __name__ != "__main__":
    # Only create the app when imported by Studio, not when run directly
    try:
        _studio_agent = create_memory_agent(max_iterations=5)
        app = _studio_agent.workflow
        
        # Studio will use this compiled workflow
        logger.info("LangGraph Studio app compiled successfully")
        
    except Exception as e:
        logger.error(f"Failed to create Studio app: {e}")
        # Create a dummy app to prevent import errors
        from langgraph.graph import StateGraph, END, START
        dummy_workflow = StateGraph(dict)
        dummy_workflow.add_node("error", lambda x: {"error": f"Failed to initialize: {e}"})
        dummy_workflow.add_edge(START, "error")
        dummy_workflow.add_edge("error", END)
        app = dummy_workflow.compile()