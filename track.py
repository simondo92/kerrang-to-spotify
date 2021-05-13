from statistics import mean
from typing import Optional

from fuzzywuzzy import fuzz
import spotipy


class NotFound(Exception):
    pass


class Track:
    def __init__(
            self, title: str, artist: Optional[str] = None, album: Optional[str] = None, fuzzy_threshold: int = 90):
        self.title = title
        self.artist = artist
        self.album = album
        self.fuzzy_threshold = fuzzy_threshold
        self.spotify_id = None

    def __str__(self):
        album = self.album or 'Unknown album'
        artist = self.artist or 'Unknown artist'
        spotify_id = self.spotify_id or 'Unknown spotify id'
        return f'{self.title} - {artist} - {album} - {spotify_id}'

    def __repr__(self):
        return self.__str__()

    @property
    def uri(self):
        return f'spotify:track:{self.spotify_id}'

    def get_fuzzy_match_score(self, item):
        name = item['name']
        album_name = item['album']['name']
        artists = item['artists']

        name_ratio = fuzz.ratio(name.lower(), self.title.lower())
        album_ratio = fuzz.ratio(album_name.lower(), self.album.lower()) if self.album else None

        # get the best matching artists score
        artist_ratio = None
        if self.artist:
            for artist in artists:
                artist_name = artist['name']
                ratio = fuzz.ratio(artist_name.lower(), self.artist.lower())
                if not artist_ratio or ratio > artist_ratio:
                    artist_ratio = ratio

        return mean(ratio for ratio in [name_ratio, album_ratio, artist_ratio] if ratio)

    def set_spotify_id(self, spotify=None):
        if not spotify:
            spotify = spotipy.Spotify(auth_manager=spotipy.SpotifyClientCredentials())

        result = spotify.search(f'{self.title} {self.artist}')
        tracks = result['tracks']
        if not tracks:
            raise NotFound()

        items = tracks['items']
        if not items:
            raise NotFound()

        for item in items:
            score = self.get_fuzzy_match_score(item)
            if score >= self.fuzzy_threshold:
                self.spotify_id = item['id']
                return

        raise NotFound()
