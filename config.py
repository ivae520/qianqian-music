"""千千动听 - 配置管理"""
from __future__ import annotations
import sys, os, json, shutil


def _config_dir() -> str:
    if getattr(sys, 'frozen', False):
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
        d = os.path.join(base, '千千动听')
    else:
        d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
    os.makedirs(d, exist_ok=True)
    return d


def _migrate() -> None:
    if not getattr(sys, 'frozen', False):
        return
    old = os.path.join(os.path.dirname(sys.executable), "config")
    if not os.path.isdir(old) or any(not f.startswith('.') for f in os.listdir(CONFIG_DIR)):
        return
    for item in os.listdir(old):
        src, dst = os.path.join(old, item), os.path.join(CONFIG_DIR, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)


CONFIG_DIR = _config_dir()
_migrate()

FAVORITES_FILE = os.path.join(CONFIG_DIR, "songs.json")
RECENT_FILE = os.path.join(CONFIG_DIR, "played.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
DOWNLOAD_DIR_DEFAULT = os.path.join(CONFIG_DIR, "music")
PLAYLISTS_FILE = os.path.join(CONFIG_DIR, "imported_playlists.json")
DOWNLOADS_FILE = os.path.join(CONFIG_DIR, "downloads.json")
os.makedirs(DOWNLOAD_DIR_DEFAULT, exist_ok=True)


def load_json(path: str, default=None):
    if default is None:
        default = []
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    return json.loads(content) if content else default


def save_json(path: str, data) -> None:
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
    os.replace(tmp, path)


def load_favorites() -> list: return load_json(FAVORITES_FILE, []) or []
def save_favorites(v: list) -> None: save_json(FAVORITES_FILE, v)
def load_recent() -> list: return load_json(RECENT_FILE, []) or []
def save_recent(v: list) -> None: save_json(RECENT_FILE, v)
def load_downloads() -> list: return load_json(DOWNLOADS_FILE, []) or []
def save_downloads(v: list) -> None: save_json(DOWNLOADS_FILE, v)
def load_playlists() -> list: return load_json(PLAYLISTS_FILE, []) or []
def save_playlists(v: list) -> None: save_json(PLAYLISTS_FILE, v)


def load_settings() -> dict:
    data = load_json(SETTINGS_FILE, {})
    return data if isinstance(data, dict) else {}


def save_settings(s: dict) -> None:
    save_json(SETTINGS_FILE, s)


def load_volume() -> int:
    return max(0, min(100, int(load_settings().get("volume", 80))))


def save_volume(v: int) -> None:
    s = load_settings()
    s["volume"] = max(0, min(100, int(v)))
    save_settings(s)


def get_download_dir() -> str:
    d = load_settings().get('download_dir', '')
    return d if d and os.path.isdir(d) else DOWNLOAD_DIR_DEFAULT
