import base64
import io
from PIL import Image
import re

def validate_image(image_base64):
    """
    Validate that the provided base64 string is a valid image.
    
    Args:
        image_base64: Base64 encoded image data
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        image_data = base64.b64decode(image_base64)
        
        Image.open(io.BytesIO(image_data))
        
        return True
    except Exception:
        return False

def resize_image_if_needed(image_base64, max_size=1024 * 1024):
    """
    Resize the image if it's too large.
    
    Args:
        image_base64: Base64 encoded image data
        max_size: Maximum size in bytes
        
    Returns:
        str: Base64 encoded resized image data
    """
    try:
        image_data = base64.b64decode(image_base64)
        
        if len(image_data) <= max_size:
            return image_base64
        
        image = Image.open(io.BytesIO(image_data))
        
        width, height = image.size
        ratio = (max_size / len(image_data)) ** 0.5
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        resized_image.save(buffer, format=image.format or 'JPEG')
        resized_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return resized_base64
    except Exception:
        return image_base64

def process_image(image_base64):
    """
    Process an image for analysis.
    
    Args:
        image_base64: Base64 encoded image data
        
    Returns:
        str: Processed base64 encoded image data
    """
    if image_base64 and isinstance(image_base64, str) and image_base64.startswith('data:image'):
        image_base64 = image_base64.split(',')[1]
    
    if not validate_image(image_base64):
        raise ValueError("Invalid image format")
    
    return resize_image_if_needed(image_base64)
