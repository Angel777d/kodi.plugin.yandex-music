# -*- coding: utf-8 -*-
import sys

import xbmc
import xbmcaddon

import radio
from utils import create_track_list_item, get_track_url
from yandex_service import checkLogin


def log(msg, level=xbmc.LOGNOTICE):
	plugin = "[Radio Service]"
	xbmc.log("%s %s" % (plugin, msg), level)


class MyPlayer(xbmc.Player):
	def __init__(self, playerCore=0):
		self.station_id = None
		self.station_from = None
		self.result = None
		self.urls = []
		self.valid = True
		xbmc.Player.__init__(self, playerCore=playerCore)

	def start(self, radio_type, station_key):
		station = stations[radio_type][station_key]
		self.station_id = station.getId()
		self.station_from = station.source.station.id_for_from
		self.result = radio.start_radio(client, self.station_id, self.station_from)
		# add first track
		self.add_next_track(self.result)
		# add next track
		self.queue_next()
		# start playing
		self.play(pl, startpos=0)

	def queue_next(self):
		try:
			self.result = radio.play_next(client, self.station_id, self.station_from, *self.result)
			self.add_next_track(self.result)
		except Exception as ex:
			pass

	def add_next_track(self, play_info):
		# log("Add track to playlist")
		# log("index: %s, batch_id: %s, track_ids: %s" % (index, batch_id, track_ids))
		index, play_id, batch_id, track_ids = play_info
		track = client.tracks([track_ids[index]])[0]
		url = get_track_url(track)
		li = create_track_list_item(track)
		li.setPath(url)
		playIndex = pl.size()
		pl.add(url, li, playIndex)
		self.urls.append(url)

	def onPlayBackStopped(self):
		log(" --> onPlayBackStopped !!! ")
		self.queue_next()

	def onQueueNextItem(self):
		log(" --> onQueueNextItem !!! ")
		self.queue_next()

	def check(self):
		try:
			url = self.getPlayingFile()
			self.valid = (url in self.urls) and pl.size() == len(self.urls)
			log("check valid: %s" % self.valid)
		except Exception as ex:
			log("can't get current: %s" % ex)


# info
# def onPlayBackEnded(self):
# 	log("onPlayBackEnded")
#
# def onPlayBackStarted(self):
# 	log("onPlayBackStarted")
#
# def onAVStarted(self):
# 	log("onAVStarted")
#
# def onAVChange(self):
# 	log("onAVChange")
#
# def onPlayBackError(self):
# 	log("onPlayBackError")
#
# def onPlayBackPaused(self):
# 	log("onPlayBackPaused")
#
# def onPlayBackResumed(self):
# 	log("onPlayBackResumed")
#
# def onPlayBackSpeedChanged(self, speed):
# 	log("onPlayBackSpeedChanged")
#
# def onPlayBackSeek(self, time, seekOffset):
# 	log("onPlayBackSeek")
#
# def onPlayBackSeekChapter(self, chapter):
# 	log("onPlayBackSeekChapter")


if __name__ == '__main__':
	log("Started")
	monitor = xbmc.Monitor()
	settings = xbmcaddon.Addon("plugin.yandex-music")
	token = settings.getSetting('token')

	log(sys.argv)
	radio_type_ = sys.argv[1]
	station_key_ = sys.argv[2]

	# get stations info
	auth, client = checkLogin(settings)
	stations = radio.make_structure(client)

	# init playlist
	pl = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	pl.clear()

	# init player
	player = MyPlayer()
	player.start(radio_type_, station_key_)

	while not monitor.abortRequested():
		player.check()
		if not player.valid:
			break
		# Sleep/wait for abort for 10 seconds
		if monitor.waitForAbort(3):
			# Abort was requested while waiting. We should exit
			break

	log("Stopped")
	del monitor
	del player
	del client