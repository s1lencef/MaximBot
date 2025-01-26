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
        labels_tracks = {"RuMedia": {
            "tracks": [],
            "total": 0
        }, "IMixes": {
            "tracks": [],
            "total": 0
        }, "Unknown": {
            "tracks": [],
            "total": 0
        },
            "total": 0
        }

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
                    labels_tracks["Unknown"]["tracks"].append(track.title)
                    labels_tracks["Unknown"]["total"] += 1
                for artist in track.artists:
                    if artist.id == id:
                        labels = track.albums[0].labels
                        if labels:
                            if labels[0].id == 2034252:
                                labels_tracks["IMixes"]["tracks"].append(track.title)
                                labels_tracks["IMixes"]["total"] += 1
                            elif labels[0].id == 1813536:
                                labels_tracks["RuMedia"]["tracks"].append(track.title)
                                labels_tracks["RuMedia"]["total"] += 1
                            else:
                                labels_tracks["Unknown"]["tracks"].append(track.title)
                                labels_tracks["Unknown"]["total"] += 1
                        else:
                            labels_tracks["Unknown"]["tracks"].append(track.title)
                            labels_tracks["Unknown"]["total"] += 1
                    else:
                        pass
        else:
            raise RuntimeError("Артист не найден")
        return labels_tracks

    def get_artist_tracks(self, artist_id):
        labels_tracks = {"RuMedia": {
            "releases": [],
            "total": 0
        }, "IMixes": {
            "releases": [],
            "total": 0
        }, "Unknown": {
            "releases": [],
            "total": 0
        },
            "total": 0
        }
        albums = self.client.artists_direct_albums(artist_id, page_size=100000, sort_by='year')
        if not albums:
            raise RuntimeError("Треков не обнаружено")
        albums = albums.albums
        if not albums:
            raise RuntimeError("Треков не обнаружено")
        for album in albums:
            if not album:
                continue

            album = album.withTracks()
            if not album.artists:
                labels_tracks["Unknown"]["releases"].append({
                    "title": album.title,
                    "tracks": [volume.title for volume in album.volumes[0]],
                    "count":len(album.volumes[0])
                })
                labels_tracks["Unknown"]["total"] += 1
            else:
                labels_tracks["total"] += 1
                labels = album.labels
                if labels:
                    for label in labels:
                        if 2034252 == label.id:
                            labels_tracks["IMixes"]["releases"].append({
                                "title": album.title,
                                "tracks": [volume.title for volume in album.volumes[0]],
                                "count": len(album.volumes[0])
                            })
                            labels_tracks["IMixes"]["total"] += 1
                        elif 1813536 == label.id:
                            labels_tracks["RuMedia"]["releases"].append({
                                "title": album.title,
                                "tracks": [volume.title for volume in album.volumes[0]],
                                "count": len(album.volumes[0])
                            })
                            labels_tracks["RuMedia"]["total"] += 1
                        else:
                            labels_tracks["Unknown"]["releases"].append({
                                "title": album.title,
                                "tracks": [volume.title for volume in album.volumes[0]],
                                "count":len(album.volumes[0])

                            })
                            labels_tracks["Unknown"]["total"] += 1
                else:
                    labels_tracks["Unknown"]["releases"].append({
                        "title": album.title,
                        "tracks": [volume.title for volume in album.volumes[0]],
                        "count": len(album.volumes[0])
                    })
                    labels_tracks["Unknown"]["total"] += 1

        print(labels_tracks)
        return labels_tracks

    def get_artists(self, artist_name):

        result = self.client.search(artist_name, nocorrect=True)

        if result.artists:

            artist_list = []
            for artist in result.artists.results:

                if artist.name == artist_name:
                    artist_list.append(Artist(artist.name, artist.id))
        else:

            raise RuntimeError("Артист не найден")

        return artist_list
