# SoundCloud Integration Setup Guide

This guide will walk you through setting up SoundCloud integration so you can upload tracks directly from Release OS to your SoundCloud account.

## Features

- **OAuth 2.1 Authentication** - Securely connect your SoundCloud account
- **One-Click Upload** - Upload tracks with metadata (BPM, key, genre, tags)
- **Automatic Artwork** - Waveform visualizations uploaded as track artwork
- **Track URLs** - Direct links to uploaded tracks on SoundCloud
- **Auto Status Update** - Projects move to "Released" status after upload

## Prerequisites

- A SoundCloud account ([create one here](https://soundcloud.com/signup))
- SoundCloud Developer credentials (see below)

## Step 1: Create a SoundCloud App

1. Visit the [SoundCloud Developer Portal](https://soundcloud.com/you/apps)
2. Click "Register a new application"
3. Fill in the application details:
   - **App Name**: "Release OS" (or your preferred name)
   - **Description**: "Music production release management tool"
   - **Redirect URI**: `http://localhost:8000/soundcloud/callback`
4. Click "Register"
5. You'll receive:
   - **Client ID** - A unique identifier for your app
   - **Client Secret** - A secret key (keep this private!)

## Step 2: Configure Release OS

1. **Create environment file:**
   ```bash
   cd ~/Developer/release-os/backend
   cp .env.example .env
   ```

2. **Edit the .env file:**
   ```bash
   nano .env
   # or use your preferred editor
   ```

3. **Add your credentials:**
   ```env
   SOUNDCLOUD_CLIENT_ID=your_actual_client_id_here
   SOUNDCLOUD_CLIENT_SECRET=your_actual_client_secret_here
   SOUNDCLOUD_REDIRECT_URI=http://localhost:8000/soundcloud/callback
   ```

4. **Save and close the file** (in nano: Ctrl+X, then Y, then Enter)

## Step 3: Install Additional Dependencies

The requests library should already be installed, but verify:

```bash
cd ~/Developer/release-os/backend
source venv/bin/activate
pip install requests
```

## Step 4: Restart Release OS

```bash
cd ~/Developer/release-os
./stop.sh
./start.sh
```

## Step 5: Connect Your SoundCloud Account

1. Open Release OS in your browser: http://localhost:5173

2. Click the **"Connect SoundCloud"** button in the top right

3. You'll be redirected to SoundCloud's authorization page

4. Click **"Connect"** to authorize Release OS

5. You'll be redirected back to Release OS

6. You should see your SoundCloud username in the header

## Using SoundCloud Integration

### Uploading a Track

1. **Ensure your project has audio:**
   - Project must have a generated preview (audio files must exist)
   - You'll see an "Upload to SoundCloud" button on projects with audio

2. **Click "Upload to SoundCloud"** on any project card

3. **Wait for upload to complete:**
   - Upload happens in the background
   - Check backend logs to see progress
   - After ~5-10 seconds, reload to see the SoundCloud link

4. **View on SoundCloud:**
   - Click the "On SoundCloud" badge on uploaded projects
   - Opens the track page on SoundCloud

### What Gets Uploaded

- **Audio**: The 30-second preview MP3
- **Title**: Project name
- **Artwork**: Waveform visualization (if available)
- **Description**: "Created with Release OS" + BPM + Key
- **Genre**: Your project's genre
- **Tags**: Genre + any custom tags you've added
- **BPM**: Tempo metadata
- **Key**: Musical key metadata
- **Visibility**: Private (you can make it public on SoundCloud)

### Upload Status

- **Before Upload**: "Upload to SoundCloud" button visible
- **During Upload**: Button shows "Uploading..."
- **After Upload**: "On SoundCloud" badge appears
- **Status Change**: Project automatically moves to "Released" status

## Troubleshooting

### "Not connected to SoundCloud" Error

**Solution**: Click "Connect SoundCloud" button and authorize the app

### "No audio preview available" Error

**Cause**: Project doesn't have audio files or preview wasn't generated

**Solution**:
1. Ensure the Ableton project references audio files that exist
2. Click "Scan Projects" to regenerate previews
3. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for audio issues

### "Invalid client credentials" Error

**Cause**: SoundCloud API credentials are incorrect

**Solution**:
1. Double-check your `.env` file
2. Verify Client ID and Client Secret from SoundCloud app settings
3. Restart the backend: `./stop.sh && ./start.sh`

### OAuth Callback Error

**Cause**: Redirect URI doesn't match what's configured in SoundCloud app

**Solution**:
1. Check SoundCloud app settings
2. Ensure Redirect URI is exactly: `http://localhost:8000/soundcloud/callback`
3. No trailing slash!

### Token Expired

**Cause**: Access token expired (happens after 6 hours)

**Solution**: The system automatically refreshes tokens. If it fails, disconnect and reconnect:
1. Click "Disconnect" in Release OS
2. Click "Connect SoundCloud" again

### Upload Fails Silently

**Check backend logs:**
```bash
tail -f ~/Developer/release-os/backend.log
```

Common issues:
- File size too large (SoundCloud limit: 500MB)
- Invalid audio format
- Network timeout

## API Endpoints

For developers or advanced users:

- `GET /soundcloud/status` - Check connection status
- `GET /soundcloud/connect` - Get OAuth URL
- `GET /soundcloud/callback` - OAuth callback (used automatically)
- `POST /soundcloud/disconnect` - Disconnect account
- `POST /projects/{id}/upload-soundcloud` - Upload a project

## Security Notes

- **Client Secret**: Never commit your `.env` file to git
- **Tokens**: Stored encrypted in local SQLite database
- **Auto-Refresh**: Tokens refresh automatically before expiring
- **Private by Default**: Uploaded tracks are private until you change them

## Limitations

- **Audio Length**: Currently uploads the 30-second preview (not full track)
- **File Size**: Maximum 500MB per upload (SoundCloud API limit)
- **Rate Limits**: SoundCloud may rate-limit uploads (typically 100/hour)
- **Private Tracks**: Uploads are private by default

## Future Enhancements

- [ ] Upload full exported tracks (not just previews)
- [ ] Batch upload multiple tracks
- [ ] Edit track metadata after upload
- [ ] Make tracks public from Release OS
- [ ] Add to playlists
- [ ] View upload stats and analytics

## Useful Resources

- [SoundCloud API Documentation](https://developers.soundcloud.com/docs/api/guide)
- [SoundCloud Developer Dashboard](https://soundcloud.com/you/apps)
- [OAuth 2.1 Specification](https://developers.soundcloud.com/docs/api/guide#authentication)

## Support

If you encounter issues:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review backend logs: `tail -f backend.log`
3. Verify SoundCloud app settings
4. Test API access at http://localhost:8000/docs

---

**Note**: SoundCloud's API is designed for uploading tracks on behalf of users. Make sure you comply with SoundCloud's Terms of Service when using this integration.
