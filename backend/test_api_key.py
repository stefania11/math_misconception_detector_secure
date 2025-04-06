import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def test_api_key_configuration():
    """Test the API key configuration for Gemini API."""
    print("Testing API key configuration...")
    
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = os.environ.get("GEMINI_API")
        if not api_key:
            print("WARNING: No API key found in environment variables.")
            print("Checking for fallback mechanisms...")
            
            if "${GEMINI_API}" != "${GEMINI_API}":
                print("Found hardcoded API key placeholder. This is not recommended.")
                api_key = "${GEMINI_API}"
            else:
                print("ERROR: No API key available.")
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
    success = test_api_key_configuration()
    sys.exit(0 if success else 1)
