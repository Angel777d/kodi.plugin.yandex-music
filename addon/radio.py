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


def start_radio(client, station_id, station_from):
	index = 0
	station_tracks, batch_id = get_radio(client, station_id)
	client.rotor_station_feedback_radio_started(station=station_id, from_=station_from, batch_id=batch_id)

	tracks = [t.track for t in station_tracks.sequence]
	current = tracks[index]
	play_id = do_play_start(client, current, station_id, batch_id)

	return index, play_id, batch_id, [t.track_id for t in tracks]


def play_next(client, station_id, station_from, index, play_id, batch_id, track_ids):
	tracks = client.tracks(track_ids)
	current = tracks[index]

	# finish
	do_play_end(client, current, play_id, station_id, batch_id)

	# get next
	index += 1
	if not (len(tracks) > index):
		index = 0
		station_tracks, batch_id = get_radio(client, station_id, current.track_id)
		tracks = [t.track for t in station_tracks.sequence]
		client.rotor_station_feedback_radio_started(station=station_id, from_=station_from, batch_id=batch_id)

	current = tracks[index]

	# start
	play_id = do_play_start(client, current, station_id, batch_id)

	return index, play_id, batch_id, [t.track_id for t in tracks]


def get_radio(client, station_id, queue=None):
	station_tracks = client.rotor_station_tracks(station_id, queue=queue)
	batch_id = station_tracks.batch_id
	return station_tracks, batch_id


def do_play_start(client, track, station_id, batch_id):
	play_id = "%s-%s-%s" % (int(random() * 1000), int(random() * 1000), int(random() * 1000))
	total_seconds = track.duration_ms / 1000
	client.play_audio(
		from_="desktop_win-home-playlist_of_the_day-playlist-default",
		track_id=track.track_id,
		album_id=track.albums[0].id,
		play_id=play_id,
		track_length_seconds=0,
		total_played_seconds=0,
		end_position_seconds=total_seconds,
	)
	client.rotor_station_feedback_track_started(
		station=station_id,
		track_id=track.track_id,
		batch_id=batch_id
	)
	return play_id


def do_play_end(client, track, play_id, station_id, batch_id):
	# played_seconds = 5.0
	played_seconds = track.duration_ms / 1000
	total_seconds = track.duration_ms / 1000

	client.play_audio(
		from_="desktop_win-home-playlist_of_the_day-playlist-default",
		track_id=track.track_id,
		album_id=track.albums[0].id,
		play_id=play_id,
		track_length_seconds=int(total_seconds),
		total_played_seconds=played_seconds,
		end_position_seconds=total_seconds,
	)

	client.rotor_station_feedback_track_finished(
		station=station_id,
		track_id=track.track_id,
		total_played_seconds=played_seconds,
		batch_id=batch_id
	)

	# client.rotor_station_feedback_skip(
	# 	station=station_id,
	# 	track_id=track.track_id,
	# 	total_played_seconds=played_seconds,
	# 	batch_id=batch_id
	# )
	pass


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
