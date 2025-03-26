import os
import requests
import json
import base64
from PIL import Image
import io
import time

def test_exercise_generation():
    print("Testing exercise generation endpoint...")
    
    url = "http://localhost:8000/api/generate-exercise"
    
    test_data = {
        "misconception_id": "MaE03",
        "description": "Confusion with negative numbers in equations"
    }
    
    try:
        response = requests.post(url, data=test_data)
        
        if response.status_code == 200:
            print(f"Request successful: Status code {response.status_code}")
            
            result = response.json()
            
            print("\nExercise Text:")
            print(result.get("exercise_text", "No exercise text found"))
            
            print("\nSolution:")
            print(result.get("solution", "No solution found"))
            
            image_data = result.get("image_data")
            if image_data:
                print("\nImage data found!")
                
                if image_data.startswith("data:image"):
                    image_base64 = image_data.split(",")[1]
                    
                    image_bytes = base64.b64decode(image_base64)
                    
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    timestamp = int(time.time())
                    filename = f"test_exercise_image_{timestamp}.png"
                    image.save(filename)
                    print(f"Image saved to {filename}")
                else:
                    print("Image data is not in expected format")
            else:
                print("No image data found in response")
                
            return True
        else:
            print(f"Request failed: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing exercise generation: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_exercise_generation()
    print(f"\nExercise generation test {'succeeded' if success else 'failed'}")
