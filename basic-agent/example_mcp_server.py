#!/usr/bin/env python3
"""
Example MCP Server for Agentic Agent

This is a simple MCP server implementation that the agentic agent can connect to
for testing and demonstration purposes.
"""

import asyncio
import json
import logging
from aiohttp import web
from typing import Dict, Any, List
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExampleMCPServer:
    """Example MCP server implementation"""
    
    def __init__(self, server_type: str = "filesystem"):
        self.server_type = server_type
        self.app = web.Application()
        self.setup_routes()
        
    def setup_routes(self):
        """Setup the web routes"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/call', self.handle_call)
        self.app.router.add_get('/methods', self.list_methods)
        
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "server_type": self.server_type,
            "timestamp": asyncio.get_event_loop().time()
        })
        
    async def list_methods(self, request):
        """List available methods"""
        methods = self.get_available_methods()
        return web.json_response({
            "methods": methods,
            "server_type": self.server_type
        })
        
    def get_available_methods(self) -> List[str]:
        """Get list of available methods based on server type"""
        if self.server_type == "filesystem":
            return ["list_files", "read_file", "write_file", "delete_file"]
        elif self.server_type == "git":
            return ["clone", "commit", "push", "status", "log"]
        elif self.server_type == "web_search":
            return ["search", "get_page_content", "extract_text"]
        else:
            return ["generic_method"]
            
    async def handle_call(self, request):
        """Handle method calls"""
        try:
            data = await request.json()
            method = data.get("method")
            params = data.get("params", {})
            
            logger.info(f"Received call to method: {method} with params: {params}")
            
            # Route to appropriate handler
            if self.server_type == "filesystem":
                result = await self.handle_filesystem_method(method, params)
            elif self.server_type == "git":
                result = await self.handle_git_method(method, params)
            elif self.server_type == "web_search":
                result = await self.handle_web_search_method(method, params)
            else:
                result = {"error": f"Unknown server type: {self.server_type}"}
                
            return web.json_response(result)
            
        except Exception as e:
            logger.error(f"Error handling call: {e}")
            return web.json_response({
                "error": str(e),
                "success": False
            }, status=500)
            
    async def handle_filesystem_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle filesystem-related methods"""
        if method == "list_files":
            path = params.get("path", ".")
            try:
                files = []
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    files.append({
                        "name": item,
                        "path": item_path,
                        "is_directory": os.path.isdir(item_path),
                        "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                    })
                return {"files": files, "success": True}
            except Exception as e:
                return {"error": str(e), "success": False}
                
        elif method == "read_file":
            path = params.get("path")
            if not path:
                return {"error": "Path parameter required", "success": False}
            try:
                with open(path, 'r') as f:
                    content = f.read()
                return {"content": content, "success": True}
            except Exception as e:
                return {"error": str(e), "success": False}
                
        elif method == "write_file":
            path = params.get("path")
            content = params.get("content")
            if not path or content is None:
                return {"error": "Path and content parameters required", "success": False}
            try:
                with open(path, 'w') as f:
                    f.write(content)
                return {"success": True}
            except Exception as e:
                return {"error": str(e), "success": False}
                
        elif method == "delete_file":
            path = params.get("path")
            if not path:
                return {"error": "Path parameter required", "success": False}
            try:
                os.remove(path)
                return {"success": True}
            except Exception as e:
                return {"error": str(e), "success": False}
                
        else:
            return {"error": f"Unknown method: {method}", "success": False}
            
    async def handle_git_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Git-related methods"""
        if method == "clone":
            repo_url = params.get("repo_url")
            local_path = params.get("local_path")
            return {
                "message": f"Git clone operation planned for {repo_url} to {local_path}",
                "success": True
            }
            
        elif method == "commit":
            message = params.get("message", "Auto-commit")
            files = params.get("files", [])
            return {
                "message": f"Git commit planned with message: {message}",
                "files": files,
                "success": True
            }
            
        elif method == "push":
            return {
                "message": "Git push operation planned",
                "success": True
            }
            
        elif method == "status":
            return {
                "status": "clean",
                "modified_files": [],
                "untracked_files": [],
                "success": True
            }
            
        elif method == "log":
            return {
                "commits": [
                    {
                        "hash": "abc123",
                        "author": "Agentic Agent",
                        "message": "Auto-commit",
                        "date": "2024-01-01T00:00:00Z"
                    }
                ],
                "success": True
            }
            
        else:
            return {"error": f"Unknown Git method: {method}", "success": False}
            
    async def handle_web_search_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web search-related methods"""
        if method == "search":
            query = params.get("query", "")
            max_results = params.get("max_results", 5)
            
            # Simulate search results
            results = []
            for i in range(min(max_results, 5)):
                results.append({
                    "title": f"Search result {i+1} for '{query}'",
                    "url": f"https://example.com/result{i+1}",
                    "snippet": f"This is a simulated search result for the query '{query}'",
                    "rank": i+1
                })
                
            return {
                "results": results,
                "query": query,
                "total_results": len(results),
                "success": True
            }
            
        elif method == "get_page_content":
            url = params.get("url")
            if not url:
                return {"error": "URL parameter required", "success": False}
                
            # Simulate page content
            content = f"<html><body><h1>Page Content</h1><p>This is simulated content for {url}</p></body></html>"
            return {
                "content": content,
                "url": url,
                "success": True
            }
            
        elif method == "extract_text":
            content = params.get("content", "")
            # Simulate text extraction
            extracted_text = content.replace("<html>", "").replace("</html>", "").replace("<body>", "").replace("</body>", "")
            return {
                "extracted_text": extracted_text,
                "success": True
            }
            
        else:
            return {"error": f"Unknown web search method: {method}", "success": False}
            
    async def start(self, host: str = "localhost", port: int = 8001):
        """Start the MCP server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"Example MCP Server ({self.server_type}) started at http://{host}:{port}")
        logger.info(f"Health check: http://{host}:{port}/health")
        logger.info(f"Available methods: http://{host}:{port}/methods")
        
        return runner


async def main():
    """Main function to run the example MCP server"""
    import sys
    
    # Parse command line arguments
    server_type = "filesystem"
    port = 8001
    
    if len(sys.argv) > 1:
        server_type = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
        
    # Create and start server
    server = ExampleMCPServer(server_type)
    runner = await server.start(port=port)
    
    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down MCP server...")
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 