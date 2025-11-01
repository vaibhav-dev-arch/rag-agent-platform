"""
LlamaIndex Agent Example - Enhanced RAG with Agent Architecture
This extends the existing project with agent capabilities
"""

import os
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Any

load_dotenv()

# Setup LlamaIndex with OpenAI
def setup_llamaindex():
    """Setup LlamaIndex with OpenAI models"""
    Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20

# Agent Tools
def web_search_tool(query: str) -> str:
    """Search the web for current information"""
    try:
        # This is a mock implementation - in production, use a real search API
        print(f"🔍 Searching web for: {query}")
        
        # Mock search results
        mock_results = {
            "artificial intelligence": "AI is transforming industries with machine learning, natural language processing, and computer vision.",
            "machine learning": "ML algorithms learn from data to make predictions and decisions without explicit programming.",
            "llamaindex": "LlamaIndex is a data framework for LLM applications that helps structure and access data for language models."
        }
        
        return mock_results.get(query.lower(), f"Search results for '{query}': No specific information found.")
    except Exception as e:
        return f"Error searching web: {str(e)}"

def document_search_tool(query: str) -> str:
    """Search through indexed documents"""
    try:
        print(f"📚 Searching documents for: {query}")
        
        # Load and search documents
        documents = SimpleDirectoryReader("documents").load_data()
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        
        response = query_engine.query(query)
        return str(response)
    except Exception as e:
        return f"Error searching documents: {str(e)}"

def web_scrape_tool(url: str) -> str:
    """Scrape content from a web page"""
    try:
        print(f"🌐 Scraping content from: {url}")
        
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract main content
        content = soup.get_text()
        return content[:1000] + "..." if len(content) > 1000 else content
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"

def calculate_tool(expression: str) -> str:
    """Perform mathematical calculations"""
    try:
        print(f"🧮 Calculating: {expression}")
        
        # Simple calculation - in production, use a proper math parser
        allowed_chars = set('0123456789+-*/()., ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"
        
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

def get_current_time_tool() -> str:
    """Get current date and time"""
    from datetime import datetime
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

# Create Agent with Tools
def create_rag_agent():
    """Create a RAG agent with multiple tools"""
    
    # Define tools
    tools = [
        FunctionTool.from_defaults(fn=web_search_tool, name="web_search"),
        FunctionTool.from_defaults(fn=document_search_tool, name="document_search"),
        FunctionTool.from_defaults(fn=web_scrape_tool, name="web_scrape"),
        FunctionTool.from_defaults(fn=calculate_tool, name="calculate"),
        FunctionTool.from_defaults(fn=get_current_time_tool, name="get_time"),
    ]
    
    # Create agent
    agent = ReActAgent.from_tools(
        tools=tools,
        llm=Settings.llm,
        verbose=True,
        system_prompt="""You are a helpful AI assistant with access to multiple tools. 
        
        You can:
        - Search the web for current information
        - Search through indexed documents
        - Scrape content from web pages
        - Perform calculations
        - Get current time
        
        Always use the most appropriate tool(s) to answer user questions.
        If you need multiple pieces of information, use multiple tools.
        Be thorough and provide comprehensive answers."""
    )
    
    return agent

# Main Agent Interface
def run_agent_chat():
    """Run interactive chat with the agent"""
    print("🤖 LlamaIndex Agent Chat")
    print("=" * 50)
    print("Available capabilities:")
    print("- Web search for current information")
    print("- Document search through indexed content")
    print("- Web scraping from URLs")
    print("- Mathematical calculations")
    print("- Current time information")
    print("=" * 50)
    
    # Setup
    setup_llamaindex()
    agent = create_rag_agent()
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Agent: Thinking...")
            response = agent.chat(user_input)
            print(f"\n🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

# Example Agent Queries
def demo_agent_capabilities():
    """Demonstrate agent capabilities with example queries"""
    print("🎯 Agent Capabilities Demo")
    print("=" * 50)
    
    setup_llamaindex()
    agent = create_rag_agent()
    
    demo_queries = [
        "What is artificial intelligence? Search both documents and web.",
        "Calculate 15 * 23 + 45",
        "What time is it now?",
        "Search for information about machine learning in our documents",
        "Scrape content from https://example.com (if accessible)"
    ]
    
    for query in demo_queries:
        print(f"\n👤 Query: {query}")
        print("🤖 Agent: Processing...")
        try:
            response = agent.chat(query)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        print("-" * 50)

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Interactive chat")
    print("2. Demo capabilities")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        run_agent_chat()
    elif choice == "2":
        demo_agent_capabilities()
    else:
        print("Invalid choice. Running interactive chat...")
        run_agent_chat()
