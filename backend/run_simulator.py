#!/usr/bin/env python3
"""
IntelliBin Simulator Launcher

Run this script to start the IntelliBin desktop simulator.
"""

import sys
from pathlib import Path

# Add the backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    print("=" * 60)
    print("  🧪 IntelliBin Simulator")
    print("  Laboratory Waste Routing System")
    print("=" * 60)
    print()
    print("Starting desktop application...")
    print()
    
    try:
        from simulator.app import main as run_app
        run_app()
    except ImportError as e:
        print(f"Error: {e}")
        print()
        print("Please install dependencies first:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting simulator: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
