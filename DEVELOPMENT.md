# NeuroCapture Development Guide

## Getting Started for New Developers

This guide will help new team members get up and running with the NeuroCapture project quickly.

## Prerequisites Setup

### Required Software
1. **Node.js 18+** - Download from [nodejs.org](https://nodejs.org/)
2. **Python 3.8+** - Download from [python.org](https://python.org/)
3. **Docker Desktop** - Download from [docker.com](https://www.docker.com/products/docker-desktop/)
4. **Git** - Download from [git-scm.com](https://git-scm.com/)

### Recommended Tools
- **VS Code** with extensions:
  - Python
  - Pylance
  - ES7+ React/Redux/React-Native snippets
  - Tailwind CSS IntelliSense
  - Docker
- **Postman** or **Insomnia** for API testing
- **DBeaver** or **pgAdmin** for database management

## First-Time Setup

### 1. Clone and Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd NeuroCapture

# Install root dependencies and setup workspaces
npm install

# Install all project dependencies
npm run install:all
```

### 2. Database Setup
```bash
# Start PostgreSQL container
npm run db:up

# Wait for database to be ready (check with docker logs)
docker logs neurocapture-db

# Run database migrations
npm run db:migrate
```

### 3. Start Development Environment
```bash
# Terminal 1: Start the backend API
npm run dev:backend

# Terminal 2: Start the frontend application
npm run dev:frontend
```

### 4. Verify Setup
- Backend API: http://localhost:8000/docs
- Database: localhost:5432 (user: neuro, password: capture)
- Frontend: Automatically opens Electron window

## Project Structure Deep Dive

### Backend Architecture (`/backend`)

```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── models.py            # SQLAlchemy database models
│   ├── api/v1/endpoints/    # API route handlers
│   ├── crud/                # Database operations
│   ├── schemas/             # Pydantic data models
│   ├── services/            # Business logic
│   └── core/                # Core functionality
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── uploads/                 # File storage
└── requirements.txt         # Python dependencies
```

#### Key Files to Know

**`app/main.py`**
- FastAPI application entry point
- Router registration
- CORS configuration
- Static file serving

**`app/models.py`**
- SQLAlchemy ORM models
- Database schema definitions
- Relationship configurations

**`app/services/audio_processing.py`**
- Core audio analysis algorithms
- Feature extraction functions
- Signal processing pipeline

### Frontend Architecture (`/frontend`)

```
frontend/
├── main/                    # Electron main process
│   ├── index.js            # Electron app initialization
│   └── preload.js          # Secure context bridge
└── renderer/               # React application
    ├── src/
    │   ├── App.jsx         # Main React component
    │   ├── components/     # Reusable UI components
    │   ├── pages/          # Page-level components
    │   ├── context/        # React context providers
    │   ├── services/       # API communication
    │   └── utils/          # Helper functions
    ├── index.html          # HTML template
    └── vite.config.js      # Build configuration
```

#### Key Files to Know

**`renderer/src/App.jsx`**
- Main application component
- Routing configuration
- Global state management

**`renderer/src/components/PatientTable.jsx`**
- Patient list interface
- Search and filtering
- Action handling

**`renderer/src/services/api.js`**
- Centralized API communication
- Error handling
- Request/response processing

## Development Workflow

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend && pytest -v
   
   # Frontend tests (when implemented)
   cd frontend && npm test
   
   # Manual testing
   npm run dev
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat(scope): description of changes"
   git push origin feature/your-feature-name
   ```

### Code Standards

#### Python (Backend)
- **Style**: Follow PEP 8
- **Type Hints**: Required for all function signatures
- **Docstrings**: Google style for all public functions
- **Imports**: Organized (standard, third-party, local)

```python
def extract_audio_features(
    file_path: str, 
    target_sr: int = 16000
) -> Dict[str, float]:
    """
    Extract acoustic features from audio file.
    
    Args:
        file_path: Path to audio file
        target_sr: Target sample rate in Hz
        
    Returns:
        Dictionary of feature names and values
        
    Raises:
        AudioProcessingError: If feature extraction fails
    """
```

#### JavaScript/React (Frontend)
- **Style**: ES6+ features, functional components
- **Components**: Use hooks instead of class components
- **Props**: Document with JSDoc comments
- **Naming**: camelCase for variables, PascalCase for components

```javascript
/**
 * Patient detail component for editing patient information
 * @param {Object} props - Component props
 * @param {number} props.patientId - ID of patient to display
 * @param {Function} props.onSuccess - Callback after successful update
 */
function PatientDetail({ patientId, onSuccess }) {
  // Component implementation
}
```

#### Git Commit Messages
Use conventional commits format:
```
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
Scopes: api, ui, audio, db, tests, etc.

Examples:
feat(audio): add formant analysis
fix(api): resolve patient deletion issue
docs(readme): update installation steps
```

## Database Operations

### Creating Migrations
```bash
cd backend

# Generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Review the generated migration file
# Edit if necessary (especially for data migrations)

# Apply migration
alembic upgrade head
```

### Common Migration Patterns
```python
# Adding a new column
op.add_column('table_name', sa.Column('new_column', sa.String(50), nullable=True))

# Creating an index
op.create_index('idx_table_column', 'table_name', ['column_name'])

# Data migration example
connection = op.get_bind()
connection.execute(
    text("UPDATE table_name SET new_column = 'default_value'")
)
```

### Database Reset (Development)
```bash
# Nuclear option: destroy and recreate database
npm run db:reset
```

## API Development

### Adding New Endpoints

1. **Create Schema** (`app/schemas/`)
   ```python
   class NewEntityCreate(BaseModel):
       name: str
       description: Optional[str] = None
   ```

2. **Add CRUD Operations** (`app/crud/`)
   ```python
   async def create_entity(db: AsyncSession, obj_in: NewEntityCreate):
       # Implementation
   ```

3. **Create Endpoint** (`app/api/v1/endpoints/`)
   ```python
   @router.post("/", response_model=NewEntity)
   async def create_entity(entity_in: NewEntityCreate, db: AsyncSession = Depends(get_db)):
       # Implementation
   ```

4. **Register Router** (`app/main.py`)
   ```python
   app.include_router(new_entity_router, prefix="/api/v1", tags=["entities"])
   ```

### API Testing
Use the automatic documentation at http://localhost:8000/docs for interactive testing.

## Frontend Development

### Adding New Components

1. **Create Component** (`renderer/src/components/`)
   ```jsx
   export default function NewComponent({ prop1, prop2 }) {
     return (
       <div className="component-styles">
         {/* Component JSX */}
       </div>
     );
   }
   ```

2. **Add to Parent Component**
   ```jsx
   import NewComponent from './components/NewComponent';
   
   function ParentComponent() {
     return <NewComponent prop1="value" prop2={variable} />;
   }
   ```

### State Management
- Use React hooks (useState, useEffect, useContext)
- Context providers for global state
- Local state for component-specific data

### Styling with TailwindCSS
```jsx
// Good: Use utility classes
<button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md">
  Submit
</button>

// Avoid: Inline styles
<button style={{ padding: '8px 16px', backgroundColor: 'blue' }}>
  Submit
</button>
```

## Audio Processing Development

### Understanding the Pipeline

1. **Preprocessing**: Noise reduction, normalization
2. **VAD**: Voice activity detection
3. **Feature Extraction**: Prosodic and acoustic features
4. **Validation**: Filter invalid values
5. **Storage**: Save to database

### Adding New Features

1. **Implement Extraction Function**
   ```python
   def extract_new_feature(audio_data: np.ndarray, sr: int) -> float:
       """Extract new acoustic feature."""
       # Implementation
       return feature_value
   ```

2. **Add to Feature Pipeline**
   ```python
   # In extract_acoustic_features function
   features['new_feature'] = extract_new_feature(audio_data, sr)
   ```

3. **Test with Sample Audio**
   ```python
   # Add test in tests/test_audio_processing.py
   def test_new_feature_extraction():
       # Test implementation
   ```

## Testing Guidelines

### Backend Testing
```python
# Test filename: test_*.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_patient(client: AsyncClient):
    response = await client.post("/api/v1/patients", json={
        "study_identifier": "TEST001"
    })
    assert response.status_code == 201
    assert response.json()["study_identifier"] == "TEST001"
```

### Frontend Testing (Future)
```javascript
// Test filename: *.test.js
import { render, screen } from '@testing-library/react';
import PatientTable from './PatientTable';

test('renders patient table', () => {
  render(<PatientTable patients={[]} />);
  expect(screen.getByText('Patient List')).toBeInTheDocument();
});
```

## Debugging Tips

### Backend Debugging
```python
# Add debug prints
print(f"Debug: variable value = {variable}")

# Use Python debugger
import pdb; pdb.set_trace()

# Check logs
tail -f backend/logs/app.log
```

### Frontend Debugging
```javascript
// Console logging
console.log('Debug:', variable);

// React Developer Tools
// Network tab for API calls
// Performance tab for rendering issues
```

### Database Debugging
```sql
-- Connect to database
psql -h localhost -U neuro -d neurocapture

-- Check table contents
SELECT * FROM patients LIMIT 5;

-- Check relationships
SELECT p.study_identifier, COUNT(a.assessment_id) as assessment_count
FROM patients p
LEFT JOIN cognitive_assessments a ON p.patient_id = a.patient_id
GROUP BY p.patient_id, p.study_identifier;
```

## Deployment Preparation

### Environment Configuration
```bash
# Production environment variables
DATABASE_URL=postgresql://user:pass@prod-host:5432/neurocapture
DEBUG=false
UPLOAD_DIRECTORY=/app/uploads
```

### Build for Production
```bash
# Frontend build
cd frontend
npm run build

# Backend requirements
cd backend
pip freeze > requirements-prod.txt
```

## Getting Help

### Resources
- **Documentation**: See DOCUMENTATION.md for comprehensive details
- **API Docs**: http://localhost:8000/docs (when backend is running)
- **Code Comments**: Most functions have detailed docstrings

### Team Communication
- Create GitHub issues for bugs and feature requests
- Use descriptive titles and provide reproduction steps
- Include relevant logs and error messages
- Tag appropriate team members

## Common Tasks Cheat Sheet

```bash
# Database operations
npm run db:up           # Start database
npm run db:down         # Stop database  
npm run db:migrate      # Run migrations
npm run db:reset        # Reset database

# Development
npm run dev:backend     # Start API server
npm run dev:frontend    # Start Electron app
npm run test           # Run all tests

# Dependencies
npm run install:all    # Install all dependencies
npm install            # Install root dependencies
cd frontend && npm install  # Frontend only
cd backend && pip install -r requirements.txt  # Backend only
```

Welcome to the NeuroCapture team! 🧠🎵
