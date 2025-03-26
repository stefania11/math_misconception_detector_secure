import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print('GEMINI_API_KEY environment variable not set')
    exit(1)

genai.configure(api_key=api_key)

model_name = 'gemini-2.5-pro-exp-03-25'

model = genai.GenerativeModel(model_name)
prompt = 'Create a visual representation of an algebra exercise about solving linear equations for middle school students.'
response = model.generate_content(prompt)

print('Response type:', type(response))
print('Response attributes:', dir(response))
print('Response text:', response.text)

if hasattr(response, 'parts'):
    print('Response has parts:', len(response.parts))
    for i, part in enumerate(response.parts):
        print(f'Part {i} type:', type(part))
        print(f'Part {i} attributes:', dir(part))
        if hasattr(part, 'text') and part.text:
            print(f'Part {i} text:', part.text[:100] + '...' if len(part.text) > 100 else part.text)
        if hasattr(part, 'image') and part.image:
            print(f'Part {i} has image data')
