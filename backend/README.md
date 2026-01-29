# IntelliBin Backend & Simulator

A complete Python backend with an Apple-style desktop simulator for the IntelliBin laboratory waste routing system.

---

## Quick Start

### 1. Setup Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Simulator

```bash
python run_simulator.py
```

---

## Project Structure

```
backend/
├── app/
│   ├── models/           # Pydantic data models
│   │   ├── substance.py  # Chemical substance models
│   │   ├── container.py  # Waste container models
│   │   └── responses.py  # API response models
│   ├── services/         # Business logic
│   │   ├── state.py      # In-memory state management
│   │   ├── classification.py  # Substance classification
│   │   ├── compatibility.py   # Compatibility checking
│   │   └── routing.py    # Main routing logic
│   └── data/             # Knowledge base (JSON)
│       ├── substances.json    # 25 chemical substances
│       ├── containers.json    # 10 waste containers
│       └── rules.json         # Incompatibility rules
├── simulator/
│   └── app.py            # Desktop UI application
├── tests/
│   └── test_services.py  # Unit tests
├── requirements.txt
├── run_simulator.py      # Main entry point
└── README.md
```

---

## Features

### Substances Database
- 25 pre-configured chemical substances
- Categories: Acids, Bases, Metals, Solvents, Oxidizers, Heavy Metals
- Alias support (e.g., "NaOH" → "Sodium Hydroxide")

### Waste Containers
- 10 containers across 8 waste streams
- Tracks fill level, contents, and pickup deadlines
- Status: Empty, Active, Full, AwaitingPickup

### Safety Logic
- Automatic waste stream routing
- Incompatibility detection (Acid+Metal, Oxidizer+Solvent, etc.)
- Capacity checking
- Deadline tracking

### Desktop Simulator
- Apple-inspired clean UI design
- Real-time container status display
- Substance routing with safety feedback
- Disposal confirmation flow
- Time simulation for deadline testing
- Reset to initial state

---

## Simulator UI

The simulator provides a 3-column layout:

| Left Panel | Center Panel | Right Panel |
|------------|--------------|-------------|
| Substance input form | Container status cards | Alerts & disposal log |
| Route/Confirm buttons | Fill level indicators | Time controls |

### Color Coding
- 🟢 **Green** - Safe (fill < 70%, no issues)
- 🟡 **Yellow** - Caution (fill 70-90%, deadline warning)
- 🔴 **Red** - Danger (fill > 90%, incompatibility)

---

## Using the Simulator

### Basic Disposal Flow

1. **Enter substance name** (e.g., "Acetone", "HCl", "Sodium Metal")
2. **Enter quantity** in mL
3. **Click "Check Routing"** to see where it should go
4. **Review the result**:
   - Container ID and location
   - Fill level change
   - Any warnings
5. **Click "Confirm Disposal"** to complete

### Testing Scenarios

| Substance | Expected Result |
|-----------|-----------------|
| Acetone | Routes to SOLV-001/002 (Non-Halogenated) |
| Chloroform | Routes to HSW-001/002 (Halogenated) |
| HCl dilute | Routes to ACID-001/002 (Aqueous Acid) |
| Sodium Metal | Routes to METAL-001 (Reactive Metal) |
| Unknown Chemical | Fails with "Unknown substance" |

### Time Simulation

- Click **"+7 Days"** to advance simulated time
- Watch for deadline alerts as containers approach 90-day limit
- Click **"Reset"** to restore initial state

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pip install pytest
pytest tests/ -v
```

---

## API Usage (Programmatic)

```python
from app.services import routing_service, state_manager
from app.models.responses import RouteRequest

# Route a substance
request = RouteRequest(
    substance="Acetone",
    quantity_ml=100,
    concentration="Pure"
)
result = routing_service.route(request)

if result.success:
    print(f"Route to: {result.routed_to.container_id}")
    print(f"Location: {result.routed_to.location}")
    
    # Confirm disposal
    disposal = routing_service.dispose(
        container_id=result.routed_to.container_id,
        substance_name="Acetone",
        quantity_ml=100,
        concentration="Pure"
    )
    print(f"New fill: {disposal.fill_percent}%")
else:
    print(f"Error: {result.message}")

# Reset simulation
state_manager.reset()
```

---

## Customization

### Adding Substances

Edit `app/data/substances.json`:

```json
{
  "id": "new-chemical",
  "name": "New Chemical",
  "aliases": ["NC", "NewChem"],
  "category": "Solvent",
  "default_waste_stream": "NonHalogenatedSolvent",
  "properties": {
    "ph_range": [7, 7],
    "flammable": true,
    "oxidizer": false,
    "water_reactive": false,
    "toxicity": "Low"
  },
  "incompatible_with": ["Oxidizer"]
}
```

### Adding Containers

Edit `app/data/containers.json`:

```json
{
  "container_id": "NEW-001",
  "waste_stream": "NonHalogenatedSolvent",
  "location": "Lab 301",
  "capacity_ml": 4000,
  "current_fill_ml": 0,
  "contents": [],
  "accumulation_start": null,
  "pickup_deadline": null,
  "status": "Empty"
}
```

### Adding Incompatibility Rules

Edit `app/data/rules.json`:

```json
{
  "category_pair": ["CategoryA", "CategoryB"],
  "risk_level": "Danger",
  "hazard_type": "Description of hazard",
  "explanation": "Detailed explanation..."
}
```

---

## Design Notes

### Fonts
The UI uses:
- JetBrains Mono (primary)
- Fira Code (fallback)
- System monospace (fallback)

### Colors (Apple-inspired)
- Background: `#F5F5F7` (light gray)
- Cards: `#FFFFFF` (white)
- Text: `#1D1D1F` (near black)
- Blue accent: `#007AFF`
- Green (Safe): `#34C759`
- Yellow (Caution): `#FF9500`
- Red (Danger): `#FF3B30`

---

## Troubleshooting

### "ModuleNotFoundError"
Make sure you've activated the virtual environment:
```bash
source venv/bin/activate
```

### "tkinter not found"
On macOS: `brew install python-tk`
On Ubuntu: `sudo apt install python3-tk`

### UI doesn't appear
Check if you're running via SSH or headless - tkinter requires a display.

---

## License

MIT License - Educational/Hackathon project
