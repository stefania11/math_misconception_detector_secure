import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini_connection():
    """Test the connection to Gemini API."""
    print("Testing Gemini API connection...")
    
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = os.environ.get("GEMINI_API")
        if not api_key:
            print("ERROR: No API key found in environment variables.")
            return False
    
    masked_key = f"{api_key[:5]}...{api_key[-5:]}" if api_key else "None"
    print(f"API key found: {masked_key}")
    
    try:
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
        response = model.generate_content("Hello, are you working correctly?")
        
        print("API test successful!")
        print(f"Model response: {response.text[:100]}...")
        return True
    except Exception as e:
        print(f"ERROR: API test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_connection()
    sys.exit(0 if success else 1)
