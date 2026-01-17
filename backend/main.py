from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from datetime import datetime, timedelta
from typing import Optional, List
import secrets

from database import init_db, get_db, Project, SoundCloudAuth, SessionLocal
from ableton_parser import parse_ableton_project, find_longest_audio_clip
from audio_processor import (
    generate_audio_preview,
    generate_waveform_image,
    find_best_preview_start
)
from soundcloud_integration import (
    get_authorization_url,
    exchange_code_for_token,
    get_user_info,
    upload_track,
    is_authenticated,
    get_authenticated_user,
    disconnect as soundcloud_disconnect
)

app = FastAPI(title="Release OS API", version="0.1.0")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("data/previews", exist_ok=True)
os.makedirs("data/covers", exist_ok=True)

# Mount static files
app.mount("/previews", StaticFiles(directory="data/previews"), name="previews")
app.mount("/covers", StaticFiles(directory="data/covers"), name="covers")

WATCH_FOLDER = os.path.expanduser("~/Music/ReleaseDrop")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    # Create watch folder if it doesn't exist
    os.makedirs(WATCH_FOLDER, exist_ok=True)


@app.get("/")
def read_root():
    return {"status": "Release OS API running", "version": "0.1.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/projects")
def get_projects(
    status: Optional[str] = None,
    search: Optional[str] = None,
    min_bpm: Optional[int] = None,
    max_bpm: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all projects with optional filtering"""
    query = db.query(Project)

    if status:
        query = query.filter(Project.status == status)

    if search:
        query = query.filter(Project.name.contains(search))

    if min_bpm:
        query = query.filter(Project.bpm >= min_bpm)

    if max_bpm:
        query = query.filter(Project.bpm <= max_bpm)

    projects = query.order_by(Project.updated_at.desc()).all()

    return [{
        "id": p.id,
        "name": p.name,
        "bpm": p.bpm,
        "key": p.key,
        "status": p.status,
        "audio_clips": p.audio_clips_count,
        "preview_url": f"/previews/{p.id}.mp3" if p.preview_path else None,
        "cover_url": f"/covers/{p.id}.png" if p.cover_path else None,
        "genre": p.genre,
        "vibe": p.vibe,
        "tags": p.tags.split(",") if p.tags else [],
        "soundcloud_url": p.soundcloud_url,
        "soundcloud_uploaded": p.soundcloud_uploaded_at.isoformat() if p.soundcloud_uploaded_at else None,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat()
    } for p in projects]


@app.post("/projects/scan")
def scan_projects(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Scan watch folder and import/update projects"""
    found_projects = []
    scanned_paths = set()

    # Walk through watch folder
    for root, dirs, files in os.walk(WATCH_FOLDER):
        for file in files:
            if file.endswith('.als'):
                als_path = os.path.join(root, file)
                scanned_paths.add(als_path)

                try:
                    # Check if project already exists
                    existing = db.query(Project).filter(Project.als_path == als_path).first()

                    # Parse project metadata
                    parsed = parse_ableton_project(als_path)
                    longest_clip = find_longest_audio_clip(parsed)

                    if existing:
                        # Update existing project
                        existing.bpm = parsed['bpm']
                        existing.audio_clips_count = len(parsed['audio_clips'])
                        existing.longest_clip_path = longest_clip['path'] if longest_clip else None
                        existing.updated_at = datetime.utcnow()
                        db.commit()
                        found_projects.append(existing.id)
                    else:
                        # Create new project
                        new_project = Project(
                            name=parsed['name'],
                            als_path=als_path,
                            bpm=parsed['bpm'],
                            key=parsed['key'],
                            audio_clips_count=len(parsed['audio_clips']),
                            longest_clip_path=longest_clip['path'] if longest_clip else None,
                            status="idea"
                        )
                        db.add(new_project)
                        db.commit()
                        db.refresh(new_project)
                        found_projects.append(new_project.id)

                        # Generate preview and waveform in background
                        if longest_clip and longest_clip['exists']:
                            background_tasks.add_task(
                                generate_project_assets,
                                new_project.id,
                                longest_clip['path']
                            )

                except Exception as e:
                    print(f"Error processing {als_path}: {e}")

    # Remove projects that no longer exist in watch folder
    all_projects = db.query(Project).all()
    for project in all_projects:
        if project.als_path not in scanned_paths:
            db.delete(project)

    db.commit()

    return {
        "scanned": len(found_projects),
        "message": f"Scanned {len(found_projects)} projects"
    }


def generate_project_assets(project_id: int, audio_file_path: str):
    """Background task to generate preview and waveform for a project"""
    from database import SessionLocal

    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return

        preview_path = f"data/previews/{project_id}.mp3"
        cover_path = f"data/covers/{project_id}.png"

        # Find best preview start time
        start_time = find_best_preview_start(audio_file_path)

        # Generate preview
        generate_audio_preview(audio_file_path, preview_path, start_offset=start_time)
        project.preview_path = preview_path

        # Generate waveform cover
        generate_waveform_image(audio_file_path, cover_path)
        project.cover_path = cover_path

        db.commit()
        print(f"✓ Generated assets for project {project_id}: {project.name}")

    except Exception as e:
        print(f"Error generating assets for project {project_id}: {e}")
    finally:
        db.close()


@app.patch("/projects/{project_id}")
def update_project(
    project_id: int,
    status: Optional[str] = None,
    genre: Optional[str] = None,
    vibe: Optional[str] = None,
    tags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update project metadata"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if status:
        project.status = status
    if genre:
        project.genre = genre
    if vibe:
        project.vibe = vibe
    if tags is not None:
        project.tags = tags

    project.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Project updated", "id": project_id}


@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project from the database"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete associated files
    if project.preview_path and os.path.exists(project.preview_path):
        os.remove(project.preview_path)
    if project.cover_path and os.path.exists(project.cover_path):
        os.remove(project.cover_path)

    db.delete(project)
    db.commit()

    return {"message": "Project deleted", "id": project_id}


# SoundCloud Integration Endpoints

@app.get("/soundcloud/status")
def soundcloud_status():
    """Check SoundCloud connection status"""
    authenticated = is_authenticated()
    user = get_authenticated_user() if authenticated else None

    return {
        "connected": authenticated,
        "user": user
    }


@app.get("/soundcloud/connect")
def soundcloud_connect():
    """Initiate SoundCloud OAuth flow"""
    state = secrets.token_urlsafe(32)
    auth_url = get_authorization_url(state)

    return {
        "auth_url": auth_url,
        "message": "Visit this URL to connect your SoundCloud account"
    }


@app.get("/soundcloud/callback")
def soundcloud_callback(code: str = Query(...), state: str = Query(...), db: Session = Depends(get_db)):
    """Handle SoundCloud OAuth callback"""
    try:
        # Exchange code for token
        token_data = exchange_code_for_token(code)

        # Get user info
        user_info = get_user_info(token_data["access_token"])

        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 21600))

        # Store or update authentication
        existing_auth = db.query(SoundCloudAuth).first()

        if existing_auth:
            existing_auth.access_token = token_data["access_token"]
            existing_auth.refresh_token = token_data.get("refresh_token")
            existing_auth.expires_at = expires_at
            existing_auth.user_id = str(user_info["id"])
            existing_auth.username = user_info.get("username", "Unknown")
            existing_auth.updated_at = datetime.utcnow()
        else:
            new_auth = SoundCloudAuth(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_at=expires_at,
                user_id=str(user_info["id"]),
                username=user_info.get("username", "Unknown")
            )
            db.add(new_auth)

        db.commit()

        # Redirect to frontend with success message
        return RedirectResponse(url="http://localhost:5173?soundcloud=connected")

    except Exception as e:
        print(f"Error in SoundCloud callback: {e}")
        return RedirectResponse(url=f"http://localhost:5173?soundcloud=error&message={str(e)}")


@app.post("/soundcloud/disconnect")
def soundcloud_disconnect_endpoint():
    """Disconnect SoundCloud account"""
    soundcloud_disconnect()
    return {"message": "SoundCloud account disconnected"}


@app.post("/projects/{project_id}/upload-soundcloud")
def upload_project_to_soundcloud(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Upload a project to SoundCloud"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Not connected to SoundCloud. Please connect your account first.")

    # Check if project has audio to upload
    if not project.preview_path or not os.path.exists(project.preview_path):
        raise HTTPException(
            status_code=400,
            detail="No audio preview available. Cannot upload to SoundCloud."
        )

    # Upload in background
    background_tasks.add_task(
        upload_project_background,
        project_id,
        project.preview_path,
        project.cover_path
    )

    return {
        "message": "Upload started",
        "project_id": project_id
    }


def upload_project_background(project_id: int, audio_path: str, artwork_path: Optional[str] = None):
    """Background task to upload project to SoundCloud"""
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return

        print(f"Uploading {project.name} to SoundCloud...")

        # Prepare track metadata
        description = f"Created with Release OS"
        if project.bpm:
            description += f"\nBPM: {project.bpm}"
        if project.key:
            description += f"\nKey: {project.key}"

        tags = []
        if project.tags:
            tags = project.tags.split(",")
        if project.genre:
            tags.append(project.genre)

        # Upload track
        track_data = upload_track(
            audio_file_path=audio_path,
            title=project.name,
            description=description,
            genre=project.genre or "",
            tag_list=" ".join(tags),
            sharing="private",  # Start as private, user can make public on SoundCloud
            artwork_path=artwork_path if artwork_path and os.path.exists(artwork_path) else None,
            bpm=project.bpm,
            key_signature=project.key
        )

        # Update project with SoundCloud URL
        project.soundcloud_url = track_data.get("permalink_url")
        project.soundcloud_uploaded_at = datetime.utcnow()
        project.status = "released"  # Move to released status
        project.updated_at = datetime.utcnow()
        db.commit()

        print(f"✓ Uploaded to SoundCloud: {project.soundcloud_url}")

    except Exception as e:
        print(f"Error uploading to SoundCloud: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)