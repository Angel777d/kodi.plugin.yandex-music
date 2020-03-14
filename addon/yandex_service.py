import os
import sys
sys.path.append("./")
sys.path.append(os.path.join(os.path.dirname(__file__), "lib/yandex-music-api/"))

import xbmcaddon
import xbmcgui


from yandex_music import Client
from yandex_music.exceptions import Unauthorized, BadRequest


def tr(value):
	addon = xbmcaddon.Addon()
	return addon.getLocalizedString(value)


def checkLogin(settings):
	token = settings.getSetting('token')
	if not token:
		return False, Client()

	try:
		client = Client.from_token(token)
		return True, client
	except Unauthorized as ex:
		return False, Client()


def login(settings):
	result, client = checkLogin(settings)
	if result:
		return True

	username = settings.getSetting("username")
	password = settings.getSetting("password")

	if doLogin(settings, username, password):
		return True

	while True:
		username, password = getLoginPassword(settings)
		if doLogin(settings, username, password):
			return True
		heading = tr(32103)
		line1 = tr(32104)
		# todo: localize
		stop_, retry_ = "Close", "Retry"
		doRetry = xbmcgui.Dialog().yesno(heading, line1, username, password, nolabel=stop_, yeslabel=retry_)
		if not doRetry:
			break

	return False


def doLogin(settings, username, password):
	try:
		token = Client().generate_token_by_username_and_password(username, password)
		settings.setSetting('token', token)
		return True
	except Unauthorized as ex:
		return False
	except BadRequest as ex:
		return False


def getLoginPassword(settings):
	username = settings.getSetting("username")
	password = settings.getSetting("password")

	if not username:
		heading = tr(32101)
		username = xbmcgui.Dialog().input(heading, type=xbmcgui.INPUT_ALPHANUM)
		settings.setSetting('username', username)

	heading = tr(32102)
	password = xbmcgui.Dialog().input(heading, type=xbmcgui.INPUT_ALPHANUM, defaultt=password)
	settings.setSetting('password', password)

	return username, password
