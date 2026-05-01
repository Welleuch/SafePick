# PESE MVP - Technical Specification

## Overview

**PESE** (Pre-Engineering Standardization Engine) is a specialized software tool for German system integrators (Sondermaschinenbauer) in the Pick & Place automation industry. It enables junior engineers to create valid sales offers in under 10 minutes that previously required 30-60 minutes of senior engineer review.

## Problem Statement

- **Core Issue**: German system integrators have senior engineers spending 30-60 minutes validating every sales offer
- **Bottleneck**: Limits company growth when only 1-2 senior engineers can sign off on offers
- **Target**: Pharma/Food high-speed delta robots

## Solution

Three-pillar validation engine:

1. **Inertia-Guard**: Calculate reflected inertia at robot flange
2. **Cycle-Time-Realist**: Estimate cycle time with 15% buffer
3. **Interface-Checker**: Mechanical/Electrical/Digital compatibility

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vite + React + TypeScript |
| Backend | Python/FastAPI + NumPy |
| Database | Cloudflare D1 (SQLite) - switchable to Supabase |
| PDF | WeasyPrint |

## Architecture

### Backend API Endpoints

```
GET  /api/v1/robots           - List all robots
GET  /api/v1/grippers       - List all grippers
POST /api/v1/validate       - Run full validation
GET  /health                - Health check
```

### Physics Engine

**Pillar 1: Inertia-Guard**
- Uses Parallel Axis Theorem: `J = J_cm + m * d²`
- Safety margin: 90% of OEM max inertia
- Output: Status "GRÜN" or "KRITISCH"

**Pillar 2: Cycle-Time-Realist**
- Trapezoidal velocity profile
- 15% buffer ("Mittelstands-Puffer")
- Output: Estimated cycle time in seconds

**Pillar 3: Interface-Checker**
- Mechanical: ISO mounting pattern match
- Electrical: I/O current capacity
- Digital: Protocol intersection

### Database Schema

Tables:
- `robots` - Robot technical specs (KUKA, Fanuc, ABB)
- `grippers` - Gripper specs (Schunk, Zimmer, Festo)
- `validations` - Validation records
- `assumptions` - Critical assumptions check
- `knowledge_tips` - Senior engineer tips
- `license_bundles` - Project bundle tracking

## UI Design

**Industrial Dark Theme**
- Colors: Dark grays (#1a1a1a, #252525)
- Accents: Green (#22c55e) for pass, Red (#ef4444) for fail

**3-Step Wizard**:
1. Component Selection (Robot + Gripper)
2. Process Parameters (Mass, Distance)
3. Critical Assumptions (Mandatory checkboxes)

**Live Results Panel**:
- Inertia gauge with utilization %
- Cycle time display
- Interface check status

## Business Model

- **Project bundles** (NOT SaaS)
- **Pricing**: €2,500 for 25 validations/year
- **Target**: German Mittelstand (20-200 employees)

## Pre-loaded Data

### Robots
| Brand | Model | Type | Max Payload | Max Inertia |
|-------|-------|------|-------------|-------------|
| KUKA | KR 3 Delta | Delta | 3.0 kg | 0.05 kgm² |
| Fanuc | M-1iA | Delta | 1.0 kg | 0.02 kgm² |
| ABB | IRB 360 | Delta | 3.0 kg | 0.05 kgm² |

### Grippers
| Manufacturer | Model | Mass | Mounting Pattern |
|--------------|-------|------|-----------------|
| Schunk | PGN-plus-P 100 | 0.45 kg | ISO 9409-1-31.5-4-M5 |
| Zimmer | GP400 | 0.38 kg | ISO 9409-1-31.5-4-M5 |
| Festo | HEW-16 | 0.25 kg | ISO 9409-1-31.5-4-M5 |

## Key Safety Features

1. **10% Conservative Buffer**: Inertia calculations use 90% of OEM max
2. **15% Time Buffer**: Cycle time includes 15% "Mittelstands-Puffer"
3. **Mandatory Assumptions**: Junior must check critical assumptions
4. **Liability Framing**: Output is "information" not "recommendations"

## Success Metrics

- **Junior time**: <10 minutes (down from 45-60 min)
- **Senior time**: <3 minutes for sign-off
- **PDF Output**: Professional "Internal Technical Audit" format

## Future Considerations

### Phase 2: Senior-Configurable Assumptions (Option B)
- **Status**: Planned feature
- **Description**: Senior engineers define company-specific mandatory assumptions stored in database
- **Features**:
  - Senior Portal UI for managing assumption master list
  - Different assumption sets for different project types (food vs. pharma)
  - Per-customer assumption profiles
  - Version history for assumptions
- **Database Changes**: Add `assumption_templates` table

### Phase 1 Update: Simplified Assumption Check (Implemented)
- **Current**: Single checkbox replacement for multi-assumption requirements
- **Rationale**: Not all assumptions apply to every use case; enforce thinking not checkbox clicking
- **Implementation**: 
  ```text
  Checkbox: "Ich bestätige, dass die technischen Parameter meinem Anwendungsfall entsprechen"
  ```
- **Warning**: If unchecked, add warning to output

---

- Switch to Supabase for PostgreSQL when needed
- Add PDF report generation
- Add Senior Portal for knowledge management
- Add offline capability (PWA)

## Project Structure

```
pese-mvp/
├── AGENTS.md              # Development guidelines
├── frontend/
│   ├── src/
│   │   ├── App.tsx       # Main application
│   │   ├── main.tsx      # Entry point
│   │   ├── index.css    # Industrial dark theme
│   │   ├── types.ts     # TypeScript interfaces
│   │   └── services/    # API services
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
├── backend/
│   ├── main.py           # FastAPI application
│   ├── requirements.txt
│   └── app/
│       └── physics/
│           └── engine.py # Physics engine
├── database/
│   ├── schema.sql       # Cloudflare D1 schema
│   └── wrangler.toml    # D1 configuration
└── docs/
    └── SPEC.md          # This file
```

## Setup Instructions

### Frontend
```bash
cd frontend
npm install
npm run dev      # Start on http://localhost:5173
```

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload  # Start on http://localhost:8000
```

### Database (Cloudflare D1)
```bash
wrangler d1 execute pese_db --local --file=database/schema.sql
```

## Environment Variables

Frontend (.env):
```
VITE_API_URL=http://localhost:8000
```

Backend (.env):
```
DATABASE_URL=libere local D1
```