# [Unofficial] Yandex Music Kodi plugin

## Kodi 19 "Matrix" supported

### Disclaimer

This project and its author neither associated, nor affiliated with Yandex in any way.

### Install

1. Download [plugin zip file][plugin_zip] from repository
2. In Kodi open Settings->System->Add-ons
3. Allow Unknown Sources
4. Open Settings->Add-ons->Install from ZIP file
5. Select downloaded [plugin zip file][plugin_zip]
6. That's all. You are awesome!
 
### Configure

All features will be available only after signing in Yandex.Music account.

1. Get Yandex Music auth token. [How to get token][get_token]
2. Start plugin and select Login option.
3. Paste your token and press ok.
4. Token can be changed in plugin settings.


 Yandex will
generate token. It can be found in plugin settings.

### Refs

* based on [yandex-music python library][ym_lib] by [MarshalX](https://github.com/MarshalX)

## [Неофициальный] плагин Яндекс Музыки для Kodi
### Установка

1. Скачайте [zip файл плагина][plugin_zip] из репозитория
2. В Kodi откройте Settings->System->Add-ons
3. Разрешите установку из неизвестных источников (Unknown Sources)
4. Откройте Settings->Add-ons->Install from ZIP file
5. Выберете скачаный [zip файл][plugin_zip]
6. Готово! Вы великолепны!


### Настройка:

Все возможности плагина станут доступны после логина в аккаунт Яндекса.

1. Раздобыть токен от яндекс музыки. [Как получить токен][get_token]
2. Запустите плагин и передите в поле Login.
3. Введите ваш токен и нажмите OK.
4. Токен может быть изменен в конфиге плагина в любой момент

### Old version

Older Kodi 18 "Leia" plugin is [here][plugin_18_zip]
Old versions not supported and can be outdated.

### Changelog
#### Version 0.1.7

* Update to latest YandexMusic lib.
* Some logs improved

#### Version 0.1.6

* Update to latest YandexMusic lib.
* User+Password login method removed
* How to get token link added to README

#### Version 0.1.5

* Login issues.
* Note: 16.01.22 - Login available with 2FA only

#### Version 0.1.4

* Search fixed
* Mixes fixed


<details>
  <summary>More</summary>

#### Version 0.1.3

* New YM authorization added.

#### Version 0.1.2

* Update YM lib to release.
* Update Mutagen to Head.
* Kodi 18 "Leia" version is no longer supported.

#### Version 0.1.1

* Library version updated

#### Version 0.1.0

* Python 3 for Kodi 19 supported
* Track item info updated
* Clear logs

#### Version 0.0.39

* Search api changes fixed

#### Version 0.0.38

* New yandex music account crash fixed

#### Version 0.0.37

* Mixes added

#### Version 0.0.36

* User playlist and user likes moved to own folder
* Chart added
* Russian description added to README.md

#### Version 0.0.35

* Radio and stream code refactoring and cleanup

#### Version 0.0.34

* Stream by track fixes

#### Version 0.0.30

* Radio fixed

#### Version 0.0.29

* Stream from a track, album, artist

#### Version 0.0.28

* Smart playlists update fixed

#### Version 0.0.27

* Get cover image crash fixed

#### Version 0.0.26

* codec option added
* high-res audio option added
* auto download option added

</details>

[plugin_zip]: https://github.com/Angel777d/kodi.plugin.yandex-music/raw/master/bin/kodi.plugin.yandex-music-0.1.7.zip

[plugin_18_zip]: https://github.com/Angel777d/kodi.plugin.yandex-music/raw/master/bin/kodi.plugin.yandex-music-0.0.39.zip

[ym_lib]: https://github.com/MarshalX/yandex-music-api

[get_token]: https://github.com/MarshalX/yandex-music-token