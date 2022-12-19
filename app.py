import os
from flask import Flask, session, request, redirect, url_for, render_template
from flask_session import Session
import spotipy
from spotipy.oauth2 import SpotifyOAuth 

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
## https://developer.spotify.com/documentation/general/guides/authorization/client-credentials/
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)
TOKEN_INFO = 'token_info'

@app.route('/')
def index():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private user-modify-playback-state', cache_handler=cache_handler,show_dialog=True)

    # Step 1. Display sign in link when no token
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 3. Signed in with token, display data
    if auth_manager.validate_token(cache_handler.get_cached_token()):
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        
        return f'<h2>Hi {spotify.me()["display_name"]}, ' \
            f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
            f'<a href="/playlists">my playlists</a> | ' \
            f'<a href="/currently_playing">currently playing</a> | ' \
            f'<a href="/current_user">me</a>  | ' \
            f'<a href="/get_tracks">Daft punk top 10 tracks + Meditation Playlist</a>  | ' \

# # Step 2. Being redirected from Spotify auth page
@app.route('/redirect')
def redirectPage():

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private user-modify-playback-state', cache_handler=cache_handler, show_dialog=True)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    session.clear()
    code = request.args.get('code')
    token_info = auth_manager.get_access_token(code)

    if token_info:
        session[TOKEN_INFO] = token_info
    else:
        token_info = sp_oauth.refresh_access_token(code)
        session[TOKEN_INFO] = token_info 

    return redirect('/')

@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)

    return redirect('/')

@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    current_playlists = spotify.current_user_playlists()

    return current_playlists ##JSON data

@app.route('/currently_playing')
def currently_playing():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track ##JSON data

    return "No track currently playing."

@app.route('/current_user')
def current_user():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    current_user = spotify.current_user()

    return current_user ##JSON data

@app.route('/get_tracks')
def tracks():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    dp_uri = 'spotify:artist:4tZwfgrHOc3mvqYlEYSvVi'
    tracks = spotify.artist_top_tracks(dp_uri)

    ids = []
    for track in tracks['tracks'][:10]:
        if track != None:
            ids.append(track['id'])

    return render_template('tracks.html', ids=ids)

'''
## https://datafireball.com/2021/11/29/is-flask-synchronous-threaded-vs-processes/
'''
if __name__ == '__main__':
    app.run(debug=True,threaded=True, host="0.0.0.0")