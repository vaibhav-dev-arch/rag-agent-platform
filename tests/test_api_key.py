import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

def test_api_key():
    """Test if the OpenAI API key is working"""
    print("🔑 Testing OpenAI API Key")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ Error: No API key found in .env file")
        print("Please add your OpenAI API key to the .env file")
        return False
    
    if api_key == "your_openai_api_key_here":
        print("❌ Error: API key not updated")
        print("Please replace 'your_openai_api_key_here' with your actual API key")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple request
        print("🔄 Testing API connection...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello, API key is working!'"}],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Test Successful!")
        print(f"🤖 Response: {result}")
        return True
        
    except openai.AuthenticationError:
        print("❌ Authentication Error: Invalid API key")
        print("Please check your API key and try again")
        return False
    except openai.RateLimitError:
        print("❌ Rate Limit Error: Too many requests")
        print("Please wait a moment and try again")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_api_key()
    if success:
        print("\n🎉 Your API key is working! You can now run the app.")
    else:
        print("\n💡 Please fix the API key issue and try again.") 