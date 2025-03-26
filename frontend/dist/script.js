const camera = document.getElementById('camera');
const cameraCanvas = document.getElementById('camera-canvas');
const captureBtn = document.getElementById('capture-btn');
const switchCameraBtn = document.getElementById('switch-camera-btn');
const previewContainer = document.getElementById('preview-container');
const previewImage = document.getElementById('preview-image');
const analyzeBtn = document.getElementById('analyze-btn');
const retakeBtn = document.getElementById('retake-btn');
const processingIndicator = document.getElementById('processing-indicator');
const fileInput = document.getElementById('file-input');
const resultSection = document.getElementById('result-section');
const exerciseSection = document.getElementById('exercise-section');
const showSolutionBtn = document.getElementById('show-solution-btn');
const solutionContent = document.getElementById('solution-content');

const API_URL = "https://math-misconception-api-secure.fly.dev";
const ANALYZE_ENDPOINT = `${API_URL}/api/analyze`;
const EXERCISE_ENDPOINT = `${API_URL}/api/generate-exercise`;

let stream = null;
let facingMode = 'environment'; // Start with back camera
let compressedImage = null;

function init() {
  if (resultSection) {
    resultSection.style.display = 'none';
  }
  
  if (exerciseSection) {
    exerciseSection.style.display = 'none';
  }
  
  startCamera();
  
  if (captureBtn) {
    captureBtn.addEventListener('click', captureImage);
  }
  
  if (switchCameraBtn) {
    switchCameraBtn.addEventListener('click', switchCamera);
  }
  
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', analyzeImage);
  }
  
  if (retakeBtn) {
    retakeBtn.addEventListener('click', resetCamera);
  }
  
  if (fileInput) {
    fileInput.addEventListener('change', handleFileUpload);
  }
  
  if (showSolutionBtn) {
    showSolutionBtn.addEventListener('click', toggleSolution);
  }
}

async function startCamera() {
  try {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
    
    stream = await navigator.mediaDevices.getUserMedia({
      video: { 
        facingMode: facingMode,
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: false
    });
    
    camera.srcObject = stream;
    
    camera.style.display = 'block';
    if (previewContainer) {
      previewContainer.style.display = 'none';
    }
    
  } catch (error) {
    console.error('Error accessing camera:', error);
    alert('Could not access the camera. Please make sure you have granted camera permissions.');
  }
}

function switchCamera() {
  facingMode = facingMode === 'user' ? 'environment' : 'user';
  startCamera();
}

function captureImage() {
  const context = cameraCanvas.getContext('2d');
  
  cameraCanvas.width = camera.videoWidth;
  cameraCanvas.height = camera.videoHeight;
  
  context.drawImage(camera, 0, 0, cameraCanvas.width, cameraCanvas.height);
  
  const imageData = cameraCanvas.toDataURL('image/jpeg', 0.9);
  
  previewImage.src = imageData;
  camera.style.display = 'none';
  previewContainer.style.display = 'block';
  
  compressedImage = imageData;
}

function handleFileUpload(event) {
  const file = event.target.files[0];
  
  if (file) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
      previewImage.src = e.target.result;
      camera.style.display = 'none';
      previewContainer.style.display = 'block';
      
      compressImagePromise(e.target.result)
        .then(compressed => {
          compressedImage = compressed;
        })
        .catch(error => {
          console.error('Error compressing image:', error);
          compressedImage = e.target.result; // Use original if compression fails
        });
    };
    
    reader.readAsDataURL(file);
  }
}

function compressImagePromise(dataUrl) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = function() {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      let width = img.width;
      let height = img.height;
      const maxDimension = 800;
      
      if (width > height && width > maxDimension) {
        height = Math.round((height * maxDimension) / width);
        width = maxDimension;
      } else if (height > maxDimension) {
        width = Math.round((width * maxDimension) / height);
        height = maxDimension;
      }
      
      canvas.width = width;
      canvas.height = height;
      
      ctx.drawImage(img, 0, 0, width, height);
      
      const compressedDataUrl = canvas.toDataURL('image/jpeg', 0.7);
      
      const originalSize = Math.round(dataUrl.length / 1024);
      const compressedSize = Math.round(compressedDataUrl.length / 1024);
      const reduction = Math.round(((originalSize - compressedSize) / originalSize) * 100);
      console.log(`Image compressed from ${originalSize}KB to ${compressedSize}KB (${reduction}% reduction)`);
      
      resolve(compressedDataUrl);
    };
    
    img.onerror = function() {
      reject(new Error('Failed to load image for compression'));
    };
    
    img.src = dataUrl;
  });
}

async function analyzeImage() {
  try {
    if (processingIndicator) {
      processingIndicator.style.display = 'flex';
    }
    
    if (previewContainer) {
      previewContainer.style.display = 'none';
    }
    
    if (!compressedImage) {
      throw new Error('No image to analyze');
    }
    
    let imageData;
    if (compressedImage.includes('base64,')) {
      imageData = compressedImage.split('base64,')[1];
      console.log('Base64 data extracted from data URL');
    } else {
      imageData = compressedImage;
      console.log('Using compressed image directly');
    }
    
    const formData = new FormData();
    formData.append('image_base64', imageData);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
    
    console.log('Sending request to API with image data');
    
    const response = await fetch(ANALYZE_ENDPOINT, {
      method: 'POST',
      body: formData,
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`Error analyzing image: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (processingIndicator) {
      processingIndicator.style.display = 'none';
    }
    
    displayMisconception(result);
    
    if (result && result.id) {
      generateExercise(result.id, result.description);
    }
    
  } catch (error) {
    console.error('Error processing image:', error);
    
    if (processingIndicator) {
      processingIndicator.style.display = 'none';
    }
    
    alert(`Error analyzing image: ${error.message}`);
    
    resetCamera();
  }
}

function displayMisconception(misconception) {
  if (!misconception) return;
  
  if (resultSection) {
    resultSection.style.display = 'block';
  }
  
  const misconceptionId = document.getElementById('misconception-id');
  const misconceptionDescription = document.getElementById('misconception-description');
  const misconceptionExplanation = document.getElementById('misconception-explanation');
  const misconceptionFeedback = document.getElementById('misconception-feedback');
  
  if (misconceptionId) {
    misconceptionId.textContent = misconception.id || 'Unknown';
  }
  
  if (misconceptionDescription) {
    misconceptionDescription.textContent = misconception.description || 'No description available';
  }
  
  if (misconceptionExplanation) {
    const explanation = misconception.example ? 
      `This is a common misconception where students ${misconception.example.toLowerCase()}. Understanding this concept is important for mastering algebra.` :
      'This is a common misconception in algebra. Understanding the underlying concepts is important for mastering algebra.';
    
    misconceptionExplanation.textContent = explanation;
  }
  
  if (misconceptionFeedback) {
    misconceptionFeedback.textContent = misconception.feedback || 'No feedback available';
  }
}

async function generateExercise(misconceptionId, description) {
  try {
    const formData = new FormData();
    formData.append('misconception_id', misconceptionId);
    formData.append('description', description);
    
    const response = await fetch(EXERCISE_ENDPOINT, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`Error generating exercise: ${response.status}`);
    }
    
    const result = await response.json();
    
    displayExercise(result);
    
  } catch (error) {
    console.error('Error generating exercise:', error);
    
    if (exerciseSection) {
      exerciseSection.style.display = 'none';
    }
  }
}

function displayExercise(exercise) {
  if (!exercise) return;
  
  if (exerciseSection) {
    exerciseSection.style.display = 'block';
  }
  
  const exerciseText = document.getElementById('exercise-text');
  const exerciseImage = document.getElementById('exercise-image');
  const exerciseSolution = document.getElementById('exercise-solution');
  const exerciseImageContainer = document.getElementById('exercise-image-container');
  const downloadBtn = document.getElementById('download-exercise-image');
  
  if (exerciseText) {
    exerciseText.textContent = exercise.exercise_text || 'Try this practice exercise to reinforce the concept.';
  }
  
  if (exerciseImage) {
    if (exercise.image_data) {
      exerciseImage.src = exercise.image_data;
      
      if (downloadBtn) {
        downloadBtn.style.display = 'block';
        
        const newDownloadBtn = downloadBtn.cloneNode(true);
        if (downloadBtn.parentNode) {
          downloadBtn.parentNode.replaceChild(newDownloadBtn, downloadBtn);
        }
        
        newDownloadBtn.addEventListener('click', function() {
          const link = document.createElement('a');
          link.href = exercise.image_data;
          link.download = `math-exercise-${Date.now()}.png`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        });
      }
    } else {
      exerciseImage.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZAAAADICAYAAADGFbfiAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAB3RJTUUH4wIJBywfp3IOswAAACZJREFUeNrtwTEBAAAAwqD1T20ND6AAAAAAAAAAAAAAAAAAAID3AEbQAAFc0JXoAAAAAElFTkSuQmCC';
      
      if (downloadBtn) {
        downloadBtn.style.display = 'none';
      }
    }
    exerciseImage.alt = 'Practice exercise for ' + exercise.exercise_text;
  }
  
  if (exerciseSolution) {
    exerciseSolution.textContent = exercise.solution || 'Solution not available.';
  }
  
  if (solutionContent) {
    solutionContent.style.display = 'none';
  }
}

function toggleSolution() {
  if (solutionContent) {
    if (solutionContent.style.display === 'none') {
      solutionContent.style.display = 'block';
      showSolutionBtn.textContent = 'Hide Solution';
    } else {
      solutionContent.style.display = 'none';
      showSolutionBtn.textContent = 'Show Solution';
    }
  }
}

function resetCamera() {
  if (previewContainer) {
    previewContainer.style.display = 'none';
  }
  
  if (processingIndicator) {
    processingIndicator.style.display = 'none';
  }
  
  if (fileInput) {
    fileInput.value = '';
  }
  
  if (camera) {
    camera.style.display = 'block';
  }
  
  compressedImage = null;
}

document.addEventListener('DOMContentLoaded', init);
