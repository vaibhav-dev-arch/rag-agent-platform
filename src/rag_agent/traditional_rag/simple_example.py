import os
from dotenv import load_dotenv
from llama_index import VectorStoreIndex, Document, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# Load environment variables
load_dotenv()

def simple_llamaindex_example():
    """Simple example showing basic LlamaIndex functionality"""
    print("🔍 Simple LlamaIndex Example")
    print("=" * 40)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found")
        print("Please create a .env file with your OpenAI API key")
        return
    
    try:
        # Setup OpenAI
        llm = OpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Configure settings
        Settings.llm = llm
        Settings.embed_model = embed_model
        
        print("✅ OpenAI configured successfully")
        
        # Create sample documents
        documents = [
            Document(text="Python is a high-level programming language known for its simplicity and readability. It's widely used in data science, web development, and automation."),
            Document(text="Machine learning is a subset of artificial intelligence that enables computers to learn and make predictions from data without being explicitly programmed."),
            Document(text="LlamaIndex is a data framework for LLM applications that helps you ingest, structure, and access your data for LLMs."),
            Document(text="OpenAI provides powerful language models like GPT-3.5 and GPT-4 that can understand and generate human-like text.")
        ]
        
        print(f"📄 Created {len(documents)} sample documents")
        
        # Create index
        index = VectorStoreIndex.from_documents(documents)
        print("✅ Vector index created successfully")
        
        # Create query engine
        query_engine = index.as_query_engine()
        
        # Example queries
        test_queries = [
            "What is Python?",
            "How does machine learning work?",
            "What is LlamaIndex used for?",
            "Tell me about OpenAI models"
        ]
        
        print("\n🔍 Running test queries:")
        print("-" * 30)
        
        for query in test_queries:
            print(f"\nQ: {query}")
            response = query_engine.query(query)
            print(f"A: {response}")
        
        print("\n🎉 Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_llamaindex_example() 