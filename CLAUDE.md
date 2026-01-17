# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Release OS is a desktop application for music producers that solves the "shipping problem" by turning DAW chaos into released music. It parses Ableton .als files, generates audio previews/waveforms, and manages a workflow pipeline from Idea → Exported → Packaged → Released.

## Development Commands

### Quick Start
```bash
./setup.sh    # One-time setup (checks prerequisites, installs dependencies)
./start.sh    # Start all services (backend, frontend, folder watcher)
./stop.sh     # Stop all services
```

### Manual Start (3 terminals)
```bash
# Terminal 1 - Backend API (http://localhost:8000)
cd backend && source venv/bin/activate && python main.py

# Terminal 2 - Frontend (http://localhost:5173)
cd frontend && npm run dev

# Terminal 3 - Folder Watcher (optional, monitors ~/Music/ReleaseDrop)
cd backend && source venv/bin/activate && python folder_watcher.py
```

### Lint
```bash
cd frontend && npm run lint
```

### Build Frontend
```bash
cd frontend && npm run build
```

### Database Operations
```bash
# Reset database (deletes all data)
rm backend/data/release_os.db

# Inspect database
sqlite3 backend/data/release_os.db "SELECT * FROM projects;"
```

## Architecture

### Backend (Python/FastAPI)
- `main.py` - All API endpoints and app initialization (~600 lines)
- `database.py` - SQLAlchemy models (Project, SoundCloudAuth)
- `ableton_parser.py` - Decompresses and parses .als files (gzipped XML)
- `audio_processor.py` - RMS analysis, preview extraction (FFmpeg), waveform generation (PIL)
- `folder_watcher.py` - watchdog-based file system monitoring

### Frontend (React/Vite)
- `App.jsx` - Single-file React app with all components (~800 lines)
- Uses WaveSurfer.js for audio playback, Tailwind CSS for styling, React Query for state

### Data Flow
1. User drops .als file into `~/Music/ReleaseDrop`
2. Folder watcher detects file, triggers `POST /projects/scan`
3. Backend parses .als XML, extracts metadata (BPM, key, audio clips)
4. Background task generates 30-second MP3 preview (highest RMS energy section)
5. Background task generates waveform PNG visualization
6. Frontend polls `/projects` endpoint and displays cards

### Key Directories
- `backend/data/` - SQLite database, generated previews and covers
- `frontend/dist/` - Production build output

## API Documentation

Interactive docs available at http://localhost:8000/docs when backend is running.

Key endpoints:
- `GET /projects` - List with filters (status, search, min_bpm, max_bpm)
- `POST /projects/scan` - Trigger manual folder scan
- `PATCH /projects/{id}` - Update status/genre/vibe/tags
- `POST /projects/{id}/cover` - Upload cover art
- `POST /projects/{id}/audio` - Upload audio file

## Schema Changes

No migration system is currently configured. To add a database field:
1. Update model in `backend/database.py`
2. Delete `backend/data/release_os.db`
3. Restart backend (tables recreate automatically)

## External Dependencies

- FFmpeg required for audio processing (`brew install ffmpeg`)
- Python 3.10+ with venv at `backend/venv/`
- Node.js 18+

## Environment Variables

Optional SoundCloud integration requires `backend/.env`:
```
SOUNDCLOUD_CLIENT_ID=your_client_id
SOUNDCLOUD_CLIENT_SECRET=your_client_secret
SOUNDCLOUD_REDIRECT_URI=http://localhost:8000/soundcloud/callback
```
