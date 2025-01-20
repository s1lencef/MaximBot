
from yandex_music import Client
from pprint import pprint
import json


class Artist():
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def get_uri(self):
        return "https://music.yandex.ru/artist/" + str(self.id)


class YandexMusicService():
    def __init__(self):
        self.client = Client();
        self.client.init();

    def get_tracks(self, query):
        result = self.client.search(query)
        labels_tracks = {"Rumedia": [], "Imixes": [], "Unknown": []}
        if (result.artists):
            id = None
            for artist in result.artists.results:

                if (query == artist.name):
                    id = artist.id
            if (id == None):
                raise RuntimeError("Артист не найден")
            tracks = self.client.artistsTracks(id)
            if not tracks:
                raise RuntimeError("Треков не обнаружено")
            if not tracks.tracks:
                raise RuntimeError("Треков не обнаружено")

            for track in tracks.tracks:

                if not track:
                    continue
                if not track.artists:
                    labels_tracks["Unknown"].append(track.title)
                for artist in track.artists:
                    if artist.id == id:
                        labels = track.albums[0].labels
                        if labels:
                            if (labels[0].id == 2034252):
                                labels_tracks["Imixes"].append(track.title)
                            elif (labels[0].id == 1813536):
                                labels_tracks["Rumedia"].append(track.title)
                            else:
                                labels_tracks["Unknown"].append(track.title)
                        else:
                            labels_tracks["Unknown"].append(track.title)
                    else:
                        pass
        else:
            raise RuntimeError("Артист не найден")

        return labels_tracks

    def get_artist_tracks(self, artist_id):
        labels_tracks = {"Rumedia": [], "Imixes": [], "Unknown": []}
        tracks = self.client.artistsTracks(artist_id)
        if not tracks:
            raise RuntimeError("Треков не обнаружено")
        if not tracks.tracks:
            raise RuntimeError("Треков не обнаружено")

        for track in tracks.tracks:

            if not track:
                continue
            elif not track.artists:
                labels_tracks["Unknown"].append(track.title)
            else:
                labels = track.albums[0].labels
                if labels:
                    if (labels[0].id == 2034252):
                        labels_tracks["Imixes"].append(track.title)
                    elif (labels[0].id == 1813536):
                        labels_tracks["Rumedia"].append(track.title)
                    else:
                        labels_tracks["Unknown"].append(track.title)
                else:
                    labels_tracks["Unknown"].append(track.title)

        return labels_tracks

    def get_artists(self, artist_name):

        result = self.client.search(artist_name)

        if result.artists:

            artist_list = []
            for artist in result.artists.results:
                if artist.name == artist_name:

                    artist_list.append(Artist(artist.name, artist.id))
        else:

            raise RuntimeError("Артист не найден")

        return artist_list
