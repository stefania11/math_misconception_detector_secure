from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import google.generativeai as genai
import base64
import os
import json
from ..image_utils import process_image, validate_image, resize_image_if_needed
from .image_generation import generate_exercise_with_gemini

router = APIRouter()

model_name = 'gemini-2.5-pro-exp-03-25'

@router.post("/analyze")
async def analyze_image(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None)
):
    """
    Analyze a math problem image to detect misconceptions.
    
    Args:
        file: Uploaded image file
        image_base64: Base64 encoded image data
        
    Returns:
        JSON response with detected misconception
    """
    try:
        if file:
            contents = await file.read()
            processed_image = base64.b64encode(contents).decode('utf-8')
            
            if not validate_image(processed_image):
                raise HTTPException(status_code=400, detail="Invalid image format")
                
            processed_image = resize_image_if_needed(processed_image)
        elif image_base64:
            if image_base64 and image_base64.startswith('data:image'):
                image_base64 = image_base64.split(',')[1]
                
            processed_image = image_base64
            
            if not validate_image(processed_image):
                raise HTTPException(status_code=400, detail="Invalid image format")
                
            processed_image = resize_image_if_needed(processed_image)
        else:
            raise HTTPException(status_code=400, detail="No image provided")
        
        model = genai.GenerativeModel(model_name)
        
        prompt = '''
        Analyze this math problem and identify any misconceptions in the student's work.
        
        Return a JSON object with the following structure:
        {
            "id": "MaE##", // A unique ID for the misconception (e.g., MaE01, MaE02, etc.)
            "description": "Brief description of the misconception",
            "example": "Specific example of how this misconception manifests",
            "feedback": "Constructive feedback to help the student understand and correct the misconception",
            "exercise": "A suggested practice exercise to help reinforce the correct concept"
        }
        
        Common algebra misconceptions include:
        - MaE01: Misunderstanding the equals sign as an operation rather than a relation
        - MaE02: Incorrectly applying the distributive property
        - MaE03: Confusion with negative numbers in equations
        - MaE04: Misunderstanding the concept of variables
        - MaE05: Difficulty with fractions in algebraic expressions
        - MaE06: Confusion about order of operations
        - MaE07: Misinterpreting the denominator
        - MaE08: Difficulty with word problems
        - MaE09: Overgeneralization of rules
        - MaE10: Misunderstanding of exponents
        
        If you cannot identify a clear misconception, respond with null.
        '''
        
        if not processed_image:
            raise ValueError("Image data is missing or invalid")
            
        image_data = {'mime_type': 'image/jpeg', 'data': processed_image}
        
        response = model.generate_content([prompt, image_data])
        
        response_text = response.text
        
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                return {"error": "No misconception detected", "raw_response": response_text}
                
        except json.JSONDecodeError:
            return {"error": "Failed to parse response", "raw_response": response_text}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")

@router.post("/generate-exercise")
async def generate_exercise(misconception_id: str = Form(...), description: str = Form(...)):
    """
    Generate a practice exercise based on the detected misconception.
    
    Args:
        misconception_id: ID of the detected misconception
        description: Description of the misconception
        
    Returns:
        JSON response with generated exercise and image
    """
    try:
        exercise_data = generate_exercise_with_gemini(misconception_id, description)
        
        return exercise_data
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating exercise: {str(e)}")
