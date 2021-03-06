# -*- coding: utf-8 -*-
import sys

import xbmc
import xbmcaddon

import radio
from radio import Radio
from utils import create_track_list_item, get_track_url
from yandex_service import check_login


def log(msg, level=xbmc.LOGWARNING):
	plugin = "[Radio Service]"
	xbmc.log("%s %s" % (plugin, msg), level)


class MyPlayer(xbmc.Player):
	def __init__(self, playerCore=0):
		self.radio = None

		self.urls = []
		self.valid = True
		self.started = False
		xbmc.Player.__init__(self, playerCore=playerCore)

	def start(self, station_id, station_from):
		log("Yandex.Radio::start")
		self.radio = Radio(client, station_id, station_from)
		self.radio.start_radio(self.__on_start)

	def __on_start(self, track, next_track):
		log("Yandex.Radio::__on_start")
		self.add_next_track(track)
		self.add_next_track(next_track)
		self.play(pl, startpos=0)
		self.started = True

	def __on_play_next(self, track):
		log("Yandex.Radio::__on_play_next")
		self.add_next_track(track)

	def queue_next(self):
		log("Yandex.Radio::queue_next")
		self.radio.play_next(self.__on_play_next)

	def add_next_track(self, track):
		log("Yandex.Radio::add_next_track")
		track, url = track
		li = create_track_list_item(track)
		li.setPath(url)
		playIndex = pl.size()
		pl.add(url, li, playIndex)

		self.urls.append(url)

	def onPlayBackStopped(self):
		log("Yandex.Radio::onPlayBackStopped")
		self.queue_next()

	def onQueueNextItem(self):
		log("Yandex.Radio::onQueueNextItem")
		self.queue_next()

	def check(self):
		if not self.started:
			return

		try:
			url = self.getPlayingFile()
			self.valid = (url in self.urls) and pl.size() == len(self.urls)
			log("check valid: %s" % self.valid)
		except BaseException as ex:
			self.valid = False
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
	type_ = sys.argv[1]
	radio_type_ = sys.argv[2]
	station_key_ = sys.argv[3]

	# get stations info
	auth, client = check_login(settings)

	# init playlist
	pl = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	pl.clear()

	# init player
	player = MyPlayer()

	if type_ == "custom":
		player.start("%s:%s" % (radio_type_, station_key_), radio_type_)
	else:
		stations = radio.make_structure(client)
		stations["dashboard"] = radio.make_dashboard(client)
		station = stations[radio_type_][station_key_]
		player.start(station.getId(), station.source.station.id_for_from)

	while not monitor.abortRequested():
		player.check()
		if not player.valid:
			break
		# Sleep/wait for abort for 10 seconds
		if monitor.waitForAbort(10):
			# Abort was requested while waiting. We should exit
			break

	log("Stopped")
	del monitor
	del player
	del client
