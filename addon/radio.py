import threading
from random import random


class StationNode:
    def __init__(self, source):
        self.source = source
        self.children = []

    def getId(self):
        return "%s:%s" % (self.source.station.id.type, self.source.station.id.tag)

    def getTitle(self):
        return self.source.station.name

    def getImage(self, size='200x200'):
        return self.source.station.icon.get_url(size)

    def __repr__(self):
        return "[StationNode] name: %s, children: %s" % (self.source.station.name, len(self.children))


class Radio:
    def __init__(self, client, station_id, station_from):
        self.client = client
        self.station_id = station_id
        self.station_from = station_from
        self.batch_id = None
        self.play_id = None
        self.tracks = None
        self.index = 0

    def start_radio(self):
        station_tracks = self.client.rotor_station_tracks(self.station_id, queue=None)
        self.tracks = self.client.tracks([t.track.track_id for t in station_tracks.sequence])
        self.batch_id = station_tracks.batch_id

        current = self.tracks[0]
        self.play_id = self.__generate_play_id()

        threading.Thread(target=self.__send_start_radio, kwargs={
            "track": current,
            "play_id": self.play_id,
            "batch_id": self.batch_id,
        }).start()

        return current

    def play_next(self):
        current = self.tracks[self.index]

        # finish
        play_end_kwargs = {
            "track": current,
            "play_id": self.play_id,
            "batch_id": self.batch_id,
        }

        # get next
        self.index += 1
        next_function = self.__do_play_start
        if self.index >= len(self.tracks):
            self.index = 0
            station_tracks = self.client.rotor_station_tracks(self.station_id, queue=current.track_id)
            self.batch_id = station_tracks.batch_id
            self.tracks = self.client.tracks([t.track.track_id for t in station_tracks.sequence])
            next_function = self.__send_start_radio

        current = self.tracks[self.index]
        self.play_id = self.__generate_play_id()

        play_end_kwargs["next_function"] = next_function
        play_end_kwargs["next_args"] = {
            "track": current,
            "play_id": self.play_id,
            "batch_id": self.batch_id,
        }

        threading.Thread(target=self.__do_play_end, kwargs=play_end_kwargs).start()
        return current

    @staticmethod
    def __generate_play_id():
        return "%s-%s-%s" % (int(random() * 1000), int(random() * 1000), int(random() * 1000))

    def __send_start_radio(self, track, play_id, batch_id):
        self.__do_play_start(track, play_id, batch_id)
        while True:
            try:
                self.client.rotor_station_feedback_radio_started(
                    station=self.station_id,
                    from_=self.station_from,
                    batch_id=batch_id
                )
                break
            except BaseException as ex:
                continue

    def __do_play_start(self, track, play_id, batch_id):
        total_seconds = track.duration_ms / 1000

        while True:
            try:
                self.client.play_audio(
                    from_="desktop_win-home-playlist_of_the_day-playlist-default",
                    track_id=track.id,
                    album_id=track.albums[0].id,
                    play_id=play_id,
                    track_length_seconds=0,
                    total_played_seconds=0,
                    end_position_seconds=total_seconds
                )
                break
            except BaseException as ex:
                continue

        while True:
            try:
                self.client.play_audio(
                    station=self.station_id,
                    track_id=track.id,
                    batch_id=batch_id
                )
                break
            except BaseException as ex:
                continue

    def __do_play_end(self, track, play_id, batch_id, next_function, next_args):
        # played_seconds = 5.0
        played_seconds = track.duration_ms / 1000
        total_seconds = track.duration_ms / 1000
        try_counter = 0
        while True:
            try:
                self.client.play_audio(
                    from_="desktop_win-home-playlist_of_the_day-playlist-default",
                    track_id=track.id,
                    album_id=track.albums[0].id,
                    play_id=play_id,
                    track_length_seconds=int(total_seconds),
                    total_played_seconds=played_seconds,
                    end_position_seconds=total_seconds
                )
                break
            except BaseException as ex:
                continue

        while True:
            try:
                self.client.rotor_station_feedback_track_finished(
                    station=self.station_id,
                    track_id=track.id,
                    total_played_seconds=played_seconds,
                    batch_id=batch_id

                )
                break
            except BaseException as ex:
                continue

        # client.rotor_station_feedback_skip(
        # 	station=station_id,
        # 	track_id=track.track_id,
        # 	total_played_seconds=played_seconds,
        # 	batch_id=batch_id
        # )

        next_function(**next_args)


def make_structure(client):
    stations = client.rotor_stations_list()
    types = {}
    for s_info in stations:
        type_container = types.setdefault(s_info.station.id.type, {})
        type_container[s_info.station.id.tag] = StationNode(s_info)

    root_genre = {}
    for k, v in types["genre"].items():
        station = v.source.station
        if station.parent_id:
            parent_tag = station.parent_id.tag
            if station.parent_id.tag in types["genre"]:
                types["genre"][parent_tag].children.append(v)
        else:
            root_genre[station.id.tag] = v

    types["genre"] = root_genre

    return types


def make_dashboard(client):
    dashboard = client.rotor_stations_dashboard()
    return {s_info.station.id.tag: StationNode(s_info) for s_info in dashboard.stations}
