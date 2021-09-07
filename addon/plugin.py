# coding=utf-8
import sys
import threading
import urllib
from threading import Thread

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import radio
from utils import create_track_list_item, fixPath, getTrackPath, checkFolder, get_track_url, get_track_download_info, \
	log, notify
from yandex_service import check_login, login
from mutagen import mp3, easyid3

settings = xbmcaddon.Addon("plugin.yandex-music")
SERVICE_SCRIPT = "special://home/addons/plugin.yandex-music/service.py"


def build_url(query, base_url=None):
	if not base_url:
		base_url = sys.argv[0]
	return base_url + '?' + urllib.parse.urlencode(query, 'utf-8')


def build_url2(**query):
	return build_url(query)


def checkSettings():
	folder = settings.getSetting('folder')
	if not folder:
		dialogType = 3  # ShowAndGetWriteableDirectory
		heading = "Select download folder"
		while not folder:
			folder = xbmcgui.Dialog().browseSingle(dialogType, heading, "music", defaultt=folder)
		settings.setSetting('folder', folder)


def build_menu_download_playlist(li, playlist_id):
	li.addContextMenuItems([(
		'Download tracks',
		'Container.Update(%s)' % build_url2(mode='download_playlist', playlist_id=playlist_id),
	)])


def build_menu_download_artist(li, artist_id):
	li.addContextMenuItems([
		(
			'Stream From Artist',
			"RunScript(%s, %s, %s, %s)" % (SERVICE_SCRIPT, 'custom', 'artist', artist_id)
		),
		(
			'Download all tracks',
			'Container.Update(%s)' % build_url2(mode='download_artist', artist_id=artist_id),
		)
	])


def build_menu_download_album(li, album_id):
	li.addContextMenuItems([
		(
			'Stream From Album',
			"RunScript(%s, %s, %s, %s)" % (SERVICE_SCRIPT, 'custom', 'album', album_id)
		),
		(
			'Download all tracks',
			'Container.Update(%s)' % build_url2(mode='download_album', album_id=album_id),
		)
	])


def build_menu_download_user_likes(li):
	li.addContextMenuItems([(
		'Download all',
		'Container.Update(%s)' % build_url2(mode='download_user_likes'),
	)])


def build_menu_track(li, track):
	commands = []

	commands.append((
		'Stream From Track',
		"RunScript(%s, %s, %s, %s)" % (SERVICE_SCRIPT, 'custom', 'track', track.id)
	))

	if track.albums:
		album = track.albums[0]
		commands.append((
			'Go To Album',
			'Container.Update(%s)' % build_url2(mode='album', album_id=album.id, title=album.title),
		))
	if track.artists:
		artist = track.artists[0]
		commands.append((
			'Go To Artist',
			'Container.Update(%s)' % build_url2(mode='artist', artist_id=artist.id, title=artist.name),
		))
	if commands:
		li.addContextMenuItems(commands)


def build_item_stub(label):
	li = xbmcgui.ListItem(label=label)
	li.setProperty('IsPlayable', 'false')
	url = build_url({'mode': 'stub'})
	return url, li, False


def build_item_simple(title, data, mode, isFolder=False):
	li = xbmcgui.ListItem(label=title)
	li.setProperty('fanart_image', "")
	li.setProperty('IsPlayable', 'false')
	li.setInfo("music", {'Title': title, 'Album': title})
	url = build_url({'mode': mode, 'data': data, 'title': title})
	return url, li, isFolder


def build_item_track(track, titleFormat="%s", force_url=False, show_artist=True):
	prefixPath = settings.getSetting('folder')
	downloaded, path, folder = getTrackPath(prefixPath, track, codec)

	if downloaded:
		url = path
	elif force_url:
		url = get_track_url(track, codec, high_res)
	else:
		url = build_url({'mode': 'track', 'track_id': track.track_id, 'title': track.title})
	li = create_track_list_item(track, titleFormat, show_artist)
	build_menu_track(li, track)

	return url, li, False


def build_item_playlist(playlist, titleFormat="%s"):
	if playlist.animated_cover_uri:
		img_url = "https://%s" % (playlist.animated_cover_uri.replace("%%", "460x460"))
	else:
		img_url = get_cover_img(playlist.cover)

	li = xbmcgui.ListItem(label=titleFormat % playlist.title)
	li.setArt({"thumb": img_url, "icon": img_url, "fanart": img_url})
	li.setProperty('fanart_image', img_url)
	url = build_url({'mode': 'playlist', 'playlist_id': playlist.playlist_id, 'title': playlist.title})
	build_menu_download_playlist(li, playlist.playlist_id)
	return url, li, True


def build_item_artist(artist, titleFormat="%s"):
	img_url = get_cover_img(artist.cover)
	li = xbmcgui.ListItem(label=titleFormat % artist.name)
	li.setArt({"thumb": img_url, "icon": img_url, "fanart": img_url})
	li.setProperty('fanart_image', img_url)
	url = build_url({'mode': 'artist', 'artist_id': artist.id, 'title': artist.name})
	build_menu_download_artist(li, artist.id)
	return url, li, True


def build_item_album(album, titleFormat="%s"):
	if album.cover_uri:
		img_url = "https://%s" % (album.cover_uri.replace("%%", "460x460"))
	elif album.artists and album.artists[0].cover:
		img_url = get_cover_img(album.artists[0].cover)
	else:
		img_url = ""

	li = xbmcgui.ListItem(label=titleFormat % album.title)
	li.setArt({"thumb": img_url, "icon": img_url, "fanart": img_url})
	li.setProperty('fanart_image', img_url)
	url = build_url({'mode': 'album', 'album_id': album.id, 'title': album.title})
	build_menu_download_album(li, album.id)
	return url, li, True


def build_main(authorized, client):
	li = xbmcgui.ListItem(label="Search")
	# li.setProperty('fanart_image', "")
	url = build_url({'mode': 'search', 'title': "Search"})
	entry_list = [(url, li, True), ]

	if authorized:
		# Show User Playlists
		li = xbmcgui.ListItem(label="User Playlists")
		# li.setProperty('fanart_image', "")
		url = build_url({'mode': 'user_playlists', 'title': "User Playlists"})
		entry_list.append((url, li, True))

		# Show Radio
		li = xbmcgui.ListItem(label="Radio")
		# li.setProperty('fanart_image', "")
		url = build_url({'mode': 'radio', 'title': "Radio"})
		entry_list.append((url, li, True))

		# Show Chart
		li = xbmcgui.ListItem(label="Chart")
		# li.setProperty('fanart_image', "")
		url = build_url({'mode': 'chart', 'title': "Chart"})
		entry_list.append((url, li, True))

		# Show Mixes
		li = xbmcgui.ListItem(label="Mixes")
		# li.setProperty('fanart_image', "")
		url = build_url({'mode': 'mixes', 'title': "Mixes"})
		entry_list.append((url, li, True))

		# show Landing playlists
		landing = client.landing(["personal-playlists"])
		block = [b for b in landing.blocks if b.type == "personal-playlists"][0]
		playlists = [entity.data.data for entity in block.entities]
		entry_list += [build_item_playlist(playlist) for playlist in playlists]

	else:
		li = xbmcgui.ListItem(label="Login")
		# li.setProperty('fanart_image', "")
		url = build_url({'mode': 'login', 'title': "Login"})
		entry_list.append((url, li, True))

	xbmcplugin.addDirectoryItems(addon_handle, entry_list, len(entry_list))
	xbmcplugin.endOfDirectory(addon_handle, updateListing=True, cacheToDisc=False)


def build_mixes(client):
	landing = client.landing(["mixes"])
	mixes = landing.blocks[0]

	elements = []
	for mix in mixes.entities:
		params = mix.data.url.split("/")
		mix_type = params[1]
		if mix_type == "tag":
			tag = params[2].split("?")[0].encode("utf-8")
			img_url = "https://" + mix.data.background_image_uri.replace("%%", "400x400")
			url = build_url({'mode': 'mix', 'title': mix.data.title, "tag": tag})
			li = xbmcgui.ListItem(label=mix.data.title)
			li.setArt({"thumb": img_url, "icon": img_url, "fanart": img_url})
			li.setProperty('fanart_image', img_url)
			elements.append((url, li, True))
		else:
			log("Mix type " + mix_type + " not supported")

	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_mix(client, tag: str):
	tag_obj = client.tags(tag)

	elements = []
	playlist_ids = ["%s:%s" % (plid.uid, plid.kind) for plid in tag_obj.ids]
	if playlist_ids:
		playlists = client.playlists_list(playlist_ids)
		elements += [build_item_playlist(playlist) for playlist in playlists]

	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_chart(client):
	chart = client.chart()

	tracks = client.tracks([t.track_id for t in chart.chart.tracks])
	position = 0
	elements = []
	for t in tracks:
		position += 1
		elements.append(build_item_track(t, (str(position) + ": %s")))

	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_user_playlists(client):
	elements = []

	# Show user like item
	li = xbmcgui.ListItem(label="User Likes")
	# li.setProperty('fanart_image', "")
	url = build_url({'mode': 'like', 'title': "User Likes"})
	elements.append((url, li, True))
	build_menu_download_user_likes(li)

	# other user playlists
	users_playlists_list = client.users_playlists_list()
	elements += [build_item_playlist(playlist, "User playlist: %s") for playlist in users_playlists_list]

	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def get_radio_group_name(key):
	return {
		'genre': "By Genre",
		'mood': "By Mood",
		'activity': "By Activity",
		'epoch': "By Epoch",
		'author': "By Author",
		'local': "By Place",
		'personal': "Personal",
	}.get(key, key)


def build_item_radio_type(key):
	title = get_radio_group_name(key)
	li = xbmcgui.ListItem(label=title)
	url = build_url({'mode': 'radio_type', 'title': title, "radio_type": key})
	return url, li, True


def build_item_radio_station(radio_type, key, s_info):
	title = s_info.getTitle()
	img_url = s_info.getImage()
	li = xbmcgui.ListItem(label=title)
	li.setArt({"thumb": img_url, "icon": img_url, "fanart": img_url})
	li.setProperty('fanart_image', s_info.getImage("460x460"))
	url = build_url({'mode': 'radio_station', 'title': title, "radio_type": radio_type, "station_key": key})
	return url, li, True


def build_radio(client):
	stations = radio.make_structure(client)
	dashboard = radio.make_dashboard(client)
	elements = [build_item_radio_station("dashboard", key, dashboard[key]) for key in dashboard.keys()]
	elements += [build_item_radio_type(key) for key in stations.keys()]

	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_radio_type(client, radio_type):
	stations = radio.make_structure(client)[radio_type]

	elements = [build_item_radio_station(radio_type, key, stations[key]) for key in stations.keys()]

	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_album(client, album_id):
	album = client.albums_with_tracks(album_id)
	tracks = [track for volume in album.volumes for track in volume]

	elements = [build_item_track(t, show_artist=False) for t in tracks]

	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_all_albums(client, artist_id):
	artist = client.artists([artist_id])[0]
	artist_albums = client.artists_direct_albums(artist.id, page=0, page_size=artist.counts.direct_albums)
	albums = artist_albums.albums
	elements = [build_item_album(t) for t in albums]
	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_artist(client, artist_id):
	artist_brief = client.artists_brief_info(artist_id)
	counts = artist_brief.artist.counts

	elements = []

	# all albums
	albums = artist_brief.albums
	showAllAlbums = len(albums) < counts.direct_albums
	elements += [build_item_album(album) for album in albums]
	if showAllAlbums:
		item = build_item_simple("Show All [%s] Albums" % counts.direct_albums, artist_id, "show_all_albums", True)
		elements.append(item)

	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_all_tracks(client, artist_id):
	artist = client.artists([artist_id])[0]
	artist_tracks = client.artists_tracks(artist_id, page=0, page_size=artist.counts.tracks)
	tracks = artist_tracks.tracks
	elements = [build_item_track(t) for t in tracks]
	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_playlist(client, playlist_id):
	uid, kind = playlist_id.split(":")
	tracksShort = client.users_playlists(kind=kind, user_id=uid).tracks
	tracks = client.tracks([t.track_id for t in tracksShort])

	elements = [build_item_track(track) for track in tracks]
	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

	if tracks:
		sendPlayTrack(client, tracks[0])


def build_likes(client):
	tracks = client.tracks([t.track_id for t in client.users_likes_tracks()])
	elements = [build_item_track(track) for track in tracks]
	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_search(client):
	searchString = xbmcgui.Dialog().input("", type=xbmcgui.INPUT_ALPHANUM)
	if not searchString:
		return

	func = {
		"albums": build_item_album,
		"artists": build_item_artist,
		"playlists": build_item_playlist,
		"tracks": build_item_track,
	}

	templates = {
		"albums": "Album: %s",
		"artists": "Artist: %s",
		"playlists": "Playlist: %s",
		"tracks": "Track: %s",
	}

	results = getSortedResults(client.search(searchString))

	for resultType, searchResult in results:
		if resultType == "videos":
			continue
		entry_list = [func[resultType](entry, templates.get(resultType, "%s")) for entry in searchResult.results]
		if entry_list:
			xbmcplugin.addDirectoryItems(addon_handle, entry_list, len(entry_list))

	xbmcplugin.endOfDirectory(addon_handle)


def play_track(client, track_id):
	track = client.tracks([track_id])[0]
	prefixPath = settings.getSetting('folder')
	downloaded, path, folder = getTrackPath(prefixPath, track, codec)
	li = xbmcgui.ListItem(path=path if downloaded else get_track_url(track, codec, high_res))
	xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)

	sendPlayTrack(client, track)

	if not downloaded and auto_download:
		t = Thread(target=download_track, args=(track,))
		t.start()


def download_user_likes(client):
	download_all(client, [t.track_id for t in client.users_likes_tracks()])


def download_playlist(client, playlist_id):
	uid, kind = playlist_id.split(":")
	tracksShort = client.users_playlists(kind=kind, user_id=uid)[0].tracks
	download_all(client, [t.track_id for t in tracksShort])


def download_artist(client, artist_id):
	artist = client.artists([artist_id])[0]
	artist_tracks = client.artists_tracks(artist_id, page=0, page_size=artist.counts.tracks)
	download_all(client, [t.track_id for t in artist_tracks.tracks])


def download_album(client, album_id):
	album = client.albums_with_tracks(album_id)
	download_all(client, [track.track_id for volume in album.volumes for track in volume])


def download_all(client, track_ids):
	tracks = client.tracks(track_ids)
	li = xbmcgui.ListItem()
	xbmcplugin.setResolvedUrl(addon_handle, False, listitem=li)

	t = Thread(target=do_download, args=(tracks,))
	t.start()


def main():
	# Stop Radio script on any change
	# xbmc.executebuiltin("StopScript(%s)" % SERVICE_SCRIPT)

	checkSettings()
	authorized, client = check_login(settings)
	# log("authorized: %s" % authorized)

	args = urllib.parse.parse_qs(sys.argv[2][1:])
	mode = args.get('mode', None)

	xbmcplugin.setContent(addon_handle, 'songs')

	log("[Yandex music plugin] authorized: %s, mode: %s, args: %s" % (authorized, mode, args))

	if mode is None:
		if authorized:
			updateStatus(client)
		build_main(authorized, client)
	elif mode[0] == 'login':
		if not authorized:
			login(settings)
		authorized, client = check_login(settings)
		build_main(authorized, client)
	elif mode[0] == 'user_playlists':
		build_user_playlists(client)
	elif mode[0] == 'mixes':
		build_mixes(client)
	elif mode[0] == 'mix':
		tag = args['tag'][0]
		build_mix(client, tag)
	elif mode[0] == 'chart':
		build_chart(client)
	elif mode[0] == 'search':
		build_search(client)
	elif mode[0] == 'like':
		build_likes(client)
	elif mode[0] == 'playlist':
		playlist_id = args['playlist_id'][0]
		build_playlist(client, playlist_id)
	elif mode[0] == 'track':
		track_id = args['track_id'][0]
		play_track(client, track_id)
	elif mode[0] == 'download_all':
		tracks_ids = args['tracks'][0].split(",")
		download_all(client, tracks_ids)
	elif mode[0] == 'download_playlist':
		playlist_id = args['playlist_id'][0]
		download_playlist(client, playlist_id)
	elif mode[0] == 'download_user_likes':
		download_user_likes(client)
	elif mode[0] == 'download_artist':
		artist_id = args['artist_id'][0]
		download_artist(client, artist_id)
	elif mode[0] == 'download_album':
		album_id = args['album_id'][0]
		download_album(client, album_id)
	elif mode[0] == 'album':
		album_id = args['album_id'][0]
		build_album(client, album_id)
	elif mode[0] == 'artist':
		artist_id = args['artist_id'][0]
		build_artist(client, artist_id)
	elif mode[0] == 'video':
		pass
	elif mode[0] == 'show_all_albums':
		album_id = args['data'][0]
		build_all_albums(client, album_id)
	elif mode[0] == 'show_all_tracks':
		album_id = args['data'][0]
		build_all_tracks(client, album_id)
	elif mode[0] == 'radio':
		build_radio(client)
	elif mode[0] == 'radio_type':
		radio_type = args["radio_type"][0]
		build_radio_type(client, radio_type)
	elif mode[0] == 'radio_station':
		radio_type = args["radio_type"][0]
		station_key = args["station_key"][0]
		url = "RunScript(%s, %s, %s, %s)" % (SERVICE_SCRIPT, 'radio', radio_type, station_key)
		log("Run radio with url: %s" % url)
		threading.Thread(target=xbmc.executebuiltin, args=(url,)).run()


# misc
def get_cover_img(cover):
	if not cover:
		return ""
	uri = ""
	if cover.uri:
		uri = cover.uri
	elif cover.items_uri:
		uri = cover.items_uri[0]
	if uri:
		return "https://%s" % uri.replace("%%", "460x460")
	return ""


def sendPlayTrack(client, track):
	if not track.duration_ms:
		return

	play_id = "1354-123-123123-123"
	album_id = track.albums[0].id if track.albums else 0
	from_ = "desktop_win-home-playlist_of_the_day-playlist-default"
	# client.play_audio(
	# 	from_=from_,
	# 	track_id=track.track_id,
	# 	album_id=album_id,
	# 	play_id=play_id,
	# 	track_length_seconds=0,
	# 	total_played_seconds=0,
	# 	end_position_seconds=track.duration_ms / 1000,
	# )

	import threading
	t = threading.Thread(target=client.play_audio, kwargs={
		"from_": from_,
		"track_id": track.id,
		"album_id": album_id,
		"play_id": play_id,
		"track_length_seconds": int(track.duration_ms / 1000),
		"total_played_seconds": track.duration_ms / 1000,
		"end_position_seconds": track.duration_ms / 1000
	})
	t.start()

	# notify("Notify play", "play: " + track.track_id)
	pass


def do_download(tracks):
	notify("Download", "Download %s files" % len(tracks), 5)
	[download_track(track) for track in tracks]
	notify("Download", "All files downloaded.", 5)


def updateStatus(client):
	def do_update(cl):
		cl.account_status()
		cl.account_experiments()
		cl.settings()
		cl.permission_alerts()
		cl.rotor_account_status()

	Thread(target=do_update, args=(client,)).start()


def getSortedResults(search):
	fields = ["albums", "artists", "playlists", "tracks", "videos"]
	tmp = [(getattr(search, field).order, field) for field in fields if getattr(search, field)]
	tmp = sorted(tmp, key=lambda v: v[0])
	return [(field, getattr(search, field)) for order, field in tmp]


def download_track(track):
	download_dir = settings.getSetting('folder')
	downloaded, path, folder = getTrackPath(download_dir, track, codec)
	if not downloaded:
		checkFolder(folder)
		info = get_track_download_info(track, codec, high_res)
		log("download: %s, %s" % (info.codec, info.bitrate_in_kbps))
		info.download(fixPath(path))
		if codec == "mp3":
			audio = mp3.MP3(path, ID3=easyid3.EasyID3)
			audio["title"] = track.title
			audio["length"] = str(track.duration_ms)
			if track.artists:
				audio["artist"] = track.artists[0].name
			if track.albums:
				audio["album"] = track.albums[0].title
				audio["tracknumber"] = str(track.albums[0].track_position.index)
				audio["date"] = str(track.albums[0].year)
				audio["genre"] = track.albums[0].genre
			audio.save()
		elif codec == "aac":
			log("TODO: add tags to aac files")
	# notify("Download", "Done: %s" % path, 1)
	return path


if __name__ == '__main__':
	codec_index = settings.getSettingInt('codec')
	codec = ("mp3", "aac")[codec_index]
	high_res = bool(settings.getSettingBool('high_res'))
	auto_download = bool(settings.getSettingBool('auto_download'))

	log("codec: %s, high_res: %s" % (codec, high_res))
	addon_handle = int(sys.argv[1])
	main()
