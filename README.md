# Spotify Shutdown

A Python utility that schedules a Windows shutdown when the currently playing
Spotify song finishes. Cancel the countdown with Ctrl+C.

## Setup

1. Install Python and run `python -m pip install -r requirements.txt`.
2. Register a Spotify developer application with redirect URI
   `http://127.0.0.1:8888/callback` and the permissions required to read playback.
3. Copy `.env.example` to `.env` and fill in your own credentials locally.
4. Export those variables into your shell before running the script. On
   Bash/WSL: `set -a; . ./.env; set +a`.
5. Run `python spotify_shutdown.py`.

For the initial authorization-code exchange, supply
`SPOTIFY_AUTHORIZATION_CODE`. Save the returned refresh token in the ignored
local `.env` file as `SPOTIFY_REFRESH_TOKEN`, then export the variables again.
The initial setup displays that token in your terminal; do not share or commit
the terminal output. No credentials are included in this repository.

The script calls Windows `shutdown.exe` with forced application closure after
the countdown, so save your work first.
