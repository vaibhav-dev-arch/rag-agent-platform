# RAG Agent Platform

A comprehensive RAG (Retrieval-Augmented Generation) platform with agent architecture.

## 🚀 Features

### Core RAG Platform
- **RAG System**: Retrieval-Augmented Generation with vector embeddings
- **Agent Architecture**: ReActAgent for reasoning and action-taking
- **LlamaIndex Integration**: Robust document indexing and retrieval
- **OpenAI Support**: GPT-3.5-turbo for high-quality language generation
- **Web Scraping**: BeautifulSoup for information gathering
- **Local LLM Support**: Ollama integration for offline operation
- **Mock RAG**: Development and testing without API costs

### Technology Stack
- **Python 3.11+**: Core programming language
- **LlamaIndex Framework**: Document processing and indexing
- **OpenAI API**: Language model integration
- **FastAPI**: Modern REST API
- **Flask**: Web user interface

## 📁 Project Structure

```
rag-agent-platform/
├── src/                    # Source code
│   ├── rag_agent/         # RAG platform core
│   │   ├── api_server.py  # FastAPI server
│   │   ├── web_ui.py      # Flask web interface
│   │   ├── agent_architecture/  # Agent implementations
│   │   └── traditional_rag/     # Traditional RAG examples
│   │
│   ├── shared/            # Shared utilities
│   └── examples/          # Example implementations
│
├── config/                # Configuration files
├── docs/                  # Documentation
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── output/                # Generated content
└── data/                  # Data files
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+

### Setup
1. Clone the repository:
```bash
git clone https://github.com/ragagentplatform/rag-agent-platform.git
cd rag-agent-platform
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## 🚀 Quick Start

### Running the RAG Platform

1. **Start the API server**:
```bash
python -m src api
# or
python scripts/rag_platform.py api
```

2. **Start the web interface**:
```bash
python -m src web
# or
python scripts/rag_platform.py web
```

3. **Generate a video**:
```bash
python -m src video
# or
python scripts/rag_platform.py video
```

### Using the RAG System

1. **API Usage**:
```python
import requests

# Query the RAG system
response = requests.post("http://localhost:8000/query", 
                        json={"query": "What is RAG?"})
print(response.json())
```

2. **Web Interface**:
- Open http://localhost:5000 in your browser
- Enter your query in the interface
- View results and generated responses

## 📚 Documentation

- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Agent Architecture](AGENT_ARCHITECTURE_README.md) - Agent system details
- [Project Overview](project_overview.md) - Detailed project information
- [Execution Workflows](execution_workflows.md) - System workflows

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific tests:
```bash
python -m pytest tests/test_rag_agent.py
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `OLLAMA_BASE_URL`: Ollama server URL (optional)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/ragagentplatform/rag-agent-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ragagentplatform/rag-agent-platform/discussions)
- **Documentation**: [Project Wiki](https://github.com/ragagentplatform/rag-agent-platform/wiki)

## 🎯 Roadmap

- [ ] Enhanced agent capabilities
- [ ] Additional LLM integrations
- [ ] Advanced video templates
- [ ] Cloud deployment options
- [ ] Performance optimizations
- [ ] Extended documentation

## 🙏 Acknowledgments

- [LlamaIndex](https://github.com/jerryjliu/llama_index) for the RAG framework
- [OpenAI](https://openai.com/) for language models
- [Playwright](https://playwright.dev/) for browser automation
- [FFmpeg](https://ffmpeg.org/) for video processing
- [Microsoft Edge TTS](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/) for text-to-speech