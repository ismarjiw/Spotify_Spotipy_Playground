import os
from flask import Flask, session, request, redirect, url_for
from flask_session import Session
import spotipy
from spotipy.oauth2 import SpotifyOAuth 

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
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
            f'<a href="/current_user">me</a>' \

# # Step 2. Being redirected from Spotify auth page
@app.route('/redirect')
def redirectPage():

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private user-modify-playback-state', cache_handler=cache_handler,show_dialog=True)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    # sp_oauth = create_spotify_oauth()
    sp_oauth = auth_manager
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    if token_info:
        session[TOKEN_INFO] = token_info
    else:
        token_info = sp_oauth.refresh_access_token(code)
        session[TOKEN_INFO] =  token_info 

    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
        f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
        f'<a href="/playlists">my playlists</a> | ' \
        f'<a href="/currently_playing">currently playing</a> | ' \
        f'<a href="/current_user">me</a>' \

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

'''
## https://datafireball.com/2021/11/29/is-flask-synchronous-threaded-vs-processes/
'''
if __name__ == '__main__':
    app.run(debug=True,threaded=True, host="0.0.0.0")