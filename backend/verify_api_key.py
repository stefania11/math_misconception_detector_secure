import os
import sys
import json
from dotenv import load_dotenv
import google.generativeai as genai

def verify_api_key():
    """Verify the Gemini API key configuration."""
    print("Verifying Gemini API key configuration...")
    
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = os.environ.get("GEMINI_API")
        if not api_key:
            print("ERROR: No API key found in environment variables.")
            return False
    
    masked_key = f"{api_key[:5]}...{api_key[-5:]}" if api_key and len(api_key) > 10 else "Invalid key format"
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
        error_details = str(e)
        
        if "API_KEY_INVALID" in error_details:
            print("The API key is invalid. Please check your Gemini API key.")
        elif "PERMISSION_DENIED" in error_details:
            print("Permission denied. The API key may not have access to the Gemini 2.5 Pro model.")
        elif "RESOURCE_EXHAUSTED" in error_details:
            print("Resource exhausted. You may have reached your API quota limit.")
        
        return False

if __name__ == "__main__":
    success = verify_api_key()
    
    result = {
        "success": success,
        "timestamp": os.popen("date").read().strip(),
        "environment": {
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY") is not None,
            "GEMINI_API": os.environ.get("GEMINI_API") is not None
        }
    }
    
    print("\nResult summary:")
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if success else 1)
