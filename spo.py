import sys
import os
import spotipy 
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth


CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
REDIRECT_URI = os.environ['REDIRECT_URI']

def test(user,track_ids,playlistName ):

    # print('user: ',user,'   playlistname: ',playlistName, 'track_ids: ', track_ids)
    if playlistName == '': playlistName = 'Top100 Billboard PlayList'

    token = ''
    scope = 'playlist-modify-public'

    try:

        token = util.prompt_for_user_token(scope=scope,
                                    client_id=CLIENT_ID,
                                    client_secret=CLIENT_SECRET,
                                    redirect_uri=REDIRECT_URI,
                                    username = user)

        # sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
        #                                             client_id=client_id,
        #                                             client_secret=client_secret,
        #                                             redirect_uri=redirect_uri,
        #                                             username = user))
        if token:
            sp = spotipy.Spotify(auth=token)
            sp.trace = False

            playlists = sp.user_playlists(user)
            playlistId = ''

            for playlist in playlists['items']:
                if playlist['name'] == playlistName:
                    playlistId = playlist['id']
                    break
            if playlistId == '':
                playlistInfo = sp.user_playlist_create(user, playlistName, public=True, collaborative=False, description='Created from Top100 songs')
                playlistId = playlistInfo['id']

            playlistInfo = sp.user_playlist_replace_tracks(user, playlistId, track_ids)


    except Exception:
        print(Exception)

    finally:

        return token
    



if __name__ == '__main__':
    test('wll4i22dh2mtchhracrmjb4az', ['3w8Mw9GHYepoTWOSdiyosj', '6fA7akEuTUL3dW1V0GELaZ', '4pmc2AxSEq6g7hPVlJCPyP', '52IKUZIr66lMvy7COxmG9x', '1m2xMsxbtxv21Brome189p', '4cKGldbhGJniI8BrB3K6tb', '3mNecsYFb6LQg7822DPXCP', '0fJAcQZyy0C2qyt0LluAWp', '046MBhhgQJJghnbgZCkaAR', '2WfhlEjoUII31H6imnQdvF', '7f1Dmr246cJ9uQYdbplTbh', '1PmHkalaUHhh0fz23SBHDL', '6znv7i4Wif5fLwI6OjKHZ4'])