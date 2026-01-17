import requests
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from database import SessionLocal, SoundCloudAuth


# SoundCloud API Configuration
# You'll need to create a SoundCloud app at: https://soundcloud.com/you/apps
SOUNDCLOUD_CLIENT_ID = os.getenv("SOUNDCLOUD_CLIENT_ID", "")
SOUNDCLOUD_CLIENT_SECRET = os.getenv("SOUNDCLOUD_CLIENT_SECRET", "")
SOUNDCLOUD_REDIRECT_URI = os.getenv("SOUNDCLOUD_REDIRECT_URI", "http://localhost:8000/soundcloud/callback")

SOUNDCLOUD_API_BASE = "https://api.soundcloud.com"
SOUNDCLOUD_AUTH_URL = "https://soundcloud.com/connect"
SOUNDCLOUD_TOKEN_URL = f"{SOUNDCLOUD_API_BASE}/oauth2/token"


def get_authorization_url(state: str = "random_state") -> str:
    """
    Generate the SoundCloud OAuth authorization URL

    Args:
        state: Random state string for CSRF protection

    Returns:
        Authorization URL to redirect user to
    """
    params = {
        "client_id": SOUNDCLOUD_CLIENT_ID,
        "redirect_uri": SOUNDCLOUD_REDIRECT_URI,
        "response_type": "code",
        "scope": "non-expiring",  # Request non-expiring token
        "state": state
    }

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{SOUNDCLOUD_AUTH_URL}?{query_string}"


def exchange_code_for_token(code: str) -> Dict:
    """
    Exchange authorization code for access token

    Args:
        code: Authorization code from OAuth callback

    Returns:
        Dict with access_token, refresh_token, expires_in, scope
    """
    data = {
        "client_id": SOUNDCLOUD_CLIENT_ID,
        "client_secret": SOUNDCLOUD_CLIENT_SECRET,
        "redirect_uri": SOUNDCLOUD_REDIRECT_URI,
        "grant_type": "authorization_code",
        "code": code
    }

    response = requests.post(SOUNDCLOUD_TOKEN_URL, data=data)
    response.raise_for_status()

    return response.json()


def refresh_access_token(refresh_token: str) -> Dict:
    """
    Refresh an expired access token

    Args:
        refresh_token: The refresh token

    Returns:
        Dict with new access_token, refresh_token, expires_in
    """
    data = {
        "client_id": SOUNDCLOUD_CLIENT_ID,
        "client_secret": SOUNDCLOUD_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(SOUNDCLOUD_TOKEN_URL, data=data)
    response.raise_for_status()

    return response.json()


def get_valid_access_token() -> Optional[str]:
    """
    Get a valid access token, refreshing if necessary

    Returns:
        Valid access token or None if not authenticated
    """
    db = SessionLocal()
    try:
        auth = db.query(SoundCloudAuth).first()

        if not auth:
            return None

        # Check if token is expired
        if auth.expires_at and datetime.utcnow() >= auth.expires_at:
            # Refresh the token
            token_data = refresh_access_token(auth.refresh_token)

            # Update database
            auth.access_token = token_data["access_token"]
            auth.refresh_token = token_data.get("refresh_token", auth.refresh_token)
            auth.expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
            auth.updated_at = datetime.utcnow()
            db.commit()

        return auth.access_token

    finally:
        db.close()


def get_user_info(access_token: str) -> Dict:
    """
    Get authenticated user's information

    Args:
        access_token: Valid access token

    Returns:
        Dict with user information
    """
    headers = {"Authorization": f"OAuth {access_token}"}
    response = requests.get(f"{SOUNDCLOUD_API_BASE}/me", headers=headers)
    response.raise_for_status()

    return response.json()


def upload_track(
    audio_file_path: str,
    title: str,
    description: str = "",
    genre: str = "",
    tag_list: str = "",
    sharing: str = "public",
    artwork_path: Optional[str] = None,
    bpm: Optional[int] = None,
    key_signature: Optional[str] = None
) -> Dict:
    """
    Upload a track to SoundCloud

    Args:
        audio_file_path: Path to the audio file to upload
        title: Track title
        description: Track description
        genre: Music genre
        tag_list: Space-separated tags
        sharing: "public" or "private"
        artwork_path: Optional path to artwork image
        bpm: Optional BPM
        key_signature: Optional musical key

    Returns:
        Dict with track information including permalink_url
    """
    access_token = get_valid_access_token()

    if not access_token:
        raise ValueError("Not authenticated with SoundCloud. Please connect your account first.")

    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    # Prepare multipart form data
    headers = {"Authorization": f"OAuth {access_token}"}

    # Build track data
    track_data = {
        "title": title,
        "sharing": sharing,
    }

    if description:
        track_data["description"] = description
    if genre:
        track_data["genre"] = genre
    if tag_list:
        track_data["tag_list"] = tag_list
    if bpm:
        track_data["bpm"] = bpm
    if key_signature:
        track_data["key_signature"] = key_signature

    # Prepare files
    files = {
        "track[asset_data]": open(audio_file_path, "rb")
    }

    if artwork_path and os.path.exists(artwork_path):
        files["track[artwork_data]"] = open(artwork_path, "rb")

    try:
        # Upload track
        response = requests.post(
            f"{SOUNDCLOUD_API_BASE}/tracks",
            headers=headers,
            data={f"track[{k}]": v for k, v in track_data.items()},
            files=files
        )
        response.raise_for_status()

        return response.json()

    finally:
        # Close file handles
        for file_handle in files.values():
            file_handle.close()


def delete_track(track_id: str) -> bool:
    """
    Delete a track from SoundCloud

    Args:
        track_id: SoundCloud track ID

    Returns:
        True if successful
    """
    access_token = get_valid_access_token()

    if not access_token:
        raise ValueError("Not authenticated with SoundCloud")

    headers = {"Authorization": f"OAuth {access_token}"}
    response = requests.delete(
        f"{SOUNDCLOUD_API_BASE}/tracks/{track_id}",
        headers=headers
    )
    response.raise_for_status()

    return True


def is_authenticated() -> bool:
    """Check if user is authenticated with SoundCloud"""
    db = SessionLocal()
    try:
        auth = db.query(SoundCloudAuth).first()
        return auth is not None
    finally:
        db.close()


def get_authenticated_user() -> Optional[Dict]:
    """Get info about authenticated SoundCloud user"""
    db = SessionLocal()
    try:
        auth = db.query(SoundCloudAuth).first()
        if not auth:
            return None

        return {
            "user_id": auth.user_id,
            "username": auth.username,
            "connected_at": auth.created_at.isoformat() if auth.created_at else None
        }
    finally:
        db.close()


def disconnect():
    """Remove SoundCloud authentication"""
    db = SessionLocal()
    try:
        db.query(SoundCloudAuth).delete()
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    # Test configuration
    print("SoundCloud Integration Configuration:")
    print(f"  Client ID: {'✓ Set' if SOUNDCLOUD_CLIENT_ID else '✗ Not set'}")
    print(f"  Client Secret: {'✓ Set' if SOUNDCLOUD_CLIENT_SECRET else '✗ Not set'}")
    print(f"  Redirect URI: {SOUNDCLOUD_REDIRECT_URI}")
    print(f"  Authenticated: {is_authenticated()}")

    if is_authenticated():
        user = get_authenticated_user()
        print(f"  User: {user['username']} (ID: {user['user_id']})")
