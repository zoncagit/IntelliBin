# IntelliBin Backend Development Plan

> **24-Hour Python Backend Simulation**  
> A step-by-step guide to building the IntelliBin backend without hardware or database dependencies.

---

## Overview

| Aspect | Decision |
|--------|----------|
| **Language** | Python 3.11+ |
| **Framework** | FastAPI |
| **Database** | In-memory (dict) + optional JSON file persistence |
| **Hardware** | None (full simulation) |
| **Frontend** | Not included (API-only) |
| **Timeline** | 24 hours |

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── substance.py        # Substance data models
│   │   ├── container.py        # Container data models
│   │   └── responses.py        # API response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── classification.py   # Substance classification
│   │   ├── routing.py          # Container routing logic
│   │   ├── compatibility.py    # Compatibility checking
│   │   └── state.py            # In-memory state management
│   ├── data/
│   │   ├── substances.json     # Substance knowledge base
│   │   ├── containers.json     # Initial container state
│   │   └── rules.json          # Incompatibility rules
│   └── routers/
│       ├── __init__.py
│       ├── route.py            # /route endpoint
│       ├── dispose.py          # /dispose endpoint
│       ├── containers.py       # /containers endpoints
│       └── simulation.py       # /simulate endpoints
├── tests/
│   ├── __init__.py
│   ├── test_classification.py
│   ├── test_routing.py
│   └── test_api.py
├── requirements.txt
└── run.py                      # Simple run script
```

---

## Hour-by-Hour Development Plan

### Phase 1: Setup & Foundation (Hours 0-4)

---

#### Hour 0-1: Project Setup

**Tasks:**
1. Create project directory structure
2. Set up virtual environment
3. Install dependencies
4. Create basic FastAPI app

**Commands:**
```bash
# Create project
mkdir -p backend/app/{models,services,data,routers}
mkdir -p backend/tests
cd backend

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic python-dotenv

# Create requirements.txt
pip freeze > requirements.txt
```

**File: `requirements.txt`**
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
python-dotenv==1.0.0
```

**File: `app/__init__.py`**
```python
# Empty file to make app a package
```

**File: `app/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="IntelliBin API",
    description="Laboratory Waste Routing & Safety System",
    version="1.0.0"
)

# CORS for future frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "IntelliBin API is running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**File: `run.py`**
```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

**Verify:**
```bash
python run.py
# Visit http://localhost:8000 - should see welcome message
# Visit http://localhost:8000/docs - should see Swagger UI
```

---

#### Hour 1-2: Data Models (Pydantic)

**File: `app/models/__init__.py`**
```python
from .substance import SubstanceProfile, ChemicalCategory
from .container import WasteContainer, ContainerContent, WasteStream
from .responses import RouteRequest, RouteResponse, DisposalResponse
```

**File: `app/models/substance.py`**
```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ChemicalCategory(str, Enum):
    ACID = "Acid"
    BASE = "Base"
    METAL = "Metal"
    ORGANIC = "Organic"
    OXIDIZER = "Oxidizer"
    HALOGEN = "Halogen"
    SOLVENT = "Solvent"
    WATER_REACTIVE = "Water-Reactive"
    HEAVY_METAL = "Heavy-Metal"
    UNKNOWN = "Unknown"

class SubstanceProperties(BaseModel):
    ph_range: tuple[float, float] = (7.0, 7.0)
    flammable: bool = False
    oxidizer: bool = False
    water_reactive: bool = False
    toxicity: str = "Low"  # Low, Medium, High
    flash_point_c: Optional[float] = None

class SubstanceProfile(BaseModel):
    id: str
    name: str
    aliases: list[str] = []
    category: ChemicalCategory
    default_waste_stream: str
    properties: SubstanceProperties
    incompatible_with: list[ChemicalCategory] = []
```

**File: `app/models/container.py`**
```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class WasteStream(str, Enum):
    AQUEOUS_ACID = "AqueousAcid"
    AQUEOUS_BASE = "AqueousBase"
    HALOGENATED_SOLVENT = "HalogenatedSolvent"
    NON_HALOGENATED_SOLVENT = "NonHalogenatedSolvent"
    OXIDIZER = "Oxidizer"
    REACTIVE_METAL = "ReactiveMetal"
    HEAVY_METAL = "HeavyMetal"
    FLAMMABLE = "Flammable"
    CORROSIVE = "Corrosive"
    GENERAL = "GeneralChemical"

class ContainerStatus(str, Enum):
    ACTIVE = "Active"
    FULL = "Full"
    AWAITING_PICKUP = "AwaitingPickup"
    EMPTY = "Empty"

class ContainerContent(BaseModel):
    substance: str
    category: str
    quantity_ml: float
    concentration: str
    added_at: str  # ISO format datetime string

class WasteContainer(BaseModel):
    container_id: str
    waste_stream: WasteStream
    location: str
    capacity_ml: float
    current_fill_ml: float
    contents: list[ContainerContent] = []
    accumulation_start: Optional[str] = None
    pickup_deadline: Optional[str] = None
    status: ContainerStatus = ContainerStatus.EMPTY
```

**File: `app/models/responses.py`**
```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class RiskLevel(str, Enum):
    SAFE = "Safe"
    CAUTION = "Caution"
    DANGER = "Danger"

class RouteRequest(BaseModel):
    substance: str
    quantity_ml: float
    concentration: str = "Pure"

class RoutedContainer(BaseModel):
    container_id: str
    location: str
    current_fill_percent: float
    after_fill_percent: float
    days_until_deadline: Optional[int] = None

class ClassificationResult(BaseModel):
    category: str
    waste_stream: str

class RouteResponse(BaseModel):
    success: bool
    substance: str
    classified_as: ClassificationResult
    routed_to: Optional[RoutedContainer] = None
    safety_status: RiskLevel
    message: str
    warnings: list[str] = []

class DisposalResponse(BaseModel):
    success: bool
    container_id: str
    new_fill_ml: float
    fill_percent: float
    logged_at: str
```

---

#### Hour 2-3: Knowledge Base (JSON Data Files)

**File: `app/data/substances.json`**
```json
{
  "substances": [
    {
      "id": "hcl-dilute",
      "name": "Hydrochloric Acid (dilute)",
      "aliases": ["HCl dilute", "Dilute HCl", "10% HCl", "Dilute Hydrochloric"],
      "category": "Acid",
      "default_waste_stream": "AqueousAcid",
      "properties": {
        "ph_range": [2, 4],
        "flammable": false,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "Medium"
      },
      "incompatible_with": ["Metal", "Base", "Oxidizer", "Water-Reactive"]
    },
    {
      "id": "hcl-conc",
      "name": "Hydrochloric Acid (concentrated)",
      "aliases": ["HCl", "Conc HCl", "37% HCl", "Muriatic Acid", "Concentrated HCl"],
      "category": "Acid",
      "default_waste_stream": "Corrosive",
      "properties": {
        "ph_range": [0, 1],
        "flammable": false,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "High"
      },
      "incompatible_with": ["Metal", "Base", "Oxidizer", "Water-Reactive"]
    },
    {
      "id": "sulfuric-dilute",
      "name": "Sulfuric Acid (dilute)",
      "aliases": ["H2SO4 dilute", "Dilute Sulfuric", "10% Sulfuric"],
      "category": "Acid",
      "default_waste_stream": "AqueousAcid",
      "properties": {
        "ph_range": [1, 3],
        "flammable": false,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "Medium"
      },
      "incompatible_with": ["Metal", "Base", "Oxidizer", "Water-Reactive"]
    },
    {
      "id": "naoh",
      "name": "Sodium Hydroxide",
      "aliases": ["NaOH", "Caustic Soda", "Lye", "Sodium Hydroxide Solution"],
      "category": "Base",
      "default_waste_stream": "AqueousBase",
      "properties": {
        "ph_range": [12, 14],
        "flammable": false,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "Medium"
      },
      "incompatible_with": ["Acid", "Metal"]
    },
    {
      "id": "sodium-metal",
      "name": "Sodium Metal",
      "aliases": ["Na", "Sodium", "Metallic Sodium", "Sodium Metal Pieces"],
      "category": "Metal",
      "default_waste_stream": "ReactiveMetal",
      "properties": {
        "ph_range": [7, 7],
        "flammable": true,
        "oxidizer": false,
        "water_reactive": true,
        "toxicity": "Medium"
      },
      "incompatible_with": ["Acid", "Base", "Water-Reactive", "Halogen"]
    },
    {
      "id": "potassium-metal",
      "name": "Potassium Metal",
      "aliases": ["K", "Potassium", "Metallic Potassium"],
      "category": "Metal",
      "default_waste_stream": "ReactiveMetal",
      "properties": {
        "ph_range": [7, 7],
        "flammable": true,
        "oxidizer": false,
        "water_reactive": true,
        "toxicity": "Medium"
      },
      "incompatible_with": ["Acid", "Base", "Water-Reactive", "Halogen"]
    },
    {
      "id": "acetone",
      "name": "Acetone",
      "aliases": ["Propanone", "Dimethyl Ketone", "2-Propanone"],
      "category": "Solvent",
      "default_waste_stream": "NonHalogenatedSolvent",
      "properties": {
        "ph_range": [7, 7],
        "flammable": true,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "Low",
        "flash_point_c": -20
      },
      "incompatible_with": ["Oxidizer"]
    },
    {
      "id": "ethanol",
      "name": "Ethanol",
      "aliases": ["Ethyl Alcohol", "EtOH", "Alcohol", "95% Ethanol"],
      "category": "Solvent",
      "default_waste_stream": "NonHalogenatedSolvent",
      "properties": {
        "ph_range": [7, 7],
        "flammable": true,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "Low",
        "flash_point_c": 13
      },
      "incompatible_with": ["Oxidizer"]
    },
    {
      "id": "methanol",
      "name": "Methanol",
      "aliases": ["Methyl Alcohol", "MeOH", "Wood Alcohol"],
      "category": "Solvent",
      "default_waste_stream": "NonHalogenatedSolvent",
      "properties": {
        "ph_range": [7, 7],
        "flammable": true,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "High",
        "flash_point_c": 11
      },
      "incompatible_with": ["Oxidizer"]
    },
    {
      "id": "chloroform",
      "name": "Chloroform",
      "aliases": ["CHCl3", "Trichloromethane"],
      "category": "Solvent",
      "default_waste_stream": "HalogenatedSolvent",
      "properties": {
        "ph_range": [7, 7],
        "flammable": false,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "High"
      },
      "incompatible_with": ["Oxidizer", "Metal"]
    },
    {
      "id": "dcm",
      "name": "Dichloromethane",
      "aliases": ["DCM", "Methylene Chloride", "CH2Cl2"],
      "category": "Solvent",
      "default_waste_stream": "HalogenatedSolvent",
      "properties": {
        "ph_range": [7, 7],
        "flammable": false,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "Medium"
      },
      "incompatible_with": ["Oxidizer", "Metal"]
    },
    {
      "id": "h2o2-30",
      "name": "Hydrogen Peroxide (30%)",
      "aliases": ["H2O2", "Peroxide", "30% Peroxide", "Hydrogen Peroxide"],
      "category": "Oxidizer",
      "default_waste_stream": "Oxidizer",
      "properties": {
        "ph_range": [4, 5],
        "flammable": false,
        "oxidizer": true,
        "water_reactive": false,
        "toxicity": "Medium"
      },
      "incompatible_with": ["Organic", "Solvent", "Metal"]
    },
    {
      "id": "kmno4",
      "name": "Potassium Permanganate",
      "aliases": ["KMnO4", "Permanganate"],
      "category": "Oxidizer",
      "default_waste_stream": "Oxidizer",
      "properties": {
        "ph_range": [7, 8],
        "flammable": false,
        "oxidizer": true,
        "water_reactive": false,
        "toxicity": "Medium"
      },
      "incompatible_with": ["Organic", "Solvent", "Metal"]
    },
    {
      "id": "mercury-solution",
      "name": "Mercury Solution",
      "aliases": ["Hg", "Mercury", "Mercuric"],
      "category": "Heavy-Metal",
      "default_waste_stream": "HeavyMetal",
      "properties": {
        "ph_range": [5, 7],
        "flammable": false,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "High"
      },
      "incompatible_with": []
    },
    {
      "id": "lead-solution",
      "name": "Lead Solution",
      "aliases": ["Pb", "Lead", "Lead Nitrate Solution"],
      "category": "Heavy-Metal",
      "default_waste_stream": "HeavyMetal",
      "properties": {
        "ph_range": [5, 7],
        "flammable": false,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "High"
      },
      "incompatible_with": []
    }
  ]
}
```

**File: `app/data/containers.json`**
```json
{
  "containers": [
    {
      "container_id": "ACID-001",
      "waste_stream": "AqueousAcid",
      "location": "Fume Hood A, Room 201",
      "capacity_ml": 4000,
      "current_fill_ml": 1500,
      "contents": [
        {
          "substance": "Hydrochloric Acid (dilute)",
          "category": "Acid",
          "quantity_ml": 1000,
          "concentration": "10%",
          "added_at": "2026-01-15T09:00:00Z"
        },
        {
          "substance": "Sulfuric Acid (dilute)",
          "category": "Acid",
          "quantity_ml": 500,
          "concentration": "5%",
          "added_at": "2026-01-20T14:30:00Z"
        }
      ],
      "accumulation_start": "2026-01-15T09:00:00Z",
      "pickup_deadline": "2026-04-15T09:00:00Z",
      "status": "Active"
    },
    {
      "container_id": "ACID-002",
      "waste_stream": "AqueousAcid",
      "location": "Fume Hood B, Room 201",
      "capacity_ml": 4000,
      "current_fill_ml": 500,
      "contents": [
        {
          "substance": "Hydrochloric Acid (dilute)",
          "category": "Acid",
          "quantity_ml": 500,
          "concentration": "10%",
          "added_at": "2026-01-25T10:00:00Z"
        }
      ],
      "accumulation_start": "2026-01-25T10:00:00Z",
      "pickup_deadline": "2026-04-25T10:00:00Z",
      "status": "Active"
    },
    {
      "container_id": "BASE-001",
      "waste_stream": "AqueousBase",
      "location": "Fume Hood A, Room 201",
      "capacity_ml": 4000,
      "current_fill_ml": 2000,
      "contents": [
        {
          "substance": "Sodium Hydroxide",
          "category": "Base",
          "quantity_ml": 2000,
          "concentration": "10%",
          "added_at": "2026-01-18T11:00:00Z"
        }
      ],
      "accumulation_start": "2026-01-18T11:00:00Z",
      "pickup_deadline": "2026-04-18T11:00:00Z",
      "status": "Active"
    },
    {
      "container_id": "SOLV-001",
      "waste_stream": "NonHalogenatedSolvent",
      "location": "Flammables Cabinet, Room 201",
      "capacity_ml": 4000,
      "current_fill_ml": 1200,
      "contents": [
        {
          "substance": "Acetone",
          "category": "Solvent",
          "quantity_ml": 700,
          "concentration": "Pure",
          "added_at": "2026-01-18T11:00:00Z"
        },
        {
          "substance": "Ethanol",
          "category": "Solvent",
          "quantity_ml": 500,
          "concentration": "95%",
          "added_at": "2026-01-22T16:00:00Z"
        }
      ],
      "accumulation_start": "2026-01-18T11:00:00Z",
      "pickup_deadline": "2026-04-18T11:00:00Z",
      "status": "Active"
    },
    {
      "container_id": "HSW-001",
      "waste_stream": "HalogenatedSolvent",
      "location": "Fume Hood C, Room 201",
      "capacity_ml": 4000,
      "current_fill_ml": 3800,
      "contents": [
        {
          "substance": "Chloroform",
          "category": "Solvent",
          "quantity_ml": 2500,
          "concentration": "Pure",
          "added_at": "2026-01-10T08:00:00Z"
        },
        {
          "substance": "Dichloromethane",
          "category": "Solvent",
          "quantity_ml": 1300,
          "concentration": "Pure",
          "added_at": "2026-01-25T10:00:00Z"
        }
      ],
      "accumulation_start": "2026-01-10T08:00:00Z",
      "pickup_deadline": "2026-04-10T08:00:00Z",
      "status": "Active"
    },
    {
      "container_id": "OXI-001",
      "waste_stream": "Oxidizer",
      "location": "Oxidizer Cabinet, Room 202",
      "capacity_ml": 2000,
      "current_fill_ml": 300,
      "contents": [
        {
          "substance": "Hydrogen Peroxide (30%)",
          "category": "Oxidizer",
          "quantity_ml": 300,
          "concentration": "10%",
          "added_at": "2026-01-20T09:00:00Z"
        }
      ],
      "accumulation_start": "2026-01-20T09:00:00Z",
      "pickup_deadline": "2026-04-20T09:00:00Z",
      "status": "Active"
    },
    {
      "container_id": "METAL-001",
      "waste_stream": "ReactiveMetal",
      "location": "Dry Storage Cabinet, Room 202",
      "capacity_ml": 1000,
      "current_fill_ml": 0,
      "contents": [],
      "accumulation_start": null,
      "pickup_deadline": null,
      "status": "Empty"
    },
    {
      "container_id": "HEAVY-001",
      "waste_stream": "HeavyMetal",
      "location": "Secure Storage, Room 203",
      "capacity_ml": 2000,
      "current_fill_ml": 0,
      "contents": [],
      "accumulation_start": null,
      "pickup_deadline": null,
      "status": "Empty"
    }
  ]
}
```

**File: `app/data/rules.json`**
```json
{
  "incompatibility_rules": [
    {
      "category_pair": ["Acid", "Metal"],
      "risk_level": "Danger",
      "hazard_type": "Gas Release",
      "explanation": "Acids react with metals producing hydrogen gas, which is flammable and can cause explosions in enclosed spaces."
    },
    {
      "category_pair": ["Acid", "Base"],
      "risk_level": "Caution",
      "hazard_type": "Exothermic Reaction",
      "explanation": "Neutralization reactions release heat. Large quantities may cause boiling or spattering."
    },
    {
      "category_pair": ["Oxidizer", "Organic"],
      "risk_level": "Danger",
      "hazard_type": "Fire/Explosion",
      "explanation": "Oxidizers can cause rapid combustion of organic materials, leading to fires or explosions."
    },
    {
      "category_pair": ["Oxidizer", "Solvent"],
      "risk_level": "Danger",
      "hazard_type": "Fire/Explosion",
      "explanation": "Oxidizers react violently with organic solvents, potentially causing fire or explosion."
    },
    {
      "category_pair": ["Oxidizer", "Metal"],
      "risk_level": "Danger",
      "hazard_type": "Fire/Explosion",
      "explanation": "Strong oxidizers can react violently with reactive metals."
    },
    {
      "category_pair": ["Metal", "Water-Reactive"],
      "risk_level": "Danger",
      "hazard_type": "Fire/Explosion",
      "explanation": "Reactive metals can ignite or explode when exposed to water or moisture."
    },
    {
      "category_pair": ["Halogen", "Metal"],
      "risk_level": "Danger",
      "hazard_type": "Violent Reaction",
      "explanation": "Halogens react violently with many metals, especially alkali metals."
    }
  ],
  "waste_stream_rules": {
    "AqueousAcid": {
      "accepts_categories": ["Acid"],
      "max_ph": 6,
      "description": "Dilute aqueous acid solutions only"
    },
    "AqueousBase": {
      "accepts_categories": ["Base"],
      "min_ph": 8,
      "description": "Dilute aqueous base solutions only"
    },
    "HalogenatedSolvent": {
      "accepts_categories": ["Solvent"],
      "requires_halogenated": true,
      "description": "Chlorinated and other halogenated solvents"
    },
    "NonHalogenatedSolvent": {
      "accepts_categories": ["Solvent", "Organic"],
      "requires_halogenated": false,
      "description": "Non-halogenated organic solvents"
    },
    "Oxidizer": {
      "accepts_categories": ["Oxidizer"],
      "description": "Oxidizing agents only - keep separate from organics"
    },
    "ReactiveMetal": {
      "accepts_categories": ["Metal"],
      "description": "Reactive metals under mineral oil"
    },
    "HeavyMetal": {
      "accepts_categories": ["Heavy-Metal"],
      "description": "Heavy metal solutions - mercury, lead, cadmium"
    }
  }
}
```

---

#### Hour 3-4: State Management Service

**File: `app/services/__init__.py`**
```python
from .state import StateManager
from .classification import ClassificationService
from .routing import RoutingService
from .compatibility import CompatibilityService
```

**File: `app/services/state.py`**
```python
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from app.models.container import WasteContainer, ContainerContent, ContainerStatus

class StateManager:
    """
    Manages in-memory state for the simulation.
    Loads initial data from JSON files.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.data_path = Path(__file__).parent.parent / "data"
        self.substances = {}
        self.containers = {}
        self.rules = {}
        self.disposal_log = []
        self.alerts = []
        self.simulated_time = datetime.now()
        
        self._load_data()
        self._initialized = True
    
    def _load_data(self):
        """Load all JSON data files"""
        # Load substances
        with open(self.data_path / "substances.json") as f:
            data = json.load(f)
            for s in data["substances"]:
                self.substances[s["id"]] = s
        
        # Load containers
        with open(self.data_path / "containers.json") as f:
            data = json.load(f)
            for c in data["containers"]:
                self.containers[c["container_id"]] = c
        
        # Load rules
        with open(self.data_path / "rules.json") as f:
            self.rules = json.load(f)
        
        print(f"Loaded {len(self.substances)} substances")
        print(f"Loaded {len(self.containers)} containers")
    
    def reset(self):
        """Reset state to initial values"""
        self.disposal_log = []
        self.alerts = []
        self.simulated_time = datetime.now()
        self._load_data()
    
    def get_substance(self, substance_id: str) -> Optional[dict]:
        """Get substance by ID"""
        return self.substances.get(substance_id)
    
    def get_all_substances(self) -> list[dict]:
        """Get all substances"""
        return list(self.substances.values())
    
    def get_container(self, container_id: str) -> Optional[dict]:
        """Get container by ID"""
        return self.containers.get(container_id)
    
    def get_all_containers(self) -> list[dict]:
        """Get all containers"""
        return list(self.containers.values())
    
    def get_containers_by_stream(self, waste_stream: str) -> list[dict]:
        """Get all containers for a specific waste stream"""
        return [c for c in self.containers.values() 
                if c["waste_stream"] == waste_stream]
    
    def update_container(self, container_id: str, 
                         substance_name: str,
                         category: str,
                         quantity_ml: float,
                         concentration: str) -> dict:
        """Add substance to container and update state"""
        container = self.containers[container_id]
        
        # Create content entry
        content = {
            "substance": substance_name,
            "category": category,
            "quantity_ml": quantity_ml,
            "concentration": concentration,
            "added_at": self.simulated_time.isoformat() + "Z"
        }
        
        container["contents"].append(content)
        container["current_fill_ml"] += quantity_ml
        
        # Set accumulation start if first disposal
        if container["accumulation_start"] is None:
            container["accumulation_start"] = self.simulated_time.isoformat() + "Z"
            # Set 90-day deadline
            from datetime import timedelta
            deadline = self.simulated_time + timedelta(days=90)
            container["pickup_deadline"] = deadline.isoformat() + "Z"
            container["status"] = "Active"
        
        # Check if full
        fill_percent = (container["current_fill_ml"] / container["capacity_ml"]) * 100
        if fill_percent >= 95:
            container["status"] = "Full"
        
        # Log disposal
        log_entry = {
            "timestamp": self.simulated_time.isoformat() + "Z",
            "container_id": container_id,
            "substance": substance_name,
            "quantity_ml": quantity_ml,
            "concentration": concentration
        }
        self.disposal_log.append(log_entry)
        
        return container
    
    def add_alert(self, container_id: str, alert_type: str, 
                  severity: str, title: str, message: str):
        """Add an alert"""
        alert = {
            "id": f"alert-{len(self.alerts) + 1}",
            "container_id": container_id,
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "message": message,
            "created_at": self.simulated_time.isoformat() + "Z",
            "acknowledged": False
        }
        self.alerts.append(alert)
        return alert
    
    def get_alerts(self, include_acknowledged: bool = False) -> list[dict]:
        """Get alerts"""
        if include_acknowledged:
            return self.alerts
        return [a for a in self.alerts if not a["acknowledged"]]
    
    def advance_time(self, days: int):
        """Advance simulated time"""
        from datetime import timedelta
        self.simulated_time += timedelta(days=days)
        self._check_deadlines()
    
    def _check_deadlines(self):
        """Check for deadline alerts"""
        for container in self.containers.values():
            if container["pickup_deadline"]:
                deadline = datetime.fromisoformat(
                    container["pickup_deadline"].replace("Z", "")
                )
                days_remaining = (deadline - self.simulated_time).days
                
                if days_remaining <= 7 and days_remaining > 0:
                    self.add_alert(
                        container["container_id"],
                        "Deadline",
                        "Caution",
                        "Pickup deadline approaching",
                        f"Container {container['container_id']} must be picked up within {days_remaining} days."
                    )
                elif days_remaining <= 0:
                    self.add_alert(
                        container["container_id"],
                        "Deadline",
                        "Danger",
                        "Pickup deadline exceeded",
                        f"Container {container['container_id']} has exceeded its pickup deadline!"
                    )


# Singleton instance
state_manager = StateManager()
```

---

### Phase 2: Core Services (Hours 4-10)

---

#### Hour 4-5: Classification Service

**File: `app/services/classification.py`**
```python
from typing import Optional
from app.services.state import state_manager

class ClassificationService:
    """
    Classifies substances by name lookup and alias resolution.
    """
    
    def __init__(self):
        self.state = state_manager
        self._build_lookup_index()
    
    def _build_lookup_index(self):
        """Build reverse lookup index for aliases"""
        self.name_index = {}  # lowercase name -> substance
        self.alias_index = {}  # lowercase alias -> substance
        
        for substance in self.state.substances.values():
            # Index by name
            self.name_index[substance["name"].lower()] = substance
            
            # Index by aliases
            for alias in substance.get("aliases", []):
                self.alias_index[alias.lower()] = substance
    
    def classify(self, substance_name: str) -> Optional[dict]:
        """
        Classify a substance by name.
        Returns substance profile or None if not found.
        """
        name_lower = substance_name.lower().strip()
        
        # Try exact name match
        if name_lower in self.name_index:
            return self.name_index[name_lower]
        
        # Try alias match
        if name_lower in self.alias_index:
            return self.alias_index[name_lower]
        
        # Try partial match (contains)
        for name, substance in self.name_index.items():
            if name_lower in name or name in name_lower:
                return substance
        
        for alias, substance in self.alias_index.items():
            if name_lower in alias or alias in name_lower:
                return substance
        
        return None
    
    def get_waste_stream(self, substance: dict) -> str:
        """Get the default waste stream for a substance"""
        return substance.get("default_waste_stream", "GeneralChemical")
    
    def get_category(self, substance: dict) -> str:
        """Get the category for a substance"""
        return substance.get("category", "Unknown")
    
    def search_substances(self, query: str) -> list[dict]:
        """Search for substances matching query"""
        query_lower = query.lower().strip()
        results = []
        
        for substance in self.state.substances.values():
            if query_lower in substance["name"].lower():
                results.append(substance)
                continue
            
            for alias in substance.get("aliases", []):
                if query_lower in alias.lower():
                    results.append(substance)
                    break
        
        return results


# Singleton instance
classification_service = ClassificationService()
```

---

#### Hour 5-6: Compatibility Service

**File: `app/services/compatibility.py`**
```python
from typing import Optional, Tuple
from app.services.state import state_manager

class CompatibilityService:
    """
    Checks compatibility between substances and container contents.
    """
    
    def __init__(self):
        self.state = state_manager
    
    def check_compatibility(self, substance: dict, container: dict) -> Tuple[bool, Optional[dict]]:
        """
        Check if a substance is compatible with container contents.
        
        Returns:
            Tuple of (is_compatible, incompatibility_info)
        """
        substance_category = substance.get("category", "Unknown")
        incompatible_categories = substance.get("incompatible_with", [])
        
        # Check against each item in container
        for content in container.get("contents", []):
            content_category = content.get("category", "Unknown")
            
            # Check if this substance is incompatible with existing content
            if content_category in incompatible_categories:
                rule = self._get_rule(substance_category, content_category)
                return False, {
                    "conflicting_substance": content["substance"],
                    "conflicting_category": content_category,
                    "rule": rule
                }
            
            # Check reverse - if existing content is incompatible with new substance
            existing_substance = self._find_substance_by_category(content_category)
            if existing_substance:
                existing_incompatible = existing_substance.get("incompatible_with", [])
                if substance_category in existing_incompatible:
                    rule = self._get_rule(content_category, substance_category)
                    return False, {
                        "conflicting_substance": content["substance"],
                        "conflicting_category": content_category,
                        "rule": rule
                    }
        
        return True, None
    
    def _get_rule(self, category1: str, category2: str) -> Optional[dict]:
        """Get the incompatibility rule for two categories"""
        rules = self.state.rules.get("incompatibility_rules", [])
        
        for rule in rules:
            pair = rule.get("category_pair", [])
            if (category1 in pair and category2 in pair):
                return rule
        
        # Return default rule if no specific rule found
        return {
            "risk_level": "Danger",
            "hazard_type": "Chemical Incompatibility",
            "explanation": f"{category1} and {category2} are chemically incompatible and should not be mixed."
        }
    
    def _find_substance_by_category(self, category: str) -> Optional[dict]:
        """Find any substance with the given category (for rule lookup)"""
        for substance in self.state.substances.values():
            if substance.get("category") == category:
                return substance
        return None
    
    def get_compatible_streams(self, substance: dict) -> list[str]:
        """Get list of waste streams that could accept this substance"""
        category = substance.get("category", "Unknown")
        compatible = []
        
        stream_rules = self.state.rules.get("waste_stream_rules", {})
        
        for stream_name, stream_rule in stream_rules.items():
            accepted = stream_rule.get("accepts_categories", [])
            if category in accepted:
                compatible.append(stream_name)
        
        return compatible


# Singleton instance
compatibility_service = CompatibilityService()
```

---

#### Hour 6-8: Routing Service

**File: `app/services/routing.py`**
```python
from typing import Optional, Tuple
from datetime import datetime
from app.services.state import state_manager
from app.services.classification import classification_service
from app.services.compatibility import compatibility_service
from app.models.responses import (
    RouteRequest, RouteResponse, RiskLevel,
    ClassificationResult, RoutedContainer
)

class RoutingService:
    """
    Routes substances to appropriate containers.
    This is the main orchestration service.
    """
    
    def __init__(self):
        self.state = state_manager
        self.classifier = classification_service
        self.compatibility = compatibility_service
    
    def route(self, request: RouteRequest) -> RouteResponse:
        """
        Main routing method.
        Takes a substance and finds the appropriate container.
        """
        # Step 1: Classify the substance
        substance = self.classifier.classify(request.substance)
        
        if not substance:
            return RouteResponse(
                success=False,
                substance=request.substance,
                classified_as=ClassificationResult(
                    category="Unknown",
                    waste_stream="Unknown"
                ),
                routed_to=None,
                safety_status=RiskLevel.DANGER,
                message=f"Unknown substance: '{request.substance}'. Please verify the chemical name or contact your supervisor.",
                warnings=["Substance not found in database"]
            )
        
        # Step 2: Get target waste stream
        waste_stream = self.classifier.get_waste_stream(substance)
        category = self.classifier.get_category(substance)
        
        # Step 3: Find compatible container
        container, compatibility_issue = self._find_best_container(
            substance, 
            waste_stream, 
            request.quantity_ml
        )
        
        if not container:
            return RouteResponse(
                success=False,
                substance=request.substance,
                classified_as=ClassificationResult(
                    category=category,
                    waste_stream=waste_stream
                ),
                routed_to=None,
                safety_status=RiskLevel.DANGER,
                message=self._build_no_container_message(waste_stream, compatibility_issue),
                warnings=self._build_warnings(None, compatibility_issue)
            )
        
        # Step 4: Build successful response
        return self._build_success_response(
            request, substance, container, category, waste_stream
        )
    
    def _find_best_container(self, substance: dict, waste_stream: str, 
                             quantity_ml: float) -> Tuple[Optional[dict], Optional[dict]]:
        """
        Find the best container for a substance.
        Returns (container, compatibility_issue) tuple.
        """
        containers = self.state.get_containers_by_stream(waste_stream)
        compatibility_issue = None
        
        # Sort by fill level (prefer less full containers)
        containers.sort(key=lambda c: c["current_fill_ml"])
        
        for container in containers:
            # Check capacity
            if container["current_fill_ml"] + quantity_ml > container["capacity_ml"]:
                continue
            
            # Check compatibility
            is_compatible, issue = self.compatibility.check_compatibility(
                substance, container
            )
            
            if is_compatible:
                return container, None
            else:
                compatibility_issue = issue  # Save for error message
        
        return None, compatibility_issue
    
    def _build_success_response(self, request: RouteRequest, substance: dict,
                                container: dict, category: str, 
                                waste_stream: str) -> RouteResponse:
        """Build a successful routing response"""
        
        fill_before = container["current_fill_ml"]
        fill_after = fill_before + request.quantity_ml
        capacity = container["capacity_ml"]
        fill_percent_before = (fill_before / capacity) * 100
        fill_percent_after = (fill_after / capacity) * 100
        
        # Calculate days until deadline
        days_until = None
        if container.get("pickup_deadline"):
            deadline = datetime.fromisoformat(
                container["pickup_deadline"].replace("Z", "")
            )
            days_until = (deadline - self.state.simulated_time).days
        
        # Determine safety status and warnings
        warnings = []
        safety_status = RiskLevel.SAFE
        
        if fill_percent_after > 80:
            warnings.append(f"Container will be at {fill_percent_after:.0f}% capacity")
            safety_status = RiskLevel.CAUTION
        
        if days_until and days_until < 14:
            warnings.append(f"Pickup deadline in {days_until} days")
            if safety_status == RiskLevel.SAFE:
                safety_status = RiskLevel.CAUTION
        
        return RouteResponse(
            success=True,
            substance=request.substance,
            classified_as=ClassificationResult(
                category=category,
                waste_stream=waste_stream
            ),
            routed_to=RoutedContainer(
                container_id=container["container_id"],
                location=container["location"],
                current_fill_percent=round(fill_percent_before, 1),
                after_fill_percent=round(fill_percent_after, 1),
                days_until_deadline=days_until
            ),
            safety_status=safety_status,
            message=f"Route to {container['container_id']} at {container['location']}. Safe to dispose.",
            warnings=warnings
        )
    
    def _build_no_container_message(self, waste_stream: str, 
                                    compatibility_issue: Optional[dict]) -> str:
        """Build error message when no container available"""
        if compatibility_issue:
            rule = compatibility_issue.get("rule", {})
            return (
                f"Cannot route: {rule.get('hazard_type', 'Incompatibility')}. "
                f"{rule.get('explanation', 'Chemical incompatibility detected.')}"
            )
        
        return (
            f"No container available for {waste_stream}. "
            f"All containers are full or at capacity."
        )
    
    def _build_warnings(self, container: Optional[dict], 
                        compatibility_issue: Optional[dict]) -> list[str]:
        """Build list of warnings"""
        warnings = []
        
        if compatibility_issue:
            warnings.append(
                f"Incompatible with {compatibility_issue.get('conflicting_substance', 'existing contents')}"
            )
        
        if not container:
            warnings.append("No suitable container found")
        
        return warnings


# Singleton instance
routing_service = RoutingService()
```

---

#### Hour 8-10: API Routers

**File: `app/routers/__init__.py`**
```python
from .route import router as route_router
from .dispose import router as dispose_router
from .containers import router as containers_router
from .simulation import router as simulation_router
```

**File: `app/routers/route.py`**
```python
from fastapi import APIRouter
from app.models.responses import RouteRequest, RouteResponse
from app.services.routing import routing_service

router = APIRouter(prefix="/api/v1", tags=["routing"])

@router.post("/route", response_model=RouteResponse)
def route_substance(request: RouteRequest):
    """
    Route a substance to the appropriate waste container.
    
    This is the primary endpoint for the IntelliBin system.
    
    - Classifies the substance
    - Finds a compatible container
    - Checks for hazardous combinations
    - Returns routing instructions or warnings
    """
    return routing_service.route(request)
```

**File: `app/routers/dispose.py`**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.state import state_manager
from app.services.classification import classification_service
from app.models.responses import DisposalResponse

router = APIRouter(prefix="/api/v1", tags=["disposal"])

class DisposeRequest(BaseModel):
    container_id: str
    substance: str
    quantity_ml: float
    concentration: str = "Pure"

@router.post("/dispose", response_model=DisposalResponse)
def confirm_disposal(request: DisposeRequest):
    """
    Confirm a disposal after routing.
    
    This endpoint should be called after /route returns success.
    It updates the container state and logs the disposal.
    """
    # Verify container exists
    container = state_manager.get_container(request.container_id)
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    
    # Classify substance
    substance = classification_service.classify(request.substance)
    if not substance:
        raise HTTPException(status_code=400, detail="Unknown substance")
    
    # Verify capacity
    new_fill = container["current_fill_ml"] + request.quantity_ml
    if new_fill > container["capacity_ml"]:
        raise HTTPException(
            status_code=400, 
            detail="Disposal would exceed container capacity"
        )
    
    # Update state
    updated = state_manager.update_container(
        container_id=request.container_id,
        substance_name=substance["name"],
        category=substance["category"],
        quantity_ml=request.quantity_ml,
        concentration=request.concentration
    )
    
    fill_percent = (updated["current_fill_ml"] / updated["capacity_ml"]) * 100
    
    # Check if we need to create capacity alert
    if fill_percent >= 90:
        state_manager.add_alert(
            container_id=request.container_id,
            alert_type="Capacity",
            severity="Caution" if fill_percent < 95 else "Danger",
            title="Container nearly full",
            message=f"Container {request.container_id} is at {fill_percent:.0f}% capacity."
        )
    
    return DisposalResponse(
        success=True,
        container_id=request.container_id,
        new_fill_ml=updated["current_fill_ml"],
        fill_percent=round(fill_percent, 1),
        logged_at=state_manager.simulated_time.isoformat() + "Z"
    )
```

**File: `app/routers/containers.py`**
```python
from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.state import state_manager

router = APIRouter(prefix="/api/v1", tags=["containers"])

@router.get("/containers")
def list_containers(waste_stream: Optional[str] = None):
    """
    List all waste containers.
    
    Optionally filter by waste_stream.
    """
    if waste_stream:
        containers = state_manager.get_containers_by_stream(waste_stream)
    else:
        containers = state_manager.get_all_containers()
    
    # Add computed fields
    result = []
    for c in containers:
        container_info = {
            **c,
            "fill_percent": round(
                (c["current_fill_ml"] / c["capacity_ml"]) * 100, 1
            ),
            "contents_count": len(c.get("contents", []))
        }
        
        # Calculate days until deadline
        if c.get("pickup_deadline"):
            from datetime import datetime
            deadline = datetime.fromisoformat(c["pickup_deadline"].replace("Z", ""))
            days = (deadline - state_manager.simulated_time).days
            container_info["days_until_deadline"] = days
        
        result.append(container_info)
    
    return {"containers": result, "count": len(result)}

@router.get("/containers/{container_id}")
def get_container(container_id: str):
    """
    Get detailed information about a specific container.
    """
    container = state_manager.get_container(container_id)
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    
    # Add computed fields
    fill_percent = (container["current_fill_ml"] / container["capacity_ml"]) * 100
    
    result = {
        **container,
        "fill_percent": round(fill_percent, 1)
    }
    
    if container.get("pickup_deadline"):
        from datetime import datetime
        deadline = datetime.fromisoformat(container["pickup_deadline"].replace("Z", ""))
        result["days_until_deadline"] = (deadline - state_manager.simulated_time).days
    
    return result

@router.get("/substances")
def list_substances(search: Optional[str] = None):
    """
    List all known substances.
    
    Optionally search by name/alias.
    """
    if search:
        from app.services.classification import classification_service
        substances = classification_service.search_substances(search)
    else:
        substances = state_manager.get_all_substances()
    
    # Return simplified list
    result = [
        {
            "id": s["id"],
            "name": s["name"],
            "category": s["category"],
            "waste_stream": s["default_waste_stream"],
            "aliases": s.get("aliases", [])
        }
        for s in substances
    ]
    
    return {"substances": result, "count": len(result)}

@router.get("/alerts")
def get_alerts(include_acknowledged: bool = False):
    """
    Get active alerts.
    """
    alerts = state_manager.get_alerts(include_acknowledged)
    return {"alerts": alerts, "count": len(alerts)}

@router.get("/disposal-log")
def get_disposal_log(limit: int = 50):
    """
    Get recent disposal log entries.
    """
    log = state_manager.disposal_log[-limit:]
    return {"log": list(reversed(log)), "count": len(log)}
```

**File: `app/routers/simulation.py`**
```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.state import state_manager

router = APIRouter(prefix="/api/v1/simulate", tags=["simulation"])

class TimeAdvanceResponse(BaseModel):
    new_time: str
    days_advanced: int
    new_alerts: int

@router.post("/reset")
def reset_simulation():
    """
    Reset the simulation to initial state.
    
    Clears all disposals and alerts, reloads container data.
    """
    alerts_before = len(state_manager.alerts)
    disposals_before = len(state_manager.disposal_log)
    
    state_manager.reset()
    
    return {
        "message": "Simulation reset to initial state",
        "cleared_alerts": alerts_before,
        "cleared_disposals": disposals_before,
        "current_time": state_manager.simulated_time.isoformat() + "Z"
    }

@router.post("/advance-time")
def advance_time(days: int = 1):
    """
    Advance the simulated time.
    
    Useful for testing deadline alerts.
    """
    alerts_before = len(state_manager.alerts)
    
    state_manager.advance_time(days)
    
    alerts_after = len(state_manager.alerts)
    
    return TimeAdvanceResponse(
        new_time=state_manager.simulated_time.isoformat() + "Z",
        days_advanced=days,
        new_alerts=alerts_after - alerts_before
    )

@router.get("/time")
def get_simulated_time():
    """
    Get the current simulated time.
    """
    return {
        "simulated_time": state_manager.simulated_time.isoformat() + "Z"
    }
```

---

#### Hour 10: Wire Up Main App

**Update: `app/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import route_router, dispose_router, containers_router, simulation_router

app = FastAPI(
    title="IntelliBin API",
    description="Laboratory Waste Routing & Safety System - Simulation Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(route_router)
app.include_router(dispose_router)
app.include_router(containers_router)
app.include_router(simulation_router)

@app.get("/", tags=["health"])
def root():
    return {
        "message": "IntelliBin API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "route": "POST /api/v1/route",
            "dispose": "POST /api/v1/dispose", 
            "containers": "GET /api/v1/containers",
            "substances": "GET /api/v1/substances",
            "alerts": "GET /api/v1/alerts",
            "reset": "POST /api/v1/simulate/reset"
        }
    }

@app.get("/health", tags=["health"])
def health_check():
    from app.services.state import state_manager
    return {
        "status": "healthy",
        "substances_loaded": len(state_manager.substances),
        "containers_loaded": len(state_manager.containers),
        "simulated_time": state_manager.simulated_time.isoformat() + "Z"
    }
```

---

### Phase 3: Testing & Verification (Hours 10-16)

---

#### Hour 10-12: Manual API Testing

**Test Script: `test_api_manual.sh`**
```bash
#!/bin/bash
# Manual API testing script

BASE_URL="http://localhost:8000"

echo "=== IntelliBin API Tests ==="
echo ""

# Health check
echo "1. Health Check:"
curl -s "$BASE_URL/health" | python -m json.tool
echo ""

# List substances
echo "2. List Substances:"
curl -s "$BASE_URL/api/v1/substances" | python -m json.tool
echo ""

# List containers
echo "3. List Containers:"
curl -s "$BASE_URL/api/v1/containers" | python -m json.tool
echo ""

# Route acetone (should succeed)
echo "4. Route Acetone (should succeed):"
curl -s -X POST "$BASE_URL/api/v1/route" \
  -H "Content-Type: application/json" \
  -d '{"substance": "Acetone", "quantity_ml": 100, "concentration": "Pure"}' \
  | python -m json.tool
echo ""

# Route chloroform (halogenated - different stream)
echo "5. Route Chloroform (halogenated solvent):"
curl -s -X POST "$BASE_URL/api/v1/route" \
  -H "Content-Type: application/json" \
  -d '{"substance": "Chloroform", "quantity_ml": 50, "concentration": "Pure"}' \
  | python -m json.tool
echo ""

# Route sodium metal (reactive metal)
echo "6. Route Sodium Metal:"
curl -s -X POST "$BASE_URL/api/v1/route" \
  -H "Content-Type: application/json" \
  -d '{"substance": "Sodium Metal", "quantity_ml": 10, "concentration": "Pure"}' \
  | python -m json.tool
echo ""

# Route unknown substance (should fail)
echo "7. Route Unknown Substance (should fail):"
curl -s -X POST "$BASE_URL/api/v1/route" \
  -H "Content-Type: application/json" \
  -d '{"substance": "Mystery Chemical", "quantity_ml": 100, "concentration": "Pure"}' \
  | python -m json.tool
echo ""

# Confirm disposal
echo "8. Confirm Disposal:"
curl -s -X POST "$BASE_URL/api/v1/dispose" \
  -H "Content-Type: application/json" \
  -d '{"container_id": "SOLV-001", "substance": "Acetone", "quantity_ml": 100, "concentration": "Pure"}' \
  | python -m json.tool
echo ""

# Check updated container
echo "9. Check Container After Disposal:"
curl -s "$BASE_URL/api/v1/containers/SOLV-001" | python -m json.tool
echo ""

# Check disposal log
echo "10. Check Disposal Log:"
curl -s "$BASE_URL/api/v1/disposal-log" | python -m json.tool
echo ""

# Advance time and check alerts
echo "11. Advance Time 80 Days:"
curl -s -X POST "$BASE_URL/api/v1/simulate/advance-time?days=80" | python -m json.tool
echo ""

echo "12. Check Alerts:"
curl -s "$BASE_URL/api/v1/alerts" | python -m json.tool
echo ""

# Reset simulation
echo "13. Reset Simulation:"
curl -s -X POST "$BASE_URL/api/v1/simulate/reset" | python -m json.tool
echo ""

echo "=== Tests Complete ==="
```

---

#### Hour 12-14: Unit Tests

**File: `tests/test_classification.py`**
```python
import pytest
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.classification import ClassificationService
from app.services.state import StateManager

@pytest.fixture
def classifier():
    # Reset state for each test
    state = StateManager()
    state.reset()
    return ClassificationService()

def test_classify_by_exact_name(classifier):
    result = classifier.classify("Acetone")
    assert result is not None
    assert result["name"] == "Acetone"
    assert result["category"] == "Solvent"

def test_classify_by_alias(classifier):
    result = classifier.classify("NaOH")
    assert result is not None
    assert result["name"] == "Sodium Hydroxide"
    assert result["category"] == "Base"

def test_classify_case_insensitive(classifier):
    result = classifier.classify("ACETONE")
    assert result is not None
    assert result["name"] == "Acetone"

def test_classify_unknown_returns_none(classifier):
    result = classifier.classify("Unknown Chemical XYZ")
    assert result is None

def test_get_waste_stream(classifier):
    substance = classifier.classify("Chloroform")
    stream = classifier.get_waste_stream(substance)
    assert stream == "HalogenatedSolvent"

def test_search_substances(classifier):
    results = classifier.search_substances("acid")
    assert len(results) > 0
    assert all("acid" in r["name"].lower() for r in results)
```

**File: `tests/test_routing.py`**
```python
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.routing import RoutingService
from app.services.state import StateManager
from app.models.responses import RouteRequest, RiskLevel

@pytest.fixture
def router():
    state = StateManager()
    state.reset()
    return RoutingService()

def test_route_solvent_to_solvent_container(router):
    request = RouteRequest(
        substance="Acetone",
        quantity_ml=100,
        concentration="Pure"
    )
    response = router.route(request)
    
    assert response.success is True
    assert response.classified_as.category == "Solvent"
    assert response.classified_as.waste_stream == "NonHalogenatedSolvent"
    assert response.routed_to.container_id == "SOLV-001"
    assert response.safety_status == RiskLevel.SAFE

def test_route_halogenated_solvent_separately(router):
    request = RouteRequest(
        substance="Chloroform",
        quantity_ml=50,
        concentration="Pure"
    )
    response = router.route(request)
    
    assert response.success is True
    assert response.classified_as.waste_stream == "HalogenatedSolvent"
    assert response.routed_to.container_id == "HSW-001"

def test_route_acid_to_acid_container(router):
    request = RouteRequest(
        substance="HCl dilute",
        quantity_ml=200,
        concentration="10%"
    )
    response = router.route(request)
    
    assert response.success is True
    assert response.classified_as.category == "Acid"
    assert "ACID" in response.routed_to.container_id

def test_route_unknown_substance_fails(router):
    request = RouteRequest(
        substance="Mystery Chemical",
        quantity_ml=100,
        concentration="Pure"
    )
    response = router.route(request)
    
    assert response.success is False
    assert response.safety_status == RiskLevel.DANGER
    assert "Unknown substance" in response.message

def test_route_reactive_metal(router):
    request = RouteRequest(
        substance="Sodium Metal",
        quantity_ml=10,
        concentration="Pure"
    )
    response = router.route(request)
    
    assert response.success is True
    assert response.classified_as.category == "Metal"
    assert response.routed_to.container_id == "METAL-001"
```

**File: `tests/test_compatibility.py`**
```python
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.compatibility import CompatibilityService
from app.services.state import StateManager

@pytest.fixture
def compat():
    state = StateManager()
    state.reset()
    return CompatibilityService()

@pytest.fixture
def state():
    s = StateManager()
    s.reset()
    return s

def test_same_category_compatible(compat, state):
    acid_substance = state.substances["hcl-dilute"]
    acid_container = state.containers["ACID-001"]
    
    is_compatible, issue = compat.check_compatibility(acid_substance, acid_container)
    
    assert is_compatible is True
    assert issue is None

def test_oxidizer_incompatible_with_solvent(compat, state):
    oxidizer = state.substances["h2o2-30"]
    solvent_container = state.containers["SOLV-001"]
    
    is_compatible, issue = compat.check_compatibility(oxidizer, solvent_container)
    
    assert is_compatible is False
    assert issue is not None
    assert issue["rule"]["risk_level"] == "Danger"

def test_acid_incompatible_with_metal(compat, state):
    # First add acid to metal container (simulated)
    metal_container = {
        "container_id": "TEST",
        "contents": [
            {"substance": "Sodium Metal", "category": "Metal", "quantity_ml": 100}
        ]
    }
    
    acid = state.substances["hcl-dilute"]
    
    is_compatible, issue = compat.check_compatibility(acid, metal_container)
    
    assert is_compatible is False
```

**Run tests:**
```bash
pip install pytest
pytest tests/ -v
```

---

### Phase 4: Documentation & Polish (Hours 16-20)

---

#### Hour 16-18: API Documentation

FastAPI auto-generates documentation at `/docs` and `/redoc`.

Add better descriptions to your endpoints and models for clearer docs.

**Create: `API_DOCUMENTATION.md`**
```markdown
# IntelliBin API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and available endpoints |
| GET | `/health` | Health check with loaded data counts |
| POST | `/api/v1/route` | **Primary** - Route substance to container |
| POST | `/api/v1/dispose` | Confirm disposal after routing |
| GET | `/api/v1/containers` | List all containers |
| GET | `/api/v1/containers/{id}` | Get specific container |
| GET | `/api/v1/substances` | List/search substances |
| GET | `/api/v1/alerts` | Get active alerts |
| GET | `/api/v1/disposal-log` | Get disposal history |
| POST | `/api/v1/simulate/reset` | Reset simulation |
| POST | `/api/v1/simulate/advance-time` | Advance time for testing |

## Key Endpoint: POST /api/v1/route

### Request
```json
{
  "substance": "Acetone",
  "quantity_ml": 100,
  "concentration": "Pure"
}
```

### Response (Success)
```json
{
  "success": true,
  "substance": "Acetone",
  "classified_as": {
    "category": "Solvent",
    "waste_stream": "NonHalogenatedSolvent"
  },
  "routed_to": {
    "container_id": "SOLV-001",
    "location": "Flammables Cabinet, Room 201",
    "current_fill_percent": 30.0,
    "after_fill_percent": 32.5,
    "days_until_deadline": 79
  },
  "safety_status": "Safe",
  "message": "Route to SOLV-001 at Flammables Cabinet, Room 201. Safe to dispose.",
  "warnings": []
}
```

### Response (Failure - Unknown Substance)
```json
{
  "success": false,
  "substance": "Mystery Chemical",
  "classified_as": {
    "category": "Unknown",
    "waste_stream": "Unknown"
  },
  "routed_to": null,
  "safety_status": "Danger",
  "message": "Unknown substance: 'Mystery Chemical'. Please verify the chemical name.",
  "warnings": ["Substance not found in database"]
}
```

## Interactive Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
```

---

#### Hour 18-20: Final Testing & Cleanup

1. Run all tests: `pytest tests/ -v`
2. Test manually with the shell script
3. Review and clean up code
4. Check all files have proper docstrings

---

### Phase 5: Demo Preparation (Hours 20-24)

---

#### Hour 20-22: Demo Scenarios

**File: `DEMO_SCENARIOS.md`**
```markdown
# IntelliBin Demo Scenarios

## Scenario 1: Successful Routing
```bash
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"substance": "Acetone", "quantity_ml": 100, "concentration": "Pure"}'
```
Expected: Routes to SOLV-001, Safe status

## Scenario 2: Different Waste Streams
```bash
# Non-halogenated
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"substance": "Ethanol", "quantity_ml": 50}'

# Halogenated (different container)
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"substance": "Chloroform", "quantity_ml": 50}'
```
Expected: Different containers, explaining why separation matters

## Scenario 3: Reactive Metal Safety
```bash
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"substance": "Sodium Metal", "quantity_ml": 5}'
```
Expected: Routes to METAL-001 (dry storage)

## Scenario 4: Unknown Substance
```bash
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"substance": "Unknown Chemical X", "quantity_ml": 100}'
```
Expected: Fails with Danger status, asks to verify

## Scenario 5: Capacity Warning
```bash
# HSW-001 is at 95% capacity
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"substance": "DCM", "quantity_ml": 300}'
```
Expected: No capacity, warning message

## Scenario 6: Deadline Alerts
```bash
# Advance time 80 days
curl -X POST "http://localhost:8000/api/v1/simulate/advance-time?days=80"

# Check alerts
curl http://localhost:8000/api/v1/alerts
```
Expected: Deadline alerts for containers
```

---

#### Hour 22-24: Final Verification

**Checklist:**
- [ ] `python run.py` starts without errors
- [ ] `/docs` shows all endpoints
- [ ] All demo scenarios work
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Code is clean and documented

---

## Quick Reference

### Start Server
```bash
cd backend
source venv/bin/activate
python run.py
```

### Run Tests
```bash
pytest tests/ -v
```

### Key Files
| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI entry point |
| `app/services/routing.py` | Main routing logic |
| `app/services/classification.py` | Substance classification |
| `app/services/compatibility.py` | Compatibility checking |
| `app/services/state.py` | In-memory state management |
| `app/data/substances.json` | Substance database |
| `app/data/containers.json` | Container initial state |

---

## Summary Timeline

| Hours | Phase | Deliverable |
|-------|-------|-------------|
| 0-4 | Setup | Project structure, models, data files |
| 4-10 | Core Services | Classification, compatibility, routing |
| 10-16 | Testing | Manual tests, unit tests |
| 16-20 | Documentation | API docs, code cleanup |
| 20-24 | Demo Prep | Demo scenarios, final verification |

**Total: 24 hours to a working simulation backend.**
