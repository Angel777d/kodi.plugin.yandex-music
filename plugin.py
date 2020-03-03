# coding=utf-8
import sys
import urllib
import urlparse

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

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
	xbmc.log("[---] download folder is: %s" % folder, level=xbmc.LOGNOTICE)


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


def build_stub(label):
	li = xbmcgui.ListItem(label=label, thumbnailImage="")
	li.setProperty('IsPlayable', 'false')
	url = build_url({'mode': 'stub'})
	return url, li, False


def build_track_item(track, titleFormat="%s"):
	li = xbmcgui.ListItem(label=titleFormat % track.title, thumbnailImage="")
	li.setProperty('fanart_image', "")
	li.setProperty('IsPlayable', 'true')
	album = track.albums[0].title if track.albums else ""
	li.setInfo("music", {'Title': track.title, 'Album': album})
	url = build_url({'mode': 'track', 'track_id': track.track_id, 'title': track.title})
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


def build_album(client, album_id):
	album = client.albums([album_id])[0]
	xbmcplugin.addDirectoryItems(addon_handle, [build_stub("TODO: create album: %s" % album.title)], 1)
	xbmcplugin.endOfDirectory(addon_handle)


def build_artist(client, artist_id):
	artist = client.artists([artist_id])[0]
	xbmcplugin.addDirectoryItems(addon_handle, [build_stub("TODO: create artist: %s" % artist.name)], 1)
	xbmcplugin.endOfDirectory(addon_handle)


def build_playlist(client, playlist_id):
	uid, kind = playlist_id.split(":")
	xbmc.log("playlist_id. %s %s %s" % (playlist_id, kind, uid), level=xbmc.LOGNOTICE)
	tracksShort = client.users_playlists(kind=kind, user_id=uid)[0].tracks
	tracks = client.tracks([t.track_id for t in tracksShort])

	xbmc.log("build_tracks. len: %s" % len(tracks), level=xbmc.LOGNOTICE)
	entry_list = [build_track_item(track) for track in tracks]
	xbmcplugin.addDirectoryItems(addon_handle, entry_list, len(entry_list))
	xbmcplugin.endOfDirectory(addon_handle)


def build_likes(client):
	tracks = client.tracks([t.track_id for t in client.users_likes_tracks()])
	entry_list = [build_track_item(track) for track in tracks]
	xbmcplugin.addDirectoryItems(addon_handle, entry_list, len(entry_list))
	xbmcplugin.endOfDirectory(addon_handle)


def getSortedResults(search):
	fields = ["albums", "artists", "playlists", "tracks", "videos"]
	tmp = [(getattr(search, field).order, field) for field in fields]
	tmp = sorted(tmp, key=lambda v: v[0])
	return [(field, getattr(search, field)) for order, field in tmp]


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
	xbmc.log("[---] play_track: %s" % track_id, level=xbmc.LOGNOTICE)
	track = client.tracks([track_id])[0]

	dInfo = [d for d in track.get_download_info() if (d.codec == "mp3" and d.bitrate_in_kbps == 192)][0]
	dInfo.get_direct_link()
	dlink = dInfo.direct_link

	play_item = xbmcgui.ListItem(path=dlink)
	xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
	pass


def main():
	checkSettings()
	authorized, client = checkLogin(settings)
	xbmc.log("[---] authorized: %s" % authorized, level=xbmc.LOGNOTICE)

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
	elif mode[0] == 'album':
		album_id = args['album_id'][0]
		build_album(client, album_id)
	elif mode[0] == 'artist':
		artist_id = args['artist_id'][0]
		build_artist(client, artist_id)
	elif mode[0] == 'video':
		pass


if __name__ == '__main__':
	xbmc.log("[---] sys.argv: %s" % sys.argv, level=xbmc.LOGNOTICE)
	addon_handle = int(sys.argv[1])
	main()
