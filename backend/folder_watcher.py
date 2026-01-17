import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from database import SessionLocal, Project
from ableton_parser import parse_ableton_project, find_longest_audio_clip
from audio_processor import generate_audio_preview, generate_waveform_image, find_best_preview_start
from datetime import datetime


class AbletonProjectHandler(FileSystemEventHandler):
    """Handler for file system events related to Ableton projects"""

    def __init__(self, watch_folder):
        self.watch_folder = watch_folder
        super().__init__()

    def on_created(self, event):
        """Called when a file is created"""
        if event.is_directory:
            return

        if event.src_path.endswith('.als'):
            print(f"\n📁 New Ableton project detected: {event.src_path}")
            self.process_project(event.src_path)

    def on_modified(self, event):
        """Called when a file is modified"""
        if event.is_directory:
            return

        if event.src_path.endswith('.als'):
            print(f"\n📝 Ableton project modified: {event.src_path}")
            self.process_project(event.src_path, is_update=True)

    def on_deleted(self, event):
        """Called when a file is deleted"""
        if event.is_directory:
            return

        if event.src_path.endswith('.als'):
            print(f"\n🗑️  Ableton project deleted: {event.src_path}")
            self.remove_project(event.src_path)

    def process_project(self, als_path, is_update=False):
        """Process an Ableton project file"""
        db = SessionLocal()
        try:
            # Check if project already exists
            existing = db.query(Project).filter(Project.als_path == als_path).first()

            # Parse project metadata
            parsed = parse_ableton_project(als_path)
            longest_clip = find_longest_audio_clip(parsed)

            if existing:
                # Update existing project
                print(f"  Updating existing project: {parsed['name']}")
                existing.name = parsed['name']
                existing.bpm = parsed['bpm']
                existing.key = parsed['key']
                existing.audio_clips_count = len(parsed['audio_clips'])
                existing.longest_clip_path = longest_clip['path'] if longest_clip else None
                existing.updated_at = datetime.utcnow()
                db.commit()

                project_id = existing.id
            else:
                # Create new project
                print(f"  Creating new project: {parsed['name']}")
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

                project_id = new_project.id

            # Generate preview and waveform
            if longest_clip and longest_clip['exists']:
                print(f"  Generating audio preview and waveform...")
                self.generate_assets(db, project_id, longest_clip['path'])
                print(f"  ✅ Project processed successfully!")
            else:
                print(f"  ⚠️  No audio clips found - skipping preview generation")

        except Exception as e:
            print(f"  ❌ Error processing project: {e}")
        finally:
            db.close()

    def generate_assets(self, db, project_id, audio_file_path):
        """Generate preview and waveform for a project"""
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

        except Exception as e:
            print(f"  ❌ Error generating assets: {e}")

    def remove_project(self, als_path):
        """Remove a project from the database when its file is deleted"""
        db = SessionLocal()
        try:
            project = db.query(Project).filter(Project.als_path == als_path).first()
            if project:
                # Delete associated files
                if project.preview_path and os.path.exists(project.preview_path):
                    os.remove(project.preview_path)
                if project.cover_path and os.path.exists(project.cover_path):
                    os.remove(project.cover_path)

                db.delete(project)
                db.commit()
                print(f"  ✅ Project removed from database")
        except Exception as e:
            print(f"  ❌ Error removing project: {e}")
        finally:
            db.close()


def start_watching(watch_folder):
    """Start watching a folder for Ableton projects"""
    # Ensure folder exists
    os.makedirs(watch_folder, exist_ok=True)

    print("=" * 70)
    print("🎵 Release OS - Folder Watcher")
    print("=" * 70)
    print(f"\n👀 Watching folder: {watch_folder}")
    print("\nWaiting for Ableton projects to be added, modified, or deleted...")
    print("Press Ctrl+C to stop\n")

    event_handler = AbletonProjectHandler(watch_folder)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping folder watcher...")
        observer.stop()

    observer.join()
    print("✅ Folder watcher stopped")


if __name__ == "__main__":
    import sys

    watch_folder = os.path.expanduser("~/Music/ReleaseDrop")

    if len(sys.argv) > 1:
        watch_folder = sys.argv[1]

    start_watching(watch_folder)
