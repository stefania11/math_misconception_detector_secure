"""
Image generation utilities for math exercises using Gemini 2.5 Pro.
"""
import google.generativeai as genai
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

model_name = 'gemini-2.5-pro-exp-03-25'

def generate_exercise_image(prompt, width=800, height=600):
    """
    Generate an image for a math exercise using Gemini 2.5 Pro.
    
    Since Gemini doesn't directly generate images, we'll create a simple
    image with the exercise text rendered on it.
    
    Args:
        prompt: Text description of the exercise
        width: Image width
        height: Image height
        
    Returns:
        str: Base64 encoded image data
    """
    try:
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        try:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            title_font = ImageFont.truetype(font_path, 32)
            body_font = ImageFont.truetype(font_path, 24)
        except IOError:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        
        draw.rectangle([(10, 10), (width-10, height-10)], outline=(70, 130, 180), width=4)
        
        title = "Math Exercise"
        draw.text((width//2, 50), title, font=title_font, fill=(70, 130, 180), anchor="mm")
        
        wrapper = textwrap.TextWrapper(width=40)
        wrapped_text = wrapper.fill(prompt)
        
        lines = wrapped_text.split('\n')
        y_position = 120
        
        for line in lines:
            draw.text((width//2, y_position), line, font=body_font, fill=(0, 0, 0), anchor="mm")
            y_position += 40
        
        symbols = ["∑", "π", "√", "∫"]
        positions = [(40, 40), (width-40, 40), (40, height-40), (width-40, height-40)]
        
        for symbol, pos in zip(symbols, positions):
            draw.text(pos, symbol, font=title_font, fill=(200, 200, 200), anchor="mm")
        
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"Error generating exercise image: {str(e)}")
        return None

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
        model = genai.GenerativeModel(model_name)
        
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
        
        response = model.generate_content(prompt)
        response_text = response.text
        
        exercise_text = ""
        solution_text = ""
        
        if "EXERCISE:" in response_text and "SOLUTION:" in response_text:
            parts = response_text.split("SOLUTION:")
            exercise_part = parts[0]
            solution_part = parts[1]
            
            exercise_text = exercise_part.replace("EXERCISE:", "").strip()
            solution_text = solution_part.strip()
        else:
            exercise_text = "Practice solving this problem related to " + description
            solution_text = "Solution not available."
        
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
