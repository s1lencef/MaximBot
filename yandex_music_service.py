from playhouse.reflection import print_table_sql
from yandex_music import Client
from pprint import pprint
import json
class YandexMusicService():
    def __init__(self):
        self.client = Client();
        self.client.init();
    def get_tracks(self, query):
        result = self.client.search(query)
        labels_tracks = {"Rumedia":[],"Imixes":[],"Unknown":[]}
        if(result.artists):
            id = None
            for artist in result.artists.results:
                if(query == artist.name):
                    id = artist.id
            if(id == None):
                raise RuntimeError("Артист не найден")
            tracks = self.client.artistsTracks(id)
            if not tracks:
                raise RuntimeError("Треков не обнаружено")
            if not tracks.tracks:
                raise RuntimeError("Треков не обнаружено")
            print()
            for track in tracks.tracks:
                if not track:
                    continue
                if not track.artists:
                    labels_tracks["Unknown"].append(track.title)
                for artist in track.artists:
                    if artist.id == id:
                        labels = track.albums[0].labels
                        if labels:
                            if(labels[0].id == 2034252):
                                labels_tracks["Imixes"].append(track.title)
                            elif(labels[0].id == 1813536):
                                labels_tracks["Rumedia"].append(track.title)
                            else:
                                labels_tracks["Unknown"].append(track.title)
                        else:
                            labels_tracks["Unknown"].append(track.title)
                    else:
                        print("Not found")
        else:
            raise RuntimeError("Артист не найден")
        print(labels_tracks)
        return labels_tracks
