import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
import base64
from typing import Optional
import json
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = os.environ.get("GEMINI_API")
    if not api_key:
        print("WARNING: No API key found in environment variables")
        print("Please set GEMINI_API_KEY or GEMINI_API environment variable")
    else:
        print(f"Using GEMINI_API environment variable: {api_key[:5] if api_key else 'None'}...")
else:
    print(f"Using GEMINI_API_KEY environment variable: {api_key[:5] if api_key else 'None'}...")

print(f"API key configured: {api_key[:5] + '...' if api_key and len(api_key) > 5 else 'Not configured'}")
genai.configure(api_key=api_key)

text_model_name = 'gemini-2.5-pro-exp-03-25'
image_model_name = 'imagen-3.0-generate-002'
