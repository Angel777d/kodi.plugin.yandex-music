import os
import sys

sys.path.append("./")
sys.path.append(os.path.join(os.path.dirname(__file__), "lib/"))

import xbmcaddon
import xbmcgui

from yandex_music import Client
from yandex_music.exceptions import UnauthorizedError
from utils import log, notify


def tr(value):
	addon = xbmcaddon.Addon()
	return addon.getLocalizedString(value)


def check_login(settings):
	token = settings.getSetting('token')
	if not token:
		return False, Client().init()
	try:
		client = Client(token).init()
		return True, client
	except UnicodeEncodeError as _:
		log(f"Failed to login with token '{token}'")
		notify("Error", "Wrong token format. Please update token", 5)
		return False, Client().init()
	except UnauthorizedError as _:
		log(f"Failed to login with token '{token}'")
		notify("Error", "Failed to login. Please update token.", 5)
		return False, Client().init()


def login(settings):
	result, client = check_login(settings)
	if result:
		return True

	while True:
		heading = tr(32101)
		token = xbmcgui.Dialog().input(heading, type=xbmcgui.INPUT_ALPHANUM)

		settings.setSetting('token', token)
		result, client = check_login(settings)

		if result:
			return True

		stop_ = tr(32102)
		retry_ = tr(32103)
		line1_ = tr(32104)

		do_retry = xbmcgui.Dialog().yesno(heading, line1_, nolabel=stop_, yeslabel=retry_)
		if not do_retry:
			break

	return False
