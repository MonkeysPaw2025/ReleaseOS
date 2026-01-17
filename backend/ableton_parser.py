import gzip
import xml.etree.ElementTree as ET
import os

def parse_ableton_project(als_file_path):
    """
    Parse an Ableton .als file and extract metadata
    
    Returns dict with:
    - name: project name
    - bpm: tempo
    - key: musical key (if available)
    - audio_clips: list of audio file paths referenced
    """
    
    if not os.path.exists(als_file_path):
        raise FileNotFoundError(f"File not found: {als_file_path}")
    
    # Decompress the gzipped XML
    with gzip.open(als_file_path, 'rb') as f:
        xml_content = f.read()
    
    # Parse XML
    root = ET.fromstring(xml_content)
    
    # Extract project name (from filename)
    project_name = os.path.splitext(os.path.basename(als_file_path))[0]
    
    # Extract BPM (Tempo)
    bpm = None
    tempo_element = root.find('.//MasterTrack/DeviceChain/Mixer/Tempo/Manual')
    if tempo_element is not None:
        bpm = float(tempo_element.get('Value'))
    
    # Extract Key (if present in root key)
    key = None
    key_element = root.find('.//MasterTrack/DeviceChain/Mixer/CrossfadeState')
    # Note: Key detection is complex, this is simplified
    
    # Extract audio clips
    audio_clips = []
    for sample_ref in root.findall('.//SampleRef'):
        file_ref = sample_ref.find('.//FileRef/RelativePath')
        if file_ref is not None:
            relative_path = file_ref.get('Value')
            
            # Get absolute path (relative to .als file location)
            project_dir = os.path.dirname(als_file_path)
            audio_path = os.path.join(project_dir, relative_path)
            
            # Get duration if available
            duration_elem = sample_ref.find('.//DefaultDuration')
            duration = float(duration_elem.get('Value')) if duration_elem is not None else 0
            
            audio_clips.append({
                'path': audio_path,
                'relative_path': relative_path,
                'duration': duration,
                'exists': os.path.exists(audio_path)
            })
    
    return {
        'name': project_name,
        'bpm': int(bpm) if bpm else None,
        'key': key,
        'audio_clips': audio_clips,
        'als_path': als_file_path
    }


def find_longest_audio_clip(parsed_project):
    """Find the longest audio clip for preview generation"""
    clips = parsed_project['audio_clips']
    if not clips:
        return None
    
    # Filter only clips that exist
    existing_clips = [c for c in clips if c['exists']]
    if not existing_clips:
        return None
    
    # Return longest
    return max(existing_clips, key=lambda x: x['duration'])


# Test the parser
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ableton_parser.py <path_to_als_file>")
        sys.exit(1)
    
    als_file = sys.argv[1]
    
    try:
        result = parse_ableton_project(als_file)
        print(f"\n✓ Parsed: {result['name']}")
        print(f"  BPM: {result['bpm']}")
        print(f"  Audio clips found: {len(result['audio_clips'])}")
        
        longest = find_longest_audio_clip(result)
        if longest:
            print(f"  Longest clip: {longest['relative_path']} ({longest['duration']:.2f}s)")
        
    except Exception as e:
        print(f"✗ Error: {e}")