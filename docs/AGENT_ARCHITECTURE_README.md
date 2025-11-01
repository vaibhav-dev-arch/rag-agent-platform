# 🤖 LlamaIndex Agent Architecture Integration

This document explains how to integrate agent architecture with your existing LlamaIndex RAG project.

## 🎯 What is Agent Architecture?

Agent architecture adds **reasoning, planning, and tool usage** capabilities to your RAG system:

### **Traditional RAG:**
```
User Query → Vector Search → Retrieve Docs → Generate Response
```

### **Agent Architecture:**
```
User Query → Agent Reasoning → Tool Selection → Multiple Actions → Response Generation
```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Architecture                      │
├─────────────────────────────────────────────────────────────┤
│  User Interface (Chat/API)                                 │
├─────────────────────────────────────────────────────────────┤
│  Agent Core (ReActAgent)                                   │
│  ├── Reasoning Engine                                      │
│  ├── Tool Selection                                        │
│  ├── Memory Management                                      │
│  └── Response Generation                                    │
├─────────────────────────────────────────────────────────────┤
│  Tool Layer                                                │
│  ├── Document Search Tool                                  │
│  ├── Web Search Tool                                       │
│  ├── Web Scraping Tool                                     │
│  ├── Calculation Tool                                       │
│  ├── Time/Date Tool                                        │
│  ├── Sentiment Analysis Tool                               │
│  ├── Summarization Tool                                     │
│  └── Custom Tools (Legal, Healthcare, etc.)               │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                │
│  ├── Vector Index (LlamaIndex)                             │
│  ├── Document Storage                                      │
│  ├── Memory Storage                                        │
│  └── External APIs                                         │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Files Overview

### **Core Agent Files:**
- `agent_example.py` - Basic agent with 5 tools
- `advanced_agent.py` - Advanced agent with 10 tools and memory
- `specialized_agents.py` - Industry-specific agents (Legal, Healthcare)

### **API Integration:**
- `api_server_with_agent.py` - Enhanced API server with agent endpoints
- `api_client_with_agent.py` - Client for testing both RAG and agent capabilities

### **Requirements:**
- `agent_requirements.txt` - Additional dependencies for agent functionality

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
pip install -r agent_requirements.txt
```

### **2. Set Environment Variables**
```bash
cp env_example.txt .env
# Add your OpenAI API key to .env
```

### **3. Run Basic Agent**
```bash
python agent_example.py
```

### **4. Run Advanced Agent**
```bash
python advanced_agent.py
```

### **5. Run API Server with Agent**
```bash
python api_server_with_agent.py
```

### **6. Test with Client**
```bash
python api_client_with_agent.py
```

## 🛠️ Available Tools

### **Basic Tools:**
1. **Document Search** - Search through indexed documents
2. **Web Search** - Search the web for current information
3. **Web Scraping** - Extract content from web pages
4. **Calculations** - Perform mathematical operations
5. **Time/Date** - Get current time information

### **Advanced Tools:**
6. **Sentiment Analysis** - Analyze text sentiment
7. **Text Summarization** - Summarize long text
8. **Translation** - Translate text between languages
9. **Weather** - Get weather information
10. **Todo Management** - Create and manage tasks

### **Specialized Tools:**
- **Legal Tools**: Case law search, contract analysis, compliance checking
- **Healthcare Tools**: Medical literature search, drug interactions, symptom analysis

## 🔧 API Endpoints

### **Traditional RAG Endpoints:**
- `POST /query` - Traditional RAG query
- `POST /documents` - Add documents
- `POST /scrape` - Scrape web pages
- `GET /documents` - List documents
- `DELETE /documents` - Clear documents

### **Agent Endpoints:**
- `POST /agent/query` - Agent query with reasoning
- `GET /agent/tools` - List available tools
- `POST /agent/clear-memory` - Clear conversation memory

### **System Endpoints:**
- `GET /health` - System health check
- `GET /status` - Index and system status

## 💡 Usage Examples

### **Traditional RAG Query:**
```python
# Simple document search
response = client.query_traditional_rag("What is artificial intelligence?")
print(response['answer'])
```

### **Agent Query:**
```python
# Complex reasoning with multiple tools
response = client.query_agent(
    "Search our documents about AI, then search the web for latest AI news, and summarize the key differences"
)
print(response['answer'])
print(f"Tools used: {response['tools_used']}")
```

### **Specialized Agent:**
```python
# Legal agent
legal_agent = LegalAgent()
response = legal_agent.chat("Search for case law on contract breach")
print(response)
```

## 🎯 Use Cases

### **1. Customer Support**
- Multi-step problem resolution
- Document search + web search + calculation
- Context-aware responses

### **2. Research Assistant**
- Literature review + web research + summarization
- Citation generation + fact-checking
- Data analysis + reporting

### **3. Legal Research**
- Case law search + precedent analysis
- Contract review + compliance checking
- Brief generation + damage calculation

### **4. Healthcare Support**
- Medical literature search + drug interaction checking
- Symptom analysis + treatment guidelines
- Patient summary generation + HIPAA compliance

## 🔄 Integration with Existing Project

The agent architecture **extends** your existing project:

### **Backward Compatibility:**
- All existing endpoints work unchanged
- Traditional RAG functionality preserved
- Same document indexing process

### **New Capabilities:**
- Agent reasoning and tool selection
- Multi-step problem solving
- Conversation memory
- Specialized domain tools

### **API Structure:**
```
/api/v1/
├── /query          # Traditional RAG
├── /documents      # Document management
├── /scrape         # Web scraping
├── /agent/         # Agent endpoints
│   ├── /query      # Agent reasoning
│   ├── /tools      # Available tools
│   └── /clear-memory # Memory management
├── /health         # System health
└── /status         # System status
```

## 🚀 Deployment Options

### **1. Local Development**
```bash
python api_server_with_agent.py
# Access at http://localhost:8000
```

### **2. Docker Deployment**
```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt -r agent_requirements.txt
CMD ["python", "api_server_with_agent.py"]
```

### **3. Cloud Deployment**
- **AWS**: ECS, Lambda, EC2
- **Google Cloud**: Cloud Run, App Engine
- **Azure**: Container Instances, App Service

## 📊 Performance Considerations

### **Memory Usage:**
- Agent memory: ~2KB per conversation
- Tool execution: Varies by tool
- Vector index: Same as traditional RAG

### **Response Time:**
- Traditional RAG: 1-3 seconds
- Agent queries: 3-10 seconds (depending on tools used)
- Specialized agents: 5-15 seconds

### **Scaling:**
- Horizontal scaling supported
- Memory can be shared across instances
- Tools can be optimized individually

## 🔒 Security Considerations

### **API Security:**
- Authentication required for agent endpoints
- Rate limiting on tool usage
- Input validation for all tools

### **Data Privacy:**
- Conversation memory can be cleared
- Sensitive data handling in specialized agents
- HIPAA compliance for healthcare agents

## 🎯 Next Steps

### **1. Customize for Your Use Case:**
- Add domain-specific tools
- Customize agent prompts
- Integrate with your data sources

### **2. Production Deployment:**
- Set up monitoring and logging
- Implement proper authentication
- Add error handling and recovery

### **3. Advanced Features:**
- Multi-agent systems
- Tool chaining and workflows
- Custom reasoning engines

## 📚 Additional Resources

- [LlamaIndex Agent Documentation](https://docs.llamaindex.ai/en/stable/use_cases/agents/)
- [ReAct Agent Paper](https://arxiv.org/abs/2210.03629)
- [Tool Use in LLMs](https://openai.com/blog/function-calling-and-other-api-updates)

## 🤝 Contributing

Feel free to contribute by:
- Adding new tools
- Creating specialized agents
- Improving error handling
- Adding tests
- Writing documentation

## 📄 License

This project is for educational purposes. Feel free to modify and use as needed.

