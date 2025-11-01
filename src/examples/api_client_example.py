import requests
import json
import time

# API Configuration
API_BASE_URL = "http://localhost:8000"

def print_response(response, title=""):
    """Pretty print API response"""
    print(f"\n{'='*50}")
    if title:
        print(f"📋 {title}")
        print(f"{'='*50}")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
    print(f"{'='*50}")

def test_api():
    """Test the LlamaIndex RAG API"""
    print("🚀 Testing LlamaIndex RAG API")
    print("Make sure the API server is running on http://localhost:8000")
    
    # 1. Health Check
    print("\n1️⃣ Testing Health Check...")
    response = requests.get(f"{API_BASE_URL}/health")
    print_response(response, "Health Check")
    
    # 2. Get Status
    print("\n2️⃣ Testing Status Check...")
    response = requests.get(f"{API_BASE_URL}/status")
    print_response(response, "Index Status")
    
    # 3. Add Sample Documents
    print("\n3️⃣ Adding Sample Documents...")
    sample_documents = [
        {
            "text": "Python is a high-level programming language known for its simplicity and readability. It's widely used in data science, web development, and automation.",
            "metadata": {"source": "sample", "topic": "programming"}
        },
        {
            "text": "Machine learning is a subset of artificial intelligence that enables computers to learn and make predictions from data without being explicitly programmed.",
            "metadata": {"source": "sample", "topic": "AI/ML"}
        },
        {
            "text": "LlamaIndex is a data framework for LLM applications that helps you ingest, structure, and access your data for LLMs.",
            "metadata": {"source": "sample", "topic": "framework"}
        }
    ]
    
    for i, doc in enumerate(sample_documents):
        response = requests.post(f"{API_BASE_URL}/documents", json=doc)
        print_response(response, f"Adding Document {i+1}")
    
    # 4. List Documents
    print("\n4️⃣ Listing Documents...")
    response = requests.get(f"{API_BASE_URL}/documents")
    print_response(response, "Document List")
    
    # 5. Test Queries
    print("\n5️⃣ Testing Queries...")
    test_queries = [
        "What is Python?",
        "How does machine learning work?",
        "What is LlamaIndex used for?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        response = requests.post(f"{API_BASE_URL}/query", json={
            "query": query,
            "include_sources": True
        })
        print_response(response, f"Query Response: {query}")
        time.sleep(1)  # Small delay between queries
    
    # 6. Test Web Scraping
    print("\n6️⃣ Testing Web Scraping...")
    scrape_request = {
        "urls": ["https://en.wikipedia.org/wiki/Artificial_intelligence"],
        "chunk_size": 1024,
        "chunk_overlap": 20
    }
    response = requests.post(f"{API_BASE_URL}/scrape", json=scrape_request)
    print_response(response, "Web Scraping")
    
    # 7. Query Scraped Content
    print("\n7️⃣ Querying Scraped Content...")
    response = requests.post(f"{API_BASE_URL}/query", json={
        "query": "What is artificial intelligence?",
        "include_sources": True
    })
    print_response(response, "Query Scraped Content")
    
    # 8. Final Status
    print("\n8️⃣ Final Status...")
    response = requests.get(f"{API_BASE_URL}/status")
    print_response(response, "Final Index Status")

def interactive_mode():
    """Interactive mode for testing queries"""
    print("\n🤖 Interactive Query Mode")
    print("Type 'quit' to exit")
    print("-" * 40)
    
    while True:
        try:
            query = input("\n❓ Enter your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if not query:
                continue
            
            print("🤔 Processing...")
            response = requests.post(f"{API_BASE_URL}/query", json={
                "query": query,
                "include_sources": True
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n💡 Answer: {data['answer']}")
                print(f"⏱️  Processing time: {data['processing_time']:.2f}s")
                
                if data['sources']:
                    print(f"\n📚 Sources ({len(data['sources'])}):")
                    for i, source in enumerate(data['sources']):
                        print(f"  {i+1}. Score: {source['score']:.3f}")
                        print(f"     Text: {source['text'][:100]}...")
            else:
                print(f"❌ Error: {response.text}")
                
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        test_api()
        print("\n🎉 API testing completed!")
        print("\nTo run in interactive mode: python api_client_example.py --interactive") 