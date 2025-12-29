from pathlib import Path
from zipfile import ZipFile

libs = {
	"yarl",
	"aiofiles",
	"aiohttp",
	"aiosignal",
	"async_timeout",
	"attr",
	"charset_normalizer",
	"frozenlist",
	"multidict",
	"mutagen",
	"requests",
	"yandex_music",
}


def save_to_zip(myzip: ZipFile, path: Path, root: Path, prefix: str = ""):
	for item in path.iterdir():
		if item.is_dir():
			save_to_zip(myzip, item, root, prefix)
		else:
			myzip.write(item, f"{prefix}{item.relative_to(root)}")


def build(major: int, minor: int, patch: int):
	path = Path(f"bin/kodi.plugin.yandex-music-{major}.{minor}.{patch}.zip")
	with ZipFile(path, mode="w") as myzip:
		save_to_zip(myzip, Path("addon"), Path("."))

		lib_path: Path = Path("./.venv/Lib/site-packages")
		for item in lib_path.iterdir():
			if item.is_dir() and item.name in libs:
				save_to_zip(myzip, item, lib_path, "addon/lib/")


build(0, 1, 7)
