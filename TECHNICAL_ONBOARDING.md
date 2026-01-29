# IntelliBin — Technical Onboarding Guide

> **Smart Laboratory Waste Routing & Safety System**  
> A proof-of-concept decision-intelligence platform that routes chemical waste to correct containers and prevents hazardous interactions.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Tech Stack Recommendations](#tech-stack-recommendations)
4. [Data Contracts](#data-contracts)
5. [Parallel Development Timeline](#parallel-development-timeline)
6. [Development Setup](#development-setup)
7. [API Specifications](#api-specifications)
8. [Simulation Guide](#simulation-guide)
9. [Testing Strategy](#testing-strategy)
10. [Deployment](#deployment)

---

## Project Overview

### One-Liner
IntelliBin is a smart laboratory waste routing and safety system that directs chemical waste to the correct containers and prevents hazardous combinations through rule-based intelligence.

### Core Design Principle

| Layer | Responsibility |
|-------|----------------|
| **User Input** | Substance name + concentration + quantity |
| **Classification** | Identify waste category and properties |
| **Routing** | Find correct waste stream and container |
| **Safety Check** | Verify compatibility with existing contents |
| **Output** | Routing instructions + safety status + explanation |

**Golden Rules:**
1. **Route first, then check** — The system tells users WHERE to dispose, not just whether it's safe
2. **Frontend never decides** — All routing and safety logic runs in the intelligence layer
3. **Concentration matters** — 1% HCl and 37% HCl have different handling requirements
4. **Track everything** — Every container's contents, fill level, and timeline are monitored

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      INTELLIBIN ROUTING ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        USER INPUT                                    │  │
│  │         Substance: "Chloroform"  |  Qty: 50mL  |  Conc: Pure         │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
│                                     │                                      │
│                                     ▼                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────┐  │
│  │   WEB APP    │    │  MOBILE APP  │    │     IoT LAYER (Future)      │  │
│  │   (React)    │    │   (React     │    │  ┌────────┐ ┌────────────┐  │  │
│  │              │    │    Native)   │    │  │pH Sensor│ │ Gas Sensor │  │  │
│  └──────┬───────┘    └──────┬───────┘    │  └────┬───┘ └─────┬──────┘  │  │
│         │                   │            │  ┌────┴───┐ ┌─────┴──────┐  │  │
│         │                   │            │  │Temp    │ │Weight      │  │  │
│         └─────────┬─────────┘            │  │Sensor  │ │Sensor      │  │  │
│                   │                      │  └────┬───┘ └─────┬──────┘  │  │
│                   │                      └───────┼─────┬─────┘         │  │
│                   ▼                              │     │               │  │
│  ┌───────────────────────────────────────────────┼─────┼────────────┐  │  │
│  │                 BACKEND API LAYER             │     │            │  │  │
│  │                (FastAPI + Pydantic)           ▼     ▼            │  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐  │  │  │
│  │  │  /route    │  │ /dispose   │  │/containers │  │ /alerts   │  │  │  │
│  │  │ (primary)  │  │ (confirm)  │  │  (status)  │  │           │  │  │  │
│  │  └─────┬──────┘  └─────┬──────┘  └──────┬─────┘  └─────┬─────┘  │  │  │
│  └────────┼───────────────┼────────────────┼──────────────┼────────┘  │  │
│           │               │                │              │           │  │
│           └───────────────┼────────────────┼──────────────┘           │  │
│                           ▼                ▼                          │  │
│  ┌──────────────────────────────────────────────────────────────────┐ │  │
│  │                   INTELLIGENCE LAYER                             │ │  │
│  │                                                                  │ │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐  │ │  │
│  │  │  CLASSIFICATION │  │    ROUTING      │  │   COMPATIBILITY  │  │ │  │
│  │  │     ENGINE      │  │    ENGINE       │  │      CHECK       │  │ │  │
│  │  │                 │  │                 │  │                  │  │ │  │
│  │  │ • Name lookup   │  │ • Find stream   │  │ • Category rules │  │ │  │
│  │  │ • Alias resolve │  │ • Check capacity│  │ • Concentration  │  │ │  │
│  │  │ • Concentration │  │ • Select best   │  │ • Existing       │  │ │  │
│  │  │   handling      │  │   container     │  │   contents       │  │ │  │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬─────────┘  │ │  │
│  │           │                    │                    │            │ │  │
│  │           └────────────────────┼────────────────────┘            │ │  │
│  │                                ▼                                 │ │  │
│  │  ┌──────────────────────────────────────────────────────────┐   │ │  │
│  │  │              KNOWLEDGE BASE (Substances + Rules)          │   │ │  │
│  │  │  • 50+ substance profiles with properties                 │   │ │  │
│  │  │  • Incompatibility matrix (category × category)           │   │ │  │
│  │  │  • Waste stream definitions and routing rules             │   │ │  │
│  │  │  • Concentration thresholds and handling differences      │   │ │  │
│  │  └──────────────────────────────────────────────────────────┘   │ │  │
│  └──────────────────────────────────────────────────────────────────┘ │  │
│                                                                       │  │
│  ┌──────────────────────────────────────────────────────────────────┐ │  │
│  │                        DATA LAYER                                │ │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐  │ │  │
│  │  │ Container State │  │  Disposal Log   │  │   Alert Queue    │  │ │  │
│  │  │  (In-Memory/    │  │  (SQLite/       │  │  (In-Memory)     │  │ │  │
│  │  │   Redis)        │  │   Postgres)     │  │                  │  │ │  │
│  │  │                 │  │                 │  │                  │  │ │  │
│  │  │ • Fill levels   │  │ • History       │  │ • Capacity       │  │ │  │
│  │  │ • Contents      │  │ • Audit trail   │  │ • Deadline       │  │ │  │
│  │  │ • Deadlines     │  │ • Compliance    │  │ • Compatibility  │  │ │  │
│  │  └─────────────────┘  └─────────────────┘  └──────────────────┘  │ │  │
│  └──────────────────────────────────────────────────────────────────┘ │  │
│                                                                       │  │
│  ┌──────────────────────────────────────────────────────────────────┐ │  │
│  │                        OUTPUT                                    │ │  │
│  │  ┌───────────────────────────────────────────────────────────┐   │ │  │
│  │  │  ✓ Route to: HSW-001 (Halogenated Solvents)               │   │ │  │
│  │  │    Location: Fume Hood C, Room 201                        │   │ │  │
│  │  │    Fill: 45% → 46%  |  Days until deadline: 71            │   │ │  │
│  │  │    Status: SAFE                                           │   │ │  │
│  │  └───────────────────────────────────────────────────────────┘   │ │  │
│  └──────────────────────────────────────────────────────────────────┘ │  │
└───────────────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
1. User Input         →  "Chloroform, 50mL, Pure"
2. Classification     →  Category: Solvent, Stream: HalogenatedSolvent
3. Routing            →  Find containers for HalogenatedSolvent stream
4. Capacity Check     →  HSW-001 has space (3800 + 50 < 4000)
5. Compatibility      →  No incompatible substances in HSW-001
6. Response           →  "Route to HSW-001, Fume Hood C. Safe to dispose."
7. Confirmation       →  User confirms → State updated → Log recorded
```

---

## Tech Stack Recommendations

### 🌐 Frontend (Web Application)

| Component | Recommended | Alternative | Why |
|-----------|-------------|-------------|-----|
| **Framework** | React 18+ with Vite | Next.js 14 | Fast HMR, simple setup for SPA |
| **Language** | TypeScript | JavaScript | Type safety, better DX |
| **Styling** | Tailwind CSS | Chakra UI, shadcn/ui | Rapid prototyping, consistent design |
| **State Management** | Zustand | Redux Toolkit | Lightweight, minimal boilerplate |
| **HTTP Client** | Axios / TanStack Query | fetch + SWR | Caching, retry logic built-in |
| **Animations** | Framer Motion | GSAP | React-native feel, declarative |
| **Charts/Viz** | Recharts | Chart.js, D3.js | Simple API for dashboards |
| **Icons** | Lucide React | Heroicons | Clean, consistent iconography |

**Recommended Project Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI components
│   │   ├── dashboard/       # Dashboard-specific components
│   │   └── layout/          # Header, Footer, Navigation
│   ├── pages/
│   │   ├── Landing.tsx
│   │   ├── HowItWorks.tsx
│   │   ├── Dashboard.tsx
│   │   └── WasteLog.tsx
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API client functions
│   ├── stores/              # Zustand stores
│   ├── types/               # TypeScript interfaces
│   └── utils/               # Helper functions
├── public/
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

---

### 🧩 Backend (API Layer)

| Component | Recommended | Alternative | Why |
|-----------|-------------|-------------|-----|
| **Framework** | FastAPI (Python) | Node.js + Express | Python ecosystem for AI, auto-docs |
| **Language** | Python 3.11+ | TypeScript (Node) | Easier AI/ML integration |
| **Validation** | Pydantic v2 | Marshmallow | Native FastAPI integration |
| **Database** | SQLite (dev) → PostgreSQL (prod) | MongoDB | Structured data, ACID compliance |
| **ORM** | SQLAlchemy 2.0 | Prisma (Node) | Async support, mature ecosystem |
| **Task Queue** | None (hackathon) | Celery + Redis | Future: async processing |
| **API Docs** | Swagger UI (auto) | Redoc | Built into FastAPI |

**Recommended Project Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Environment configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── substance.py     # Substance domain model
│   │   ├── bin.py           # Bin state model
│   │   └── risk.py          # Risk event model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── requests.py      # API request schemas
│   │   └── responses.py     # API response schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── substances.py    # /analyze-substance
│   │   ├── bins.py          # /bin-status
│   │   └── alerts.py        # /alerts
│   ├── services/
│   │   ├── __init__.py
│   │   ├── classification.py
│   │   └── risk_engine.py
│   └── data/
│       └── substances.json  # Knowledge base
├── tests/
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

---

### 🤖 Intelligence Layer (AI / Decision Engine)

| Component | Recommended | Alternative | Why |
|-----------|-------------|-------------|-----|
| **Engine Type** | Rule-based (deterministic) | ML classifier | Explainable, no training needed |
| **Knowledge Base** | JSON/YAML files | SQLite | Easy to edit, version control |
| **Logic Framework** | Pure Python functions | Drools, Rete | Simplicity for hackathon |
| **Explainability** | Template-based reasons | SHAP/LIME | Human-readable outputs |

**Knowledge Base Schema:**
```yaml
# substances.yaml
substances:
  - name: "Hydrochloric Acid"
    aliases: ["HCl", "Muriatic Acid"]
    category: "Acid"
    properties:
      ph_range: [0, 2]
      gas_emission: false
      heat_reactive: false
      toxicity: "High"
    incompatible_with: ["Metal", "Base", "Oxidizer"]
    
  - name: "Sodium Metal"
    aliases: ["Na", "Sodium"]
    category: "Metal"
    properties:
      ph_range: [7, 7]
      gas_emission: true  # Produces H2 with water/acid
      heat_reactive: true
      toxicity: "Medium"
    incompatible_with: ["Acid", "Water", "Halogen"]
```

**Risk Rules Engine:**
```python
# risk_rules.py
INCOMPATIBILITY_RULES = [
    {
        "condition": ("Acid", "Metal"),
        "risk": "Danger",
        "hazard": "Gas Release",
        "explanation": "Acids react with metals producing hydrogen gas, which is flammable and can cause explosions in enclosed spaces."
    },
    {
        "condition": ("Oxidizer", "Organic"),
        "risk": "Danger", 
        "hazard": "Fire/Explosion",
        "explanation": "Oxidizers can cause rapid combustion of organic materials, leading to fires or explosions."
    },
    {
        "condition": ("Acid", "Base"),
        "risk": "Caution",
        "hazard": "Exothermic Reaction",
        "explanation": "Neutralization reactions release heat. Large quantities may cause boiling or spattering."
    },
]
```

---

### 📱 Mobile Application

| Component | Recommended | Alternative | Why |
|-----------|-------------|-------------|-----|
| **Framework** | React Native + Expo | Flutter | Code sharing with web, JS ecosystem |
| **Language** | TypeScript | Dart (Flutter) | Consistency with web frontend |
| **Navigation** | Expo Router | React Navigation | File-based routing, simpler |
| **State** | Zustand | Jotai | Same as web for consistency |
| **Notifications** | Expo Notifications | Firebase FCM | Easier setup for demo |
| **Demo Alerts** | Telegram Bot API | Discord Webhook | Quick to implement |

**Recommended Project Structure:**
```
mobile/
├── app/
│   ├── (tabs)/
│   │   ├── index.tsx        # Home screen
│   │   ├── dispose.tsx      # Disposal flow
│   │   └── history.tsx      # Disposal history
│   ├── _layout.tsx
│   └── alerts.tsx           # Alert screen
├── components/
├── hooks/
├── services/
├── types/
├── app.json
├── package.json
└── tsconfig.json
```

---

### 🧪 IoT Layer (Conceptual)

| Component | Recommended | Alternative | Why |
|-----------|-------------|-------------|-----|
| **Microcontroller** | ESP32 | Arduino Nano 33 IoT | WiFi built-in, cheap |
| **Protocol** | MQTT | HTTP REST | Lightweight, real-time |
| **Broker** | Mosquitto | HiveMQ Cloud | Self-hosted or free cloud |
| **pH Sensor** | DFRobot Analog pH Sensor | Atlas Scientific | Affordable for prototype |
| **Gas Sensor** | MQ-135 (Air Quality) | BME680 | Detects multiple gases |
| **Temp Sensor** | DS18B20 | DHT22 | Waterproof, accurate |

**Sensor-to-Feature Mapping:**
```
┌─────────────────┬─────────────────────┬─────────────────────────────┐
│ Physical Sensor │ AI Feature          │ Risk Detection              │
├─────────────────┼─────────────────────┼─────────────────────────────┤
│ pH Sensor       │ Acidity inference   │ Acid/Base incompatibility   │
│ Gas Sensor      │ Vapor risk          │ Toxic gas release           │
│ Temp Sensor     │ Reaction detection  │ Exothermic reaction warning │
│ Weight Sensor   │ Fill level          │ Capacity alerts             │
└─────────────────┴─────────────────────┴─────────────────────────────┘
```

---

### 🛠️ Development Tools

| Purpose | Tool | Why |
|---------|------|-----|
| **Version Control** | Git + GitHub | Standard, CI/CD integration |
| **API Testing** | Postman / Insomnia | Visual API exploration |
| **API Mocking** | MSW (Mock Service Worker) | Frontend can work independently |
| **Code Formatting** | Prettier + ESLint (JS) / Black + Ruff (Python) | Consistency |
| **Containerization** | Docker + Docker Compose | Reproducible environments |
| **Documentation** | Notion / GitHub Wiki | Team collaboration |
| **Design** | Figma | Wireframes, handoff |
| **Diagramming** | Excalidraw / draw.io | Architecture diagrams |

---

## Data Contracts

### Global Data Contract (All Teams Must Agree)

```typescript
// ============================================
// CORE TYPES
// ============================================

// Waste stream categories (what type of container)
type WasteStream = 
  | "AqueousAcid"           // Dilute acid solutions
  | "AqueousBase"           // Dilute base solutions
  | "HalogenatedSolvent"    // Chloroform, DCM, etc.
  | "NonHalogenatedSolvent" // Acetone, ethanol, etc.
  | "Oxidizer"              // Peroxides, permanganates
  | "ReactiveMetal"         // Sodium, potassium, etc.
  | "HeavyMetal"            // Mercury, lead solutions
  | "Flammable"             // Low flash-point liquids
  | "Corrosive"             // Concentrated acids/bases
  | "GeneralChemical";      // Miscellaneous

// Chemical category (what type of substance)
type ChemicalCategory = 
  | "Acid"
  | "Base"
  | "Metal"
  | "Organic"
  | "Oxidizer"
  | "Halogen"
  | "Solvent"
  | "Water-Reactive"
  | "Heavy-Metal";

type RiskLevel = "Safe" | "Caution" | "Danger";
type ConcentrationLevel = "Dilute" | "Moderate" | "Concentrated" | "Pure";

// ============================================
// INPUT TYPES (What users provide)
// ============================================

interface DisposalRequest {
  substance: string;              // "Hydrochloric Acid"
  quantity_ml: number;            // 100
  concentration: ConcentrationLevel | string;  // "37%" or "Concentrated"
  physical_state?: "Liquid" | "Solid" | "Solution";
  container_id?: string;          // Optional: specific container request
}

// ============================================
// SUBSTANCE DATABASE
// ============================================

interface SubstanceProfile {
  id: string;
  name: string;
  aliases: string[];              // ["HCl", "Muriatic Acid"]
  category: ChemicalCategory;
  default_waste_stream: WasteStream;
  properties: {
    ph_range: [number, number];   // [0, 2] for strong acids
    flammable: boolean;
    oxidizer: boolean;
    water_reactive: boolean;
    toxicity: "Low" | "Medium" | "High";
    flash_point_c?: number;       // For flammables
  };
  concentration_rules: {
    dilute_threshold: number;     // Below this % = dilute
    drain_disposable_below?: number;  // May go down drain below this %
  };
  incompatible_with: ChemicalCategory[];
}

// ============================================
// CONTAINER MANAGEMENT
// ============================================

interface WasteContainer {
  container_id: string;           // "ACID-001"
  waste_stream: WasteStream;
  location: string;               // "Fume Hood B, Room 201"
  capacity_ml: number;            // 4000
  current_fill_ml: number;        // 2100
  contents: ContainerContent[];
  accumulation_start: string;     // ISO 8601 - when first waste added
  pickup_deadline: string;        // ISO 8601 - regulatory deadline
  status: "Active" | "Full" | "AwaitingPickup" | "Empty";
}

interface ContainerContent {
  substance: string;
  category: ChemicalCategory;
  quantity_ml: number;
  concentration: string;
  added_at: string;               // ISO 8601
  added_by?: string;              // User ID
}

// ============================================
// ROUTING RESPONSE
// ============================================

interface RoutingResult {
  success: boolean;
  substance: string;
  classified_as: {
    category: ChemicalCategory;
    waste_stream: WasteStream;
  };
  routed_to?: {
    container_id: string;
    container_name: string;
    location: string;
    current_fill_percent: number;
    after_fill_percent: number;
    days_until_deadline: number;
  };
  safety_status: RiskLevel;
  message: string;                // Human-readable explanation
  warnings?: string[];            // Any cautions to note
  alternative_containers?: string[];  // If primary unavailable
  requires_confirmation: boolean;
}

// ============================================
// ALERTS & COMPLIANCE
// ============================================

interface Alert {
  id: string;
  container_id: string;
  severity: RiskLevel;
  alert_type: "Compatibility" | "Capacity" | "Deadline" | "Reaction";
  title: string;
  message: string;
  created_at: string;
  acknowledged: boolean;
  acknowledged_by?: string;
}

interface ComplianceStatus {
  container_id: string;
  days_since_accumulation_start: number;
  days_until_deadline: number;
  fill_percentage: number;
  compliance_status: "Compliant" | "Warning" | "Violation";
  issues: string[];
}
```

### Waste Stream Definitions

| Waste Stream | Accepts | Container Type | Special Rules |
|--------------|---------|----------------|---------------|
| AqueousAcid | Dilute acids (pH 2-6) | Plastic carboy | No metals, no oxidizers |
| AqueousBase | Dilute bases (pH 8-12) | Plastic carboy | No acids, no metals |
| HalogenatedSolvent | Cl, Br, F containing | Amber glass | No water, no oxidizers |
| NonHalogenatedSolvent | Acetone, alcohols, etc. | Glass or metal | No oxidizers, no water |
| Oxidizer | Peroxides, permanganates | Separate storage | No organics, no metals |
| ReactiveMetal | Na, K, Li, Mg | Dry, sealed container | No water, no acids |
| HeavyMetal | Hg, Pb, Cd solutions | Plastic, sealed | Special disposal |
| Corrosive | Conc. acids/bases | Compatible container | Segregate acids from bases |

### Demo Substances (Start with These)

| # | Substance | Category | Default Stream | Key Property |
|---|-----------|----------|----------------|--------------|
| 1 | Hydrochloric Acid (dilute) | Acid | AqueousAcid | pH 2-4, reacts with metals |
| 2 | Hydrochloric Acid (conc.) | Acid | Corrosive | pH 0-1, fuming, metal reactive |
| 3 | Sulfuric Acid (dilute) | Acid | AqueousAcid | pH 1-3, dehydrating |
| 4 | Sodium Hydroxide | Base | AqueousBase | pH 12-14, neutralizes acids |
| 5 | Sodium Metal | Metal | ReactiveMetal | Water-reactive, H2 release |
| 6 | Acetone | Solvent | NonHalogenatedSolvent | Flammable, flash point -20°C |
| 7 | Chloroform | Solvent | HalogenatedSolvent | Halogenated, special disposal |
| 8 | Ethanol | Solvent | NonHalogenatedSolvent | Flammable |
| 9 | Hydrogen Peroxide (30%) | Oxidizer | Oxidizer | Strong oxidizer, exothermic |
| 10 | Potassium Permanganate | Oxidizer | Oxidizer | Fire risk with organics |
| 11 | Mercury Solution | Heavy-Metal | HeavyMetal | Highly toxic |
| 12 | Calcium Carbonate | Base | GeneralChemical | Safe with most |

### Demo Containers (Initial State)

| Container ID | Waste Stream | Location | Capacity | Initial Fill | Contents |
|--------------|--------------|----------|----------|--------------|----------|
| ACID-001 | AqueousAcid | Fume Hood A | 4L | 1.5L | Dilute HCl, Dilute H2SO4 |
| ACID-002 | AqueousAcid | Fume Hood B | 4L | 0.5L | Dilute HCl |
| BASE-001 | AqueousBase | Fume Hood A | 4L | 2.0L | NaOH solution |
| SOLV-001 | NonHalogenatedSolvent | Flammables Cabinet | 4L | 1.0L | Acetone, Ethanol |
| HSW-001 | HalogenatedSolvent | Fume Hood C | 4L | 3.8L | Chloroform, DCM |
| OXI-001 | Oxidizer | Oxidizer Cabinet | 2L | 0.3L | H2O2 (dilute) |
| METAL-001 | ReactiveMetal | Dry Storage | 1L | 0.1L | Empty (mineral oil) |

---

## Parallel Development Timeline

### 🧠 PHASE 0 — SYSTEM ALIGNMENT (Hours 0–2)

**All teams together:**

- [ ] Define final substance list (10-15 max)
- [ ] Agree on waste categories
- [ ] Finalize risk level definitions
- [ ] Sign off on data contract (TypeScript interfaces above)
- [ ] Set up shared GitHub repository
- [ ] Create project boards (one per team)
- [ ] Establish communication channels (Slack/Discord)

**Deliverable:** `contracts/` folder with shared type definitions

---

### 🌐 FRONTEND TRACK

#### Phase 1: UX & Information Architecture (Hours 0–6)

**Tasks:**
- [ ] Set up Vite + React + TypeScript project
- [ ] Configure Tailwind CSS
- [ ] Create page structure (routes)
- [ ] Design component hierarchy
- [ ] Set up MSW for API mocking

**Pages to Design:**
1. **Landing** — Problem/solution narrative
2. **How It Works** — Interactive system diagram
3. **Dashboard** — Live bin visualization
4. **Waste Log** — Historical disposal records
5. **Mobile Preview** — Future app teaser

**Commands:**
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install -D tailwindcss postcss autoprefixer
npm install axios @tanstack/react-query zustand framer-motion recharts lucide-react
npm install -D msw
npx tailwindcss init -p
```

#### Phase 2: Interactive Demo Logic (Hours 6–14)

**Tasks:**
- [ ] Build substance input component (autocomplete)
- [ ] Create bin visualization component
- [ ] Implement API service layer
- [ ] Connect to backend (or mock)
- [ ] Build alert notification system
- [ ] Create risk level color coding

**Key Interactions:**
```
User types substance → API call → Receive result → Update bin visual → Show alert if needed
```

#### Phase 3: Storytelling & Polish (Hours 14–24)

**Tasks:**
- [ ] Animated waste drop effect
- [ ] Step-by-step decision visualization
- [ ] Tooltips explaining risk logic
- [ ] Loading states and error handling
- [ ] Responsive design check
- [ ] Accessibility audit (basic)

---

### 🧩 BACKEND TRACK

#### Phase 1: Domain Models (Hours 0–4)

**Tasks:**
- [ ] Set up FastAPI project structure
- [ ] Define Pydantic models (Substance, Bin, Risk)
- [ ] Create in-memory bin state manager
- [ ] Set up CORS for frontend

**Commands:**
```bash
mkdir backend && cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install fastapi uvicorn pydantic python-dotenv
pip install -D pytest httpx
```

**Initial Models:**
```python
# app/schemas/responses.py
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

RiskLevel = Literal["Safe", "Caution", "Danger"]
WasteCategory = Literal["Acid", "Base", "Metal", "Organic", "Oxidizer", "Halogen", "Solvent", "Water-Reactive"]

class AnalysisResult(BaseModel):
    substance: str
    category: WasteCategory
    risk: RiskLevel
    reason: str
    hazard_type: Optional[str] = None
    recommended_action: Optional[str] = None
```

#### Phase 2: Business Logic (Hours 4–12)

**Tasks:**
- [ ] Implement substance → category mapping
- [ ] Build bin content tracker
- [ ] Create compatibility checker
- [ ] Implement risk decision logic

**Core Logic Pattern:**
```python
def check_compatibility(new_substance: str, bin_contents: list[str]) -> AnalysisResult:
    new_category = classify_substance(new_substance)
    existing_categories = [classify_substance(s) for s in bin_contents]
    
    for existing in existing_categories:
        if (new_category, existing) in INCOMPATIBLE_PAIRS:
            return AnalysisResult(
                substance=new_substance,
                category=new_category,
                risk="Danger",
                reason=get_reason(new_category, existing),
                hazard_type=get_hazard(new_category, existing)
            )
    
    return AnalysisResult(
        substance=new_substance,
        category=new_category,
        risk="Safe",
        reason="No incompatibilities detected with current bin contents."
    )
```

#### Phase 3: API Contract (Hours 12–18)

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analyze` | Analyze substance compatibility |
| GET | `/api/v1/bins/{bin_id}` | Get bin status |
| POST | `/api/v1/bins/{bin_id}/dispose` | Add substance to bin |
| GET | `/api/v1/bins/{bin_id}/alerts` | Get active alerts |
| POST | `/api/v1/bins/{bin_id}/clear` | Empty the bin |
| GET | `/api/v1/substances` | List known substances |

---

### 🤖 AI / INTELLIGENCE TRACK

#### Phase 1: Knowledge Base (Hours 0–6)

**Tasks:**
- [ ] Research chemical incompatibilities (SDS sources)
- [ ] Create substance profiles JSON/YAML
- [ ] Define property ranges (pH, reactivity)
- [ ] Document incompatibility rules

**Sources for Chemical Data:**
- OSHA Chemical Compatibility Chart
- Fisher Scientific SDS Database
- NIST Chemistry WebBook

#### Phase 2: Classification Engine (Hours 6–12)

**Tasks:**
- [ ] Build substance name normalizer
- [ ] Implement alias resolution
- [ ] Create category classifier
- [ ] Handle unknown substances gracefully

**Example Implementation:**
```python
class ClassificationEngine:
    def __init__(self, knowledge_base_path: str):
        self.substances = self._load_knowledge_base(knowledge_base_path)
        self.alias_map = self._build_alias_map()
    
    def classify(self, substance_name: str) -> Optional[SubstanceProfile]:
        normalized = self._normalize(substance_name)
        
        # Direct match
        if normalized in self.substances:
            return self.substances[normalized]
        
        # Alias match
        if normalized in self.alias_map:
            return self.substances[self.alias_map[normalized]]
        
        # Fuzzy match (optional)
        return self._fuzzy_match(normalized)
```

#### Phase 3: Risk Reasoning (Hours 12–20)

**Tasks:**
- [ ] Implement rule engine
- [ ] Create explanation templates
- [ ] Build multi-substance conflict detection
- [ ] Generate human-readable warnings

**Explanation Templates:**
```python
EXPLANATION_TEMPLATES = {
    ("Acid", "Metal"): "Adding {substance} (an acid) to a bin containing metals may produce hydrogen gas. Hydrogen is flammable and can accumulate to explosive concentrations.",
    ("Oxidizer", "Organic"): "Oxidizers like {substance} can cause rapid, uncontrolled combustion when mixed with organic materials, potentially leading to fire or explosion.",
    ("Acid", "Base"): "Mixing {substance} with basic substances causes an exothermic neutralization reaction. This releases heat and may cause spattering.",
}
```

---

### 📱 MOBILE TRACK

#### Phase 1: User Journeys (Hours 0–4)

**Tasks:**
- [ ] Map user workflows
- [ ] Define screen transitions
- [ ] Identify critical user actions

**Primary Flow:**
```
Home → Select Bin → Enter Substance → View Warning → Confirm/Cancel → Success/Alert
```

#### Phase 2: Wireframes (Hours 4–10)

**Screens:**
1. **Home** — Bin overview, quick actions
2. **Bin Selection** — List/grid of available bins
3. **Disposal Input** — Substance entry with autocomplete
4. **Risk Alert** — Full-screen warning display
5. **Confirmation** — Success state
6. **History** — Past disposals

**Tools:** Figma, Excalidraw, or paper sketches

#### Phase 3: Notification Strategy (Hours 10–16)

**Implementation Options:**

| Method | Complexity | Demo Suitability |
|--------|------------|------------------|
| Telegram Bot | Low | ✅ Great for hackathon |
| Expo Push | Medium | Good for real demo |
| In-App Toast | Low | ✅ Always works |

**Telegram Bot Setup:**
```python
# notifications/telegram.py
import httpx

TELEGRAM_BOT_TOKEN = "your-bot-token"
TELEGRAM_CHAT_ID = "your-chat-id"

async def send_alert(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    await httpx.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"⚠️ IntelliBin Alert\n\n{message}",
        "parse_mode": "HTML"
    })
```

---

### 🧪 IoT TRACK (Conceptual Design)

#### Phase 1: Sensor-to-AI Mapping (Hours 0–4)

**Document sensor abstraction:**
```yaml
# iot/sensor_mapping.yaml
sensors:
  ph_sensor:
    model: "DFRobot Analog pH Sensor"
    output_range: [0, 14]
    maps_to: "acidity_level"
    ai_feature: "category_inference"
    
  gas_sensor:
    model: "MQ-135"
    detects: ["CO2", "NH3", "Benzene", "NOx"]
    maps_to: "vapor_risk"
    ai_feature: "gas_release_detection"
```

#### Phase 2: Data Flow Design (Hours 4–8)

**Pipeline Diagram:**
```
[Sensors] → [ESP32] → [MQTT Broker] → [Backend] → [AI Engine] → [Alerts]
                              ↓
                        [Time-Series DB]
                         (InfluxDB/future)
```

#### Phase 3: Replacement Strategy (Hours 8–12)

**Document how simulation maps to reality:**

| Current (Simulated) | Future (Real) | Change Required |
|---------------------|---------------|-----------------|
| User enters substance | Camera + ML identifies | New classification endpoint |
| Assumed pH from category | Real pH reading | Additional data source |
| Estimated gas risk | Actual gas detection | Real-time threshold alerts |
| Manual fill level | Weight sensor | Continuous monitoring |

---

## Development Setup

### Prerequisites

```bash
# Required
node --version    # v18+ 
python --version  # 3.11+
git --version     # 2.30+

# Recommended
docker --version  # For containerized deployment
```

### Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/intellibin.git
cd intellibin

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev

# Mobile setup (new terminal)
cd mobile
npm install
npx expo start
```

### Environment Variables

**Backend (`.env`):**
```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Database (future)
DATABASE_URL=sqlite:///./intellibin.db

# Notifications (optional)
TELEGRAM_BOT_TOKEN=your-token
TELEGRAM_CHAT_ID=your-chat-id
```

**Frontend (`.env.local`):**
```env
VITE_API_URL=http://localhost:8000/api/v1
```

### Docker Compose (Full Stack)

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://backend:8000/api/v1
    depends_on:
      - backend
```

---

## API Specifications

### POST `/api/v1/route`

Route a substance to the appropriate container. This is the primary endpoint.

**Request:**
```json
{
  "substance": "Acetone",
  "quantity_ml": 100,
  "concentration": "Pure"
}
```

**Response (Successful Routing):**
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
    "current_fill_percent": 25.0,
    "after_fill_percent": 27.5,
    "days_until_deadline": 79
  },
  "safety_status": "Safe",
  "message": "Route to SOLV-001 at Flammables Cabinet, Room 201. Safe to dispose.",
  "warnings": []
}
```

**Response (No Compatible Container):**
```json
{
  "success": false,
  "substance": "Chloroform",
  "classified_as": {
    "category": "Solvent",
    "waste_stream": "HalogenatedSolvent"
  },
  "routed_to": null,
  "safety_status": "Danger",
  "message": "No compatible container available for HalogenatedSolvent. All containers are full or contain incompatible substances.",
  "warnings": ["No container available", "HSW-001 at 95% capacity"]
}
```

**Response (Unknown Substance):**
```json
{
  "success": false,
  "substance": "Mystery Chemical X",
  "classified_as": {
    "category": "Unknown",
    "waste_stream": "Unknown"
  },
  "routed_to": null,
  "safety_status": "Danger",
  "message": "Unknown substance: 'Mystery Chemical X'. Please verify the name or contact your supervisor.",
  "warnings": ["Substance not in database"]
}
```

### POST `/api/v1/dispose`

Confirm and log a disposal after successful routing.

**Query Parameters:**
- `container_id` (required): Target container ID
- `substance` (required): Substance name
- `quantity_ml` (required): Amount in milliliters
- `concentration` (optional): Concentration level

**Response:**
```json
{
  "success": true,
  "container_id": "SOLV-001",
  "new_fill_ml": 1100,
  "fill_percent": 27.5,
  "logged_at": "2026-01-29T14:30:00Z"
}
```

### GET `/api/v1/containers`

List all containers and their current status.

**Response:**
```json
{
  "containers": [
    {
      "container_id": "ACID-001",
      "waste_stream": "AqueousAcid",
      "location": "Fume Hood A, Room 201",
      "capacity_ml": 4000,
      "current_fill_ml": 1500,
      "fill_percent": 37.5,
      "status": "Active",
      "days_until_deadline": 76,
      "contents_summary": ["Dilute HCl", "Dilute H2SO4"]
    },
    {
      "container_id": "HSW-001",
      "waste_stream": "HalogenatedSolvent",
      "location": "Fume Hood C, Room 201",
      "capacity_ml": 4000,
      "current_fill_ml": 3800,
      "fill_percent": 95.0,
      "status": "Full",
      "days_until_deadline": 71,
      "contents_summary": ["Chloroform", "DCM"]
    }
  ]
}
```

### GET `/api/v1/containers/{container_id}`

Get detailed status of a specific container.

**Response:**
```json
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
  "status": "Active",
  "compliance_status": {
    "days_since_start": 14,
    "days_until_deadline": 76,
    "status": "Compliant"
  }
}
```

### GET `/api/v1/alerts`

Get active alerts for all containers.

**Query Parameters:**
- `acknowledged` (optional, default=false): Include acknowledged alerts

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert-1",
      "container_id": "HSW-001",
      "severity": "Caution",
      "alert_type": "Capacity",
      "title": "Container nearly full",
      "message": "Container HSW-001 is at 95% capacity. Schedule pickup.",
      "created_at": "2026-01-29T10:00:00Z",
      "acknowledged": false
    }
  ]
}
```

### GET `/api/v1/disposal-log`

Get disposal history with optional filters.

**Query Parameters:**
- `container_id` (optional): Filter by container
- `from_date` (optional): Start date (ISO 8601)
- `to_date` (optional): End date (ISO 8601)
- `limit` (optional, default=100): Max records to return

**Response:**
```json
{
  "disposals": [
    {
      "id": "disp-001",
      "timestamp": "2026-01-29T14:30:00Z",
      "container_id": "SOLV-001",
      "substance": "Acetone",
      "quantity_ml": 100,
      "concentration": "Pure",
      "disposed_by": "user-123"
    }
  ],
  "total_count": 1
}
```

### POST `/api/v1/simulate/reset` (Demo Only)

Reset simulation to initial state.

**Response:**
```json
{
  "message": "Simulation reset to initial state",
  "containers_reset": 7,
  "alerts_cleared": 2
}
```

### POST `/api/v1/simulate/advance-time` (Demo Only)

Advance simulated time for deadline testing.

**Query Parameters:**
- `days` (required): Number of days to advance

**Response:**
```json
{
  "new_time": "2026-04-09T14:30:00Z",
  "days_advanced": 70,
  "new_alerts_generated": 3
}
```

---

## Simulation Guide

This section explains how to simulate the IntelliBin system for demonstrations without physical hardware.

### Simulation Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SIMULATION ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     SIMULATED DATA LAYER                            │   │
│  │                                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │   │
│  │  │ Substances   │  │ Containers   │  │ Disposal History         │  │   │
│  │  │ Database     │  │ State        │  │ Log                      │  │   │
│  │  │ (JSON/YAML)  │  │ (In-Memory)  │  │ (In-Memory/SQLite)       │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     SIMULATION ENGINE                               │   │
│  │                                                                     │   │
│  │  • Mimics sensor readings from substance properties                │   │
│  │  • Simulates time progression for deadlines                        │   │
│  │  • Generates realistic fill level changes                          │   │
│  │  • Creates alerts based on thresholds                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     SAME API AS PRODUCTION                          │   │
│  │                                                                     │   │
│  │  POST /api/v1/route          - Route substance to container        │   │
│  │  POST /api/v1/dispose        - Confirm disposal                    │   │
│  │  GET  /api/v1/containers     - List all containers                 │   │
│  │  GET  /api/v1/containers/:id - Get container status                │   │
│  │  GET  /api/v1/alerts         - Get active alerts                   │   │
│  │  POST /api/v1/simulate/time  - Advance simulated time              │   │
│  │  POST /api/v1/simulate/reset - Reset to initial state              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Setting Up the Simulation

#### 1. Initialize Substance Database

Create `data/substances.json`:

```json
{
  "substances": [
    {
      "id": "hcl-dilute",
      "name": "Hydrochloric Acid (dilute)",
      "aliases": ["HCl dilute", "Dilute HCl", "10% HCl"],
      "category": "Acid",
      "default_waste_stream": "AqueousAcid",
      "properties": {
        "ph_range": [2, 4],
        "flammable": false,
        "oxidizer": false,
        "water_reactive": false,
        "toxicity": "Medium"
      },
      "concentration_rules": {
        "dilute_threshold": 20,
        "drain_disposable_below": 5
      },
      "incompatible_with": ["Metal", "Base", "Oxidizer"]
    },
    {
      "id": "hcl-conc",
      "name": "Hydrochloric Acid (concentrated)",
      "aliases": ["HCl", "Conc HCl", "37% HCl", "Muriatic Acid"],
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
      "id": "sodium-metal",
      "name": "Sodium Metal",
      "aliases": ["Na", "Sodium", "Metallic Sodium"],
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
      "aliases": ["Propanone", "Dimethyl Ketone"],
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
      "id": "h2o2-30",
      "name": "Hydrogen Peroxide (30%)",
      "aliases": ["H2O2", "Peroxide"],
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
    }
  ]
}
```

#### 2. Initialize Container State

Create `data/containers_initial.json`:

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
      "container_id": "SOLV-001",
      "waste_stream": "NonHalogenatedSolvent",
      "location": "Flammables Cabinet, Room 201",
      "capacity_ml": 4000,
      "current_fill_ml": 1000,
      "contents": [
        {
          "substance": "Acetone",
          "category": "Solvent",
          "quantity_ml": 600,
          "concentration": "Pure",
          "added_at": "2026-01-18T11:00:00Z"
        },
        {
          "substance": "Ethanol",
          "category": "Solvent",
          "quantity_ml": 400,
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
      "container_id": "METAL-001",
      "waste_stream": "ReactiveMetal",
      "location": "Dry Storage Cabinet, Room 202",
      "capacity_ml": 1000,
      "current_fill_ml": 0,
      "contents": [],
      "accumulation_start": null,
      "pickup_deadline": null,
      "status": "Empty"
    }
  ]
}
```

#### 3. Simulation Engine Implementation

```python
# app/services/simulation.py
from datetime import datetime, timedelta
from typing import Optional
import json

class SimulationEngine:
    """
    Manages simulated state for demo purposes.
    In production, this would be replaced by real database queries.
    """
    
    def __init__(self):
        self.substances = self._load_substances()
        self.containers = self._load_initial_containers()
        self.disposal_log = []
        self.alerts = []
        self.simulated_time = datetime.now()
    
    def _load_substances(self) -> dict:
        with open("data/substances.json") as f:
            data = json.load(f)
        return {s["id"]: s for s in data["substances"]}
    
    def _load_initial_containers(self) -> dict:
        with open("data/containers_initial.json") as f:
            data = json.load(f)
        return {c["container_id"]: c for c in data["containers"]}
    
    def reset(self):
        """Reset simulation to initial state"""
        self.containers = self._load_initial_containers()
        self.disposal_log = []
        self.alerts = []
        self.simulated_time = datetime.now()
    
    def advance_time(self, days: int):
        """Advance simulated time for deadline testing"""
        self.simulated_time += timedelta(days=days)
        self._check_deadline_alerts()
    
    def classify_substance(self, name: str, concentration: str) -> Optional[dict]:
        """
        Classify a substance by name and concentration.
        Returns substance profile or None if unknown.
        """
        name_lower = name.lower()
        
        for substance in self.substances.values():
            if name_lower == substance["name"].lower():
                return substance
            if any(name_lower == alias.lower() for alias in substance["aliases"]):
                return substance
        
        return None  # Unknown substance
    
    def find_compatible_container(self, substance: dict, quantity_ml: int) -> Optional[str]:
        """
        Find a container that can accept this substance.
        Returns container_id or None if no compatible container found.
        """
        target_stream = substance["default_waste_stream"]
        
        for container_id, container in self.containers.items():
            # Check waste stream match
            if container["waste_stream"] != target_stream:
                continue
            
            # Check capacity
            if container["current_fill_ml"] + quantity_ml > container["capacity_ml"]:
                continue
            
            # Check compatibility with existing contents
            if self._check_compatibility(substance, container):
                return container_id
        
        return None
    
    def _check_compatibility(self, substance: dict, container: dict) -> bool:
        """Check if substance is compatible with container contents"""
        substance_category = substance["category"]
        incompatible = substance.get("incompatible_with", [])
        
        for content in container["contents"]:
            if content["category"] in incompatible:
                return False
        
        return True
    
    def simulate_disposal(self, container_id: str, substance: dict, 
                          quantity_ml: int, concentration: str) -> dict:
        """
        Simulate adding substance to container.
        Updates container state and returns result.
        """
        container = self.containers[container_id]
        
        # Add to contents
        container["contents"].append({
            "substance": substance["name"],
            "category": substance["category"],
            "quantity_ml": quantity_ml,
            "concentration": concentration,
            "added_at": self.simulated_time.isoformat()
        })
        
        # Update fill level
        container["current_fill_ml"] += quantity_ml
        
        # Set accumulation start if first disposal
        if container["accumulation_start"] is None:
            container["accumulation_start"] = self.simulated_time.isoformat()
            # Set 90-day deadline (typical EPA satellite accumulation)
            deadline = self.simulated_time + timedelta(days=90)
            container["pickup_deadline"] = deadline.isoformat()
        
        # Update status
        fill_percent = (container["current_fill_ml"] / container["capacity_ml"]) * 100
        if fill_percent >= 95:
            container["status"] = "Full"
            self._create_alert(container_id, "Capacity", 
                              "Container nearly full", 
                              f"Container {container_id} is at {fill_percent:.0f}% capacity. Schedule pickup.")
        
        # Log disposal
        log_entry = {
            "timestamp": self.simulated_time.isoformat(),
            "container_id": container_id,
            "substance": substance["name"],
            "quantity_ml": quantity_ml,
            "concentration": concentration
        }
        self.disposal_log.append(log_entry)
        
        return {
            "success": True,
            "container_id": container_id,
            "new_fill_ml": container["current_fill_ml"],
            "fill_percent": fill_percent
        }
    
    def _check_deadline_alerts(self):
        """Check for upcoming deadline alerts"""
        for container_id, container in self.containers.items():
            if container["pickup_deadline"]:
                deadline = datetime.fromisoformat(container["pickup_deadline"].replace("Z", ""))
                days_remaining = (deadline - self.simulated_time).days
                
                if days_remaining <= 7:
                    self._create_alert(
                        container_id, "Deadline",
                        "Pickup deadline approaching",
                        f"Container {container_id} must be picked up within {days_remaining} days."
                    )
    
    def _create_alert(self, container_id: str, alert_type: str, 
                      title: str, message: str):
        """Create a new alert"""
        alert = {
            "id": f"alert-{len(self.alerts)+1}",
            "container_id": container_id,
            "severity": "Caution" if alert_type == "Deadline" else "Danger",
            "alert_type": alert_type,
            "title": title,
            "message": message,
            "created_at": self.simulated_time.isoformat(),
            "acknowledged": False
        }
        self.alerts.append(alert)


# Singleton instance for the simulation
simulation = SimulationEngine()
```

#### 4. Simulation API Endpoints

```python
# app/routers/simulation.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.simulation import simulation

router = APIRouter(prefix="/api/v1", tags=["simulation"])

class RouteRequest(BaseModel):
    substance: str
    quantity_ml: int
    concentration: str = "Pure"

class RouteResponse(BaseModel):
    success: bool
    substance: str
    classified_as: dict
    routed_to: dict | None
    safety_status: str
    message: str
    warnings: list[str] = []

@router.post("/route", response_model=RouteResponse)
def route_substance(request: RouteRequest):
    """
    Route a substance to the appropriate container.
    This is the main endpoint users interact with.
    """
    # Step 1: Classify the substance
    substance = simulation.classify_substance(request.substance, request.concentration)
    
    if not substance:
        return RouteResponse(
            success=False,
            substance=request.substance,
            classified_as={"category": "Unknown", "waste_stream": "Unknown"},
            routed_to=None,
            safety_status="Danger",
            message=f"Unknown substance: '{request.substance}'. Please verify the name or contact your supervisor.",
            warnings=["Substance not in database"]
        )
    
    # Step 2: Find compatible container
    container_id = simulation.find_compatible_container(substance, request.quantity_ml)
    
    if not container_id:
        return RouteResponse(
            success=False,
            substance=request.substance,
            classified_as={
                "category": substance["category"],
                "waste_stream": substance["default_waste_stream"]
            },
            routed_to=None,
            safety_status="Danger",
            message=f"No compatible container available for {substance['default_waste_stream']}. All containers are full or contain incompatible substances.",
            warnings=["No container available"]
        )
    
    # Step 3: Return routing instructions
    container = simulation.containers[container_id]
    fill_before = container["current_fill_ml"]
    fill_after = fill_before + request.quantity_ml
    fill_percent_after = (fill_after / container["capacity_ml"]) * 100
    
    # Calculate days until deadline
    days_until = None
    if container["pickup_deadline"]:
        from datetime import datetime
        deadline = datetime.fromisoformat(container["pickup_deadline"].replace("Z", ""))
        days_until = (deadline - simulation.simulated_time).days
    
    warnings = []
    safety_status = "Safe"
    
    if fill_percent_after > 80:
        warnings.append(f"Container will be at {fill_percent_after:.0f}% capacity after disposal")
        safety_status = "Caution"
    
    if days_until and days_until < 14:
        warnings.append(f"Container pickup deadline in {days_until} days")
        safety_status = "Caution"
    
    return RouteResponse(
        success=True,
        substance=request.substance,
        classified_as={
            "category": substance["category"],
            "waste_stream": substance["default_waste_stream"]
        },
        routed_to={
            "container_id": container_id,
            "location": container["location"],
            "current_fill_percent": (fill_before / container["capacity_ml"]) * 100,
            "after_fill_percent": fill_percent_after,
            "days_until_deadline": days_until
        },
        safety_status=safety_status,
        message=f"Route to {container_id} at {container['location']}. Safe to dispose.",
        warnings=warnings
    )


@router.post("/dispose")
def confirm_disposal(container_id: str, substance: str, quantity_ml: int, concentration: str = "Pure"):
    """Confirm and log a disposal after routing"""
    substance_profile = simulation.classify_substance(substance, concentration)
    if not substance_profile:
        raise HTTPException(status_code=400, detail="Unknown substance")
    
    result = simulation.simulate_disposal(container_id, substance_profile, quantity_ml, concentration)
    return result


@router.get("/containers")
def list_containers():
    """List all containers and their status"""
    return {"containers": list(simulation.containers.values())}


@router.get("/containers/{container_id}")
def get_container(container_id: str):
    """Get detailed status of a specific container"""
    if container_id not in simulation.containers:
        raise HTTPException(status_code=404, detail="Container not found")
    return simulation.containers[container_id]


@router.get("/alerts")
def get_alerts(acknowledged: bool = False):
    """Get active alerts"""
    if acknowledged:
        return {"alerts": simulation.alerts}
    return {"alerts": [a for a in simulation.alerts if not a["acknowledged"]]}


@router.post("/simulate/advance-time")
def advance_time(days: int):
    """Advance simulated time (for demo purposes)"""
    simulation.advance_time(days)
    return {"new_time": simulation.simulated_time.isoformat(), "days_advanced": days}


@router.post("/simulate/reset")
def reset_simulation():
    """Reset simulation to initial state"""
    simulation.reset()
    return {"message": "Simulation reset to initial state"}
```

### Running Demo Scenarios

#### Scenario 1: Successful Routing (Happy Path)

```bash
# Route acetone to solvent waste
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"substance": "Acetone", "quantity_ml": 100, "concentration": "Pure"}'

# Expected response:
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
    "current_fill_percent": 25.0,
    "after_fill_percent": 27.5,
    "days_until_deadline": 79
  },
  "safety_status": "Safe",
  "message": "Route to SOLV-001 at Flammables Cabinet, Room 201. Safe to dispose.",
  "warnings": []
}
```

#### Scenario 2: Dangerous Combination Prevention

```bash
# Try to add oxidizer to solvent container (should fail)
# First, manually check what's in SOLV-001 (it has acetone)
curl http://localhost:8000/api/v1/containers/SOLV-001

# Then try to route hydrogen peroxide
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"substance": "Hydrogen Peroxide (30%)", "quantity_ml": 50, "concentration": "30%"}'

# Expected: Routes to OXI-001 (oxidizer container), NOT SOLV-001
# The system automatically prevents mixing oxidizers with organic solvents
```

#### Scenario 3: Full Container Handling

```bash
# HSW-001 is at 95% capacity (3800/4000 ml)
# Try to add 300ml of chloroform
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"substance": "Chloroform", "quantity_ml": 300, "concentration": "Pure"}'

# Expected: Fails or routes to alternative container
# Message explains no capacity in halogenated solvent containers
```

#### Scenario 4: Reactive Metal Safety

```bash
# Try to add sodium metal to acid container
# This should be blocked even if someone tries to force it
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{"substance": "Sodium Metal", "quantity_ml": 10, "concentration": "Pure"}'

# Expected: Routes to METAL-001 (reactive metal container)
# Specifically warns about keeping away from water and acids
```

#### Scenario 5: Timeline Simulation

```bash
# Advance time to near deadline
curl -X POST "http://localhost:8000/api/v1/simulate/advance-time?days=80"

# Check for deadline alerts
curl http://localhost:8000/api/v1/alerts

# Expected: Alerts for containers approaching 90-day deadline
```

### Frontend Simulation Integration

```typescript
// services/simulation.ts
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface RouteRequest {
  substance: string;
  quantity_ml: number;
  concentration: string;
}

export interface RouteResponse {
  success: boolean;
  substance: string;
  classified_as: {
    category: string;
    waste_stream: string;
  };
  routed_to?: {
    container_id: string;
    location: string;
    current_fill_percent: number;
    after_fill_percent: number;
    days_until_deadline: number | null;
  };
  safety_status: 'Safe' | 'Caution' | 'Danger';
  message: string;
  warnings: string[];
}

export const routeSubstance = async (request: RouteRequest): Promise<RouteResponse> => {
  const response = await axios.post(`${API_BASE}/route`, request);
  return response.data;
};

export const confirmDisposal = async (
  containerId: string, 
  substance: string, 
  quantityMl: number,
  concentration: string
) => {
  const response = await axios.post(`${API_BASE}/dispose`, null, {
    params: { container_id: containerId, substance, quantity_ml: quantityMl, concentration }
  });
  return response.data;
};

export const getContainers = async () => {
  const response = await axios.get(`${API_BASE}/containers`);
  return response.data.containers;
};

export const resetSimulation = async () => {
  const response = await axios.post(`${API_BASE}/simulate/reset`);
  return response.data;
};
```

### Demo Script (Step-by-Step)

Use this script when presenting IntelliBin:

```markdown
## IntelliBin Demo Script

### Setup (before demo)
1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Reset simulation: Click "Reset Demo" button or call `/simulate/reset`

### Demo Flow

**Step 1: Show the Dashboard**
- Point out the different waste containers
- Show fill levels and deadlines
- Explain the color coding (green = safe, yellow = caution, red = danger)

**Step 2: Successful Disposal**
- Enter: "Acetone, 100mL, Pure"
- Show routing to SOLV-001 (Non-Halogenated Solvents)
- Click confirm
- Show container fill level update

**Step 3: Different Waste Stream**
- Enter: "Chloroform, 50mL, Pure"  
- Show it routes to HSW-001 (Halogenated Solvents)
- Explain why halogenated solvents are separated

**Step 4: Dangerous Combination Prevention**
- Enter: "Sodium Metal, 5g, Pure"
- Show it routes to METAL-001 (Reactive Metals)
- Explain: "If we tried to put this in the acid container..."
- Show what would happen (hydrogen gas warning)

**Step 5: Capacity Warning**
- Note HSW-001 is nearly full (95%)
- Enter: "Dichloromethane, 300mL, Pure"
- Show system cannot route (no capacity)
- Explain pickup scheduling

**Step 6: Compliance Tracking**
- Show disposal history log
- Advance time 80 days
- Show deadline alerts appearing
- Explain regulatory compliance

**Closing**
- Summarize: Routing + Safety + Compliance
- Show future roadmap (sensors, scanning)
- Q&A
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_classification.py
import pytest
from app.services.simulation import SimulationEngine

@pytest.fixture
def engine():
    return SimulationEngine()

def test_acid_classification(engine):
    result = engine.classify_substance("Hydrochloric Acid (dilute)", "10%")
    assert result is not None
    assert result["category"] == "Acid"
    assert result["default_waste_stream"] == "AqueousAcid"

def test_concentrated_acid_classification(engine):
    result = engine.classify_substance("Hydrochloric Acid (concentrated)", "37%")
    assert result is not None
    assert result["category"] == "Acid"
    assert result["default_waste_stream"] == "Corrosive"

def test_alias_resolution(engine):
    result = engine.classify_substance("HCl", "10%")
    # Should resolve alias to full name
    assert result is not None
    assert "Hydrochloric" in result["name"]

def test_unknown_substance(engine):
    result = engine.classify_substance("Unobtainium", "Pure")
    assert result is None


# tests/test_routing.py
def test_solvent_routes_to_solvent_container(engine):
    substance = engine.classify_substance("Acetone", "Pure")
    container_id = engine.find_compatible_container(substance, 100)
    assert container_id == "SOLV-001"

def test_halogenated_routes_separately(engine):
    substance = engine.classify_substance("Chloroform", "Pure")
    container_id = engine.find_compatible_container(substance, 100)
    # Should NOT go to SOLV-001 (non-halogenated)
    assert container_id != "SOLV-001"
    # Should go to halogenated container
    container = engine.containers[container_id]
    assert container["waste_stream"] == "HalogenatedSolvent"

def test_metal_routes_to_metal_container(engine):
    substance = engine.classify_substance("Sodium Metal", "Pure")
    container_id = engine.find_compatible_container(substance, 10)
    assert container_id == "METAL-001"


# tests/test_compatibility.py
def test_oxidizer_not_compatible_with_organics(engine):
    # SOLV-001 contains acetone (organic)
    oxidizer = engine.classify_substance("Hydrogen Peroxide (30%)", "30%")
    solv_container = engine.containers["SOLV-001"]
    
    is_compatible = engine._check_compatibility(oxidizer, solv_container)
    assert is_compatible is False

def test_same_category_compatible(engine):
    # Adding more acid to acid container should work
    acid = engine.classify_substance("Hydrochloric Acid (dilute)", "10%")
    acid_container = engine.containers["ACID-001"]
    
    is_compatible = engine._check_compatibility(acid, acid_container)
    assert is_compatible is True


# tests/test_capacity.py
def test_rejects_when_over_capacity(engine):
    # HSW-001 is at 3800/4000 ml
    substance = engine.classify_substance("Chloroform", "Pure")
    # Try to add 300ml (would exceed capacity)
    container_id = engine.find_compatible_container(substance, 300)
    # Should not route to HSW-001
    assert container_id != "HSW-001"
```

### Integration Tests

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_route_endpoint_success():
    response = client.post("/api/v1/route", json={
        "substance": "Acetone",
        "quantity_ml": 100,
        "concentration": "Pure"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["classified_as"]["category"] == "Solvent"
    assert data["routed_to"]["container_id"] == "SOLV-001"
    assert data["safety_status"] == "Safe"

def test_route_endpoint_unknown_substance():
    response = client.post("/api/v1/route", json={
        "substance": "Unknown Chemical XYZ",
        "quantity_ml": 50,
        "concentration": "Pure"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["safety_status"] == "Danger"
    assert "Unknown substance" in data["message"]

def test_dispose_endpoint():
    # First route
    route_response = client.post("/api/v1/route", json={
        "substance": "Ethanol",
        "quantity_ml": 50,
        "concentration": "95%"
    })
    container_id = route_response.json()["routed_to"]["container_id"]
    
    # Then dispose
    dispose_response = client.post("/api/v1/dispose", params={
        "container_id": container_id,
        "substance": "Ethanol",
        "quantity_ml": 50,
        "concentration": "95%"
    })
    assert dispose_response.status_code == 200
    assert dispose_response.json()["success"] is True

def test_containers_list():
    response = client.get("/api/v1/containers")
    assert response.status_code == 200
    containers = response.json()["containers"]
    assert len(containers) > 0
    assert all("container_id" in c for c in containers)

def test_simulation_reset():
    # Make a disposal
    client.post("/api/v1/dispose", params={
        "container_id": "SOLV-001",
        "substance": "Acetone",
        "quantity_ml": 100,
        "concentration": "Pure"
    })
    
    # Reset
    reset_response = client.post("/api/v1/simulate/reset")
    assert reset_response.status_code == 200
    
    # Verify state is back to initial
    container = client.get("/api/v1/containers/SOLV-001").json()
    assert container["current_fill_ml"] == 1000  # Initial value
```

### Demo Test Scenarios

| # | Action | Expected Routing | Safety Status | Notes |
|---|--------|------------------|---------------|-------|
| 1 | Route "Acetone, 100mL, Pure" | SOLV-001 | ✅ Safe | Non-halogenated solvent |
| 2 | Route "Chloroform, 50mL, Pure" | HSW-001 | ⚠️ Caution | Container nearly full |
| 3 | Route "Sodium Metal, 5g, Pure" | METAL-001 | ✅ Safe | Reactive metal stream |
| 4 | Route "HCl dilute, 200mL, 10%" | ACID-001 | ✅ Safe | Aqueous acid stream |
| 5 | Route "H2O2 30%, 50mL" | OXI-001 | ✅ Safe | Oxidizer stream |
| 6 | Route "Chloroform, 300mL" | NONE | 🔴 Danger | No capacity available |
| 7 | Route "Unknown Chemical" | NONE | 🔴 Danger | Unknown substance |

### Compatibility Matrix Test

| New Substance | Container Contents | Expected |
|---------------|-------------------|----------|
| Acid | Empty | ✅ Route to acid container |
| Acid | Acids | ✅ Compatible |
| Acid | Metals | 🔴 Block (H2 gas risk) |
| Oxidizer | Organics | 🔴 Block (fire risk) |
| Oxidizer | Empty | ✅ Route to oxidizer container |
| Metal | Acids | 🔴 Block (H2 gas risk) |
| Metal | Water | 🔴 Block (reactive) |
| Halogenated | Non-halogenated | 🔴 Different stream |

---

## Deployment

### Demo Deployment (Recommended)

| Service | Platform | Cost |
|---------|----------|------|
| Frontend | Vercel / Netlify | Free |
| Backend | Railway / Render | Free tier |
| Database | SQLite (embedded) | Free |

### Production Considerations (Future)

- Use PostgreSQL for persistence
- Add authentication (JWT)
- Implement rate limiting
- Set up monitoring (Sentry)
- Add audit logging

---

## Final Checklist

### Before Demo

- [ ] All team members can run the full stack locally
- [ ] Demo substances are tested end-to-end
- [ ] Risk explanations are reviewed for accuracy
- [ ] UI handles loading and error states
- [ ] Alert flow works (visual + notification)
- [ ] Architecture diagram is presentation-ready

### Demo Order (Suggested)

1. Show empty bin (Safe state)
2. Add acid → Still safe
3. Add metal → DANGER alert triggers
4. Explain the reasoning
5. Show waste log
6. Demonstrate notification (Telegram)

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [OSHA Chemical Compatibility](https://www.osha.gov/chemical-hazards)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/)

---

**Questions?** Create an issue in the repository or reach out on the team channel.

*Last updated: January 29, 2026*
