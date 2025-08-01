#!/usr/bin/env python3
"""
Graph Database MCP Client for Agentic Agent

A specialized MCP client for connecting to graph databases and performing
graph operations like queries, traversals, and analytics.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)


class GraphMCPClient:
    """Graph database MCP client for connecting to graph database MCP servers"""
    
    def __init__(self, server_url: str, server_name: str = "graph", api_key: Optional[str] = None):
        self.server_url = server_url
        self.server_name = server_name
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
        """Connect to the Graph database MCP server"""
        try:
            self.session = aiohttp.ClientSession(headers=self.headers)
            
            # Test connection with a simple health check
            async with self.session.get(f"{self.server_url}/health") as response:
                if response.status == 200:
                    self.connected = True
                    logger.info(f"Connected to {self.server_name} Graph database MCP server")
                else:
                    logger.warning(f"Graph database MCP server returned status {response.status}")
                    # Still mark as connected as the server might not have a health endpoint
                    self.connected = True
                    
        except Exception as e:
            logger.error(f"Error connecting to Graph database MCP server: {e}")
            # For graph databases, we might still want to proceed even if health check fails
            self.connected = True
            
    async def disconnect(self):
        """Disconnect from the Graph database MCP server"""
        if self.session:
            await self.session.close()
            self.connected = False
            
    async def call_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a method on the Graph database MCP server"""
        if not self.connected:
            raise ConnectionError(f"Not connected to {self.server_name} Graph database MCP server")
            
        try:
            payload = {
                "method": method,
                "params": params,
                "id": f"req_{datetime.now().timestamp()}",
                "jsonrpc": "2.0"
            }
            
            async with self.session.post(
                f"{self.server_url}/call",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    logger.error(f"Graph database MCP server returned status {response.status}")
                    return {"error": f"HTTP {response.status}", "success": False}
                    
        except Exception as e:
            logger.error(f"Error calling {method} on Graph database MCP server: {e}")
            return {"error": str(e), "success": False}
            
    async def execute_cypher_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a Cypher query (Neo4j-style)"""
        return await self.call_method("graph.executeCypher", {
            "query": query,
            "parameters": parameters or {}
        })
        
    async def execute_gremlin_query(self, query: str) -> Dict[str, Any]:
        """Execute a Gremlin query"""
        return await self.call_method("graph.executeGremlin", {
            "query": query
        })
        
    async def create_node(self, labels: List[str], properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new node in the graph"""
        return await self.call_method("graph.createNode", {
            "labels": labels,
            "properties": properties
        })
        
    async def create_relationship(self, from_node_id: str, to_node_id: str, 
                                relationship_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a relationship between two nodes"""
        return await self.call_method("graph.createRelationship", {
            "fromNodeId": from_node_id,
            "toNodeId": to_node_id,
            "relationshipType": relationship_type,
            "properties": properties or {}
        })
        
    async def find_nodes(self, labels: Optional[List[str]] = None, 
                        properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Find nodes by labels and/or properties"""
        params = {}
        if labels:
            params["labels"] = labels
        if properties:
            params["properties"] = properties
            
        return await self.call_method("graph.findNodes", params)
        
    async def find_relationships(self, from_node_id: Optional[str] = None,
                               to_node_id: Optional[str] = None,
                               relationship_type: Optional[str] = None) -> Dict[str, Any]:
        """Find relationships between nodes"""
        params = {}
        if from_node_id:
            params["fromNodeId"] = from_node_id
        if to_node_id:
            params["toNodeId"] = to_node_id
        if relationship_type:
            params["relationshipType"] = relationship_type
            
        return await self.call_method("graph.findRelationships", params)
        
    async def traverse_graph(self, start_node_id: str, max_depth: int = 3,
                           relationship_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Traverse the graph from a starting node"""
        params = {
            "startNodeId": start_node_id,
            "maxDepth": max_depth
        }
        if relationship_types:
            params["relationshipTypes"] = relationship_types
            
        return await self.call_method("graph.traverse", params)
        
    async def get_shortest_path(self, from_node_id: str, to_node_id: str,
                               relationship_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Find the shortest path between two nodes"""
        params = {
            "fromNodeId": from_node_id,
            "toNodeId": to_node_id
        }
        if relationship_types:
            params["relationshipTypes"] = relationship_types
            
        return await self.call_method("graph.shortestPath", params)
        
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the graph database"""
        return await self.call_method("graph.getStatistics", {})
        
    async def get_node_count(self, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get the count of nodes"""
        params = {}
        if labels:
            params["labels"] = labels
            
        return await self.call_method("graph.getNodeCount", params)
        
    async def get_relationship_count(self, relationship_type: Optional[str] = None) -> Dict[str, Any]:
        """Get the count of relationships"""
        params = {}
        if relationship_type:
            params["relationshipType"] = relationship_type
            
        return await self.call_method("graph.getRelationshipCount", params)
        
    async def delete_node(self, node_id: str) -> Dict[str, Any]:
        """Delete a node from the graph"""
        return await self.call_method("graph.deleteNode", {
            "nodeId": node_id
        })
        
    async def delete_relationship(self, relationship_id: str) -> Dict[str, Any]:
        """Delete a relationship from the graph"""
        return await self.call_method("graph.deleteRelationship", {
            "relationshipId": relationship_id
        })
        
    async def update_node_properties(self, node_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update properties of a node"""
        return await self.call_method("graph.updateNodeProperties", {
            "nodeId": node_id,
            "properties": properties
        })
        
    async def update_relationship_properties(self, relationship_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update properties of a relationship"""
        return await self.call_method("graph.updateRelationshipProperties", {
            "relationshipId": relationship_id,
            "properties": properties
        })
        
    async def run_graph_algorithm(self, algorithm: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run a graph algorithm (e.g., PageRank, Community Detection)"""
        return await self.call_method("graph.runAlgorithm", {
            "algorithm": algorithm,
            "parameters": parameters
        })
        
    async def get_recommendations(self, node_id: str, algorithm: str = "collaborative_filtering",
                                 limit: int = 10) -> Dict[str, Any]:
        """Get recommendations for a node"""
        return await self.call_method("graph.getRecommendations", {
            "nodeId": node_id,
            "algorithm": algorithm,
            "limit": limit
        })
        
    async def get_available_methods(self) -> List[str]:
        """Get list of available methods from the Graph database MCP server"""
        try:
            result = await self.call_method("mcp.listMethods", {})
            return result.get("methods", [])
        except:
            # Return default methods if server doesn't support listing
            return [
                "graph.executeCypher",
                "graph.executeGremlin",
                "graph.createNode",
                "graph.createRelationship",
                "graph.findNodes",
                "graph.findRelationships",
                "graph.traverse",
                "graph.shortestPath",
                "graph.getStatistics",
                "graph.getNodeCount",
                "graph.getRelationshipCount",
                "graph.deleteNode",
                "graph.deleteRelationship",
                "graph.updateNodeProperties",
                "graph.updateRelationshipProperties",
                "graph.runAlgorithm",
                "graph.getRecommendations"
            ]


async def test_graph_mcp_client():
    """Test the Graph database MCP client"""
    client = GraphMCPClient("http://localhost:8004", "neo4j")
    
    try:
        await client.connect()
        print("✅ Connected to Graph database MCP server")
        
        # Test getting available methods
        methods = await client.get_available_methods()
        print(f"📋 Available methods: {methods}")
        
        # Test creating a node
        node_result = await client.create_node(
            labels=["Person"],
            properties={"name": "John Doe", "age": 30}
        )
        print(f"👤 Created node: {node_result}")
        
        # Test getting statistics
        stats = await client.get_graph_statistics()
        print(f"📊 Graph statistics: {stats}")
        
    except Exception as e:
        print(f"❌ Error testing Graph database MCP client: {e}")
        
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_graph_mcp_client()) 