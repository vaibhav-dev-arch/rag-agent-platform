import os
from dotenv import load_dotenv
from llama_index import VectorStoreIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.web import BeautifulSoupWebReader
from llama_index.node_parser import SentenceSplitter
from llama_index import Document

# Load environment variables
load_dotenv()

def setup_llamaindex():
    """Setup LlamaIndex with OpenAI configuration"""
    llm = OpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20
    
    return llm, embed_model

def scrape_tech_news():
    """Scrape content from tech news websites"""
    print("📰 Scraping tech news websites...")
    
    # Tech news URLs
    tech_urls = [
        "https://techcrunch.com/",
        "https://www.theverge.com/",
        "https://www.wired.com/"
    ]
    
    reader = BeautifulSoupWebReader()
    
    try:
        documents = reader.load_data(urls=tech_urls)
        print(f"✅ Successfully scraped {len(documents)} documents")
        return documents
    except Exception as e:
        print(f"❌ Error scraping websites: {e}")
        print("Creating sample documents instead...")
        
        # Fallback: Create sample documents
        sample_docs = [
            Document(text="Artificial Intelligence is transforming industries across the globe. Companies are adopting AI to improve efficiency and create new opportunities."),
            Document(text="Machine Learning algorithms are becoming more sophisticated, enabling better predictions and automation in various fields."),
            Document(text="The future of technology lies in the integration of AI, ML, and human creativity to solve complex problems.")
        ]
        return sample_docs

def create_chatbot(index):
    """Create a simple chatbot interface"""
    print("\n🤖 Chatbot Interface")
    print("Type 'quit' to exit")
    print("-" * 40)
    
    query_engine = index.as_query_engine()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if not user_input:
                continue
            
            print("🤔 Thinking...")
            response = query_engine.query(user_input)
            print(f"Bot: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def analyze_content(documents):
    """Analyze the scraped content"""
    print("\n📊 Content Analysis")
    print("-" * 30)
    
    total_chars = sum(len(doc.text) for doc in documents)
    avg_length = total_chars / len(documents) if documents else 0
    
    print(f"Total documents: {len(documents)}")
    print(f"Total characters: {total_chars:,}")
    print(f"Average document length: {avg_length:.0f} characters")
    
    # Show document previews
    for i, doc in enumerate(documents[:3]):  # Show first 3 docs
        preview = doc.text[:150] + "..." if len(doc.text) > 150 else doc.text
        print(f"\nDocument {i+1} preview:")
        print(f"  {preview}")

def main():
    """Advanced web scraping example"""
    print("🌐 Advanced Web Scraping with LlamaIndex")
    print("=" * 50)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found")
        print("Please set your OpenAI API key in a .env file")
        return
    
    try:
        # Setup
        llm, embed_model = setup_llamaindex()
        print("✅ LlamaIndex configured")
        
        # Scrape content
        documents = scrape_tech_news()
        
        # Analyze content
        analyze_content(documents)
        
        # Create index
        print("\n🔍 Creating search index...")
        parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
        nodes = parser.get_nodes_from_documents(documents)
        index = VectorStoreIndex(nodes)
        print(f"✅ Index created with {len(nodes)} nodes")
        
        # Start chatbot
        create_chatbot(index)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 