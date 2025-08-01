#!/usr/bin/env python3
"""
Test Graph Database MCP Integration

This script tests the integration between the agentic agent and the Graph database MCP server.
"""

import asyncio
import json
import logging
from agentic_agent import AgenticAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_graph_integration():
    """Test the Graph database MCP integration"""
    print("🧪 Testing Graph Database MCP Integration...")
    
    # Create agent instance
    agent = AgenticAgent()
    
    try:
        # Initialize the agent
        await agent.initialize()
        print("✅ Agent initialized successfully")
        
        # Check if Graph database MCP client is connected
        if "graph" in agent.mcp_clients:
            print("✅ Graph database MCP client connected")
            
            # Test Graph database operations
            test_tasks = [
                "get graph database statistics",
                "create a new node in the graph",
                "find nodes with specific properties",
                "traverse the graph from a starting node",
                "run PageRank algorithm on the graph",
                "get recommendations for a user"
            ]
            
            for task_description in test_tasks:
                print(f"\n🔄 Testing: {task_description}")
                result = await agent.plan_and_execute(task_description)
                
                print(f"📊 Result: {json.dumps(result, indent=2)}")
                
                if result.get("status") == "completed":
                    print("✅ Task completed successfully")
                else:
                    print(f"❌ Task failed: {result.get('error', 'Unknown error')}")
                    
        else:
            print("❌ Graph database MCP client not connected")
            
        # Get agent status
        status = await agent.get_status()
        print(f"\n📈 Agent Status: {json.dumps(status, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error testing Graph database integration: {e}")
        print(f"❌ Error: {e}")
        
    finally:
        await agent.shutdown()
        print("🔚 Agent shutdown complete")


async def test_graph_client_directly():
    """Test the Graph database MCP client directly"""
    print("\n🔧 Testing Graph Database MCP Client Directly...")
    
    try:
        from graph_mcp_client import GraphMCPClient
        
        client = GraphMCPClient("http://localhost:8004", "neo4j")
        await client.connect()
        
        # Test basic operations
        print("📋 Testing available methods...")
        methods = await client.get_available_methods()
        print(f"Available methods: {methods}")
        
        print("\n📊 Testing graph statistics...")
        stats = await client.get_graph_statistics()
        print(f"Graph statistics: {json.dumps(stats, indent=2)}")
        
        print("\n👤 Testing node creation...")
        node_result = await client.create_node(
            labels=["Person"],
            properties={"name": "John Doe", "age": 30}
        )
        print(f"Created node: {json.dumps(node_result, indent=2)}")
        
        await client.disconnect()
        print("✅ Direct Graph database client test completed")
        
    except Exception as e:
        print(f"❌ Direct Graph database client test failed: {e}")


async def main():
    """Main test function"""
    print("🚀 Starting Graph Database MCP Integration Tests\n")
    
    # Test direct client first
    await test_graph_client_directly()
    
    # Test full agent integration
    await test_graph_integration()
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main()) 