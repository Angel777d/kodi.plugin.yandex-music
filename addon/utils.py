import os
import platform

import xbmcgui


def create_track_list_item(track, titleFormat="%s"):
	if track.cover_uri:
		img_url = "https://%s" % (track.cover_uri.replace("%%", "460x460"))
	elif track.albums and track.albums[0].cover_uri:
		img_url = "https://%s" % (track.albums[0].cover_uri.replace("%%", "460x460"))
	elif track.artists and track.artists[0].cover:
		cover = track.artists[0].cover
		img_url = "https://%s" % ((cover.uri or cover.items_uri[0]).replace("%%", "460x460"))
	else:
		img_url = ""

	li = xbmcgui.ListItem(label=titleFormat % track.title, thumbnailImage=img_url)
	li.setProperty('fanart_image', img_url)
	li.setProperty('IsPlayable', 'true')
	info = {
		"title": track.title,
		"mediatype": "music",
		# "lyrics": "(On a dark desert highway...)"
	}
	if track.duration_ms:
		info["duration"] = int(track.duration_ms / 1000)
	if track.artists:
		info["artist"] = track.artists[0].name
	if track.albums:
		album = track.albums[0]
		info["album"] = album.title
		if album.track_position:
			info["tracknumber"] = str(album.track_position.index)
			info["discnumber"] = str(album.track_position.volume)
		info["year"] = str(album.year)
		info["genre"] = album.genre
	li.setInfo("music", info)
	return li


plt = platform.system()


def fixWindows(path):
	return path


def fixLinux(path):
	return path.encode("utf-8")


fixPath = fixWindows if plt == "Windows" else fixLinux
_EXCLUDED = ':/?|;.<>*"'


def _trackSimpleData(track):
	artist = "".join([c for c in track.artists[0].name if c not in _EXCLUDED]) if track.artists else ""
	album = "".join([c for c in track.albums[0].title if c not in _EXCLUDED]) if track.albums else ""
	title = track.title
	return title, album, artist


def get_folder(track):
	title, album, artist = _trackSimpleData(track)

	if album:
		return "%s/%s" % (artist, album)
	return artist


def get_filename(track):
	title, album, artist = _trackSimpleData(track)
	title = "".join(["_" if c in _EXCLUDED else c for c in title])
	return "%s.mp3" % title


def exists(path):
	return os.path.exists(fixPath(path))


def getTrackPath(prefixPath, track):
	folder = os.path.join(prefixPath, get_folder(track))
	f = get_filename(track)
	path = os.path.join(folder, f)
	return exists(path), os.path.normpath(path), folder


def checkFolder(path):
	if not exists(path):
		os.makedirs(fixPath(path))
	return path


def getArtistCover(artist):
	if artist.cover:
		return artist.cover.download, "artist_%s.jpg" % artist.id


def getAlbumCover(album):
	if album.cover_uri:
		return album.download_cover, "album_%s.jpg" % album.id
	return getArtistCover(album.artists[0])


def getTrackCover(track):
	if track.cover_uri:
		return track.download_cover, "track_%s.jpg" % track.trackId
	return getAlbumCover(track.albums[0])


def getPlaylistCover(playlist):
	if playlist.cover:
		return playlist.cover.download, "playlist_%s_%s.jpg" % (playlist.playlistId, playlist.uid)
	return None


def get_track_url(track):
	dInfo = [d for d in track.get_download_info() if (d.codec == "mp3" and d.bitrate_in_kbps == 192)][0]
	dInfo.get_direct_link()
	return dInfo.direct_link