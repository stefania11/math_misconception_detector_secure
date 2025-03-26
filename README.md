# Math Misconception Detector

An interactive prototype for middle schoolers to help them learn algebra using multimodal AI.

## Features

- Interactive UI for capturing math problems
- AI-powered misconception detection using Gemini 2.5 Pro
- Detailed feedback and explanations for common algebra misconceptions
- Exercise suggestion based on detected misconceptions
- Image generation for practice problems using Imagen 3.0
- Download functionality for generated exercise images

## Project Structure

- `backend/` - FastAPI backend with Gemini 2.5 Pro and Imagen 3.0 integration
- `frontend/` - Frontend UI for the application
- `test_*.py` - Test scripts for verifying functionality

## Models Used

- **Text Analysis**: Gemini 2.5 Pro (gemini-2.5-pro-exp-03-25)
- **Image Generation**: Imagen 3.0 (imagen-3.0-generate-002)

## Setup

### Backend

1. Navigate to the `backend` directory
2. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
3. Install dependencies and run the server:
   ```
   pip install -r requirements.txt
   python -m app.main
   ```

### Frontend

The frontend is pre-built in the `frontend/dist` directory and can be served statically.

## Implementation Details

### Exercise Suggestion

After detecting a misconception, the application:
1. Analyzes the misconception type and description
2. Generates a tailored exercise to address the specific misconception
3. Creates a visual representation of the exercise using Imagen 3.0
4. Provides a step-by-step solution to help students understand the concept

### Image Generation

The application uses the Imagen 3.0 model for generating exercise images. If the model is unavailable, a fallback mechanism creates images using Python's Pillow library.

## Security

- API keys are stored in environment variables
- `.env` files are excluded from git
- Proper error handling for missing credentials

## Deployment

- Frontend: https://math-misconception-app-tjar7k5y.devinapps.com
- Backend API: https://math-misconception-api-secure.fly.dev

## Credits

Research by Nancy Otero, Stefania Druga, and Andrew Lan
