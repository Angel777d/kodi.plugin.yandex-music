# coding=utf-8

import os
import platform

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


def folder(track):
	title, album, artist = _trackSimpleData(track)

	if album:
		return "%s/%s" % (artist, album)
	return artist


def filename(track):
	title, album, artist = _trackSimpleData(track)
	title = "".join(["_" if c in _EXCLUDED else c for c in title])
	return "%s.mp3" % title


def exists(path):
	return os.path.exists(fixPath(path))


def getTrackPath(prefixPath, track):
	path = checkFolder(os.path.join(prefixPath, folder(track)))
	f = filename(track)
	path = os.path.join(path, f)
	path = os.path.normpath(path)
	return exists(path), path


def checkFolder(path):
	path = os.path.normpath(path)
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
