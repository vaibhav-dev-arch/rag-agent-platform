"""
Advanced RAG Agent Architecture
This extends your existing LlamaIndex project with sophisticated agent capabilities
"""

import os
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.memory import ChatMemoryBuffer
import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import aiohttp

load_dotenv()

class RAGAgent:
    """Advanced RAG Agent with multiple capabilities"""
    
    def __init__(self):
        self.setup_llamaindex()
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=2000)
        self.tools = self.create_tools()
        self.agent = self.create_agent()
        self.conversation_history = []
    
    def setup_llamaindex(self):
        """Setup LlamaIndex with OpenAI models"""
        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        Settings.chunk_size = 1024
        Settings.chunk_overlap = 20
    
    def create_tools(self) -> List[FunctionTool]:
        """Create all available tools for the agent"""
        tools = [
            FunctionTool.from_defaults(fn=self.document_search, name="document_search"),
            FunctionTool.from_defaults(fn=self.web_search, name="web_search"),
            FunctionTool.from_defaults(fn=self.web_scrape, name="web_scrape"),
            FunctionTool.from_defaults(fn=self.calculate, name="calculate"),
            FunctionTool.from_defaults(fn=self.get_time, name="get_time"),
            FunctionTool.from_defaults(fn=self.analyze_sentiment, name="analyze_sentiment"),
            FunctionTool.from_defaults(fn=self.summarize_text, name="summarize_text"),
            FunctionTool.from_defaults(fn=self.translate_text, name="translate_text"),
            FunctionTool.from_defaults(fn=self.get_weather, name="get_weather"),
            FunctionTool.from_defaults(fn=self.create_todo, name="create_todo"),
        ]
        return tools
    
    def create_agent(self) -> ReActAgent:
        """Create the main agent with tools and memory"""
        agent = ReActAgent.from_tools(
            tools=self.tools,
            llm=Settings.llm,
            memory=self.memory,
            verbose=True,
            system_prompt="""You are an advanced AI assistant with access to multiple tools and capabilities.

            Your capabilities include:
            - Searching through indexed documents
            - Web search for current information
            - Web scraping from URLs
            - Mathematical calculations
            - Time and date information
            - Sentiment analysis
            - Text summarization
            - Translation
            - Weather information
            - Task management

            Always use the most appropriate tool(s) to answer user questions.
            If you need multiple pieces of information, use multiple tools.
            Be thorough, accurate, and provide comprehensive answers.
            Remember previous conversation context and build upon it.
            
            When uncertain, ask clarifying questions rather than making assumptions."""
        )
        return agent
    
    # Tool Implementations
    def document_search(self, query: str) -> str:
        """Search through indexed documents"""
        try:
            print(f"📚 Searching documents for: {query}")
            
            # Load documents from your existing documents folder
            if os.path.exists("documents"):
                documents = SimpleDirectoryReader("documents").load_data()
                index = VectorStoreIndex.from_documents(documents)
                query_engine = index.as_query_engine()
                response = query_engine.query(query)
                return str(response)
            else:
                return "No documents found. Please ensure the 'documents' folder exists with your content."
        except Exception as e:
            return f"Error searching documents: {str(e)}"
    
    def web_search(self, query: str) -> str:
        """Search the web for current information"""
        try:
            print(f"🔍 Searching web for: {query}")
            
            # Mock implementation - replace with real search API
            search_results = {
                "artificial intelligence": "AI is revolutionizing industries with applications in healthcare, finance, transportation, and more.",
                "machine learning": "ML enables computers to learn and improve from experience without being explicitly programmed.",
                "llamaindex": "LlamaIndex is a data framework for LLM applications that helps structure and access data for language models.",
                "rag": "Retrieval-Augmented Generation combines information retrieval with text generation for more accurate responses."
            }
            
            return search_results.get(query.lower(), f"Web search results for '{query}': Information not found in mock database.")
        except Exception as e:
            return f"Error searching web: {str(e)}"
    
    def web_scrape(self, url: str) -> str:
        """Scrape content from a web page"""
        try:
            print(f"🌐 Scraping content from: {url}")
            
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:2000] + "..." if len(text) > 2000 else text
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"
    
    def calculate(self, expression: str) -> str:
        """Perform mathematical calculations"""
        try:
            print(f"🧮 Calculating: {expression}")
            
            # Simple calculation - in production, use a proper math parser
            allowed_chars = set('0123456789+-*/()., ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
            
            result = eval(expression)
            return f"Calculation result: {result}"
        except Exception as e:
            return f"Error calculating '{expression}': {str(e)}"
    
    def get_time(self) -> str:
        """Get current date and time"""
        now = datetime.now()
        return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        try:
            print(f"😊 Analyzing sentiment of: {text[:50]}...")
            
            # Simple sentiment analysis - in production, use a proper NLP library
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = "Positive"
            elif negative_count > positive_count:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            
            return f"Sentiment analysis: {sentiment} (Positive: {positive_count}, Negative: {negative_count})"
        except Exception as e:
            return f"Error analyzing sentiment: {str(e)}"
    
    def summarize_text(self, text: str) -> str:
        """Summarize long text"""
        try:
            print(f"📝 Summarizing text...")
            
            if len(text) < 100:
                return "Text is too short to summarize meaningfully."
            
            # Simple summarization - in production, use a proper summarization model
            sentences = text.split('.')
            if len(sentences) <= 3:
                return text
            
            # Take first and last sentences as summary
            summary = sentences[0] + ". " + sentences[-1] + "."
            return f"Summary: {summary}"
        except Exception as e:
            return f"Error summarizing text: {str(e)}"
    
    def translate_text(self, text: str, target_language: str = "spanish") -> str:
        """Translate text to target language"""
        try:
            print(f"🌍 Translating to {target_language}...")
            
            # Mock translation - in production, use a proper translation API
            translations = {
                "spanish": f"[Spanish] {text}",
                "french": f"[French] {text}",
                "german": f"[German] {text}",
                "italian": f"[Italian] {text}"
            }
            
            return translations.get(target_language.lower(), f"[{target_language}] {text}")
        except Exception as e:
            return f"Error translating text: {str(e)}"
    
    def get_weather(self, location: str) -> str:
        """Get weather information for a location"""
        try:
            print(f"🌤️ Getting weather for: {location}")
            
            # Mock weather - in production, use a real weather API
            return f"Weather in {location}: 72°F, Partly Cloudy, Humidity: 65%"
        except Exception as e:
            return f"Error getting weather: {str(e)}"
    
    def create_todo(self, task: str) -> str:
        """Create a todo item"""
        try:
            print(f"✅ Creating todo: {task}")
            
            # Simple todo storage - in production, use a database
            todo_id = len(self.conversation_history) + 1
            todo_item = {
                "id": todo_id,
                "task": task,
                "created_at": datetime.now().isoformat(),
                "completed": False
            }
            
            return f"Todo created: {todo_item['task']} (ID: {todo_id})"
        except Exception as e:
            return f"Error creating todo: {str(e)}"
    
    def chat(self, message: str) -> str:
        """Main chat interface"""
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": message})
            
            # Get agent response
            response = self.agent.chat(message)
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": str(response)})
            
            return str(response)
        except Exception as e:
            return f"Error in chat: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.reset()
        self.conversation_history = []

def main():
    """Main function to run the agent"""
    print("🤖 Advanced RAG Agent")
    print("=" * 50)
    print("Available capabilities:")
    print("- Document search through indexed content")
    print("- Web search for current information")
    print("- Web scraping from URLs")
    print("- Mathematical calculations")
    print("- Time and date information")
    print("- Sentiment analysis")
    print("- Text summarization")
    print("- Translation")
    print("- Weather information")
    print("- Task management")
    print("=" * 50)
    
    # Create agent
    agent = RAGAgent()
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'history':
                print("\n📜 Conversation History:")
                for i, msg in enumerate(agent.get_conversation_history()):
                    role = "👤 You" if msg["role"] == "user" else "🤖 Agent"
                    print(f"{role}: {msg['content']}")
                continue
            
            if user_input.lower() == 'clear':
                agent.clear_memory()
                print("🧹 Memory cleared!")
                continue
            
            if not user_input:
                continue
            
            print("\n🤖 Agent: Processing...")
            response = agent.chat(user_input)
            print(f"\n🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
