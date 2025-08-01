#!/usr/bin/env python3
"""
Agentic AI Agent with MCP Server Integration

A sophisticated agent that can autonomously perform tasks by connecting to various
MCP (Model Context Protocol) servers for enhanced capabilities.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import yaml
from pydantic import BaseModel, Field

# Import MCP clients
try:
    from github_mcp_client import GitHubMCPClient
except ImportError:
    GitHubMCPClient = None

try:
    from graph_mcp_client import GraphMCPClient
except ImportError:
    GraphMCPClient = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a task execution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Represents a task to be executed by the agent"""
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    subtasks: List['Task'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MCPClient:
    """Base class for MCP server clients"""
    
    def __init__(self, server_url: str, server_name: str):
        self.server_url = server_url
        self.server_name = server_name
        self.session = None
        self.connected = False
        
    async def connect(self):
        """Connect to the MCP server"""
        try:
            self.session = aiohttp.ClientSession()
            # Test connection
            async with self.session.get(f"{self.server_url}/health") as response:
                if response.status == 200:
                    self.connected = True
                    logger.info(f"Connected to {self.server_name} MCP server")
                else:
                    logger.error(f"Failed to connect to {self.server_name} MCP server")
        except Exception as e:
            logger.error(f"Error connecting to {self.server_name} MCP server: {e}")
            
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.session:
            await self.session.close()
            self.connected = False
            
    async def call_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a method on the MCP server"""
        if not self.connected:
            raise ConnectionError(f"Not connected to {self.server_name} MCP server")
            
        try:
            async with self.session.post(
                f"{self.server_url}/call",
                json={"method": method, "params": params}
            ) as response:
                return await response.json()
        except Exception as e:
            logger.error(f"Error calling {method} on {self.server_name}: {e}")
            raise


class FileSystemMCPClient(MCPClient):
    """MCP client for file system operations"""
    
    async def list_files(self, path: str) -> List[Dict[str, Any]]:
        """List files in a directory"""
        return await self.call_method("list_files", {"path": path})
        
    async def read_file(self, path: str) -> str:
        """Read a file"""
        result = await self.call_method("read_file", {"path": path})
        return result.get("content", "")
        
    async def write_file(self, path: str, content: str) -> bool:
        """Write content to a file"""
        result = await self.call_method("write_file", {"path": path, "content": content})
        return result.get("success", False)
        
    async def delete_file(self, path: str) -> bool:
        """Delete a file"""
        result = await self.call_method("delete_file", {"path": path})
        return result.get("success", False)


class GitMCPClient(MCPClient):
    """MCP client for Git operations"""
    
    async def clone_repository(self, repo_url: str, local_path: str) -> bool:
        """Clone a repository"""
        result = await self.call_method("clone", {"repo_url": repo_url, "local_path": local_path})
        return result.get("success", False)
        
    async def commit_changes(self, message: str, files: List[str] = None) -> bool:
        """Commit changes to Git"""
        result = await self.call_method("commit", {"message": message, "files": files or []})
        return result.get("success", False)
        
    async def push_changes(self) -> bool:
        """Push changes to remote repository"""
        result = await self.call_method("push", {})
        return result.get("success", False)


class WebSearchMCPClient(MCPClient):
    """MCP client for web search operations"""
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Perform a web search"""
        result = await self.call_method("search", {"query": query, "max_results": max_results})
        return result.get("results", [])
        
    async def get_page_content(self, url: str) -> str:
        """Get content from a web page"""
        result = await self.call_method("get_page_content", {"url": url})
        return result.get("content", "")


class AgenticAgent:
    """Main agentic AI agent class"""
    
    def __init__(self, config_path: str = "agent_config.yaml"):
        self.config = self._load_config(config_path)
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.memory: Dict[str, Any] = {}
        self.goals: List[str] = []
        self.context: Dict[str, Any] = {}
        self.task_queue: List[Task] = []
        self.running = False
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "mcp_servers": {
                "filesystem": {
                    "url": "http://localhost:8001",
                    "enabled": True
                },
                "git": {
                    "url": "http://localhost:8002",
                    "enabled": True
                },
                "web_search": {
                    "url": "http://localhost:8003",
                    "enabled": True
                },
                "github": {
                    "url": "https://api.githubcopilot.com/mcp/",
                    "enabled": True
                },
                "graph": {
                    "url": "http://localhost:8004",
                    "enabled": True
                }
            },
            "agent": {
                "max_concurrent_tasks": 5,
                "task_timeout": 300,
                "memory_size": 1000
            }
        }
        
    async def initialize(self):
        """Initialize the agent and connect to MCP servers"""
        logger.info("Initializing Agentic Agent...")
        
        # Connect to MCP servers
        await self._connect_mcp_servers()
        
        # Initialize memory
        self._initialize_memory()
        
        logger.info("Agentic Agent initialized successfully")
        
    async def _connect_mcp_servers(self):
        """Connect to configured MCP servers"""
        for server_name, server_config in self.config["mcp_servers"].items():
            if server_config.get("enabled", False):
                client = self._create_mcp_client(server_name, server_config["url"])
                await client.connect()
                self.mcp_clients[server_name] = client
                
    def _create_mcp_client(self, server_name: str, server_url: str) -> MCPClient:
        """Create appropriate MCP client based on server type"""
        if server_name == "filesystem":
            return FileSystemMCPClient(server_url, server_name)
        elif server_name == "git":
            return GitMCPClient(server_url, server_name)
        elif server_name == "web_search":
            return WebSearchMCPClient(server_url, server_name)
        elif server_name == "github" and GitHubMCPClient:
            # Extract API key from URL if provided
            api_key = None
            if "api_key=" in server_url:
                base_url, api_key = server_url.split("api_key=", 1)
                server_url = base_url.rstrip("?&")
            return GitHubMCPClient(server_url, api_key)
        elif server_name == "graph" and GraphMCPClient:
            # Extract API key from URL if provided
            api_key = None
            if "api_key=" in server_url:
                base_url, api_key = server_url.split("api_key=", 1)
                server_url = base_url.rstrip("?&")
            return GraphMCPClient(server_url, server_name, api_key)
        else:
            return MCPClient(server_url, server_name)
            
    def _initialize_memory(self):
        """Initialize agent memory"""
        self.memory = {
            "conversation_history": [],
            "task_history": [],
            "learned_patterns": {},
            "preferences": {}
        }
        
    async def add_goal(self, goal: str):
        """Add a new goal for the agent to work towards"""
        self.goals.append(goal)
        logger.info(f"Added goal: {goal}")
        
    async def add_task(self, description: str, priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """Add a new task to the queue"""
        task_id = f"task_{len(self.task_queue) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task = Task(
            id=task_id,
            description=description,
            priority=priority
        )
        self.task_queue.append(task)
        logger.info(f"Added task: {task_id} - {description}")
        return task_id
        
    async def plan_and_execute(self, task_description: str) -> Dict[str, Any]:
        """Plan and execute a task"""
        task_id = await self.add_task(task_description)
        task = next(t for t in self.task_queue if t.id == task_id)
        
        try:
            # Plan the task
            plan = await self._plan_task(task)
            task.metadata["plan"] = plan
            
            # Execute the plan
            result = await self._execute_plan(task, plan)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            
            # Learn from the execution
            await self._learn_from_execution(task, result)
            
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "execution_time": (task.completed_at - task.created_at).total_seconds()
            }
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logger.error(f"Task {task_id} failed: {e}")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            }
            
    async def _plan_task(self, task: Task) -> List[Dict[str, Any]]:
        """Create a plan for executing a task"""
        # Simple planning logic - can be enhanced with more sophisticated planning
        plan = []
        
        # Analyze task description and break it down
        description_lower = task.description.lower()
        
        if "file" in description_lower or "read" in description_lower or "write" in description_lower:
            plan.append({
                "action": "filesystem_operation",
                "description": "Perform file system operation",
                "priority": 1
            })
            
        if "git" in description_lower or "commit" in description_lower or "push" in description_lower:
            plan.append({
                "action": "git_operation",
                "description": "Perform Git operation",
                "priority": 2
            })
            
        if "search" in description_lower or "find" in description_lower or "research" in description_lower:
            plan.append({
                "action": "web_search",
                "description": "Perform web search",
                "priority": 1
            })
            
        if "github" in description_lower or "repository" in description_lower or "code" in description_lower:
            plan.append({
                "action": "github_operation",
                "description": "Perform GitHub operation",
                "priority": 1
            })
            
        if "graph" in description_lower or "node" in description_lower or "relationship" in description_lower or "traverse" in description_lower:
            plan.append({
                "action": "graph_operation",
                "description": "Perform Graph database operation",
                "priority": 1
            })
            
        # Add general processing step
        plan.append({
            "action": "process_results",
            "description": "Process and synthesize results",
            "priority": 3
        })
        
        return sorted(plan, key=lambda x: x["priority"])
        
    async def _execute_plan(self, task: Task, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a planned task"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        results = {}
        
        for step in plan:
            try:
                if step["action"] == "filesystem_operation":
                    results["filesystem"] = await self._execute_filesystem_operation(task)
                elif step["action"] == "git_operation":
                    results["git"] = await self._execute_git_operation(task)
                elif step["action"] == "web_search":
                    results["web_search"] = await self._execute_web_search(task)
                elif step["action"] == "github_operation":
                    results["github"] = await self._execute_github_operation(task)
                elif step["action"] == "graph_operation":
                    results["graph"] = await self._execute_graph_operation(task)
                elif step["action"] == "process_results":
                    results["processed"] = await self._process_results(task, results)
                    
            except Exception as e:
                logger.error(f"Error executing step {step['action']}: {e}")
                results[f"{step['action']}_error"] = str(e)
                
        return results
        
    async def _execute_filesystem_operation(self, task: Task) -> Dict[str, Any]:
        """Execute file system operations"""
        if "filesystem" not in self.mcp_clients:
            return {"error": "Filesystem MCP client not available"}
            
        client = self.mcp_clients["filesystem"]
        description_lower = task.description.lower()
        
        if "list" in description_lower or "directory" in description_lower:
            # Extract path from description or use current directory
            path = "."  # Default to current directory
            return await client.list_files(path)
        elif "read" in description_lower:
            # Extract file path from description
            # This is a simplified version - in practice, you'd use NLP to extract the path
            return {"message": "File read operation planned"}
        elif "write" in description_lower:
            return {"message": "File write operation planned"}
        else:
            return {"message": "Filesystem operation planned"}
            
    async def _execute_git_operation(self, task: Task) -> Dict[str, Any]:
        """Execute Git operations"""
        if "git" not in self.mcp_clients:
            return {"error": "Git MCP client not available"}
            
        client = self.mcp_clients["git"]
        description_lower = task.description.lower()
        
        if "commit" in description_lower:
            message = "Auto-commit by Agentic Agent"
            return {"message": f"Git commit planned with message: {message}"}
        elif "push" in description_lower:
            return {"message": "Git push operation planned"}
        elif "clone" in description_lower:
            return {"message": "Git clone operation planned"}
        else:
            return {"message": "Git operation planned"}
            
    async def _execute_web_search(self, task: Task) -> Dict[str, Any]:
        """Execute web search operations"""
        if "web_search" not in self.mcp_clients:
            return {"error": "Web search MCP client not available"}
            
        client = self.mcp_clients["web_search"]
        
        # Extract search query from task description
        # This is a simplified version - in practice, you'd use NLP to extract the query
        query = task.description.replace("search for", "").replace("find", "").strip()
        return await client.search(query, max_results=5)
        
    async def _execute_github_operation(self, task: Task) -> Dict[str, Any]:
        """Execute GitHub operations"""
        if "github" not in self.mcp_clients:
            return {"error": "GitHub MCP client not available"}
            
        client = self.mcp_clients["github"]
        description_lower = task.description.lower()
        
        try:
            if "trending" in description_lower or "popular" in description_lower:
                language = None
                if "python" in description_lower:
                    language = "python"
                elif "javascript" in description_lower:
                    language = "javascript"
                elif "java" in description_lower:
                    language = "java"
                    
                return await client.get_trending_repositories(language=language)
                
            elif "repository" in description_lower or "repo" in description_lower:
                # Extract repository info from description
                # This is a simplified version - in practice, you'd use NLP to extract owner/repo
                return {"message": "GitHub repository operation planned"}
                
            elif "search" in description_lower and "code" in description_lower:
                # Extract search query from description
                query = task.description.replace("search", "").replace("code", "").replace("for", "").strip()
                return await client.search_code(query)
                
            elif "analyze" in description_lower or "improve" in description_lower:
                return {"message": "GitHub code analysis operation planned"}
                
            else:
                # Default GitHub operation
                return await client.get_trending_repositories()
                
        except Exception as e:
            logger.error(f"Error executing GitHub operation: {e}")
            return {"error": str(e), "message": "GitHub operation failed"}
        
    async def _execute_graph_operation(self, task: Task) -> Dict[str, Any]:
        """Execute Graph database operations"""
        if "graph" not in self.mcp_clients:
            return {"error": "Graph database MCP client not available"}
            
        client = self.mcp_clients["graph"]
        description_lower = task.description.lower()
        
        try:
            if "statistics" in description_lower or "stats" in description_lower:
                return await client.get_graph_statistics()
                
            elif "create" in description_lower and "node" in description_lower:
                # Extract node properties from description
                # This is a simplified version - in practice, you'd use NLP to extract properties
                return {"message": "Graph node creation operation planned"}
                
            elif "create" in description_lower and "relationship" in description_lower:
                return {"message": "Graph relationship creation operation planned"}
                
            elif "find" in description_lower and "node" in description_lower:
                return {"message": "Graph node search operation planned"}
                
            elif "traverse" in description_lower or "path" in description_lower:
                return {"message": "Graph traversal operation planned"}
                
            elif "algorithm" in description_lower or "pagerank" in description_lower:
                return {"message": "Graph algorithm operation planned"}
                
            elif "recommendation" in description_lower:
                return {"message": "Graph recommendation operation planned"}
                
            else:
                # Default graph operation - get statistics
                return await client.get_graph_statistics()
                
        except Exception as e:
            logger.error(f"Error executing Graph database operation: {e}")
            return {"error": str(e), "message": "Graph database operation failed"}
        
    async def _process_results(self, task: Task, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and synthesize results from various operations"""
        processed = {
            "summary": f"Processed task: {task.description}",
            "operations_performed": list(results.keys()),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add specific processing based on results
        if "web_search" in results:
            processed["search_results_count"] = len(results["web_search"])
            
        if "filesystem" in results:
            processed["filesystem_operations"] = "completed"
            
        return processed
        
    async def _learn_from_execution(self, task: Task, result: Dict[str, Any]):
        """Learn from task execution to improve future performance"""
        # Store successful patterns
        if task.status == TaskStatus.COMPLETED:
            pattern = {
                "description_keywords": task.description.lower().split(),
                "successful_plan": task.metadata.get("plan", []),
                "execution_time": (task.completed_at - task.started_at).total_seconds()
            }
            
            if "learned_patterns" not in self.memory:
                self.memory["learned_patterns"] = {}
                
            self.memory["learned_patterns"][task.id] = pattern
            
        # Store in task history
        self.memory["task_history"].append({
            "id": task.id,
            "description": task.description,
            "status": task.status.value,
            "result": result,
            "timestamp": task.completed_at.isoformat() if task.completed_at else None
        })
        
        # Keep memory size manageable
        if len(self.memory["task_history"]) > self.config["agent"]["memory_size"]:
            self.memory["task_history"] = self.memory["task_history"][-self.config["agent"]["memory_size"]:]
            
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "running": self.running,
            "goals": self.goals,
            "task_queue_length": len(self.task_queue),
            "connected_mcp_servers": list(self.mcp_clients.keys()),
            "memory_size": len(self.memory.get("task_history", [])),
            "learned_patterns": len(self.memory.get("learned_patterns", {}))
        }
        
    async def shutdown(self):
        """Shutdown the agent and disconnect from MCP servers"""
        logger.info("Shutting down Agentic Agent...")
        
        # Disconnect from MCP servers
        for client in self.mcp_clients.values():
            await client.disconnect()
            
        self.running = False
        logger.info("Agentic Agent shutdown complete")


async def main():
    """Main function to run the agentic agent"""
    agent = AgenticAgent()
    
    try:
        await agent.initialize()
        
        # Example usage
        print("🤖 Agentic Agent initialized!")
        print("Available commands:")
        print("1. add_goal <goal>")
        print("2. execute <task_description>")
        print("3. status")
        print("4. quit")
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command.startswith("add_goal "):
                    goal = command[9:]
                    await agent.add_goal(goal)
                    print(f"✅ Goal added: {goal}")
                    
                elif command.startswith("execute "):
                    task_description = command[8:]
                    print(f"🔄 Executing: {task_description}")
                    result = await agent.plan_and_execute(task_description)
                    print(f"📊 Result: {json.dumps(result, indent=2)}")
                    
                elif command == "status":
                    status = await agent.get_status()
                    print(f"📈 Status: {json.dumps(status, indent=2)}")
                    
                elif command == "quit":
                    break
                    
                else:
                    print("❓ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                break
                
    except Exception as e:
        logger.error(f"Error in main: {e}")
        
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main()) 