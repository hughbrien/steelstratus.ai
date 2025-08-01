# Agentic AI Agent with MCP Integration

A sophisticated agentic AI agent that can autonomously perform tasks by connecting to various MCP (Model Context Protocol) servers for enhanced capabilities.


## 🚀 Features

### Core Capabilities
- **Autonomous Decision Making**: Makes decisions and takes actions without constant human intervention
- **Goal-Oriented Behavior**: Works towards specific objectives and breaks down complex tasks
- **Learning & Adaptation**: Improves performance over time based on feedback and experience
- **Multi-Modal Capabilities**: Can process text, images, and other data types
- **Context Awareness**: Maintains context across conversations and sessions

### MCP Server Integration
The agent connects to multiple MCP servers for enhanced capabilities:

- **File System Server**: Access and manipulate files
- **Git Server**: Version control operations
- **Web Search Server**: Real-time information retrieval
- **GitHub Copilot MCP Server**: GitHub repository operations, code analysis, and AI-powered suggestions
- **Graph Database MCP Server**: Graph operations, traversals, algorithms, and analytics
- **Database Server**: Data storage and retrieval
- **API Server**: External service integration
- **Code Execution Server**: Run and test code
- **Documentation Server**: Access technical documentation

## 📋 Requirements

- Python 3.8+
- aiohttp
- pyyaml
- pydantic

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd basic-agent
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure the agent**:
Edit `agent_config.yaml` to configure MCP server endpoints and agent settings.

## 🚀 Quick Start

### 1. Start Example MCP Servers (Optional)

For testing with local MCP servers:

```bash
# Start filesystem MCP server
python example_mcp_server.py filesystem 8001

# Start Git MCP server (in another terminal)
python example_mcp_server.py git 8002

# Start web search MCP server (in another terminal)
python example_mcp_server.py web_search 8003
```

### 2. Configure GitHub MCP (Optional)

If you have a GitHub API key, you can add it to `agent_config.yaml`:

```yaml
github:
  url: "https://api.githubcopilot.com/mcp/"
  enabled: true
  api_key: "your_github_api_key_here"
```

### 3. Run the Agentic Agent

```bash
python agentic_agent.py
```

### 4. Test MCP Integrations

```bash
# Test GitHub integration
python test_github_integration.py

# Test Graph database integration
python test_graph_integration.py
```

### 3. Interact with the Agent

Once the agent is running, you can interact with it using these commands:

```
> add_goal Improve code quality and maintainability
✅ Goal added: Improve code quality and maintainability

> execute search for Python async programming best practices
🔄 Executing: search for Python async programming best practices
📊 Result: {
  "task_id": "task_1_20240101_120000",
  "status": "completed",
  "result": {
    "web_search": [...],
    "github": {
      "results": [...],
      "query": "Python async programming",
      "total_results": 5
    },
    "processed": {
      "summary": "Processed task: search for Python async programming best practices",
      "operations_performed": ["web_search", "github", "processed"],
      "search_results_count": 5,
      "timestamp": "2024-01-01T12:00:00"
    }
  },
  "execution_time": 0.5
}

> execute find trending Python repositories
📊 Result: {
  "task_id": "task_2_20240101_120100",
  "status": "completed", 
  "result": {
    "github": {
      "repositories": [...],
      "language": "python",
      "timeframe": "daily"
    },
    "processed": {
      "summary": "Processed task: find trending Python repositories",
      "operations_performed": ["github", "processed"],
      "timestamp": "2024-01-01T12:01:00"
    }
  },
  "execution_time": 0.3
}

> execute get graph database statistics
📊 Result: {
  "task_id": "task_3_20240101_120200",
  "status": "completed",
  "result": {
    "graph": {
      "nodeCount": 1250,
      "relationshipCount": 3400,
      "databaseSize": "2.3GB"
    },
    "processed": {
      "summary": "Processed task: get graph database statistics",
      "operations_performed": ["graph", "processed"],
      "timestamp": "2024-01-01T12:02:00"
    }
  },
  "execution_time": 0.2
}

> status
📈 Status: {
  "running": true,
  "goals": ["Improve code quality and maintainability"],
  "task_queue_length": 1,
  "connected_mcp_servers": ["filesystem", "git", "web_search", "github", "graph"],
  "memory_size": 1,
  "learned_patterns": 1
}
```

## 📁 Project Structure

```
basic-agent/
├── agentic_agent.py          # Main agent implementation
├── github_mcp_client.py      # GitHub Copilot MCP client
├── graph_mcp_client.py       # Graph database MCP client
├── example_mcp_server.py     # Example MCP server for testing
├── test_github_integration.py # Test script for GitHub integration
├── test_graph_integration.py # Test script for Graph database integration
├── agent_config.yaml         # Configuration file
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── basic-agent.md           # Original specification
```

## ⚙️ Configuration

The agent is configured via `agent_config.yaml`:

```yaml
# MCP Server configurations
mcp_servers:
  filesystem:
    url: "http://localhost:8001"
    enabled: true
    timeout: 30
    retry_attempts: 3
    
  git:
    url: "http://localhost:8002"
    enabled: true
    timeout: 30
    retry_attempts: 3

# Agent configuration
agent:
  max_concurrent_tasks: 5
  task_timeout: 300
  memory_size: 1000
  learning_enabled: true
```

## 🔧 Advanced Usage

### Custom MCP Servers

You can create custom MCP servers by implementing the required endpoints:

- `GET /health` - Health check
- `POST /call` - Method calls with JSON payload
- `GET /methods` - List available methods

### Extending the Agent

The agent can be extended by:

1. **Adding new MCP clients** in `agentic_agent.py`
2. **Implementing new task types** in the planning logic
3. **Adding learning algorithms** for better pattern recognition
4. **Integrating with external APIs** for enhanced capabilities

### Example Custom MCP Client

```python
class CustomMCPClient(MCPClient):
    async def custom_method(self, param1: str, param2: int) -> Dict[str, Any]:
        """Custom method implementation"""
        result = await self.call_method("custom_method", {
            "param1": param1,
            "param2": param2
        })
        return result
```

## 🧪 Testing

Run the example MCP servers and test the agent:

```bash
# Terminal 1: Start filesystem server
python example_mcp_server.py filesystem 8001

# Terminal 2: Start Git server
python example_mcp_server.py git 8002

# Terminal 3: Start web search server
python example_mcp_server.py web_search 8003

# Terminal 4: Run the agent
python agentic_agent.py
```

## 📊 Monitoring

The agent provides status information including:

- Connected MCP servers
- Task queue length
- Memory usage
- Learned patterns count
- Execution statistics

## 🔒 Security Considerations

- Secure MCP server connections
- Input validation and sanitization
- Rate limiting and resource management
- Audit logging for all actions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

1. Check the documentation
2. Review the example implementations
3. Open an issue on GitHub
4. Contact the development team

## 🎯 Future Enhancements

- **Natural Language Processing**: Better task understanding
- **Machine Learning**: Pattern recognition and optimization
- **Multi-Agent Coordination**: Multiple agents working together
- **Advanced Planning**: Sophisticated task decomposition
- **Real-time Monitoring**: Live performance metrics
- **Plugin System**: Extensible architecture for custom capabilities

---

**Happy Agentic Programming! 🤖✨** 