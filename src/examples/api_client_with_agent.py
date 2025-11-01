"""
API Client Example for LlamaIndex RAG API with Agent Architecture
Demonstrates both traditional RAG and agent capabilities
"""

import requests
import json
import time
from typing import Dict, Any, List

class RAGAPIClient:
    """Client for interacting with the RAG API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_status(self) -> Dict[str, Any]:
        """Get index and system status"""
        response = self.session.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()
    
    def add_document(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a document to the index"""
        data = {
            "text": text,
            "metadata": metadata or {}
        }
        response = self.session.post(f"{self.base_url}/documents", json=data)
        response.raise_for_status()
        return response.json()
    
    def scrape_web_pages(self, urls: List[str]) -> Dict[str, Any]:
        """Scrape web pages and add to index"""
        data = {
            "urls": urls,
            "chunk_size": 1024,
            "chunk_overlap": 20
        }
        response = self.session.post(f"{self.base_url}/scrape", json=data)
        response.raise_for_status()
        return response.json()
    
    def query_traditional_rag(self, query: str, include_sources: bool = True) -> Dict[str, Any]:
        """Query using traditional RAG approach"""
        data = {
            "query": query,
            "include_sources": include_sources
        }
        response = self.session.post(f"{self.base_url}/query", json=data)
        response.raise_for_status()
        return response.json()
    
    def query_agent(self, query: str, use_memory: bool = True, tools: List[str] = None) -> Dict[str, Any]:
        """Query using agent architecture"""
        data = {
            "query": query,
            "use_memory": use_memory,
            "tools": tools
        }
        response = self.session.post(f"{self.base_url}/agent/query", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_agent_tools(self) -> Dict[str, Any]:
        """Get available agent tools"""
        response = self.session.get(f"{self.base_url}/agent/tools")
        response.raise_for_status()
        return response.json()
    
    def clear_agent_memory(self) -> Dict[str, Any]:
        """Clear agent conversation memory"""
        response = self.session.post(f"{self.base_url}/agent/clear-memory")
        response.raise_for_status()
        return response.json()
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the index"""
        response = self.session.get(f"{self.base_url}/documents")
        response.raise_for_status()
        return response.json()
    
    def clear_documents(self) -> Dict[str, Any]:
        """Clear all documents"""
        response = self.session.delete(f"{self.base_url}/documents")
        response.raise_for_status()
        return response.json()

def demo_traditional_rag(client: RAGAPIClient):
    """Demonstrate traditional RAG capabilities"""
    print("🔍 Traditional RAG Demo")
    print("=" * 50)
    
    # Add sample documents
    sample_docs = [
        {
            "text": "Artificial Intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior. It includes machine learning, natural language processing, and computer vision.",
            "metadata": {"source": "demo", "topic": "AI"}
        },
        {
            "text": "Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms to identify patterns in data.",
            "metadata": {"source": "demo", "topic": "ML"}
        },
        {
            "text": "LlamaIndex is a data framework for LLM applications that helps you ingest, structure, and access your data for language models. It provides tools for building RAG systems.",
            "metadata": {"source": "demo", "topic": "LlamaIndex"}
        }
    ]
    
    print("Adding sample documents...")
    for doc in sample_docs:
        result = client.add_document(doc["text"], doc["metadata"])
        print(f"✅ Added document: {result['document_id']}")
    
    # Traditional RAG queries
    queries = [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "What is LlamaIndex used for?"
    ]
    
    print("\nTraditional RAG Queries:")
    print("-" * 30)
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        result = client.query_traditional_rag(query)
        print(f"🤖 Answer: {result['answer']}")
        print(f"⏱️ Processing time: {result['processing_time']:.2f}s")
        if result['sources']:
            print(f"📚 Sources: {len(result['sources'])} documents")

def demo_agent_capabilities(client: RAGAPIClient):
    """Demonstrate agent capabilities"""
    print("\n🤖 Agent Architecture Demo")
    print("=" * 50)
    
    # Get available tools
    tools_info = client.get_agent_tools()
    print("Available tools:")
    for tool in tools_info['available_tools']:
        print(f"  - {tool}: {tools_info['tool_descriptions'][tool]}")
    
    # Agent queries that demonstrate different capabilities
    agent_queries = [
        "What is artificial intelligence? Search both our documents and the web.",
        "Calculate 15 * 23 + 45",
        "What time is it now?",
        "Analyze the sentiment of this text: 'This is amazing! I love it!'",
        "Summarize this text: 'Artificial Intelligence is transforming industries worldwide. From healthcare to finance, AI applications are becoming increasingly sophisticated. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions. This technology is revolutionizing how businesses operate and how we interact with technology in our daily lives.'"
    ]
    
    print("\nAgent Queries:")
    print("-" * 30)
    
    for query in agent_queries:
        print(f"\n❓ Query: {query}")
        result = client.query_agent(query)
        print(f"🤖 Answer: {result['answer']}")
        print(f"🛠️ Tools used: {', '.join(result['tools_used'])}")
        print(f"⏱️ Processing time: {result['processing_time']:.2f}s")
        print(f"🧠 Memory used: {result['memory_used']}")

def demo_web_scraping(client: RAGAPIClient):
    """Demonstrate web scraping capabilities"""
    print("\n🌐 Web Scraping Demo")
    print("=" * 50)
    
    # Scrape some example URLs (using example.com as it's safe)
    urls = [
        "https://example.com",
        "https://httpbin.org/html"
    ]
    
    print(f"Scraping URLs: {urls}")
    result = client.scrape_web_pages(urls)
    print(f"✅ Scraped {result['message']}")
    
    # Query the scraped content
    print("\nQuerying scraped content...")
    query_result = client.query_traditional_rag("What is this website about?")
    print(f"🤖 Answer: {query_result['answer']}")

def interactive_mode(client: RAGAPIClient):
    """Interactive mode for testing"""
    print("\n🎮 Interactive Mode")
    print("=" * 50)
    print("Commands:")
    print("  'rag <query>' - Use traditional RAG")
    print("  'agent <query>' - Use agent architecture")
    print("  'tools' - Show available tools")
    print("  'clear' - Clear agent memory")
    print("  'status' - Show system status")
    print("  'quit' - Exit")
    print("-" * 30)
    
    while True:
        try:
            user_input = input("\n👤 Enter command: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'tools':
                tools_info = client.get_agent_tools()
                print("Available tools:")
                for tool in tools_info['available_tools']:
                    print(f"  - {tool}: {tools_info['tool_descriptions'][tool]}")
                continue
            
            if user_input.lower() == 'clear':
                result = client.clear_agent_memory()
                print(f"✅ {result['message']}")
                continue
            
            if user_input.lower() == 'status':
                status = client.get_status()
                print(f"📊 Status: {json.dumps(status, indent=2)}")
                continue
            
            if user_input.startswith('rag '):
                query = user_input[4:].strip()
                if query:
                    result = client.query_traditional_rag(query)
                    print(f"🤖 RAG Answer: {result['answer']}")
                continue
            
            if user_input.startswith('agent '):
                query = user_input[6:].strip()
                if query:
                    result = client.query_agent(query)
                    print(f"🤖 Agent Answer: {result['answer']}")
                    print(f"🛠️ Tools used: {', '.join(result['tools_used'])}")
                continue
            
            if user_input:
                print("❓ Unknown command. Use 'rag <query>', 'agent <query>', 'tools', 'clear', 'status', or 'quit'")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Main function"""
    print("🚀 LlamaIndex RAG API Client with Agent Architecture")
    print("=" * 60)
    
    # Initialize client
    client = RAGAPIClient()
    
    try:
        # Check API health
        health = client.health_check()
        print(f"✅ API Status: {health['status']}")
        print(f"   OpenAI configured: {health['openai_configured']}")
        print(f"   Index ready: {health['index_ready']}")
        print(f"   Agent ready: {health['agent_ready']}")
        
        if health['status'] != 'healthy':
            print("⚠️ API is not fully healthy. Some features may not work.")
        
        # Choose demo mode
        print("\nChoose demo mode:")
        print("1. Traditional RAG demo")
        print("2. Agent capabilities demo")
        print("3. Web scraping demo")
        print("4. Interactive mode")
        print("5. Run all demos")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            demo_traditional_rag(client)
        elif choice == "2":
            demo_agent_capabilities(client)
        elif choice == "3":
            demo_web_scraping(client)
        elif choice == "4":
            interactive_mode(client)
        elif choice == "5":
            demo_traditional_rag(client)
            demo_agent_capabilities(client)
            demo_web_scraping(client)
            interactive_mode(client)
        else:
            print("Invalid choice. Running interactive mode...")
            interactive_mode(client)
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server.")
        print("Make sure the API server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

