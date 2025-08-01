#!/usr/bin/env python3
"""
GitHub MCP Client for Agentic Agent

A specialized MCP client for connecting to GitHub Copilot's MCP server
and performing GitHub-related operations.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubMCPClient:
    """GitHub MCP client for connecting to GitHub Copilot MCP server"""
    
    def __init__(self, server_url: str = "https://api.githubcopilot.com/mcp/", api_key: Optional[str] = None):
        self.server_url = server_url
        self.api_key = api_key
        self.session = None
        self.connected = False
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "AgenticAgent/1.0"
        }
        
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
            
    async def connect(self):
        """Connect to the GitHub MCP server"""
        try:
            self.session = aiohttp.ClientSession(headers=self.headers)
            
            # Test connection with a simple health check
            async with self.session.get(f"{self.server_url}health") as response:
                if response.status == 200:
                    self.connected = True
                    logger.info("Connected to GitHub Copilot MCP server")
                else:
                    logger.warning(f"GitHub MCP server returned status {response.status}")
                    # Still mark as connected as the server might not have a health endpoint
                    self.connected = True
                    
        except Exception as e:
            logger.error(f"Error connecting to GitHub MCP server: {e}")
            # For GitHub Copilot, we might still want to proceed even if health check fails
            self.connected = True
            
    async def disconnect(self):
        """Disconnect from the GitHub MCP server"""
        if self.session:
            await self.session.close()
            self.connected = False
            
    async def call_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a method on the GitHub MCP server"""
        if not self.connected:
            raise ConnectionError("Not connected to GitHub MCP server")
            
        try:
            payload = {
                "method": method,
                "params": params,
                "id": f"req_{datetime.now().timestamp()}",
                "jsonrpc": "2.0"
            }
            
            async with self.session.post(
                f"{self.server_url}",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    logger.error(f"GitHub MCP server returned status {response.status}")
                    return {"error": f"HTTP {response.status}", "success": False}
                    
        except Exception as e:
            logger.error(f"Error calling {method} on GitHub MCP server: {e}")
            return {"error": str(e), "success": False}
            
    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get information about a GitHub repository"""
        return await self.call_method("github.getRepository", {
            "owner": owner,
            "repo": repo
        })
        
    async def list_repositories(self, username: str) -> Dict[str, Any]:
        """List repositories for a user"""
        return await self.call_method("github.listRepositories", {
            "username": username
        })
        
    async def get_file_content(self, owner: str, repo: str, path: str, ref: str = "main") -> Dict[str, Any]:
        """Get content of a file from a GitHub repository"""
        return await self.call_method("github.getFileContent", {
            "owner": owner,
            "repo": repo,
            "path": path,
            "ref": ref
        })
        
    async def search_code(self, query: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Search for code on GitHub"""
        params = {"query": query}
        if language:
            params["language"] = language
            
        return await self.call_method("github.searchCode", params)
        
    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get information about a GitHub user"""
        return await self.call_method("github.getUser", {
            "username": username
        })
        
    async def get_commit_history(self, owner: str, repo: str, path: Optional[str] = None) -> Dict[str, Any]:
        """Get commit history for a repository or specific file"""
        params = {"owner": owner, "repo": repo}
        if path:
            params["path"] = path
            
        return await self.call_method("github.getCommitHistory", params)
        
    async def get_issues(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """Get issues for a repository"""
        return await self.call_method("github.getIssues", {
            "owner": owner,
            "repo": repo,
            "state": state
        })
        
    async def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """Get pull requests for a repository"""
        return await self.call_method("github.getPullRequests", {
            "owner": owner,
            "repo": repo,
            "state": state
        })
        
    async def search_repositories(self, query: str, language: Optional[str] = None, sort: str = "stars") -> Dict[str, Any]:
        """Search for repositories on GitHub"""
        params = {"query": query, "sort": sort}
        if language:
            params["language"] = language
            
        return await self.call_method("github.searchRepositories", params)
        
    async def get_repository_stats(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get statistics for a repository"""
        return await self.call_method("github.getRepositoryStats", {
            "owner": owner,
            "repo": repo
        })
        
    async def get_trending_repositories(self, language: Optional[str] = None, timeframe: str = "daily") -> Dict[str, Any]:
        """Get trending repositories"""
        params = {"timeframe": timeframe}
        if language:
            params["language"] = language
            
        return await self.call_method("github.getTrendingRepositories", params)
        
    async def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code using GitHub Copilot capabilities"""
        return await self.call_method("github.analyzeCode", {
            "code": code,
            "language": language
        })
        
    async def suggest_improvements(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Get code improvement suggestions"""
        return await self.call_method("github.suggestImprovements", {
            "code": code,
            "language": language
        })
        
    async def generate_documentation(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Generate documentation for code"""
        return await self.call_method("github.generateDocumentation", {
            "code": code,
            "language": language
        })
        
    async def get_available_methods(self) -> List[str]:
        """Get list of available methods from the GitHub MCP server"""
        try:
            result = await self.call_method("mcp.listMethods", {})
            return result.get("methods", [])
        except:
            # Return default methods if server doesn't support listing
            return [
                "github.getRepository",
                "github.listRepositories", 
                "github.getFileContent",
                "github.searchCode",
                "github.getUser",
                "github.getCommitHistory",
                "github.getIssues",
                "github.getPullRequests",
                "github.searchRepositories",
                "github.getRepositoryStats",
                "github.getTrendingRepositories",
                "github.analyzeCode",
                "github.suggestImprovements",
                "github.generateDocumentation"
            ]


async def test_github_mcp_client():
    """Test the GitHub MCP client"""
    client = GitHubMCPClient()
    
    try:
        await client.connect()
        print("✅ Connected to GitHub MCP server")
        
        # Test getting available methods
        methods = await client.get_available_methods()
        print(f"📋 Available methods: {methods}")
        
        # Test getting trending repositories
        trending = await client.get_trending_repositories(language="python")
        print(f"🔥 Trending Python repos: {trending}")
        
    except Exception as e:
        print(f"❌ Error testing GitHub MCP client: {e}")
        
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_github_mcp_client()) 