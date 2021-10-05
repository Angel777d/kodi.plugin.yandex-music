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

[How to login](LOGIN.md)

### Configure

All features will be available only after signing in Yandex.Music account.

Start plugin and select Login option. Provide your login and password. Plugin doesn't store password. Yandex will
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

[Как залогинться](LOGIN.md)


### Настройка:

Все возможности плагина станут доступны после логина в аккаунт Яндекса.

1. Запустите плагин и передите в поле Login.
2. Введите ваш логин и нажмите OK.
3. Введите ваш пароль и нажмите OK.
4. Плагин не хранит пароль. Яндекс сгенерит токен. Токен можно найти в настройках плагина.

### Old version

Older Kodi 18 "Leia" plugin is [here][plugin_18_zip]

### Changelog
#### Version 0.1.4

* Search fixed
* Mixes fixed

#### Version 0.1.3

* New YM authorization added.

#### Version 0.1.2

* Update YM lib to release.
* Update Mutagen to Head.
* Kodi 18 "Leia" version is no longer supported.

<details>
  <summary>More</summary>

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

[plugin_zip]: https://github.com/Angel777d/kodi.plugin.yandex-music/raw/master/bin/kodi.plugin.yandex-music-0.1.4.zip

[plugin_18_zip]: https://github.com/Angel777d/kodi.plugin.yandex-music/raw/master/bin/kodi.plugin.yandex-music-0.0.39.zip

[ym_lib]: https://github.com/MarshalX/yandex-music-api
