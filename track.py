from typing import Optional


class Track:
    def __init__(self, title: str, artist: Optional[str] = None, album: Optional[str] = None):
        self.title = title
        self.artist = artist
        self.album = album

    def __str__(self):
        album = self.album or 'Unknown album'
        artist = self.artist or 'Unknown artist'
        return f'{self.title} - {artist} - {album}'

    def __repr__(self):
        return self.__str__()
