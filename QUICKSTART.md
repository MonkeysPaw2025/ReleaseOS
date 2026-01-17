# Quick Start Guide

Get Release OS running in 5 minutes.

## Prerequisites Check

```bash
# Check Python version (need 3.10+)
python3 --version

# Check Node.js version (need 18+)
node --version

# Install FFmpeg if not installed
brew install ffmpeg
```

## One-Time Setup

```bash
cd ~/Developer/release-os

# 1. Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# 2. Setup frontend
cd frontend
npm install
cd ..
```

## Running the App

### Option 1: Automatic (Recommended)

```bash
./start.sh
```

This starts everything and opens the app. To stop:

```bash
./stop.sh
```

### Option 2: Manual (3 terminals)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Watcher (optional):**
```bash
cd backend
source venv/bin/activate
python folder_watcher.py
```

## First Use

1. Open http://localhost:5173 in your browser
2. Drop some Ableton .als files into `~/Music/ReleaseDrop`
3. Click "Scan Projects" to import them
4. Wait for previews to generate (watch backend terminal)
5. Click any project to play its preview
6. Click the status bars to move projects through your workflow

## Test It Out

Want to test without real projects? Create a simple test:

```bash
# The watcher will detect this if it's running
# Or click "Scan Projects" in the UI
```

If you have existing Ableton projects:

```bash
# Copy some to the watch folder
cp ~/Music/MyProject.als ~/Music/ReleaseDrop/
```

## Troubleshooting

**"No projects found"**
- Make sure .als files are in `~/Music/ReleaseDrop`
- Click "Scan Projects" to manually import
- Check backend terminal for errors

**Backend won't start**
- Make sure port 8000 is not in use
- Check you activated the virtual environment
- Run `pip install -r requirements.txt` again

**Frontend won't start**
- Make sure port 5173 is not in use
- Run `npm install` again
- Check Node.js version is 18+

**Previews not generating**
- Make sure FFmpeg is installed: `ffmpeg -version`
- Check that audio files referenced in .als files exist
- Look at backend terminal for specific errors

## Next Steps

Read the full [README.md](README.md) for:
- Detailed API documentation
- How the audio processing works
- Roadmap and future features
- Contributing guidelines
