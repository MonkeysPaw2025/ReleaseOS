import subprocess
import os
import librosa
import numpy as np
from PIL import Image, ImageDraw
import soundfile as sf


def generate_audio_preview(audio_file_path, output_path, duration=30, start_offset=0):
    """
    Generate a 30-second audio preview using FFmpeg

    Args:
        audio_file_path: Path to the source audio file
        output_path: Path where the preview should be saved
        duration: Duration of the preview in seconds (default 30)
        start_offset: Where to start the preview from (default 0 - beginning)

    Returns:
        Path to the generated preview file
    """
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Use FFmpeg to extract audio preview
    # -ss: start offset, -t: duration, -y: overwrite output
    cmd = [
        'ffmpeg',
        '-i', audio_file_path,
        '-ss', str(start_offset),
        '-t', str(duration),
        '-acodec', 'libmp3lame',
        '-ab', '192k',
        '-y',
        output_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg error: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Please install FFmpeg: brew install ffmpeg")


def generate_waveform_image(audio_file_path, output_image_path, width=800, height=400,
                            bg_color=(26, 26, 46), wave_color=(99, 102, 241)):
    """
    Generate a waveform visualization image from an audio file

    Args:
        audio_file_path: Path to the audio file
        output_image_path: Path where the waveform image should be saved
        width: Image width in pixels
        height: Image height in pixels
        bg_color: Background color RGB tuple
        wave_color: Waveform color RGB tuple

    Returns:
        Path to the generated waveform image
    """
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

    try:
        # Load audio file
        y, sr = librosa.load(audio_file_path, sr=22050, mono=True, duration=30)

        # Downsample to match image width
        samples_per_pixel = len(y) // width
        if samples_per_pixel == 0:
            samples_per_pixel = 1

        waveform = []
        for i in range(0, len(y), samples_per_pixel):
            chunk = y[i:i + samples_per_pixel]
            if len(chunk) > 0:
                waveform.append(np.max(np.abs(chunk)))

        # Normalize waveform
        if len(waveform) > 0:
            max_val = max(waveform)
            if max_val > 0:
                waveform = [w / max_val for w in waveform]

        # Create image
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Draw waveform
        center_y = height // 2
        for x, amplitude in enumerate(waveform[:width]):
            bar_height = int(amplitude * (height / 2) * 0.9)  # 90% of half height

            # Draw symmetrical waveform
            draw.line(
                [(x, center_y - bar_height), (x, center_y + bar_height)],
                fill=wave_color,
                width=1
            )

        # Save image
        img.save(output_image_path, 'PNG')
        return output_image_path

    except Exception as e:
        raise RuntimeError(f"Error generating waveform: {e}")


def get_audio_duration(audio_file_path):
    """Get the duration of an audio file in seconds"""
    try:
        y, sr = librosa.load(audio_file_path, sr=None, duration=1)
        info = sf.info(audio_file_path)
        return info.duration
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return 0


def find_best_preview_start(audio_file_path, preview_duration=30):
    """
    Analyze audio to find the most interesting section for preview
    (e.g., section with highest energy)

    Returns:
        Start time in seconds for the preview
    """
    try:
        # Load audio
        y, sr = librosa.load(audio_file_path, sr=22050)
        duration = len(y) / sr

        # If audio is shorter than preview duration, start from beginning
        if duration <= preview_duration:
            return 0

        # Calculate RMS energy in chunks
        hop_length = sr * 2  # 2-second chunks
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

        # Find the chunk with highest energy
        max_energy_idx = np.argmax(rms)
        start_time = (max_energy_idx * hop_length) / sr

        # Ensure we don't go past the end
        if start_time + preview_duration > duration:
            start_time = max(0, duration - preview_duration)

        return start_time

    except Exception as e:
        print(f"Error finding best preview start: {e}")
        return 0


if __name__ == "__main__":
    # Test the audio processor
    import sys

    if len(sys.argv) < 2:
        print("Usage: python audio_processor.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]
    preview_path = "test_preview.mp3"
    waveform_path = "test_waveform.png"

    print(f"Processing: {audio_file}")

    # Generate preview
    try:
        start = find_best_preview_start(audio_file)
        print(f"Best preview start: {start:.2f}s")

        generate_audio_preview(audio_file, preview_path, start_offset=start)
        print(f"✓ Preview generated: {preview_path}")

        generate_waveform_image(audio_file, waveform_path)
        print(f"✓ Waveform generated: {waveform_path}")

    except Exception as e:
        print(f"✗ Error: {e}")
