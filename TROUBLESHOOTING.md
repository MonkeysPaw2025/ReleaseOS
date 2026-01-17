# Troubleshooting Guide

## Common Issues and Solutions

### Project Shows "No audio files found"

**Symptoms:**
- Project appears in Release OS
- Shows metadata (BPM, name)
- Can't play preview
- Shows warning: "No audio files found"

**Cause:**
The Ableton project (.als file) references audio files that don't exist at the expected locations. This commonly happens when:
- You moved the .als file without moving the audio samples
- Audio files were in a different folder structure
- Samples were from Splice/sample packs that aren't downloaded
- The project uses relative paths that don't resolve correctly

**Solution 1: Move Audio Files**
1. Open the .als file in Ableton Live
2. Note which samples are missing (Ableton will show them in orange)
3. Locate the missing audio files on your computer
4. In Ableton: Right-click on missing samples → "Manage Files" → Locate the files
5. Save the project
6. Click "Scan Projects" in Release OS

**Solution 2: Consolidate Project**
1. Open the project in Ableton Live
2. Go to File → Collect All and Save
3. This creates a new folder with all audio embedded
4. Move this consolidated project to ~/Music/ReleaseDrop
5. Click "Scan Projects" in Release OS

**Solution 3: Export a Bounce**
If you just want a preview without finding all samples:
1. Open the project in Ableton Live
2. Export audio: File → Export Audio/Video
3. Save as MP3 in the same folder as the .als file
4. Release OS will use this as the preview source

**Checking What's Missing:**
```bash
cd ~/Developer/release-os/backend
source venv/bin/activate
python ableton_parser.py "/path/to/your/project.als"
```

This will show you which audio files are referenced and whether they exist.

---

### Preview Generation is Slow

**Symptoms:**
- Projects take a long time to appear after scanning
- Backend seems to hang

**Cause:**
Audio processing (preview generation and waveform creation) is CPU-intensive.

**Solutions:**
1. Be patient - large audio files can take 10-30 seconds to process
2. Check backend.log for progress
3. Only import projects you actually want to work on
4. Consider reducing preview duration in audio_processor.py (change from 30 to 15 seconds)

---

### FFmpeg Errors

**Symptoms:**
- Backend shows "FFmpeg not found" errors
- Previews don't generate

**Solution:**
```bash
# Install FFmpeg
brew install ffmpeg

# Verify installation
ffmpeg -version

# Restart Release OS
./stop.sh
./start.sh
```

---

### Database Corruption

**Symptoms:**
- Projects disappear randomly
- Duplicate projects appear
- API returns database errors

**Solution:**
```bash
# Stop all processes
./stop.sh

# Backup existing database
cp backend/data/release_os.db backend/data/release_os.db.backup

# Delete database
rm backend/data/release_os.db

# Restart - database will be recreated
./start.sh

# Rescan projects
# Click "Scan Projects" in the UI
```

---

### Port Already in Use

**Symptoms:**
- Backend fails to start
- Error: "Address already in use"

**Solution:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or find and kill on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9

# Restart
./start.sh
```

---

### Frontend Won't Load

**Symptoms:**
- Blank page at http://localhost:5173
- Console shows connection errors

**Solutions:**

1. **Check if backend is running:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

2. **Check frontend logs:**
   ```bash
   tail -f frontend.log
   ```

3. **Clear browser cache:**
   - Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

4. **Reinstall frontend dependencies:**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run dev
   ```

---

### Waveforms Not Generating

**Symptoms:**
- Projects show music note emoji instead of waveform
- No images in backend/data/covers/

**Causes:**
1. Audio files don't exist (see first issue)
2. librosa/PIL errors

**Solutions:**

1. **Check backend logs:**
   ```bash
   tail -f backend.log
   ```

2. **Reinstall audio dependencies:**
   ```bash
   cd backend
   source venv/bin/activate
   pip install --force-reinstall librosa soundfile pillow
   ```

3. **Test manually:**
   ```bash
   cd backend
   source venv/bin/activate
   python audio_processor.py /path/to/audio/file.mp3
   ```

---

### Projects Not Auto-Importing

**Symptoms:**
- Drop .als files into ~/Music/ReleaseDrop
- Nothing happens
- Projects don't appear

**Causes:**
1. Folder watcher isn't running
2. .als file is in a subfolder

**Solutions:**

1. **Check if watcher is running:**
   ```bash
   ps aux | grep folder_watcher
   ```

2. **Start watcher manually:**
   ```bash
   cd backend
   source venv/bin/activate
   python folder_watcher.py
   ```

3. **Use manual scan instead:**
   - Click "Scan Projects" button in the UI
   - This works even if watcher isn't running

4. **Check file structure:**
   ```bash
   # Watcher searches recursively, so this should work:
   ~/Music/ReleaseDrop/MyProject/Ableton Project Info/MyProject.als

   # But it's easier if files are at the root:
   ~/Music/ReleaseDrop/MyProject.als
   ```

---

### High CPU Usage

**Symptoms:**
- Computer slows down after starting Release OS
- Fans spinning loudly

**Causes:**
- Multiple preview generations happening simultaneously
- Large audio files being processed

**Solutions:**

1. **Limit concurrent processing:**
   - Only scan when you're ready to wait
   - Don't drop many projects at once

2. **Reduce preview quality:**
   Edit backend/audio_processor.py line ~40:
   ```python
   # Change from 192k to 128k
   '-ab', '128k',
   ```

3. **Skip waveform generation:**
   Comment out waveform generation in backend/main.py

---

### Permission Errors

**Symptoms:**
- Can't write to backend/data/
- Can't read .als files

**Solutions:**

```bash
# Fix permissions
chmod -R 755 ~/Developer/release-os/backend/data
chmod 644 ~/Music/ReleaseDrop/*.als

# Make sure watch folder is accessible
ls -la ~/Music/ReleaseDrop
```

---

## Getting More Help

1. **Check API documentation:**
   http://localhost:8000/docs

2. **View backend logs:**
   ```bash
   tail -f backend.log
   ```

3. **View frontend logs:**
   ```bash
   tail -f frontend.log
   ```

4. **Check Python environment:**
   ```bash
   cd backend
   source venv/bin/activate
   pip list
   ```

5. **Check Node environment:**
   ```bash
   cd frontend
   npm list
   ```

6. **Full reset (nuclear option):**
   ```bash
   ./stop.sh
   rm -rf backend/data backend/venv
   rm -rf frontend/node_modules
   ./setup.sh
   ./start.sh
   ```

---

## Debug Mode

For more detailed logs:

**Backend:**
```bash
cd backend
source venv/bin/activate
export LOG_LEVEL=DEBUG
python main.py
```

**Frontend:**
```bash
cd frontend
npm run dev -- --debug
```

---

## Common Warning Messages (Safe to Ignore)

These warnings are normal and don't affect functionality:

- `DeprecationWarning: on_event is deprecated` - Cosmetic, will be fixed in next version
- `DeprecationWarning: datetime.datetime.utcnow()` - Cosmetic, will be fixed in next version
- `The post-install step did not complete successfully` (during FFmpeg install) - FFmpeg still works

---

## Performance Tips

1. **Only import projects you're actively working on**
2. **Use status filters to focus on specific pipeline stages**
3. **Delete old/abandoned projects**
4. **Keep audio files in consistent locations**
5. **Use Ableton's "Collect All and Save" feature**
