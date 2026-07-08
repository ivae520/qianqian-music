"""千千动听 - 播放器核心"""
from __future__ import annotations

import os, json, time, math, random, bisect, array, threading, ssl
import urllib.request, urllib.error
from urllib.parse import quote
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

from PyQt5.QtCore import QObject, QUrl, pyqtSignal, QTimer, Qt, QThread
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QLinearGradient
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QAudioProbe, QAudioFormat

import config

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

_QQ_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://y.qq.com/",
}

API_KEY = "ea8132f14298fbd6b2584af8f0b251aaf800fef8463c28829370b771b16b8774"


def _http_get_bytes(url: str, timeout: int = 15) -> bytes:
    req = urllib.request.Request(url, headers=_QQ_HEADERS)
    return urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX).read()


def _http_get_json(url: str, timeout: int = 15):
    data = _http_get_bytes(url, timeout)
    obj = json.loads(data.decode("utf-8", errors="replace"))
    return obj if isinstance(obj, (dict, list)) else {}


class QQMusicAPI:
    BASE = "https://cyapi.top/API/qq_music.php"

    @staticmethod
    def search(kw: str, count: int = 50) -> str:
        return f"{QQMusicAPI.BASE}?apikey={API_KEY}&msg={quote(kw)}&num={count}&type=json"

    @staticmethod
    def detail(mid: str, quality: str = "high") -> str:
        return f"{QQMusicAPI.BASE}?apikey={API_KEY}&mid={mid}&type=json&quality={quality}"


class HotAPI:
    BASE = "https://cyapi.top/API/music_hot.php"

    @staticmethod
    def list_() -> str:
        return f"{HotAPI.BASE}?apikey={API_KEY}"

    @staticmethod
    def detail(list_id: str) -> str:
        return f"{HotAPI.BASE}?apikey={API_KEY}&id={list_id}"


class SongListAPI:
    BASE = "https://cyapi.top/API/song_list.php"

    @staticmethod
    def import_playlist(url: str) -> str:
        return f"{SongListAPI.BASE}?apikey={API_KEY}&url={quote(url)}"


class LyricParser:
    @staticmethod
    def parse_lrc(lrc_str: str) -> Tuple[List[Tuple[int, str]], str]:
        lines: List[Tuple[int, str]] = []
        album = ""
        offset_ms = 0
        if not lrc_str:
            return lines, album
        for line in lrc_str.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("[al:"):
                album = line[4:-1].strip() if line.endswith("]") else line[4:].strip()
                continue
            if line.startswith("[offset:"):
                try:
                    offset_ms = int(line[8:-1].strip() if line.endswith("]") else line[8:].strip())
                except (ValueError, TypeError):
                    offset_ms = 0
                continue
            if line.startswith(("[ti:", "[ar:", "[by:")):
                continue
            parts = line.split("]")
            text = parts[-1].strip()
            if not text:
                continue
            for i in range(len(parts) - 1):
                tp = parts[i].strip("[")
                if ":" not in tp:
                    continue
                segs = tp.split(":", 1)
                if len(segs) != 2:
                    continue
                try:
                    total_sec = int(segs[0]) * 60 + float(segs[1])
                    lines.append((int(total_sec * 1000) + offset_ms, text))
                except (ValueError, TypeError):
                    continue
        lines.sort(key=lambda x: x[0])
        return lines, album


_default_cover_cache: Dict[int, QPixmap] = {}


def default_cover_pix(size: int = 400) -> QPixmap:
    cached = _default_cover_cache.get(size)
    if cached is not None and not cached.isNull():
        return cached
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0, QColor("#0EA5A4"))
    grad.setColorAt(1, QColor("#2DD4BF"))
    p.setBrush(grad)
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(0, 0, size, size, size // 8, size // 8)
    p.setBrush(QColor(255, 255, 255, 80))
    cx, cy = size // 2, size // 2
    s = size // 4
    p.drawRoundedRect(cx - s // 2, cy - s, 4, s * 2, 2, 2)
    p.drawRoundedRect(cx + s // 2 - 4, cy - s - s // 3, 4, s * 2 + s // 3, 2, 2)
    p.drawRect(cx - s // 2, cy - s, s + 2, 4)
    p.setBrush(QColor(255, 255, 255))
    p.drawEllipse(cx - s // 2 - 6, cy + s - 6, 16, 12)
    p.drawEllipse(cx + s // 2 - 4, cy + s // 3 - 6, 16, 12)
    p.end()
    _default_cover_cache[size] = pix
    return pix


def _fft(x):
    n = len(x)
    rev = [0] * n
    bits = (n - 1).bit_length() - 1
    for i in range(n):
        r = 0
        for j in range(bits + 1):
            r = (r << 1) | ((i >> j) & 1)
        rev[i] = r
    y = [x[rev[i]] for i in range(n)]
    m = 2
    while m <= n:
        ang = -2.0 * math.pi / m
        wr, wi = math.cos(ang), math.sin(ang)
        for s in range(0, n, m):
            wpr, wpi = 1.0, 0.0
            for j in range(m // 2):
                idx = s + j + m // 2
                t_re = wpr * y[idx].real - wpi * y[idx].imag
                t_im = wpr * y[idx].imag + wpi * y[idx].real
                u = y[s + j]
                y[s + j] = complex(u.real + t_re, u.imag + t_im)
                y[s + j + m // 2] = complex(u.real - t_re, u.imag - t_im)
                nwpr = wpr * wr - wpi * wi
                nwpi = wpr * wi + wpi * wr
                wpr, wpi = nwpr, nwpi
        m <<= 1
    return y


_shared_nam: Optional[QNetworkAccessManager] = None


def get_shared_nam() -> QNetworkAccessManager:
    global _shared_nam
    if _shared_nam is None:
        _shared_nam = QNetworkAccessManager()
    return _shared_nam


class _JsonBridge(QObject):
    done = pyqtSignal(object, object)


class _CoverBridge(QObject):
    ready = pyqtSignal(str, QImage)
    failed = pyqtSignal(str)


class CoverLoader(QObject):
    _instance: Optional["CoverLoader"] = None

    def __init__(self):
        super().__init__()
        self._bridge = _CoverBridge()
        self._bridge.ready.connect(self._on_ready)
        self._bridge.failed.connect(self._on_failed)
        self._ex = ThreadPoolExecutor(max_workers=3)
        self._pending: Dict[str, list] = {}
        self._is_shutting_down = False
        self._mem_cache: Dict[str, QPixmap] = {}
        self._mem_cache_order: List[str] = []
        self._mem_cache_max = 20

    @classmethod
    def instance(cls) -> "CoverLoader":
        if cls._instance is None:
            cls._instance = CoverLoader()
        return cls._instance

    def shutdown(self):
        self._is_shutting_down = True
        try:
            self._ex.shutdown(wait=False)
        except Exception:
            pass

    def load(self, url: str, callbacks: list):
        if self._is_shutting_down or not url:
            if callbacks:
                try:
                    callbacks[0](default_cover_pix(128))
                except Exception:
                    pass
            return
        if url in self._mem_cache:
            for cb in callbacks:
                try:
                    cb(self._mem_cache[url])
                except Exception:
                    pass
            return
        if url in self._pending:
            self._pending[url].extend(callbacks)
            return
        self._pending[url] = list(callbacks)
        self._ex.submit(self._fetch, url)

    def _fetch(self, url: str):
        img = QImage()
        try:
            data = _http_get_bytes(url, 15)
            if img.loadFromData(data):
                self._bridge.ready.emit(url, img)
                return
        except Exception:
            pass
        self._bridge.failed.emit(url)

    def _on_ready(self, url: str, img: QImage):
        cbs = self._pending.pop(url, None)
        if cbs is None:
            return
        pix = QPixmap.fromImage(img).scaled(
            128, 128, Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
        if len(self._mem_cache) >= self._mem_cache_max:
            old = self._mem_cache_order.pop(0)
            self._mem_cache.pop(old, None)
        self._mem_cache[url] = pix
        self._mem_cache_order.append(url)
        for cb in cbs:
            try:
                cb(pix)
            except Exception:
                pass

    def _on_failed(self, url: str):
        cbs = self._pending.pop(url, None)
        if cbs is None:
            return
        for cb in cbs:
            try:
                cb(default_cover_pix(128))
            except Exception:
                pass


class _SearchThread(QThread):
    result = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self._url = url

    def run(self):
        try:
            data = _http_get_json(self._url, 15)
            if not isinstance(data, (dict, list)):
                self.error.emit("接口返回格式异常")
            else:
                self.result.emit(data)
        except urllib.error.HTTPError as e:
            self.error.emit(f"网络请求失败 ({e.code})")
        except urllib.error.URLError:
            self.error.emit("无法连接服务器，请检查网络")
        except Exception as e:
            self.error.emit(f"搜索出错：{e}")


class _FFTWorker(QThread):
    levelsReady = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._queue: list = []
        self._lock = threading.Lock()
        self._running = True

    def feed(self, seg: list):
        with self._lock:
            self._queue = [seg]
        if not self.isRunning():
            self.start()

    def stop(self):
        self._running = False
        try:
            self.quit()
            self.wait(500)
        except Exception:
            pass

    def run(self):
        W = 256
        NB = 64
        half = W // 2
        two_pi = 2.0 * math.pi
        inv = 1.0 / (W - 1)
        fmin, fmax = 1.0, float(half - 1)
        ratio = fmax / fmin
        bands_pre = [(max(1, int(round(fmin * ratio ** (i / NB)))),
                      max(2, int(round(fmin * ratio ** ((i + 1) / NB))))) for i in range(NB)]
        smooth = [0.0] * NB
        while self._running:
            with self._lock:
                if not self._queue:
                    break
                seg = self._queue.pop(0)
            try:
                if len(seg) < W:
                    seg = seg + [0.0] * (W - len(seg))
                samples = [seg[i] * (0.5 - 0.5 * math.cos(two_pi * i * inv)) for i in range(W)]
                spec = _fft(samples)
                mags = [math.hypot(spec[i].real, spec[i].imag) for i in range(1, half)]
                bands = [0.0] * NB
                for i in range(NB):
                    lo, hi = bands_pre[i]
                    bands[i] = sum(mags[lo:hi]) / (hi - lo)
                rms = math.sqrt(sum(x * x for x in seg) / W)
                mx = max(bands) if max(bands) > 0 else 1.0
                overall = max(0.06, min(1.0, rms * 8.0))
                for i in range(NB):
                    smooth[i] = smooth[i] * 0.55 + (bands[i] / (mx + 1e-9)) * overall * 0.45
                self.levelsReady.emit([min(1.0, v) for v in smooth])
            except Exception:
                pass


class PlayerCore(QObject):
    playStateChanged = pyqtSignal(bool)
    positionChanged = pyqtSignal(int)
    durationChanged = pyqtSignal(int)
    songChanged = pyqtSignal(dict)
    coverReady = pyqtSignal(QPixmap)
    lyricsLoaded = pyqtSignal(list)
    lyricIndexChanged = pyqtSignal(int)
    searchFinished = pyqtSignal(list)
    searchError = pyqtSignal(str)
    hotListReady = pyqtSignal(list)
    hotDetailReady = pyqtSignal(list, str)
    playlistImported = pyqtSignal(dict)
    playlistsChanged = pyqtSignal()
    importProgress = pyqtSignal(str, int)
    downloadProgress = pyqtSignal(str, int, int)
    downloadFinished = pyqtSignal(str, bool, str)
    needRefreshFavorites = pyqtSignal()
    needRefreshRecent = pyqtSignal()
    needRefreshDownloads = pyqtSignal()
    favChanged = pyqtSignal(str, bool)
    errorMsg = pyqtSignal(str)
    audioLevels = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.player.setVolume(config.load_volume())

        self._nam = get_shared_nam()
        self._json_bridge = _JsonBridge()
        self._json_bridge.done.connect(self._on_json_done)
        self._json_ex = ThreadPoolExecutor(max_workers=3)

        self.current_song: Optional[dict] = None
        self.current_playlist: List[dict] = []
        self.current_playlist_index: int = -1
        self.current_lyrics: List[Tuple[int, str]] = []
        self.current_url: str = ""
        self._is_shutting_down = False
        self._pending_play_token = 0
        self._cover_token = 0
        self._lyric_index = -1
        self._last_pos = -1
        self._seeking = False
        self.volume = config.load_volume()
        self.manually_stopped = False
        self.play_mode = "repeat"

        self.favorites: List[dict] = config.load_favorites()
        self.recent: List[dict] = config.load_recent()
        self.downloaded_songs: List[dict] = config.load_downloads()
        self.imported_playlists: List[dict] = config.load_playlists()

        self.player.stateChanged.connect(self._on_playback_state)
        self.player.positionChanged.connect(self._on_position)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status)
        self.player.error.connect(self._on_player_error)

        self._probe = QAudioProbe()
        if self._probe.setSource(self.player):
            self._probe.audioBufferProbed.connect(self._on_audio_buffer)
        self._probe_last = 0.0
        self._fft_worker = _FFTWorker(self)
        self._fft_worker.levelsReady.connect(self.audioLevels.emit)

        QTimer.singleShot(500, self._start_scan_downloaded)

    def shutdown(self):
        self._is_shutting_down = True
        try:
            self._fft_worker.stop()
        except Exception:
            pass
        try:
            self._json_ex.shutdown(wait=False)
        except Exception:
            pass
        CoverLoader.instance().shutdown()
        try:
            self.player.stop()
        except Exception:
            pass

    def search(self, kw: str):
        if not kw:
            return
        th = _SearchThread(QQMusicAPI.search(kw, 50), self)
        th.result.connect(self._on_search_result)
        th.error.connect(self.searchError.emit)
        th.finished.connect(th.deleteLater)
        th.start()
        self._search_thread = th

    @staticmethod
    def _extract_song_list(data) -> List[dict]:
        if isinstance(data, list):
            return data
        if not isinstance(data, dict):
            return []
        for key in ("list", "data", "songs", "songlist", "song_list"):
            val = data.get(key)
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                for k in ("list", "songs", "items"):
                    if isinstance(val.get(k), list):
                        return val[k]
        return []

    def _on_search_result(self, data):
        songs = [norm for s in self._extract_song_list(data)
                 if (norm := self._normalize_song(s))]
        self.searchFinished.emit(songs)

    def load_hot_list(self):
        self._get_json(HotAPI.list_(), self._on_hot_list)

    def _on_hot_list(self, data):
        if isinstance(data, list):
            lst = data
        elif isinstance(data, dict):
            lst = data.get("data", data.get("list", []))
        else:
            lst = []
        result = []
        for x in lst:
            if isinstance(x, dict):
                result.append({
                    "id": str(x.get("list_id", x.get("id", ""))),
                    "name": x.get("list_name", x.get("name", x.get("title", ""))),
                    "cover": x.get("list_cover", x.get("cover", x.get("pic", ""))),
                    "singer": x.get("singer", x.get("artists", "")),
                    "sub": x.get("list_creator", x.get("creator",
                              x.get("nickname", x.get("list_desc", x.get("desc", ""))))),
                })
        self.hotListReady.emit(result)

    def load_hot_detail(self, list_id: str, title: str = ""):
        self._get_json(HotAPI.detail(list_id), lambda d: self._on_hot_detail(d, title))

    def _on_hot_detail(self, data, title: str):
        self.hotDetailReady.emit(self._parse_song_list(data), title)

    def import_playlist(self, url: str):
        self.importProgress.emit("正在导入歌单...", 10)
        self._get_json(SongListAPI.import_playlist(url), self._on_playlist_imported)

    def _on_playlist_imported(self, data):
        if not isinstance(data, dict):
            self.errorMsg.emit("歌单导入失败")
            return
        if data.get("error"):
            self.errorMsg.emit(f"导入失败: {data['error']}")
            self.importProgress.emit("导入失败", 100)
            return
        songs = self._parse_song_list(data)
        name = data.get("name", data.get("title", "导入的歌单"))
        cover = data.get("cover", data.get("pic", ""))
        if not cover and songs:
            cover = songs[0].get("cover", "")
        pl = {
            "id": str(data.get("id", time.time())),
            "name": name,
            "cover": cover,
            "songs": songs,
            "created": time.time(),
        }
        for i, p in enumerate(self.imported_playlists):
            if p.get("id") == pl["id"]:
                self.imported_playlists[i] = pl
                break
        else:
            self.imported_playlists.append(pl)
        config.save_playlists(self.imported_playlists)
        self.playlistImported.emit(pl)
        self.importProgress.emit(f"已导入 {len(songs)} 首", 100)

    def rename_playlist(self, pl_id: str, name: str):
        for p in self.imported_playlists:
            if p.get("id") == pl_id:
                p["name"] = name.strip() or "未命名歌单"
                config.save_playlists(self.imported_playlists)
                self.playlistsChanged.emit()
                return

    def delete_playlist(self, pl_id: str):
        self.imported_playlists = [p for p in self.imported_playlists if p.get("id") != pl_id]
        config.save_playlists(self.imported_playlists)
        self.playlistsChanged.emit()

    @staticmethod
    def _parse_duration(raw) -> int:
        if not isinstance(raw, dict):
            return 0
        v = (raw.get("duration") or raw.get("time") or raw.get("interval")
             or raw.get("songTime") or raw.get("songtime") or raw.get("dt")
             or raw.get("playTime") or raw.get("durationTime") or 0)
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return 0
            if ":" in v:
                try:
                    sec = 0
                    for p in v.split(":"):
                        sec = sec * 60 + int(p)
                    return sec * 1000
                except Exception:
                    return 0
            try:
                v = int(v)
            except Exception:
                return 0
        try:
            v = int(v)
        except (TypeError, ValueError):
            return 0
        if v <= 0:
            return 0
        return v * 1000 if v < 100000 else v

    @staticmethod
    def _normalize_song(s: dict) -> Optional[dict]:
        if not isinstance(s, dict):
            return None
        artists = (s.get("artists") or s.get("singer") or s.get("artist")
                   or s.get("singers") or s.get("singername") or s.get("artist_name")
                   or s.get("songer_name") or s.get("songer") or s.get("author")
                   or s.get("singer_name") or "")
        if isinstance(artists, list):
            artists = ", ".join(
                a.get("name", "") if isinstance(a, dict) else str(a) for a in artists)
        name = s.get("name", s.get("title", s.get("songname", s.get("song_name", ""))))
        mid = str(s.get("id", s.get("mid", s.get("songmid", s.get("song_mid", "")))))
        if not name or not mid:
            return None
        return {
            "name": name,
            "singer": str(artists) if artists else "",
            "mid": mid,
            "cover": s.get("cover", s.get("pic", s.get("album_cover", s.get("image", "")))),
            "album": s.get("album", s.get("albumname", "")),
            "duration": PlayerCore._parse_duration(s),
        }

    def _parse_song_list(self, data) -> List[dict]:
        return [norm for s in self._extract_song_list(data)
                if (norm := self._normalize_song(s))]

    def _get_json(self, url: str, callback):
        if self._is_shutting_down:
            return
        self._json_ex.submit(self._fetch_json, url, callback)

    def _fetch_json(self, url: str, callback):
        try:
            data = _http_get_json(url, 15)
        except Exception:
            data = {}
        self._json_bridge.done.emit(callback, data)

    def _on_json_done(self, callback, data):
        try:
            callback(data)
        except Exception:
            pass

    def play_song(self, song: dict, playlist: List[dict] = None, index: int = -1,
                  add_to_recent: bool = True):
        if not song or self._is_shutting_down:
            return
        song = dict(song)
        self._pending_play_token += 1
        token = self._pending_play_token
        self.current_song = song
        self.current_lyrics = []
        self._lyric_index = -1
        self._last_pos = -1
        self.songChanged.emit(song)
        self._load_cover(song.get("cover", ""))

        local_path = song.get("local_path", "")
        if playlist is not None:
            self.current_playlist = list(playlist)
            self.current_playlist_index = index if index >= 0 else -1
        else:
            self.current_playlist = []
            self.current_playlist_index = -1

        if local_path and os.path.isfile(local_path):
            self._play_local(song, token)
            if add_to_recent:
                self._add_to_recent(song)
            return
        mid = song.get("mid", "")
        if not mid:
            self.errorMsg.emit("歌曲 ID 缺失, 无法播放")
            return
        self._get_json(QQMusicAPI.detail(mid),
                       lambda d: self._on_detail_ready(d, song, add_to_recent, token))

    def _on_detail_ready(self, data, song, add_to_recent, token):
        if self._is_shutting_down or token != self._pending_play_token:
            return
        if not isinstance(data, dict) or not data:
            self.errorMsg.emit("获取歌曲信息失败")
            return
        url = data.get("url", "")
        if not url:
            self.errorMsg.emit("未找到播放链接")
            return
        url = url.replace("http://", "https://")

        artists = data.get("artists", [])
        if isinstance(artists, list) and artists:
            singer = artists[0].get("name", "") if isinstance(artists[0], dict) else str(artists[0])
        elif isinstance(artists, str):
            singer = artists
        else:
            singer = song.get("singer", "")

        album_obj = data.get("album", {})
        if isinstance(album_obj, dict):
            album = album_obj.get("name", "")
        elif isinstance(album_obj, str):
            album = album_obj
        else:
            album = song.get("album", "")

        cover_obj = data.get("cover", {})
        if isinstance(cover_obj, dict):
            cover_url = cover_obj.get("large", cover_obj.get("medium", cover_obj.get("small", "")))
        elif isinstance(cover_obj, str):
            cover_url = cover_obj
        else:
            cover_url = song.get("cover", "")

        song["cover"] = cover_url or song.get("cover", "")
        song["singer"] = singer
        song["album"] = album
        song["duration"] = PlayerCore._parse_duration(data)
        self.current_url = url

        lyric_obj = data.get("lyric", "")
        if isinstance(lyric_obj, dict):
            lrc_str = lyric_obj.get("text", "")
        elif isinstance(lyric_obj, str):
            lrc_str = lyric_obj
        else:
            lrc_str = ""
        if lrc_str:
            self.current_lyrics, album_from_lrc = LyricParser.parse_lrc(lrc_str)
            if album_from_lrc and not song.get("album"):
                song["album"] = album_from_lrc
            self.lyricsLoaded.emit(self.current_lyrics)
        if add_to_recent:
            self._add_to_recent(song)
        self._load_cover(song.get("cover", ""))
        self.current_song = song
        self.songChanged.emit(song)
        self.player.setMedia(QMediaContent(QUrl(url)))
        self.player.play()

    def _play_local(self, song: dict, token: int):
        if self._is_shutting_down or token != self._pending_play_token:
            return
        self.current_url = song.get("local_path", "")
        self.current_lyrics = []
        self.lyricsLoaded.emit([])
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(song["local_path"])))
        self.player.play()

    def toggle(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.manually_stopped = True
        else:
            self.player.play()
            self.manually_stopped = False

    def stop(self):
        self.player.stop()
        self.manually_stopped = True

    def set_play_mode(self, mode: str):
        if mode in ("repeat", "repeat_one", "shuffle"):
            self.play_mode = mode

    def next(self):
        self._advance(1, auto=False)

    def prev(self):
        self._advance(-1, auto=False)

    def _advance(self, direction: int, auto: bool = False):
        if not self.current_playlist:
            return
        n = len(self.current_playlist)
        if self.play_mode == "repeat_one" and auto:
            idx = self.current_playlist_index
        elif self.play_mode == "shuffle":
            idx = random.randrange(n) if n > 1 else 0
        else:
            idx = (self.current_playlist_index + direction) % n
        self.current_playlist_index = idx
        self.play_song(self.current_playlist[idx], self.current_playlist, idx)

    def seek(self, ms: int):
        if self._is_shutting_down:
            return
        self._seeking = True
        self.player.setPosition(ms)
        QTimer.singleShot(200, lambda: setattr(self, "_seeking", False))

    def set_volume(self, v: int):
        v = max(0, min(100, v))
        self.volume = v
        self.player.setVolume(v)
        config.save_volume(v)

    def _on_playback_state(self, state):
        self.playStateChanged.emit(state == QMediaPlayer.PlayingState)

    def _on_position(self, pos):
        if self._seeking:
            return
        self._last_pos = pos
        self.positionChanged.emit(pos)
        self._update_lyric(pos)

    def _on_duration_changed(self, dur):
        self.durationChanged.emit(dur)

    def _on_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            if self.current_playlist and self.current_playlist_index >= 0:
                self._advance(1, auto=True)
        elif status == QMediaPlayer.InvalidMedia:
            self.errorMsg.emit("无法播放该音频")

    def _on_player_error(self, err):
        if err != QMediaPlayer.NoError:
            self.errorMsg.emit(f"播放错误: {err}")

    def _on_audio_buffer(self, buffer):
        try:
            now = time.monotonic()
            if now - self._probe_last < 0.05:
                return
            self._probe_last = now
            fmt = buffer.format()
            ch = max(1, fmt.channelCount())
            st = fmt.sampleType()
            ss = fmt.sampleSize()
            data = buffer.data()
            nb = buffer.byteCount()
            if nb <= 0:
                return
            try:
                raw = data.asstring(nb) if hasattr(data, "asstring") else bytes(data)
            except Exception:
                try:
                    raw = bytes(data)
                except Exception:
                    return
            if st == QAudioFormat.Float and ss == 32:
                a = array.array("f", raw); sc = 1.0
            elif st == QAudioFormat.SignedInt and ss == 32:
                a = array.array("i", raw); sc = 1.0 / 2147483648.0
            elif st == QAudioFormat.SignedInt and ss == 16:
                a = array.array("h", raw); sc = 1.0 / 32768.0
            elif st == QAudioFormat.UnsignedInt and ss == 8:
                a = array.array("B", raw); sc = 1.0 / 128.0
            else:
                try:
                    a = array.array("h", raw); sc = 1.0 / 32768.0
                except Exception:
                    return
            W = 256
            need = W * ch
            if len(a) < need:
                a.extend([0] * (need - len(a)))
            if st == QAudioFormat.UnsignedInt and ss == 8:
                seg = [(a[i * ch] - 128) * sc for i in range(W)]
            else:
                seg = [a[i * ch] * sc for i in range(W)]
            self._fft_worker.feed(seg)
        except Exception:
            pass

    def _update_lyric(self, pos: int):
        if not self.current_lyrics:
            return
        idx = bisect.bisect_right(self.current_lyrics, (pos, "")) - 1
        idx = max(0, min(idx, len(self.current_lyrics) - 1))
        if idx != self._lyric_index:
            self._lyric_index = idx
            self.lyricIndexChanged.emit(idx)

    def _load_cover(self, url: str):
        self._cover_token += 1
        token = self._cover_token
        if url:
            CoverLoader.instance().load(url, [lambda pix: self._set_cover_pixmap(pix, token)])
        else:
            self._set_cover_pixmap(default_cover_pix(128), token)

    def _set_cover_pixmap(self, pix: QPixmap, token: int):
        if token != self._cover_token or self._is_shutting_down:
            return
        self.coverReady.emit(pix)

    def is_fav(self, mid: str) -> bool:
        return any(s.get("mid") == mid for s in self.favorites)

    def toggle_fav(self, song: dict):
        mid = song.get("mid", "")
        if not mid:
            return
        if self.is_fav(mid):
            self.favorites = [s for s in self.favorites if s.get("mid") != mid]
            self.favChanged.emit(mid, False)
        else:
            self.favorites.insert(0, song)
            self.favChanged.emit(mid, True)
        config.save_favorites(self.favorites)
        self.needRefreshFavorites.emit()

    def remove_from_recent(self, song: dict):
        mid = song.get("mid", "")
        if not mid:
            return
        self.recent = [s for s in self.recent if s.get("mid") != mid]
        config.save_recent(self.recent)
        self.needRefreshRecent.emit()

    def _add_to_recent(self, song: dict):
        mid = song.get("mid", "")
        if not mid:
            return
        self.recent = [s for s in self.recent if s.get("mid") != mid]
        self.recent.insert(0, song)
        if len(self.recent) > 100:
            self.recent = self.recent[:100]
        config.save_recent(self.recent)
        self.needRefreshRecent.emit()

    def download_song(self, song: dict, save_dir: str, filename: str = "", fmt: str = "mp3"):
        if not song:
            return
        mid = song.get("mid", "")
        if not mid:
            self.errorMsg.emit("无法下载: 缺少 ID")
            return

        def on_dl_detail(data):
            if not isinstance(data, dict) or not data:
                self.downloadFinished.emit(song.get("name", ""), False, "")
                return
            url = data.get("url", "")
            if not url:
                self.downloadFinished.emit(song.get("name", ""), False, "")
                return
            url = url.replace("http://", "https://")
            n = filename or song.get("name", "song")
            for c in '\\/:*?"<>|':
                n = n.replace(c, "_")
            ext = "flac" if "flac" in url.lower() else fmt
            save_path = os.path.join(save_dir, f"{n}.{ext}")
            self._do_download(url, save_path, song)

        quality = "lossless" if fmt == "flac" else "high"
        self._get_json(QQMusicAPI.detail(mid, quality=quality), on_dl_detail)

    def _do_download(self, url: str, save_path: str, song: dict):
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
        except Exception:
            pass
        self.downloadProgress.emit(song.get("name", ""), 0, 1)
        threading.Thread(target=self._download_worker, args=(url, save_path, song),
                         daemon=True).start()

    def _download_worker(self, url: str, save_path: str, song: dict):
        if self._is_shutting_down:
            return
        name = song.get("name", "")
        try:
            req = urllib.request.Request(url, headers=_QQ_HEADERS)
            resp = urllib.request.urlopen(req, timeout=120, context=_SSL_CTX)
            total = int(resp.headers.get("Content-Length", 0) or 0)
            got = 0
            with open(save_path, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
                    if total:
                        self.downloadProgress.emit(name, got, total)
            if self._is_shutting_down:
                return
            dl = dict(song)
            dl["local_path"] = save_path
            self.downloaded_songs = [s for s in self.downloaded_songs
                                     if s.get("local_path") != save_path]
            self.downloaded_songs.insert(0, dl)
            if len(self.downloaded_songs) > 200:
                self.downloaded_songs = self.downloaded_songs[:200]
            config.save_downloads(self.downloaded_songs)
            self.needRefreshDownloads.emit()
            self.downloadFinished.emit(name, True, save_path)
        except Exception:
            self.downloadFinished.emit(name, False, "")

    def _start_scan_downloaded(self):
        if self._is_shutting_down:
            return

        class _ScanThread(QThread):
            def __init__(self, dirs):
                super().__init__()
                self._dirs = dirs

            def run(self):
                results: List[dict] = []
                seen = set()
                for d in self._dirs:
                    if not d or not os.path.isdir(d):
                        continue
                    try:
                        for f in os.listdir(d):
                            if not f.lower().endswith((".mp3", ".flac", ".m4a", ".wav", ".ogg")):
                                continue
                            full = os.path.join(d, f)
                            if not os.path.isfile(full) or full in seen:
                                continue
                            seen.add(full)
                            results.append({
                                "name": os.path.splitext(f)[0],
                                "singer": "", "mid": "", "cover": "",
                                "local_path": full,
                            })
                    except Exception:
                        pass
                self.results = results

        dirs = []
        cfg_dd = config.get_download_dir()
        if cfg_dd and os.path.isdir(cfg_dd):
            dirs.append(cfg_dd)
        s = config.load_settings()
        if isinstance(s, dict):
            dl = s.get("download_dir", "")
            if dl and os.path.isdir(dl) and dl not in dirs:
                dirs.append(dl)
        th = _ScanThread(dirs)
        th.finished.connect(lambda: self._on_scan_done(getattr(th, "results", [])))
        th.start()
        self._scan_thread = th

    def _on_scan_done(self, results: List[dict]):
        if self._is_shutting_down:
            return
        old_map = {s.get("local_path", ""): s for s in self.downloaded_songs}
        merged = []
        for r in results:
            old = old_map.get(r.get("local_path", ""), {})
            merged.append({**r, **{k: v for k, v in old.items() if v and k != "local_path"}})
        self.downloaded_songs = merged
        config.save_downloads(merged)
        self.needRefreshDownloads.emit()
