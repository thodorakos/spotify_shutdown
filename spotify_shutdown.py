import requests
import base64
import time
import os
import sys

# ----------------- LOAD CREDENTIALS FROM ENVIRONMENT VARIABLES ----------------- #

# Set these environment variables in your system:
# SPOTIFY_CLIENT_ID: From your Spotify Developer Dashboard
# SPOTIFY_CLIENT_SECRET: From your Spotify Developer Dashboard
# SPOTIFY_AUTHORIZATION_CODE: The temporary code from the URL (for first run)
# SPOTIFY_REFRESH_TOKEN: The long-lived token from the first run

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
AUTHORIZATION_CODE = os.getenv("SPOTIFY_AUTHORIZATION_CODE")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

# -------------------------------------------------------------------------------- #

# Spotify API URLs
TOKEN_URL = "https://accounts.spotify.com/api/token"
PLAYER_URL = "https://api.spotify.com/v1/me/player/currently-playing"


def get_access_token_from_refresh_token():
    """Gets a new access token using the long-lived refresh token."""
    if not REFRESH_TOKEN:
        return None

    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN
    }
    headers = {
        'Authorization': f'Basic {b64_auth_str}'
    }
    
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        print("Successfully refreshed access token.")
        return response_data.get('access_token')
    else:
        print("Error refreshing token:")
        print(response.json())
        return None

def get_initial_tokens():
    """
    Performs the one-time exchange of the authorization code for the
    access and refresh tokens.
    """
    if not AUTHORIZATION_CODE:
        print("Error: Please provide the one-time AUTHORIZATION_CODE for the first run.")
        return None, None
        
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    payload = {
        'grant_type': 'authorization_code',
        'code': AUTHORIZATION_CODE,
        'redirect_uri': 'http://127.0.0.1:8888/callback' # Must match your dashboard
    }
    headers = {
        'Authorization': f'Basic {b64_auth_str}'
    }

    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        print("First-time setup successful!")
        print("\nIMPORTANT: Set the SPOTIFY_REFRESH_TOKEN environment variable with this value for future runs.")
        print(f"Your Refresh Token is: {response_data.get('refresh_token')}\n")
        return response_data.get('access_token'), response_data.get('refresh_token')
    else:
        print("Error getting initial tokens:")
        print(response.json())
        return None, None
        

def get_song_info(access_token):
    """Fetches currently playing song data from Spotify."""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(PLAYER_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 204: # No content
        print("No song is currently playing or the player is inactive.")
        return None
    else:
        print("Error getting song info:")
        print(response.json())
        return None

def shutdown_computer(seconds):
    """Schedules a shutdown command for Windows."""
    # This command works from both standard Windows CMD and WSL

    print(f"Windows will shut down in {seconds} seconds.")

    target_duration = max(0, seconds - 2)
    start_time = time.time()

    try:
        while True:
            elapsed = time.time() - start_time
            remaining = target_duration - elapsed

            if remaining <= 0:
                break

            # Progress bar calculation
            percent = min(1.0, elapsed / target_duration) if target_duration > 0 else 1.0
            bar_length = 30
            filled_length = int(bar_length * percent)
            bar = '=' * filled_length + '-' * (bar_length - filled_length)

            # Display the bar and remaining time
            sys.stdout.write(f"\r[{bar}] {remaining:.1f}s remaining")
            sys.stdout.flush()
            
            time.sleep(0.1)
            
        sys.stdout.write(f"\r[{'=' * 30}] 0.0s remaining\n")
        sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nShutdown cancelled by user.")
        sys.exit(0)

    os.system(f"shutdown.exe /s /f /t 0")
    
    

def main():
    access_token = get_access_token_from_refresh_token()

    if not access_token:
        print("Attempting first-time setup to get tokens...")
        access_token, _ = get_initial_tokens()
        if not access_token:
            print("\nSetup failed. Please check your credentials and authorization code.")
            sys.exit(1) # Exit the script
        print("Please paste the refresh token into the script and run it again.")
        sys.exit(0)


    song_data = get_song_info(access_token)
    
    if song_data and song_data.get('is_playing'):
        item = song_data.get('item', {})
        song_name = item.get('name')
        artist_name = item.get('artists', [{}])[0].get('name')
        
        progress_ms = song_data.get('progress_ms', 0)
        duration_ms = item.get('duration_ms', 0)
        
        remaining_ms = duration_ms - progress_ms
        remaining_seconds = int(remaining_ms / 1000)
        
        if remaining_seconds > 0:
            print(f"Currently playing: '{song_name}' by {artist_name}")
            print(f"Song ends in {remaining_seconds} seconds.")
            shutdown_computer(remaining_seconds)
        else:
            print("Song is already over.")
            
    else:
        print("Could not get song information. Is a song playing on Spotify?")


if __name__ == "__main__":
    main()