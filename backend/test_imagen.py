import os
from dotenv import load_dotenv
import google.generativeai as genai
import base64

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print('GEMINI_API_KEY environment variable not set')
    exit(1)

genai.configure(api_key=api_key)

image_model_name = 'imagen-3.0-generate-002'

def test_image_generation():
    try:
        image_model = genai.GenerativeModel(image_model_name)
        
        image_prompt = '''
        Create a visual representation of an algebra exercise about solving linear equations for middle school students.
        The image should be clear, educational, and visually appealing.
        Include relevant mathematical notation, diagrams, or visual aids that help explain the concept.
        Make sure the text is readable and the overall design is engaging for middle school students.
        '''
        
        print(f"Generating image with model: {image_model_name}")
        print(f"Using prompt: {image_prompt[:100]}...")
        
        image_response = image_model.generate_content(image_prompt)
        
        print("Response type:", type(image_response))
        print("Response attributes:", dir(image_response))
        
        if hasattr(image_response, 'candidates') and len(image_response.candidates) > 0:
            print(f"Found {len(image_response.candidates)} candidates")
            
            for i, candidate in enumerate(image_response.candidates):
                print(f"Candidate {i} type:", type(candidate))
                print(f"Candidate {i} attributes:", dir(candidate))
                
                if hasattr(candidate, 'content') and candidate.content:
                    print(f"Candidate {i} has content")
                    print(f"Content type:", type(candidate.content))
                    print(f"Content attributes:", dir(candidate.content))
                    
                    if hasattr(candidate.content, 'parts') and len(candidate.content.parts) > 0:
                        print(f"Content has {len(candidate.content.parts)} parts")
                        
                        for j, part in enumerate(candidate.content.parts):
                            print(f"Part {j} type:", type(part))
                            print(f"Part {j} attributes:", dir(part))
                            
                            if hasattr(part, 'inline_data') and part.inline_data:
                                print(f"Part {j} has inline_data")
                                print(f"Image data found! Success!")
                                return True
        
        print("No image data found in response")
        return False
        
    except Exception as e:
        print(f"Error testing image generation: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_image_generation()
    print(f"Image generation test {'succeeded' if success else 'failed'}")
