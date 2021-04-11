#!/usr/bin/env python3
import re
import typing

from bs4 import BeautifulSoup
import click
import requests

from track import Track


def get_start_of_album_index(text: str) -> int:
    """
    Get the index of the opening parenthesis which denotes where the album name starts.

    This is trickier than it first seems, and using RegEx would be difficult due to the potentially infinitely nested
    parentheses caused by parentheses appearing in the album name itself.

    For example:
    * Vermilion (Vol. 3: (The Subliminal Verses), 2004)

    Instead traverse the list in reverse, once the index of the closing parenthesis of the last matching pair has been
    found, we know where it is located in the reverse list. Then simply convert this to the equivalent index in original
    text and voila!
    """

    reversed_text = reversed(text)
    brackets_count = 0
    reverse_index = None
    for index, char in enumerate(reversed_text):
        if char == ')':
            brackets_count += 1
        elif char == '(':
            brackets_count -= 1

        if index > 0 and brackets_count == 0:
            reverse_index = index
            break

    if reverse_index is None:
        raise ValueError('Unbalance parentheses pair')

    forward_index = len(text) - reverse_index - 1
    return forward_index


def create_track(text: str) -> Track:
    start_of_album_index = get_start_of_album_index(text)

    # Todo remove the rank. The 20 greatest lists have a number too. So tracks look like...
    #  "{rank}. {track_name} ({album_name}, {album_year})"
    title = text[:start_of_album_index].strip()

    # todo is is worth keeping album year too?
    # remove the album year section
    album = re.sub(r',.*\d{4}\)$', '', text[start_of_album_index+1:]).strip()
    return Track(title=title, album=album)


def get_tracks(soup: BeautifulSoup) -> typing.List[Track]:
    headings_elements = soup.findAll('div', {'class': 'Block Block--heading'})
    headings = [heading.text.replace('\n', '') for heading in headings_elements]
    return [create_track(heading) for heading in headings]


def get_html(url: str) -> BeautifulSoup:
    response = requests.get(url)
    if not response.ok:
        raise Exception('')  # todo handle properly

    return BeautifulSoup(response.content, features='html.parser')


@click.command()
@click.option('--url', '-u', help='URL to a Kerrang article to convert to a playlist')
def kerrang_to_spotify(url: str):
    html = get_html(url)
    tracks = get_tracks(html)

    # todo need to extract artist name from soup too

    # todo remove
    for track in tracks:
        print(track)


if __name__ == '__main__':
    kerrang_to_spotify()
