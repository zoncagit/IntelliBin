#!/usr/bin/env python3
"""
Run the IntelliBin Detection API
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("  INTELLIBIN Detection API")
    print("  YOLOv8-based Waste Classification")
    print("=" * 50)
    print()
    print("Starting server at http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
