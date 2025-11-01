import os
from dotenv import load_dotenv
from llama_index import VectorStoreIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.web import BeautifulSoupWebReader
from llama_index.node_parser import SentenceSplitter

# Load environment variables
load_dotenv()

def setup_llamaindex():
    """Setup LlamaIndex with OpenAI configuration"""
    # Configure OpenAI
    llm = OpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Configure embeddings
    embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Set global settings
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20
    
    return llm, embed_model

def load_web_pages(urls):
    """Load content from web pages"""
    print("Loading web pages...")
    reader = BeautifulSoupWebReader()
    documents = reader.load_data(urls=urls)
    print(f"Loaded {len(documents)} documents from web pages")
    return documents

def create_index(documents):
    """Create a vector index from documents"""
    print("Creating vector index...")
    
    # Parse documents into nodes
    parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
    nodes = parser.get_nodes_from_documents(documents)
    
    # Create index
    index = VectorStoreIndex(nodes)
    print(f"Created index with {len(nodes)} nodes")
    return index

def query_index(index, query):
    """Query the index"""
    print(f"\nQuerying: {query}")
    print("-" * 50)
    
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    
    print(f"Response: {response}")
    print(f"Source nodes: {len(response.source_nodes)}")
    
    # Show source information
    for i, source_node in enumerate(response.source_nodes):
        print(f"\nSource {i+1}:")
        print(f"Score: {source_node.score}")
        print(f"Text preview: {source_node.text[:200]}...")
    
    return response

def main():
    """Main function to demonstrate LlamaIndex capabilities"""
    print("🚀 LlamaIndex Sample Project with OpenAI Integration")
    print("=" * 60)
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        print("See env_example.txt for reference")
        return
    
    try:
        # Setup LlamaIndex
        llm, embed_model = setup_llamaindex()
        print("✅ LlamaIndex configured successfully")
        
        # Sample web pages to process
        sample_urls = [
            "https://en.wikipedia.org/wiki/Artificial_intelligence",
            "https://en.wikipedia.org/wiki/Machine_learning"
        ]
        
        # Load web pages
        documents = load_web_pages(sample_urls)
        
        # Create index
        index = create_index(documents)
        
        # Example queries
        queries = [
            "What is artificial intelligence?",
            "How does machine learning relate to AI?",
            "What are the main applications of AI?"
        ]
        
        # Run queries
        for query in queries:
            query_index(index, query)
            print("\n" + "="*60 + "\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your OpenAI API key is valid and you have sufficient credits")

if __name__ == "__main__":
    main() 