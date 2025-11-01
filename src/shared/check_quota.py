import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

def check_quota():
    """Check OpenAI account quota and billing status"""
    print("💰 Checking OpenAI Account Status")
    print("=" * 40)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Try to get account info
        print("🔄 Checking account status...")
        
        # Test with a minimal request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        
        print("✅ Account is working!")
        print("🎉 You can now use the app!")
        
    except openai.RateLimitError as e:
        print("⚠️  Rate limit exceeded")
        print("💡 Wait a few minutes and try again")
        print(f"Details: {e}")
        
    except openai.InsufficientQuotaError as e:
        print("❌ Insufficient quota")
        print("💡 You need to add billing information or credits")
        print("🔗 Visit: https://platform.openai.com/account/billing")
        print(f"Details: {e}")
        
    except openai.AuthenticationError as e:
        print("❌ Authentication failed")
        print("💡 Check your API key")
        print(f"Details: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    check_quota() 