# Development Guide

This guide is for developers who want to modify or extend Release OS.

## Development Setup

```bash
# Clone/navigate to project
cd ~/Developer/release-os

# Run setup
./setup.sh

# Start development servers
./start.sh
```

## Project Architecture

### Backend (FastAPI)

```
backend/
├── main.py              # API routes and app initialization
├── database.py          # SQLAlchemy models
├── ableton_parser.py    # .als file parsing logic
├── audio_processor.py   # Audio generation functions
└── folder_watcher.py    # File system monitoring
```

**Key Components:**

- **FastAPI App**: Handles HTTP requests, CORS, static files
- **Database Session**: SQLAlchemy ORM with SQLite
- **Background Tasks**: Uses FastAPI BackgroundTasks for async processing
- **File Watcher**: watchdog Observer pattern for monitoring

### Frontend (React + Vite)

```
frontend/src/
├── App.jsx              # Main application component
├── main.jsx             # React entry point
└── index.css            # Tailwind imports
```

**Key Components:**

- **App.jsx**: Contains ProjectCard component and main App component
- **State Management**: React useState hooks (no Redux needed yet)
- **API Calls**: Native fetch API
- **Audio Playback**: WaveSurfer.js integration

## Adding New Features

### Adding a New API Endpoint

1. Open [backend/main.py](backend/main.py)
2. Add your route:

```python
@app.get("/my-endpoint")
def my_endpoint(db: Session = Depends(get_db)):
    # Your logic here
    return {"data": "something"}
```

3. Test at http://localhost:8000/docs

### Adding a New Database Field

1. Update the model in [backend/database.py](backend/database.py):

```python
class Project(Base):
    # ... existing fields ...
    my_new_field = Column(String)
```

2. Delete the database to recreate schema:

```bash
rm backend/data/release_os.db
```

3. Restart backend - tables will be recreated

For production, use Alembic for migrations:

```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Add my_new_field"
alembic upgrade head
```

### Adding a New Frontend Component

1. Create component in [frontend/src/App.jsx](frontend/src/App.jsx):

```javascript
function MyComponent({ data }) {
  return (
    <div className="bg-gray-800 p-4">
      {data}
    </div>
  )
}
```

2. Use it in the App component:

```javascript
<MyComponent data={someData} />
```

### Adding Audio Processing Features

1. Add function to [backend/audio_processor.py](backend/audio_processor.py):

```python
def analyze_track_key(audio_file_path):
    y, sr = librosa.load(audio_file_path)
    # Use librosa.key_estimation or other analysis
    return detected_key
```

2. Call from main.py:

```python
from audio_processor import analyze_track_key

# In your route
key = analyze_track_key(audio_path)
project.key = key
```

## Testing

### Manual Testing

1. Add test .als file to watch folder:
```bash
cp path/to/test.als ~/Music/ReleaseDrop/
```

2. Check backend logs for processing
3. Verify in frontend at http://localhost:5173

### Unit Testing (Future)

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Common Tasks

### Resetting the Database

```bash
# Stop servers
./stop.sh

# Delete database
rm backend/data/release_os.db

# Restart
./start.sh
```

### Clearing Generated Files

```bash
rm -rf backend/data/previews/*
rm -rf backend/data/covers/*
```

### Updating Dependencies

Backend:
```bash
cd backend
source venv/bin/activate
pip install --upgrade package_name
pip freeze > requirements.txt
```

Frontend:
```bash
cd frontend
npm update package_name
```

### Checking Logs

```bash
# View backend logs
tail -f backend.log

# View frontend logs
tail -f frontend.log

# View watcher logs
tail -f watcher.log
```

## Debugging

### Backend Issues

1. Check FastAPI logs in terminal or backend.log
2. Visit http://localhost:8000/docs for interactive API testing
3. Add print statements or use Python debugger:

```python
import pdb; pdb.set_trace()  # Breakpoint
```

### Frontend Issues

1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for API calls
4. Use React DevTools extension

### Database Issues

```bash
# Connect to database
cd backend
sqlite3 data/release_os.db

# Run queries
SELECT * FROM projects;
.tables
.schema projects
.exit
```

## Performance Optimization

### Backend

- Use database indexes for common queries
- Implement caching with Redis
- Use async/await for I/O operations
- Profile with `cProfile`

### Frontend

- Implement virtual scrolling for large lists
- Use React.memo for expensive components
- Lazy load images
- Debounce search input

### Audio Processing

- Process in parallel with multiprocessing
- Cache analysis results
- Use lower sample rates when possible
- Implement progressive loading

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Document with docstrings
- Keep functions small and focused

```python
def parse_project(file_path: str) -> dict:
    """Parse an Ableton project file.

    Args:
        file_path: Path to .als file

    Returns:
        Dictionary with project metadata
    """
    # Implementation
```

### JavaScript (Frontend)

- Use ESLint configuration
- Prefer functional components
- Use descriptive variable names
- Keep components under 300 lines

## Deployment

### Electron App (Desktop)

1. Install Electron:
```bash
npm install --save-dev electron electron-builder
```

2. Create electron.js wrapper
3. Build:
```bash
npm run electron:build
```

### Docker Container

Create Dockerfile:
```dockerfile
FROM python:3.10
WORKDIR /app
COPY backend/ ./backend/
RUN pip install -r backend/requirements.txt
CMD ["python", "backend/main.py"]
```

Build:
```bash
docker build -t release-os .
docker run -p 8000:8000 release-os
```

## Contributing Guidelines

1. Create a feature branch
2. Write tests for new features
3. Update documentation
4. Submit pull request with description

## Troubleshooting Development Issues

### Port Already in Use

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Python Import Errors

```bash
# Make sure venv is activated
cd backend
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Node Module Issues

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### FFmpeg Issues

```bash
# Reinstall FFmpeg
brew reinstall ffmpeg

# Verify installation
which ffmpeg
ffmpeg -version
```

## Useful Commands

```bash
# Format Python code
black backend/

# Lint JavaScript
npm run lint

# Type check (if using TypeScript)
npm run type-check

# Build frontend for production
npm run build

# Run backend tests
pytest backend/

# Check for security issues
pip-audit
npm audit
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [librosa Documentation](https://librosa.org/doc/latest/)
- [WaveSurfer.js Documentation](https://wavesurfer.xyz)
- [Tailwind CSS Documentation](https://tailwindcss.com)

## Getting Help

1. Check the [README](README.md) and [QUICKSTART](QUICKSTART.md)
2. Review this development guide
3. Check API docs at http://localhost:8000/docs
4. Look at existing code for patterns
5. Search issues on GitHub (if repository exists)
