"""千千动听 - 自动更新模块"""
from __future__ import annotations
import os, sys, json, ssl, shutil, subprocess, tempfile, urllib.request, urllib.error
from typing import Optional
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QProgressBar, QScrollArea, QApplication, QFrame)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QLinearGradient
import version

REPO = "ivae520/qianqian-music"
API_RELEASE = f"https://api.github.com/repos/{REPO}/releases/latest"

_SSL = ssl.create_default_context()
_SSL.check_hostname = False
_SSL.verify_mode = ssl.CERT_NONE

_HEADERS = {"User-Agent": "QianqianMusic-Updater", "Accept": "application/vnd.github+json"}


def _get(url: str, timeout: int = 15) -> bytes:
    req = urllib.request.Request(url, headers=_HEADERS)
    return urllib.request.urlopen(req, timeout=timeout, context=_SSL).read()


def _get_json(url: str, timeout: int = 15) -> dict:
    return json.loads(_get(url, timeout).decode("utf-8", errors="replace"))


def _ver_tuple(v: str) -> tuple:
    parts = v.strip().lstrip("vV").split(".")
    nums = []
    for p in parts:
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)


def _is_newer(remote: str, local: str) -> bool:
    return _ver_tuple(remote) > _ver_tuple(local)


def _find_asset(release: dict) -> Optional[dict]:
    for a in release.get("assets", []):
        name = a.get("name", "").lower()
        if name.endswith(".exe") and ("千千动听" in name or "qianqian" in name):
            return a
    for a in release.get("assets", []):
        if a.get("name", "").lower().endswith(".zip"):
            return a
    return None


def cleanup_old_files():
    """清理自动更新后遗留的 .exe.old / .exe.bak 文件"""
    if not getattr(sys, "frozen", False):
        return
    exe = sys.executable
    d = os.path.dirname(exe)
    for suffix in (".old", ".bak", ".tmp", ".old0", ".bak0"):
        p = exe + suffix
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass
    try:
        for f in os.listdir(d):
            if f.lower().endswith((".exe.old", ".exe.bak")):
                fp = os.path.join(d, f)
                os.remove(fp)
    except Exception:
        pass


class _CheckWorker(QThread):
    done = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def run(self):
        try:
            r = _get_json(API_RELEASE, 15)
            if not isinstance(r, dict) or "tag_name" not in r:
                self.failed.emit("无法获取版本信息")
                return
            self.done.emit(r)
        except urllib.error.URLError:
            self.failed.emit("网络连接失败，请检查网络")
        except Exception as e:
            self.failed.emit(f"检查更新出错：{e}")


class _DownloadWorker(QThread):
    progress = pyqtSignal(int, int)
    finished_ok = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, url: str, filename: str):
        super().__init__()
        self._url = url
        self._filename = filename

    def run(self):
        try:
            req = urllib.request.Request(self._url, headers=_HEADERS)
            resp = urllib.request.urlopen(req, timeout=30, context=_SSL)
            total = int(resp.headers.get("Content-Length", 0))
            tmp = self._filename + ".tmp"
            got = 0
            with open(tmp, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
                    if total > 0:
                        self.progress.emit(got, total)
            os.replace(tmp, self._filename)
            self.finished_ok.emit(self._filename)
        except Exception as e:
            self.failed.emit(f"下载失败：{e}")


class _HeaderBar(QWidget):
    """渐变标题栏"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)
        self._title = "发现新版本"
        self._sub = ""

    def set_info(self, title, sub):
        self._title = title
        self._sub = sub
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        g = QLinearGradient(0, 0, w, 0)
        g.setColorAt(0, QColor("#0F6CBD"))
        g.setColorAt(0.5, QColor("#0A85D1"))
        g.setColorAt(1, QColor("#7CC8FF"))
        p.setBrush(g)
        p.setPen(Qt.NoPen)
        p.drawRect(0, 0, w, h)
        p.setPen(QColor(255, 255, 255, 235))
        p.setFont(QFont('"Microsoft YaHei UI"', 16, QFont.Bold))
        p.drawText(24, 14, w - 48, 30, Qt.AlignVCenter | Qt.AlignLeft, self._title)
        if self._sub:
            p.setPen(QColor(255, 255, 255, 180))
            p.setFont(QFont('"Microsoft YaHei UI"', 10))
            p.drawText(24, 40, w - 48, 24, Qt.AlignVCenter | Qt.AlignLeft, self._sub)


class UpdateDialog(QWidget):
    """更新对话框 - 支持最小化、后台下载"""
    _refs = []

    def __init__(self, parent=None, release: dict = None, current_ver: str = ""):
        super().__init__(parent)
        UpdateDialog._refs.append(self)
        self._release = release or {}
        self._current_ver = current_ver
        self._dl_worker = None
        self._check_worker = None
        self._asset_url = None
        self._asset_name = None
        self._downloaded_path = None
        self._checking = False
        self._is_latest = False
        self.setWindowTitle("千千动听 - 检查更新")
        self.setFixedSize(480, 480)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet(self._ss())
        self._build_ui()
        if release:
            self._show_release_info(release)
        else:
            self._start_check()

    def _ss(self) -> str:
        return """
        QWidget#root { background: #FFFFFF; }
        QLabel { font-family: "Microsoft YaHei UI", sans-serif; }
        QLabel#title { color: #1A1B1F; font-size: 15px; font-weight: 700; }
        QLabel#ver_old { color: #8B909A; font-size: 12px; }
        QLabel#ver_new { color: #0F6CBD; font-size: 16px; font-weight: 700; }
        QLabel#arrow { color: #B6BAC2; font-size: 16px; }
        QLabel#status { color: #5C6068; font-size: 12px; }
        QLabel#desc { color: #2A2B30; font-size: 12px; line-height: 1.6; }
        QLabel#section { color: #8B909A; font-size: 11px; font-weight: 600; }
        QPushButton#btnPrimary {
            background: #0F6CBD; color: white; border: none;
            border-radius: 6px; padding: 9px 28px; font-size: 12px; font-weight: 600;
        }
        QPushButton#btnPrimary:hover { background: #0C5AA3; }
        QPushButton#btnPrimary:disabled { background: #C7CAD0; }
        QPushButton#btnSecondary {
            background: #F3F4F7; color: #5C6068; border: 1px solid #E2E5EA;
            border-radius: 6px; padding: 9px 20px; font-size: 12px;
        }
        QPushButton#btnSecondary:hover { background: #E6E8ED; color: #1A1B1F; }
        QProgressBar {
            background: #ECEEF2; border: none; border-radius: 4px; max-height: 8px;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #0F6CBD, stop:1 #7CC8FF); border-radius: 4px;
        }
        QScrollArea { border: 1px solid #E8EBF0; border-radius: 8px; background: #FAFBFC; }
        QScrollBar:vertical { background: transparent; width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background: #D0D4DB; border-radius: 3px; min-height: 30px; }
        QScrollBar::handle:vertical:hover { background: #AEAEB2; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
        """

    def _build_ui(self):
        self.setObjectName("root")
        lo = QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)

        self._header = _HeaderBar(self)
        lo.addWidget(self._header)

        body = QWidget()
        blo = QVBoxLayout(body)
        blo.setContentsMargins(24, 16, 24, 20)
        blo.setSpacing(12)

        ver_lo = QHBoxLayout()
        ver_lo.setSpacing(8)
        sec = QLabel("版本")
        sec.setObjectName("section")
        ver_lo.addWidget(sec)
        ver_lo.addStretch()
        self._v_old = QLabel(f"v{self._current_ver}")
        self._v_old.setObjectName("ver_old")
        ver_lo.addWidget(self._v_old)
        arrow = QLabel("→")
        arrow.setObjectName("arrow")
        ver_lo.addWidget(arrow)
        self._v_new = QLabel("v...")
        self._v_new.setObjectName("ver_new")
        ver_lo.addWidget(self._v_new)
        blo.addLayout(ver_lo)

        self._status = QLabel("正在检查更新...")
        self._status.setObjectName("status")
        blo.addWidget(self._status)

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        self._progress.setTextVisible(False)
        blo.addWidget(self._progress)

        notes_sec = QLabel("更新内容")
        notes_sec.setObjectName("section")
        blo.addWidget(notes_sec)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setVisible(False)
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        il = QVBoxLayout(inner)
        il.setContentsMargins(14, 12, 14, 12)
        il.setSpacing(0)
        self._desc = QLabel("")
        self._desc.setObjectName("desc")
        self._desc.setWordWrap(True)
        self._desc.setTextFormat(Qt.MarkdownText)
        self._desc.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._desc.setTextInteractionFlags(Qt.TextSelectableByMouse)
        il.addWidget(self._desc)
        il.addStretch()
        self._scroll.setWidget(inner)
        blo.addWidget(self._scroll, 1)

        btn_lo = QHBoxLayout()
        btn_lo.setContentsMargins(0, 4, 0, 0)
        btn_lo.addStretch()
        self._btn_close = QPushButton("关闭")
        self._btn_close.setObjectName("btnSecondary")
        self._btn_close.setCursor(Qt.PointingHandCursor)
        self._btn_close.clicked.connect(self._on_close)
        btn_lo.addWidget(self._btn_close)
        self._btn_action = QPushButton("立即更新")
        self._btn_action.setObjectName("btnPrimary")
        self._btn_action.setCursor(Qt.PointingHandCursor)
        self._btn_action.setVisible(False)
        self._btn_action.clicked.connect(self._do_update)
        btn_lo.addWidget(self._btn_action)
        blo.addLayout(btn_lo)

        lo.addWidget(body, 1)

    def _start_check(self):
        self._checking = True
        self._status.setText("正在检查更新...")
        self._check_worker = _CheckWorker()
        self._check_worker.done.connect(self._on_check_done)
        self._check_worker.failed.connect(self._on_check_failed)
        self._check_worker.start()

    def _on_check_done(self, release: dict):
        self._checking = False
        remote_ver = (release.get("tag_name", "") or "").lstrip("vV")
        if not remote_ver:
            self._status.setText("无法获取远程版本信息")
            return
        if _is_newer(remote_ver, self._current_ver):
            self._show_release_info(release)
        else:
            self._is_latest = True
            self._status.setText(f"已是最新版本 v{self._current_ver}")
            self._v_new.setText(f"v{self._current_ver}")
            self._header.set_info("已是最新版本", "当前版本无需更新")
            self._scroll.setVisible(False)
            self._btn_action.setVisible(False)

    def _on_check_failed(self, msg: str):
        self._checking = False
        self._status.setText(msg)
        self._header.set_info("检查更新失败", msg)

    def _show_release_info(self, release: dict):
        remote_ver = (release.get("tag_name", "") or "").lstrip("vV")
        asset = _find_asset(release)
        body = release.get("body", "") or "暂无更新说明"
        self._v_new.setText(f"v{remote_ver}")
        self._header.set_info("发现新版本", f"v{self._current_ver} → v{remote_ver}")
        if asset:
            self._asset_url = asset.get("browser_download_url", "")
            self._asset_name = asset.get("name", "千千动听.exe")
            sz = asset.get("size", 0)
            sz_str = f"  ({sz / 1048576:.1f} MB)" if sz else ""
            self._status.setText(f"发现新版本，点击立即更新{sz_str}")
            self._btn_action.setVisible(True)
            self._btn_action.setText("立即更新")
        else:
            self._status.setText("发现新版本，但暂无下载文件")
            self._btn_action.setVisible(True)
            self._btn_action.setText("前往下载")
        self._desc.setText(body)
        self._scroll.setVisible(True)

    def _do_update(self):
        if not self._asset_url:
            import webbrowser
            webbrowser.open(f"https://github.com/{REPO}/releases/latest")
            return
        if self._dl_worker and self._dl_worker.isRunning():
            return
        target_dir = tempfile.mkdtemp(prefix="qianqian_update_")
        target = os.path.join(target_dir, self._asset_name or "千千动听.exe")
        self._progress.setVisible(True)
        self._progress.setValue(0)
        self._btn_action.setVisible(False)
        self._status.setText("正在下载更新...")
        self._dl_worker = _DownloadWorker(self._asset_url, target)
        self._dl_worker.progress.connect(self._on_dl_progress)
        self._dl_worker.finished_ok.connect(self._on_dl_done)
        self._dl_worker.failed.connect(self._on_dl_failed)
        self._dl_worker.start()

    def _on_dl_progress(self, got: int, total: int):
        if total > 0:
            pct = int(got * 100 / total)
            self._progress.setValue(pct)
            mb_got = got / 1048576
            mb_total = total / 1048576
            speed = ""
            self._status.setText(f"正在下载... {pct}%  ({mb_got:.1f}/{mb_total:.1f} MB)")

    def _on_dl_done(self, path: str):
        self._progress.setValue(100)
        self._status.setText("下载完成，正在安装...")
        self._downloaded_path = path
        if self.isMinimized():
            self.showNormal()
            self.raise_()
            self.activateWindow()
        QTimer.singleShot(500, self._apply_update)

    def _on_dl_failed(self, msg: str):
        self._progress.setVisible(False)
        self._status.setText(msg)
        self._btn_action.setVisible(True)
        self._btn_action.setText("重试下载")
        if self.isMinimized():
            self.showNormal()
            self.raise_()
            self.activateWindow()

    def _apply_update(self):
        if not self._downloaded_path or not os.path.exists(self._downloaded_path):
            return
        exe = sys.executable if getattr(sys, "frozen", False) else None
        if not exe:
            self._status.setText("非打包版本，无法自动安装")
            return
        old_path = exe + ".old"
        try:
            if os.path.exists(old_path):
                os.remove(old_path)
        except Exception:
            pass
        try:
            os.rename(exe, old_path)
        except Exception as e:
            self._status.setText(f"无法替换程序文件：{e}")
            return
        shutil.move(self._downloaded_path, exe)
        subprocess.Popen([exe])
        QApplication.quit()

    def _on_close(self):
        if self._dl_worker and self._dl_worker.isRunning():
            from PyQt5.QtWidgets import QMessageBox
            ret = QMessageBox.question(self, "确认关闭", "下载尚未完成，关闭后更新将中断。确定关闭吗？",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ret != QMessageBox.Yes:
                return
        self.close()

    def closeEvent(self, e):
        if self in UpdateDialog._refs:
            UpdateDialog._refs.remove(self)
        super().closeEvent(e)


def check_and_show(parent: QWidget, auto: bool = False):
    """检查更新并显示对话框。auto=True 时静默检查，无新版本不弹窗"""
    if auto:
        w = _CheckWorker()
        def _on_done(release):
            remote = (release.get("tag_name", "") or "").lstrip("vV")
            if remote and _is_newer(remote, version.__version__):
                dlg = UpdateDialog(parent, release, version.__version__)
                dlg.show()
        w.done.connect(_on_done)
        w.start()
    else:
        dlg = UpdateDialog(parent, None, version.__version__)
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()
