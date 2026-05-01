# PESE MVP - Development Guidelines

This file defines the development workflow and conventions for the PESE MVP project.

## Tech Stack

- **Frontend**: Vite + React with TypeScript
- **Backend**: Python/FastAPI + NumPy
- **Database**: Cloudflare D1 (SQLite) - switchable to Supabase later
- **PDF Generation**: WeasyPrint

## Directory Structure

```
pese-mvp/
├── frontend/          # Vite + React application
├── backend/          # Python/FastAPI application
├── database/         # D1 schema and migrations
├── docs/            # Technical documentation
└── tests/           # Test files
```

## Build Commands

### Frontend
```bash
cd frontend
npm install
npm run dev      # Start dev server
npm run build   # Production build
```

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Database (Cloudflare D1)
```bash
wrangler d1 execute pese_db --local --file=database/schema.sql
```

## Architecture

### Backend API Endpoints
- `POST /api/v1/validate` - Run full validation (physics + interface check)
- `GET /api/v1/robots` - List robots
- `GET /api/v1/grippers` - List grippers
- `GET /api/v1/validations` - List validations

### Physics Engine
Three pillars:
1. **Inertia-Guard**: Calculate reflected inertia at robot flange
2. **Cycle-Time-Realist**: Estimate cycle with 15% buffer
3. **Interface-Checker**: Mechanical/Electrical/Digital compatibility

### Database (Cloudflare D1)
Tables:
- `robots` - Robot technical specs
- `grippers` - Gripper technical specs
- `validations` - Validation records
- `assumptions` - Critical assumptions check
- `knowledge_tips` - Senior engineer tips

## Key Conventions

1. **Safety Margins**: 10% conservative on inertia (90% of OEM max), 15% on cycle time
2. **Language**: German for UI, English for code
3. **Liability**: All outputs framed as "Information" not "Recommendations"
4. **Response Format**: JSON with status fields (GRÜN/KRITISCH)

## Linting & Typecheck

### Frontend
npm run lint     # ESLint
npm run typecheck  # TypeScript check

### Backend
ruff check .    # Python lint
mypy app/      # Type check

## Testing

pytest tests/    # Run tests