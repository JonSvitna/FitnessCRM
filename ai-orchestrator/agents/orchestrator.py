"""
Agent Orchestrator using LangGraph
Manages coordination between multiple AI agents
"""
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from utils.logger import logger
from models import db
from models.agent import Agent


class AgentState(TypedDict):
    """State passed between agents in the graph"""
    input: Dict[str, Any]
    messages: Annotated[List[str], operator.add]
    results: Dict[str, Any]
    current_agent: Optional[str]
    completed_agents: Annotated[List[str], operator.add]
    error: Optional[str]


class AgentOrchestrator:
    """Orchestrates multiple AI agents using LangGraph"""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4-turbo-preview"):
        """
        Initialize orchestrator
        
        Args:
            openai_api_key: OpenAI API key
            model: OpenAI model to use
        """
        self.logger = logger
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model,
            temperature=0.7
        )
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent type
        workflow.add_node("router", self._router_node)
        workflow.add_node("workout_optimizer", self._workout_optimizer_node)
        workflow.add_node("progress_monitor", self._progress_monitor_node)
        workflow.add_node("scheduler", self._scheduler_node)
        workflow.add_node("health_checker", self._health_checker_node)
        workflow.add_node("code_analyzer", self._code_analyzer_node)
        workflow.add_node("finalizer", self._finalizer_node)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Add conditional edges from router
        workflow.add_conditional_edges(
            "router",
            self._route_to_agent,
            {
                "workout_optimizer": "workout_optimizer",
                "progress_monitor": "progress_monitor",
                "scheduler": "scheduler",
                "health_checker": "health_checker",
                "code_analyzer": "code_analyzer",
                "end": END
            }
        )
        
        # Add edges from agents to finalizer
        for agent in ["workout_optimizer", "progress_monitor", "scheduler", "health_checker", "code_analyzer"]:
            workflow.add_edge(agent, "finalizer")
        
        # Finalizer either routes to next agent or ends
        workflow.add_conditional_edges(
            "finalizer",
            self._check_if_done,
            {
                "continue": "router",
                "end": END
            }
        )
        
        self.graph = workflow.compile()
    
    def _router_node(self, state: AgentState) -> AgentState:
        """Route to appropriate agent based on input"""
        input_data = state.get("input", {})
        task_type = input_data.get("task_type", "unknown")
        
        self.logger.info(f"Router processing task: {task_type}")
        
        state["messages"].append(f"Routing to agent for task: {task_type}")
        state["current_agent"] = self._map_task_to_agent(task_type)
        
        return state
    
    def _map_task_to_agent(self, task_type: str) -> str:
        """Map task type to agent name"""
        task_map = {
            "workout_optimization": "workout_optimizer",
            "progress_monitoring": "progress_monitor",
            "scheduling": "scheduler",
            "health_check": "health_checker",
            "code_analysis": "code_analyzer"
        }
        return task_map.get(task_type, "end")
    
    def _route_to_agent(self, state: AgentState) -> str:
        """Conditional edge function for routing"""
        return state.get("current_agent", "end")
    
    def _workout_optimizer_node(self, state: AgentState) -> AgentState:
        """Workout optimization agent node"""
        self.logger.info("Executing workout optimizer agent")
        
        input_data = state.get("input", {})
        task_type = input_data.get("task_type", "workout_optimization")
        
        # Use LLM to generate workout optimization
        messages = [
            SystemMessage(content="You are an expert fitness trainer AI that optimizes workout plans based on client data."),
            HumanMessage(content=f"Optimize workout for client: {input_data}")
        ]
        
        response = self.llm.invoke(messages)
        
        # Use task_type as key for consistency
        state["results"][task_type] = response.content
        state["completed_agents"].append("workout_optimizer")
        state["messages"].append(f"Workout optimization completed")
        
        return state
    
    def _progress_monitor_node(self, state: AgentState) -> AgentState:
        """Progress monitoring agent node"""
        self.logger.info("Executing progress monitor agent")
        
        input_data = state.get("input", {})
        task_type = input_data.get("task_type", "progress_monitoring")
        
        messages = [
            SystemMessage(content="You are an AI that monitors and analyzes client fitness progress."),
            HumanMessage(content=f"Analyze progress for: {input_data}")
        ]
        
        response = self.llm.invoke(messages)
        
        # Use task_type as key for consistency
        state["results"][task_type] = response.content
        state["completed_agents"].append("progress_monitor")
        state["messages"].append(f"Progress monitoring completed")
        
        return state
    
    def _scheduler_node(self, state: AgentState) -> AgentState:
        """Scheduling intelligence agent node"""
        self.logger.info("Executing scheduler agent")
        
        input_data = state.get("input", {})
        task_type = input_data.get("task_type", "scheduling")
        
        messages = [
            SystemMessage(content="You are an AI that optimizes trainer-client scheduling based on availability and preferences."),
            HumanMessage(content=f"Optimize schedule for: {input_data}")
        ]
        
        response = self.llm.invoke(messages)
        
        # Use task_type as key for consistency
        state["results"][task_type] = response.content
        state["completed_agents"].append("scheduler")
        state["messages"].append(f"Scheduling optimization completed")
        
        return state
    
    def _health_checker_node(self, state: AgentState) -> AgentState:
        """System health check agent node"""
        self.logger.info("Executing health checker agent")
        
        input_data = state.get("input", {})
        task_type = input_data.get("task_type", "health_check")
        
        messages = [
            SystemMessage(content="You are an AI that monitors system health and identifies potential issues."),
            HumanMessage(content=f"Check system health: {input_data}")
        ]
        
        response = self.llm.invoke(messages)
        
        # Use task_type as key for consistency
        state["results"][task_type] = response.content
        state["completed_agents"].append("health_checker")
        state["messages"].append(f"Health check completed")
        
        return state
    
    def _code_analyzer_node(self, state: AgentState) -> AgentState:
        """Code analysis and improvement agent node"""
        self.logger.info("Executing code analyzer agent")
        
        input_data = state.get("input", {})
        task_type = input_data.get("task_type", "code_analysis")
        
        messages = [
            SystemMessage(content="You are an expert code reviewer AI that identifies bugs, performance issues, and suggests improvements."),
            HumanMessage(content=f"Analyze code: {input_data}")
        ]
        
        response = self.llm.invoke(messages)
        
        # Use task_type as key for consistency
        state["results"][task_type] = response.content
        state["completed_agents"].append("code_analyzer")
        state["messages"].append(f"Code analysis completed")
        
        return state
    
    def _finalizer_node(self, state: AgentState) -> AgentState:
        """Finalize results and check if more work needed"""
        self.logger.info("Finalizing agent execution")
        
        state["messages"].append("Finalizing results")
        
        return state
    
    def _check_if_done(self, state: AgentState) -> str:
        """Check if workflow is complete"""
        # For now, always end after one agent execution
        # In future, could add logic to chain multiple agents
        return "end"
    
    async def execute(self, task_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute orchestrated agent workflow
        
        Args:
            task_type: Type of task to execute
            input_data: Input data for the task
        
        Returns:
            Results from agent execution
        """
        try:
            initial_state = AgentState(
                input={"task_type": task_type, **input_data},
                messages=[],
                results={},
                current_agent=None,
                completed_agents=[],
                error=None
            )
            
            # Execute graph
            final_state = self.graph.invoke(initial_state)
            
            return {
                'success': True,
                'results': final_state.get('results', {}),
                'completed_agents': final_state.get('completed_agents', []),
                'messages': final_state.get('messages', [])
            }
            
        except Exception as e:
            self.logger.error(f"Orchestrator execution failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_active_agents(self) -> List[Agent]:
        """Get list of active agents from database"""
        return Agent.query.filter_by(enabled=True, status='active').all()
