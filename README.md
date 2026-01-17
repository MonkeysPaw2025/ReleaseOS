# Release OS

A desktop application for music producers that solves the "shipping problem" by turning DAW chaos into released music.

## The Problem

Producers have dozens of unfinished Ableton projects sitting in folders. They don't fail at making music - they fail at finishing, packaging, and releasing consistently. The bottleneck is operational, not creative.

## The Solution

Release OS provides:

- **Library Browser**: Auto-parses Ableton .als files and displays all projects with metadata (BPM, key, audio clips)
- **Audio Previews**: Automatically generates 30-second previews from the most energetic section of your tracks
- **Waveform Visualization**: Auto-generated waveform covers for projects without artwork
- **Smart Filtering**: Filter by BPM range, status, or search by name
- **Workflow Pipeline**: Move projects through stages: Idea → Exported → Packaged → Released
- **Auto-Import**: Watches ~/Music/ReleaseDrop and automatically imports new projects
- **SoundCloud Integration**: One-click upload to SoundCloud with OAuth authentication (see [SOUNDCLOUD_SETUP.md](SOUNDCLOUD_SETUP.md))

## Tech Stack

- **Backend**: Python with FastAPI, SQLAlchemy, librosa, FFmpeg
- **Frontend**: React with Vite, Tailwind CSS, WaveSurfer.js
- **Database**: SQLite

## Prerequisites

- Python 3.10+
- Node.js 18+
- FFmpeg (for audio processing)

Install FFmpeg on macOS:
```bash
brew install ffmpeg
```

## Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 3. Create Watch Folder

```bash
mkdir -p ~/Music/ReleaseDrop
```

## Running the Application

You need to run three processes:

### Terminal 1: Backend API

```bash
cd backend
source venv/bin/activate
python main.py
```

The API will be available at http://localhost:8000

### Terminal 2: Folder Watcher (Optional)

For automatic project detection:

```bash
cd backend
source venv/bin/activate
python folder_watcher.py
```

### Terminal 3: Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:5173

## Usage

### Import Projects

1. **Automatic**: Drop Ableton .als files into `~/Music/ReleaseDrop`
   - If folder watcher is running, projects will be imported automatically
   - Previews and waveforms will be generated in the background

2. **Manual**: Click the "Scan Projects" button in the UI to manually scan the folder

### Browse Projects

- View all projects in a grid with waveform visualizations
- Click on any project card to play its 30-second preview
- Use filters to find specific projects:
  - Filter by workflow status (Idea, Exported, Packaged, Released)
  - Search by project name
  - Filter by BPM range

### Workflow Management

Each project has a status indicator with 4 stages:

- **Idea** (Blue): Initial unfinished projects
- **Exported** (Yellow): Exported to audio files
- **Packaged** (Orange): Mastered and packaged with metadata
- **Released** (Green): Published to streaming platforms

Click the colored bars at the bottom of each project card to update its status.

## Project Structure

```
release-os/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # SQLAlchemy models
│   ├── ableton_parser.py    # .als file parser
│   ├── audio_processor.py   # Audio preview & waveform generation
│   ├── folder_watcher.py    # Auto-import via watchdog
│   ├── requirements.txt     # Python dependencies
│   └── data/
│       ├── release_os.db    # SQLite database
│       ├── previews/        # Generated audio previews
│       └── covers/          # Generated waveform images
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   └── main.jsx         # Entry point
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
└── README.md
```

## API Endpoints

- `GET /projects` - List all projects with optional filters
  - Query params: `status`, `search`, `min_bpm`, `max_bpm`
- `POST /projects/scan` - Manually scan watch folder for projects
- `PATCH /projects/{id}` - Update project metadata
  - Body params: `status`, `genre`, `vibe`, `tags`
- `DELETE /projects/{id}` - Delete a project
- `GET /previews/{id}.mp3` - Audio preview file
- `GET /covers/{id}.png` - Waveform cover image

## How It Works

### Ableton Project Parsing

The system decompresses .als files (which are gzipped XML) and extracts:
- Project name
- BPM (tempo)
- Musical key (if available)
- Referenced audio files with durations

### Audio Preview Generation

1. Finds the longest audio clip in the project
2. Analyzes audio energy using RMS to find the most interesting 30-second section
3. Uses FFmpeg to extract that section as an MP3 preview

### Waveform Visualization

1. Loads audio file using librosa
2. Downsamples to match image width
3. Calculates amplitude peaks
4. Renders as a symmetric waveform image using PIL

## Roadmap

- [ ] Add genre/vibe tagging with autocomplete
- [ ] Batch export projects to audio files
- [ ] Integration with streaming platforms (Spotify, SoundCloud)
- [ ] Social media post generation
- [ ] Collaboration features (share projects with others)
- [ ] Mobile app for on-the-go browsing

## Troubleshooting

### FFmpeg not found
Make sure FFmpeg is installed:
```bash
brew install ffmpeg
```

### No projects showing up
1. Check that projects are in `~/Music/ReleaseDrop`
2. Click "Scan Projects" to manually trigger import
3. Check backend terminal for error messages

### Audio previews not generating
1. Ensure the .als file references audio clips that exist
2. Check that audio files are in the correct relative path to the .als file
3. Look at backend logs for specific errors

### Frontend can't connect to backend
1. Make sure backend is running on port 8000
2. Check for CORS errors in browser console
3. Verify both servers are running

## Contributing

This is a personal project, but suggestions and feedback are welcome!

## License

MIT
