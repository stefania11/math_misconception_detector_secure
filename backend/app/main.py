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
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=api_key)

text_model_name = 'gemini-2.5-pro-exp-03-25'
image_model_name = 'imagen-3.0-generate-002'

# Create FastAPI app
app = FastAPI(
    title="Math Misconception Detector API",
    description="API for detecting math misconceptions using Gemini 2.5 Pro",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8000",
        "http://localhost:8080",
        "https://math-misconception-app.netlify.app",
        "https://math-misconception-app-n3mniwte.devinapps.com",
        "https://math-misconception-app-tjar7k5y.devinapps.com",
        "https://math-misconception-api-odyspgkn.fly.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Image utilities
def validate_image(image_base64):
    """Validate that the provided base64 string is a valid image."""
    try:
        image_data = base64.b64decode(image_base64)
        return True
    except Exception:
        return False

def resize_image_if_needed(image_base64, max_size=1024 * 1024):
    """Resize the image if it's too large."""
    try:
        image_data = base64.b64decode(image_base64)
        
        if len(image_data) <= max_size:
            return image_base64
        
        # For simplicity, we'll just return the original image
        # In a production app, we would resize the image here
        return image_base64
    except Exception:
        return image_base64

def process_image(image_base64):
    """Process an image for analysis."""
    if image_base64 and isinstance(image_base64, str) and image_base64.startswith('data:image'):
        image_base64 = image_base64.split(',')[1]
    
    if not validate_image(image_base64):
        raise ValueError("Invalid image format")
    
    return resize_image_if_needed(image_base64)

# API endpoints
@app.post("/api/analyze")
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
        
        model = genai.GenerativeModel(text_model_name)
        
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

def generate_exercise_image(prompt, width=800, height=600):
    """
    Generate an image for a math exercise.
    
    Args:
        prompt: Text description of the exercise
        width: Image width
        height: Image height
        
    Returns:
        str: Base64 encoded image data
    """
    try:
        text_model = genai.GenerativeModel(text_model_name)
        
        description_prompt = f'''
        Create a detailed description of a visual representation for the following math exercise for middle school students:
        
        {prompt}
        
        The description should include:
        - The mathematical notation and equations to include
        - Any diagrams or visual aids that would help explain the concept
        - How the elements should be arranged
        - What colors and visual elements would make it engaging for middle school students
        
        Keep the description clear and detailed so it could be used to create an actual image.
        '''
        
        description_response = text_model.generate_content(description_prompt)
        image_description = description_response.text
        
        try:
            image_model = genai.GenerativeModel(image_model_name)
            
            image_prompt = f'''
            Create a visual representation of the following math exercise for middle school students:
            
            {prompt}
            
            Based on this description:
            {image_description}
            
            The image should be clear, educational, and visually appealing.
            Include relevant mathematical notation, diagrams, or visual aids that help explain the concept.
            Make sure the text is readable and the overall design is engaging for middle school students.
            '''
            
            image_response = image_model.generate_content(image_prompt)
            
            if hasattr(image_response, 'candidates') and len(image_response.candidates) > 0:
                for candidate in image_response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                return f"data:image/png;base64,{part.inline_data.data}"
        except Exception as e:
            print(f"Imagen model not available, using fallback: {str(e)}")
        
        import io
        from PIL import Image, ImageDraw, ImageFont
        import base64
        import random
        import math
        
        img = Image.new('RGB', (width, height), color=(245, 245, 255))
        d = ImageDraw.Draw(img)
        
        header_height = 60
        d.rectangle([(0, 0), (width, header_height)], fill=(70, 130, 180))
        
        try:
            title_font = ImageFont.truetype("Arial", 24)
            font = ImageFont.truetype("Arial", 20)
            small_font = ImageFont.truetype("Arial", 16)
        except IOError:
            title_font = ImageFont.load_default()
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        title = "Math Exercise"
        title_width = d.textlength(title, font=title_font)
        d.text(((width - title_width) // 2, 15), title, fill=(255, 255, 255), font=title_font)
        
        lines = []
        words = prompt.split()
        if words:
            current_line = words[0]
            
            for word in words[1:]:
                test_line = current_line + " " + word
                text_width = d.textlength(test_line, font=font)
                
                if text_width < width - 60:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            
            lines.append(current_line)
        
        for i in range(10):
            x = random.randint(0, width)
            y = random.randint(header_height, height)
            size = random.randint(5, 15)
            color = (random.randint(200, 240), random.randint(200, 240), random.randint(200, 255))
            d.ellipse((x, y, x + size, y + size), fill=color)
        
        margin = 80
        graph_width = width - 2 * margin
        graph_height = 150
        graph_y = header_height + 50
        
        d.line([(margin, graph_y + graph_height // 2), (margin + graph_width, graph_y + graph_height // 2)], fill=(100, 100, 100), width=2)  # x-axis
        d.line([(margin + graph_width // 2, graph_y), (margin + graph_width // 2, graph_y + graph_height)], fill=(100, 100, 100), width=2)  # y-axis
        
        for i in range(5):
            x = margin + i * graph_width // 4
            d.line([(x, graph_y), (x, graph_y + graph_height)], fill=(200, 200, 200), width=1)
            
            y = graph_y + i * graph_height // 4
            d.line([(margin, y), (margin + graph_width, y)], fill=(200, 200, 200), width=1)
        
        points = []
        for i in range(graph_width):
            x = margin + i
            scaled_x = (i / graph_width - 0.5) * 4
            scaled_y = scaled_x * scaled_x
            y = graph_y + graph_height // 2 - scaled_y * 30
            points.append((x, y))
        
        for i in range(1, len(points)):
            d.line([points[i-1], points[i]], fill=(255, 0, 0), width=2)
        
        y_position = graph_y + graph_height + 30
        for line in lines:
            d.text((30, y_position), line, fill=(0, 0, 0), font=font)
            y_position += 30
        
        footer_y = height - 40
        d.text((20, footer_y), "Math Misconception Detector", fill=(100, 100, 100), font=small_font)
        d.text((width - 150, footer_y), "Practice Exercise", fill=(100, 100, 100), font=small_font)
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Error generating exercise image: {str(e)}")
        placeholder_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        return f"data:image/png;base64,{placeholder_image}"

def generate_exercise_with_gemini(misconception_id, description):
    """
    Generate a practice exercise based on the detected misconception.
    
    Args:
        misconception_id: ID of the detected misconception
        description: Description of the misconception
        
    Returns:
        dict: Exercise data with text, solution, and image
    """
    try:
        # Get the model
        model = genai.GenerativeModel(text_model_name)
        
        # Create prompt for exercise generation
        prompt = f'''
        Generate a practice exercise to help a middle school student overcome the following algebra misconception:
        
        Misconception ID: {misconception_id}
        Description: {description}
        
        The exercise should be appropriate for middle school students and directly address the misconception.
        Include a step-by-step solution that explains the concept clearly.
        
        Format your response as:
        
        EXERCISE: [text description of the exercise]
        
        SOLUTION: [step-by-step solution to the exercise]
        '''
        
        # Generate content
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Parse the response
        exercise_text = ""
        solution_text = ""
        
        # Extract exercise and solution from response
        if "EXERCISE:" in response_text and "SOLUTION:" in response_text:
            parts = response_text.split("SOLUTION:")
            exercise_part = parts[0]
            solution_part = parts[1]
            
            exercise_text = exercise_part.replace("EXERCISE:", "").strip()
            solution_text = solution_part.strip()
        else:
            # Fallback if format is not as expected
            exercise_text = "Practice solving this problem related to " + description
            solution_text = "Solution not available."
        
        # Generate image for the exercise
        image_data = generate_exercise_image(exercise_text)
        
        return {
            "exercise_text": exercise_text,
            "solution": solution_text,
            "image_data": image_data
        }
        
    except Exception as e:
        print(f"Error generating exercise with Gemini: {str(e)}")
        return {
            "exercise_text": "Practice solving problems related to " + description,
            "solution": "Solution not available due to an error.",
            "image_data": None
        }

@app.post("/api/generate-exercise")
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
        # Use the dedicated function to create an exercise with image
        exercise_data = generate_exercise_with_gemini(misconception_id, description)
        
        # Return the exercise data
        return exercise_data
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating exercise: {str(e)}")

@app.get("/")
async def health_check():
    return {"status": "ok", "model": text_model_name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
