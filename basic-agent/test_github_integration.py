#!/usr/bin/env python3
"""
Test GitHub MCP Integration

This script tests the integration between the agentic agent and the GitHub MCP server.
"""

import asyncio
import json
import logging
from agentic_agent import AgenticAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_github_integration():
    """Test the GitHub MCP integration"""
    print("🧪 Testing GitHub MCP Integration...")
    
    # Create agent instance
    agent = AgenticAgent()
    
    try:
        # Initialize the agent
        await agent.initialize()
        print("✅ Agent initialized successfully")
        
        # Check if GitHub MCP client is connected
        if "github" in agent.mcp_clients:
            print("✅ GitHub MCP client connected")
            
            # Test GitHub operations
            test_tasks = [
                "find trending Python repositories",
                "search for machine learning code on GitHub",
                "analyze Python async programming patterns",
                "get popular JavaScript frameworks"
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
            print("❌ GitHub MCP client not connected")
            
        # Get agent status
        status = await agent.get_status()
        print(f"\n📈 Agent Status: {json.dumps(status, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error testing GitHub integration: {e}")
        print(f"❌ Error: {e}")
        
    finally:
        await agent.shutdown()
        print("🔚 Agent shutdown complete")


async def test_github_client_directly():
    """Test the GitHub MCP client directly"""
    print("\n🔧 Testing GitHub MCP Client Directly...")
    
    try:
        from github_mcp_client import GitHubMCPClient
        
        client = GitHubMCPClient()
        await client.connect()
        
        # Test basic operations
        print("📋 Testing available methods...")
        methods = await client.get_available_methods()
        print(f"Available methods: {methods}")
        
        print("\n🔥 Testing trending repositories...")
        trending = await client.get_trending_repositories(language="python")
        print(f"Trending Python repos: {json.dumps(trending, indent=2)}")
        
        await client.disconnect()
        print("✅ Direct GitHub client test completed")
        
    except Exception as e:
        print(f"❌ Direct GitHub client test failed: {e}")


async def main():
    """Main test function"""
    print("🚀 Starting GitHub MCP Integration Tests\n")
    
    # Test direct client first
    await test_github_client_directly()
    
    # Test full agent integration
    await test_github_integration()
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main()) 