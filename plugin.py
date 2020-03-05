# coding=utf-8
import sys
import urllib
import urlparse
from threading import Thread

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from Extentions import getTrackPath, checkFolder
from login import checkLogin, login

settings = xbmcaddon.Addon("plugin.yandex-music")


def build_url(query):
	base_url = sys.argv[0]
	return base_url + '?' + urllib.urlencode(query, 'utf-8')


def checkSettings():
	folder = settings.getSetting('folder')
	if not folder:
		dialogType = 3  # ShowAndGetWriteableDirectory
		heading = "Select download folder"
		while not folder:
			folder = xbmcgui.Dialog().browseSingle(dialogType, heading, "music", defaultt=folder)
		settings.setSetting('folder', folder)


def build_stub_item(label):
	li = xbmcgui.ListItem(label=label, thumbnailImage="")
	li.setProperty('IsPlayable', 'false')
	url = build_url({'mode': 'stub'})
	return url, li, False


def build_simple_item(title, data, mode, isFolder=False):
	li = xbmcgui.ListItem(label=title, thumbnailImage="")
	li.setProperty('fanart_image', "")
	li.setProperty('IsPlayable', 'false')
	li.setInfo("music", {'Title': title, 'Album': title})
	url = build_url({'mode': mode, 'data': data, 'title': title})
	return url, li, isFolder


def build_play_all_item(tracks):
	tracks = ",".join([t.track_id for t in tracks])
	li = xbmcgui.ListItem(label="Play All", thumbnailImage="")
	li.setProperty('fanart_image', "")
	li.setProperty('IsPlayable', 'false')
	li.setInfo("music", {'Title': "Play All", 'Album': "Play All"})
	url = build_url({'mode': 'download_and_play', 'tracks': tracks, 'title': "Play All"})
	return url, li, False


def build_track_item(track, titleFormat="%s"):
	prefixPath = settings.getSetting('folder')
	exists, path = getTrackPath(prefixPath, track)
	li = xbmcgui.ListItem(label=titleFormat % track.title, thumbnailImage="")
	li.setProperty('fanart_image', "")
	li.setProperty('IsPlayable', 'true')
	album = track.albums[0].title if track.albums else ""
	li.setInfo("music", {'Title': track.title, 'Album': album})
	url = path if exists else build_url({'mode': 'track', 'track_id': track.track_id, 'title': track.title})
	return url, li, False


def build_playlist_item(playlist, titleFormat="%s"):
	li = xbmcgui.ListItem(label=titleFormat % playlist.title, thumbnailImage="")
	# li.setProperty('fanart_image', "")
	url = build_url({'mode': 'playlist', 'playlist_id': playlist.playlist_id, 'title': playlist.title})
	return url, li, True


def build_artist_item(artist, titleFormat="%s"):
	li = xbmcgui.ListItem(label=titleFormat % artist.name, thumbnailImage="")
	# li.setProperty('fanart_image', "")
	url = build_url({'mode': 'artist', 'artist_id': artist.id, 'title': artist.name})
	return url, li, True


def build_album_item(album, titleFormat="%s"):
	li = xbmcgui.ListItem(label=titleFormat % album.title, thumbnailImage="")
	# li.setProperty('fanart_image', "")
	url = build_url({'mode': 'album', 'album_id': album.id, 'title': album.title})
	return url, li, True


def build_video_item(video, titleFormat="%s"):
	li = xbmcgui.ListItem(label=titleFormat % video.title, thumbnailImage=video.thumbnail_url)
	# li.setProperty('fanart_image', "")
	data = {
		'mode': 'video',
		'title': video.title,
		'youtube_url': video.youtube_url,
		'thumbnail_url': video.thumbnail_url,
		'duration': video.duration,
		'text': video.text,
		'html_auto_play_video_player': video.html_auto_play_video_player,
		'regions': video.regions,
	}
	url = build_url(data)
	return url, li, True


def build_menu(authorized, client):
	li = xbmcgui.ListItem(label="Search", thumbnailImage="")
	# li.setProperty('fanart_image', "")
	url = build_url({'mode': 'search', 'title': "Search"})
	entry_list = [(url, li, True), ]

	if authorized:
		# Show user like item
		li = xbmcgui.ListItem(label="User Likes", thumbnailImage="")
		# li.setProperty('fanart_image', "")
		url = build_url({'mode': 'like', 'title': "User Likes"})
		entry_list.append((url, li, True))

		# show Landing playlists
		landing = client.landing(["personal-playlists"])
		block = [b for b in landing.blocks if b.type == "personal-playlists"][0]
		playlists = [entity.data.data for entity in block.entities]
		entry_list += [build_playlist_item(playlist) for playlist in playlists]

		# other user playlists
		users_playlists_list = client.users_playlists_list()
		entry_list += [build_playlist_item(playlist, "User playlist: %s") for playlist in users_playlists_list]
	else:
		li = xbmcgui.ListItem(label="Login", thumbnailImage="")
		# li.setProperty('fanart_image', "")
		url = build_url({'mode': 'login', 'title': "Login"})
		entry_list.append((url, li, True))

	xbmcplugin.addDirectoryItems(addon_handle, entry_list, len(entry_list))
	xbmcplugin.endOfDirectory(addon_handle, updateListing=True, cacheToDisc=False)


def build_album(client, album_id):
	album = client.albums([album_id])[0]
	xbmcplugin.addDirectoryItems(addon_handle, [build_stub_item("TODO: create album: %s" % album.title)], 1)
	xbmcplugin.endOfDirectory(addon_handle)


def build_artist(client, artist_id):
	artist_brief = client.artists_brief_info(artist_id)
	counts = artist_brief.artist.counts

	elements = []

	# all albums
	albums = artist_brief.albums
	showAllAlbums = len(albums) < counts.direct_albums
	if showAllAlbums:
		item = build_simple_item("Show All [%s] Albums" % counts.direct_albums, artist_id, "show_all_albums", True)
		elements.append(item)
	elements += [build_album_item(album) for album in albums]

	# all tracks
	tracks = artist_brief.popular_tracks
	showAllTracks = len(tracks) < counts.tracks
	if showAllTracks:
		item = build_simple_item("Show All [%s] Tracks" % counts.tracks, artist_id, "show_all_tracks", True)
		elements.append(item)

	elements += [build_track_item(track) for track in tracks]

	# TODO: add playlists
	# playlists = client.playlists_list(artist_brief.playlist_ids)
	# elements += [build_playlist_item(playlist) for playlist in playlists]

	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_all_tracks(client, artist_id):
	artist = client.artists([artist_id])[0]
	artist_tracks = client.artists_tracks(artist_id, page=0, page_size=artist.counts.tracks)
	tracks = artist_tracks.tracks
	elements = [build_track_item(t) for t in tracks]
	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_all_albums(client, artist_id):
	artist = client.artists([artist_id])[0]
	artist_albums = client.artists_direct_albums(artist.id, page=0, page_size=artist.counts.direct_albums)
	albums = artist_albums.albums
	elements = [build_album_item(t) for t in albums]
	xbmcplugin.addDirectoryItems(addon_handle, elements, len(elements))
	xbmcplugin.endOfDirectory(addon_handle)


def build_playlist(client, playlist_id):
	uid, kind = playlist_id.split(":")
	tracksShort = client.users_playlists(kind=kind, user_id=uid)[0].tracks
	tracks = client.tracks([t.track_id for t in tracksShort])

	# TODO: replace
	# tracks = ",".join([t.track_id for t in tracks])
	# build_simple_item("Play All", tracks, "download_and_play")
	entry_list = [build_play_all_item(tracks)]

	entry_list += [build_track_item(track) for track in tracks]
	xbmcplugin.addDirectoryItems(addon_handle, entry_list, len(entry_list))
	xbmcplugin.endOfDirectory(addon_handle)


def build_likes(client):
	tracks = client.tracks([t.track_id for t in client.users_likes_tracks()])
	entry_list = [build_play_all_item(tracks)]
	entry_list += [build_track_item(track) for track in tracks]
	xbmcplugin.addDirectoryItems(addon_handle, entry_list, len(entry_list))
	xbmcplugin.endOfDirectory(addon_handle)


def build_search(client):
	searchString = xbmcgui.Dialog().input("", type=xbmcgui.INPUT_ALPHANUM)
	if not searchString:
		return

	func = {
		"albums": build_album_item,
		"artists": build_artist_item,
		"playlists": build_playlist_item,
		"tracks": build_track_item,
		"videos": build_video_item,
	}

	templates = {
		"albums": "Album: %s",
		"artists": "Artist: %s",
		"playlists": "Playlist: %s",
	}

	results = getSortedResults(client.search(searchString))

	for resultType, searchResult in results:
		entry_list = [func[resultType](entry, templates.get(resultType, "%s")) for entry in searchResult.results]
		if entry_list:
			xbmcplugin.addDirectoryItems(addon_handle, entry_list, len(entry_list))

	xbmcplugin.endOfDirectory(addon_handle)


def play_track(client, track_id):
	track = client.tracks([track_id])[0]
	prefixPath = settings.getSetting('folder')
	exists, path = getTrackPath(prefixPath, track)

	def getUrl():
		dInfo = [d for d in track.get_download_info() if (d.codec == "mp3" and d.bitrate_in_kbps == 192)][0]
		dInfo.get_direct_link()
		return dInfo.direct_link

	li = xbmcgui.ListItem(path=path if exists else getUrl())
	xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)

	if not exists:
		t = Thread(target=download_track, args=(track,))
		t.start()


def do_load(tracks):
	notify("Download", "Download %s files" % len(tracks), 5)
	playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)

	for index in range(len(tracks)):
		track = tracks[index]
		path = download_track(track)
		if path:
			url, li, isFolder = build_track_item(track)
			li.setPath(path)
			playlist.add(path, li, index)

	notify("Download", "All files downloaded.\n Play now.", 5)
	xbmc.Player().play(playlist)


def download_and_play(client, track_ids):
	tracks = client.tracks(track_ids)
	li = xbmcgui.ListItem()
	xbmcplugin.setResolvedUrl(addon_handle, False, listitem=li)

	t = Thread(target=do_load, args=(tracks,))
	t.start()


def main():
	checkSettings()
	authorized, client = checkLogin(settings)
	log("authorized: %s" % authorized)

	args = urlparse.parse_qs(sys.argv[2][1:])
	mode = args.get('mode', None)

	xbmcplugin.setContent(addon_handle, 'songs')

	if mode is None:
		build_menu(authorized, client)
	elif mode[0] == 'login':
		login(settings)
		build_menu(*checkLogin(settings))
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
	elif mode[0] == 'download_and_play':
		tracks_ids = args['tracks'][0].split(",")
		download_and_play(client, tracks_ids)
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


# misc
def getSortedResults(search):
	fields = ["albums", "artists", "playlists", "tracks", "videos"]
	tmp = [(getattr(search, field).order, field) for field in fields]
	tmp = sorted(tmp, key=lambda v: v[0])
	return [(field, getattr(search, field)) for order, field in tmp]


def download_track(track):
	download_dir = settings.getSetting('folder')
	exist, path = getTrackPath(download_dir, track)
	log("start download: %s" % path)
	if not exist:
		try:
			track.download(path)
			notify("Download", "Done: %s" % path, 1)
		except Exception as ex:
			notify("Download", "Fail download: %s" % path)
			log("Fail download: %s. ex: %s" % (path, ex))
			return None

	return path


def saveTracks(tracks):
	import os
	path = checkFolder("/addon_data/")
	path = os.path.join(path, "tracks.txt")
	f = open(path, "w")
	f.write(",".join([t.track_id for t in tracks]))
	f.close()


def loadTracks():
	import os
	path = checkFolder("/addon_data/")
	path = os.path.join(path, "tracks.txt")
	if not os.path.exists(path):
		return []
	f = open(path, "r")
	result = f.read()
	f.close()
	return result.split(",")


def notify(title, msg, duration=1):
	xbmc.executebuiltin("Notification(%s,%s,%s)" % (legalize(title), legalize(msg), duration))


def log(msg, level=xbmc.LOGNOTICE):
	plugin = "---"
	xbmc.log("[%s] %s" % (plugin, legalize(msg)), level)


def legalize(value):
	if isinstance(value, unicode):
		value = value.encode('utf-8')
	return value.__str__()


if __name__ == '__main__':
	log("sys.argv: %s" % sys.argv)
	addon_handle = int(sys.argv[1])
	main()
