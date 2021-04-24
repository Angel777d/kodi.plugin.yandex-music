import os
import sys

sys.path.append("./")
sys.path.append(os.path.join(os.path.dirname(__file__), "lib/yandex-music-api/"))
sys.path.append(os.path.join(os.path.dirname(__file__), "lib/mutagen/"))

import xbmcaddon
import xbmcgui

from yandex_music import Client
from yandex_music.exceptions import Unauthorized, BadRequest


def tr(value):
    addon = xbmcaddon.Addon()
    return addon.getLocalizedString(value)


def check_login(settings):
    token = settings.getSetting('token')
    if not token:
        return False, Client()

    try:
        client = Client.from_token(token)
        return True, client
    except Unauthorized as _:
        return False, Client()


def login(settings):
    result, client = check_login(settings)
    if result:
        return True

    while True:
        username, password = get_login_password(settings)
        if do_login(settings, username, password):
            return True
        heading = tr(32103)
        line1 = tr(32104)
        # todo: localize
        stop_, retry_ = "Close", "Retry"
        do_retry = xbmcgui.Dialog().yesno(heading, line1, username, password, nolabel=stop_, yeslabel=retry_)
        if not do_retry:
            break

    return False


def do_login(settings, username, password):
    try:
        client = Client().from_credentials(username, password)
        settings.setSetting('token', client.token)
        return True
    except Unauthorized:
        return False
    except BadRequest:
        return False


def get_login_password(settings):
    username = settings.getSetting("username")

    if not username:
        heading = tr(32101)
        username = xbmcgui.Dialog().input(heading, type=xbmcgui.INPUT_ALPHANUM)
        settings.setSetting('username', username)

    heading = tr(32102)
    password = xbmcgui.Dialog().input(heading, type=xbmcgui.INPUT_ALPHANUM)

    return username, password
