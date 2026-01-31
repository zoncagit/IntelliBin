"""
IntelliBin Detection API
Waste-specific image classification for recyclable materials
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import io
import time

# Lazy load heavy imports
_classifier = None
_processor = None


# ============================================
# WASTE CLASSIFICATION MODEL
# ============================================

# Model trained on TrashNet/garbage dataset
# Classes: cardboard, glass, metal, paper, plastic, trash
MODEL_ID = "yangy50/garbage-classification"

# Map model output labels to our 5 categories
LABEL_TO_MATERIAL = {
    "cardboard": "paper",
    "paper": "paper",
    "glass": "glass",
    "metal": "metal",
    "plastic": "plastic",
    "trash": "other",
    "organic": "other",
    "battery": "other",
    "shoes": "other",
    "clothes": "other",
}


def get_classifier():
    """Load the waste classification model (lazy loading)"""
    global _classifier, _processor
    
    if _classifier is None:
        print("[API] Loading waste classification model...")
        start = time.time()
        
        from transformers import AutoImageProcessor, AutoModelForImageClassification
        import torch
        
        # Load model and processor
        _processor = AutoImageProcessor.from_pretrained(MODEL_ID)
        _classifier = AutoModelForImageClassification.from_pretrained(MODEL_ID)
        
        # Set to eval mode
        _classifier.eval()
        
        load_time = time.time() - start
        print(f"[API] Model loaded in {load_time:.1f}s")
        print(f"[API] Labels: {_classifier.config.id2label}")
    
    return _classifier, _processor


def classify_waste(image) -> tuple[str, float, str]:
    """
    Classify an image into waste material categories.
    
    Returns: (material, confidence, raw_label)
    """
    import torch
    from PIL import Image
    
    model, processor = get_classifier()
    
    # Preprocess image
    inputs = processor(images=image, return_tensors="pt")
    
    # Run inference
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        
    # Get prediction
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
    confidence, predicted_idx = torch.max(probabilities, dim=-1)
    
    # Get label from model config
    raw_label = model.config.id2label[predicted_idx.item()]
    confidence_value = confidence.item()
    
    # Map to our material categories
    material = LABEL_TO_MATERIAL.get(raw_label.lower(), "other")
    
    return material, confidence_value, raw_label


# ============================================
# API MODELS
# ============================================

class DetectionResponse(BaseModel):
    """Response from the /detect endpoint"""
    material: str  # paper, plastic, glass, metal, other
    confidence: float  # 0.0 to 1.0
    detected_object: Optional[str] = None  # Raw model prediction


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_type: str = "waste-classifier"


# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="IntelliBin Detection API",
    description="Waste-specific image classification for recyclable materials",
    version="2.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and model status"""
    global _classifier
    return HealthResponse(
        status="online",
        model_loaded=_classifier is not None,
        model_type="waste-classifier"
    )


@app.post("/detect", response_model=DetectionResponse)
async def detect_material(image: UploadFile = File(...)):
    """
    Classify waste material in image.
    
    Accepts: Single image file (JPEG, PNG)
    Returns: Material category and confidence score
    
    Material categories:
    - paper (includes cardboard)
    - plastic
    - glass
    - metal
    - other (trash, unrecognized items)
    """
    start_time = time.time()
    
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image data
        image_data = await image.read()
        
        # Open image
        from PIL import Image
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary (handles PNG with alpha, etc.)
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Classify
        material, confidence, raw_label = classify_waste(img)
        
        inference_time = time.time() - start_time
        print(f"[API] Classification: {raw_label} -> {material} ({confidence*100:.1f}%) in {inference_time*1000:.0f}ms")
        
        # If confidence is too low, return "other"
        if confidence < 0.3:
            material = "other"
        
        return DetectionResponse(
            material=material,
            confidence=round(confidence, 2),
            detected_object=raw_label
        )
        
    except Exception as e:
        print(f"[API] Error during classification: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Pre-load model on startup for faster first request"""
    print("[API] IntelliBin Detection API v2.0 starting...")
    print("[API] Using waste-specific classification model")
    # Optionally pre-load model (comment out for faster startup)
    # get_classifier()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
