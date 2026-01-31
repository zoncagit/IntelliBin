# IntelliBin Detection API v2.0

Waste-specific image classification API using a Hugging Face model trained on recyclable materials.

## Model

**`yangy50/garbage-classification`** - A ResNet model trained on TrashNet dataset for classifying waste materials.

### Why This Model?

Unlike YOLOv8 (trained on generic objects like "bottle", "vase", "cup"), this model is specifically trained to recognize **material properties**:
- Texture patterns (crinkled paper vs smooth plastic)
- Transparency (glass vs opaque materials)
- Surface characteristics (metallic sheen, cardboard grain)

## Material Categories

The API classifies images into **5 categories**:

| Category | Model Labels | Examples |
|----------|--------------|----------|
| **Paper** | cardboard, paper | Boxes, newspapers, notebooks |
| **Plastic** | plastic | Bottles, containers, bags |
| **Glass** | glass | Jars, bottles, vases |
| **Metal** | metal | Cans, foil, utensils |
| **Other** | trash, organic | Mixed waste, food scraps |

## Quick Start

### 1. Install Dependencies

```bash
cd safebin_site/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the API

```bash
python run.py
```

The API will start at `http://localhost:8000`

First request may take ~5-10 seconds to download and load the model.

### 3. API Documentation

Open `http://localhost:8000/docs` for interactive Swagger documentation.

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "online",
  "model_loaded": true,
  "model_type": "waste-classifier"
}
```

### Classify Material

```
POST /detect
Content-Type: multipart/form-data

image: <file>
```

Response:
```json
{
  "material": "plastic",
  "confidence": 0.91,
  "detected_object": "plastic"
}
```

## Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Classify material from image
curl -X POST http://localhost:8000/detect \
  -F "image=@test_image.jpg"
```

## Performance

- **Model**: ResNet (garbage-classification)
- **First request**: ~5-10s (model download + loading)
- **Subsequent requests**: ~100-300ms on CPU
- **Accuracy**: Significantly better for recyclables than generic object detection

## Comparison: Before vs After

| Aspect | YOLOv8n (Before) | Waste Classifier (After) |
|--------|------------------|--------------------------|
| Training | Generic objects (COCO) | Recyclable materials (TrashNet) |
| Output | "bottle", "vase", "cup" | "plastic", "glass", "cardboard" |
| Water bottle | Often misclassified as "vase" | Correctly classified as "plastic" |
| Mapping | Required complex mapping logic | Direct material classification |
