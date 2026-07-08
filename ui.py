"""千千动听 v21.1.0 - UI 全面修复 (现代化UI/搜索修复/波动对齐/代码优化)"""
from __future__ import annotations
import os, sys, math, random, time
from PyQt5.QtCore import (Qt, QSize, QTimer, pyqtSignal, pyqtProperty, QRectF, QPropertyAnimation,
                           QEasingCurve, QPointF, QPoint)
from PyQt5.QtGui import (QColor, QPixmap, QFont, QPainter, QPen, QBrush,
                           QLinearGradient, QRadialGradient, QIcon, QPainterPath, QPolygonF,
                           QRegion)
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
                              QStackedWidget, QFrame, QSizePolicy, QSlider, QLineEdit,
                              QScrollArea, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
                              QFileDialog, QGridLayout, QSystemTrayIcon, QMenu, QMessageBox,
                              QDialog, QProgressBar, QApplication)
from icons import render
from core import CoverLoader
import config

C = {
    "bg": "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(234,241,255,0.80),stop:0.5 rgba(241,236,251,0.80),stop:1 rgba(255,239,247,0.80))", "bg2": "#FFFFFF", "bg3": "#ECEEF2",
    "sf": "#F3F4F7", "sfh": "#E6E8ED", "sfa": "#D8DBE2",
    "bd": "#E2E5EA", "bd2": "#D0D4DB",
    "tx": "#1A1B1F", "tx2": "#5C6068", "tx3": "#8B909A", "tx4": "#B6BAC2", "txi": "#FFFFFF",
    "pr": "#0F6CBD", "prh": "#0C5AA3", "prp": "#0A4B8A", "prs": "rgba(15,108,189,0.10)",
    "red": "#E5484D", "grn": "#2E9E5B", "org": "#F0921B",
    "pur": "#8B5CF6", "tea": "#56A0E8", "cy": "#7CC8FF", "blu": "#0F6CBD",
    "sbb": "#FFFFFF", "sbh": "rgba(15,108,189,0.07)",
    "sba": "rgba(15,108,189,0.14)", "sbbd": "#E2E5EA",
    "sbt": "#5C6068", "sbti": "#0F6CBD",
    "vz0": "#0F6CBD", "vz1": "#7CC8FF",
    "glass_sb": "rgba(255,255,255,0.92)", "glass_sb_border": "rgba(0,0,0,0.06)",
    "glass_tp": "rgba(255,255,255,0.80)", "glass_tp_border": "rgba(0,0,0,0.06)",
    "glass_pl": "rgba(255,255,255,0.94)", "glass_pl_border": "rgba(0,0,0,0.05)",
}
GP = "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(234,241,255,0.90),stop:0.5 rgba(241,236,251,0.90),stop:1 rgba(255,239,247,0.90))"
GP_S = "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(234,241,255,0.96),stop:0.5 rgba(241,236,251,0.96),stop:1 rgba(255,239,247,0.96))"
FF = '"Microsoft YaHei UI","PingFang SC","SF Pro Text","Segoe UI",sans-serif'
FFD = '"Microsoft YaHei UI","PingFang SC","SF Pro Display","Segoe UI",sans-serif'
R = {"xs": 4, "sm": 6, "md": 8, "lg": 12, "xl": 16, "xxl": 20, "fu": 9999}
S = {"sb": 138, "tp": 38, "pl": 72, "rw": 48, "cd": 48}


def _res(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def song_key(s):
    if not isinstance(s, dict):
        return ("", "", "")
    mid = str(s.get("mid", "")).strip()
    name = str(s.get("name", "")).strip().lower()
    singer = str(s.get("singer", "")).strip().lower()
    album = str(s.get("album", "")).strip().lower()
    if mid:
        return ("mid:" + mid, "", "")
    return (name, singer, album)


def rgba(hx, a):
    h = hx.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"

def fmt(ms):
    s = max(0, int(ms / 1000))
    return f"{s // 60}:{s % 60:02d}"

def _shadow(w, blur=24, off=(0, 4), co=(0, 0, 0, 24)):
    e = QGraphicsDropShadowEffect(w)
    e.setBlurRadius(blur); e.setOffset(*off); e.setColor(QColor(*co))
    w.setGraphicsEffect(e)

_SQSS = """
QScrollArea{background:transparent;border:none}
QScrollBar:vertical{background:transparent;width:8px;border-radius:4px;margin:0}
QScrollBar::handle:vertical{background:transparent;border-radius:4px;min-height:30px}
QScrollArea:hover QScrollBar::handle:vertical{background:#C7C7CC}
QScrollBar::handle:vertical:hover{background:#AEAEB2}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;background:transparent}
QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{background:transparent}
"""

class SmoothScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._anim = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._anim.setDuration(280); self._anim.setEasingCurve(QEasingCurve.OutCubic)
    def wheelEvent(self, e):
        sb = self.verticalScrollBar()
        notch = e.angleDelta().y() / 120.0
        target = max(sb.minimum(), min(sb.maximum(), sb.value() - notch * 90))
        self._anim.stop(); self._anim.setStartValue(sb.value())
        self._anim.setEndValue(int(round(target))); self._anim.start()

def _sc():
    s = SmoothScrollArea(); s.setWidgetResizable(True)
    s.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    s.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    s.setStyleSheet(_SQSS); return s

def _fade_in(rows):
    n = len(rows)
    if n == 0 or n > 20:
        return
    for i, r in enumerate(rows):
        old_eff = getattr(r, "_fade_eff", None)
        old_anim = getattr(r, "_fade_anim", None)
        if old_anim is not None:
            try: old_anim.stop()
            except Exception: pass
        if old_eff is not None:
            try: r.setGraphicsEffect(None)
            except Exception: pass
        eff = QGraphicsOpacityEffect(r); eff.setOpacity(0.0); r.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity", r)
        anim.setDuration(150); anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(0.0); anim.setEndValue(1.0)
        r._fade_anim = anim; r._fade_eff = eff
        def _clr(w=r, a=anim, e=eff):
            try:
                a.stop(); w.setGraphicsEffect(None)
            except Exception: pass
            try: a.deleteLater()
            except Exception: pass
        anim.finished.connect(_clr)
        QTimer.singleShot(i * 14, anim.start)

def _clear_rows(rows):
    from sip import isdeleted
    for r in rows:
        try:
            if isdeleted(r):
                continue
            anim = getattr(r, "_fade_anim", None)
            if anim is not None:
                try: anim.stop()
                except Exception: pass
            try: r.setGraphicsEffect(None)
            except Exception: pass
        except Exception:
            pass
        try: r.deleteLater()
        except Exception: pass
    rows.clear()

def _hd(title, cnt=None):
    w = QWidget(); w.setFixedHeight(40)
    w.setStyleSheet("background:transparent;border:none")
    lo = QHBoxLayout(w); lo.setContentsMargins(24, 0, 24, 0); lo.setSpacing(10)
    ac = QLabel(); ac.setFixedSize(3, 16)
    ac.setStyleSheet(f"background:{C['pr']};border-radius:2px")
    lo.addWidget(ac)
    hl = QLabel(title)
    hl.setStyleSheet(f"color:{C['tx']};font-family:{FFD};font-size:15px;font-weight:700;background:transparent")
    lo.addWidget(hl); lo.addStretch()
    if cnt: lo.addWidget(cnt)
    return w

def _lc(songs, rows):
    from sip import isdeleted
    cl = CoverLoader.instance()
    for s in songs:
        url, mid = s.get("cover", ""), s.get("mid", "")
        if url and mid:
            def _cb(pix, m=mid, rs=rows):
                for r in rs:
                    try:
                        if not isdeleted(r) and r.song.get("mid", "") == m:
                            r.set_cover(pix)
                    except Exception:
                        pass
            cl.load(url, [_cb])

def _btn_ss(rad=16):
    return (f"QPushButton{{background:transparent;border:none;border-radius:{rad}px}}"
            f"QPushButton:hover{{background:{rgba(C['sfh'],0.5)}}}"
            f"QPushButton:pressed{{background:{rgba(C['sfa'],0.5)}}}"
            f"QPushButton:focus{{outline:none}}")

class AnimLineEdit(QLineEdit):
    def __init__(self, w0=220, parent=None):
        super().__init__(parent)
        self._w0 = w0; self._w = w0; self.setFixedWidth(w0)
        self._anim = QPropertyAnimation(self, b"w"); self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self.setFocusPolicy(Qt.ClickFocus)
    def getw(self): return self._w
    def setw(self, v):
        self._w = v; self.setFixedWidth(int(round(v)))
    w = pyqtProperty(int, getw, setw)
    def _to(self, v):
        try:
            self._anim.stop(); self._anim.setStartValue(self._w)
            self._anim.setEndValue(int(round(v))); self._anim.start()
        except RuntimeError:
            pass
    def enterEvent(self, e):
        self._to(self._w0 * 0.92)
        super().enterEvent(e)
    def leaveEvent(self, e):
        self._to(self._w0)
        super().leaveEvent(e)

class CDDisc(QWidget):
    clicked = pyqtSignal()
    def __init__(self, sz=56, spin=True, parent=None):
        super().__init__(parent)
        self._sz = sz; self._ang = 0.0; self._px = None
        self._can_spin = spin
        self._spin = False
        self.setFixedSize(sz, sz); self.setCursor(Qt.PointingHandCursor)
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick)

    def set_pix(self, px):
        if px and not px.isNull():
            s = self._sz
            self._px = px.scaled(int(s*0.65), int(s*0.65), Qt.KeepAspectRatioByExpanding,
                                 Qt.SmoothTransformation)
        else: self._px = None
        self.update()

    def set_spin(self, v):
        if not self._can_spin: return
        self._spin = v
        if v:
            if not self._timer.isActive(): self._timer.start(60)
        else:
            self._timer.stop()

    def _tick(self):
        self._ang = (self._ang + 4.0) % 360; self.update()

    def paintEvent(self, e):
        s = self._sz; p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        cx = cy = s / 2; ro = s * 0.46; ri = s * 0.14
        if self._px:
            p.save()
            path = QPainterPath(); path.addEllipse(QPointF(cx, cy), ro, ro); p.setClipPath(path)
            p.translate(cx, cy)
            if self._spin: p.rotate(self._ang)
            p.drawPixmap(int(-ro), int(-ro), int(ro*2), int(ro*2), self._px)
            p.restore()
        else:
            g = QRadialGradient(cx-ro*0.3, cy-ro*0.3, ro)
            g.setColorAt(0, QColor("#2B5C9E")); g.setColorAt(1, QColor("#0E2440"))
            p.setBrush(QBrush(g)); p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(cx, cy), ro, ro)
            p.setPen(QPen(QColor(255,255,255,50), 1.5))
            p.setFont(QFont("Arial", int(s*0.22)))
            p.drawText(QRectF(0, 0, s, s), Qt.AlignCenter, "\u266b")
        g2 = QRadialGradient(cx, cy, ro)
        g2.setColorAt(0, QColor(255,255,255,8)); g2.setColorAt(0.65, QColor(255,255,255,15))
        g2.setColorAt(0.85, QColor(60,60,67,60)); g2.setColorAt(1, QColor(60,60,67,100))
        p.setBrush(Qt.NoBrush); p.setPen(QPen(QBrush(g2), 1.5))
        p.drawEllipse(QPointF(cx, cy), ro-1, ro-1)
        p.setBrush(QColor(240,240,242,200)); p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), ri, ri)
        p.setBrush(QColor(200,200,205,150)); p.drawEllipse(QPointF(cx, cy), 3, 3)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self.clicked.emit()


class SquareCover(QWidget):
    def __init__(self, sz=220, parent=None):
        super().__init__(parent)
        self._sz = sz; self._px = None; self._letter = ""
        self.setFixedSize(sz, sz)

    def set_pix(self, px):
        if px and not px.isNull():
            self._px = px.scaled(self._sz, self._sz, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        else: self._px = None
        self.update()

    def set_letter(self, txt):
        self._letter = (txt or "").strip()[:1]
        self._px = None; self.update()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        s = self._sz; r = R["lg"]
        path = QPainterPath(); path.addRoundedRect(0, 0, s, s, r, r); p.setClipPath(path)
        if self._px:
            p.drawPixmap(0, 0, s, s, self._px)
        else:
            g = QRadialGradient(s*0.35, s*0.35, s*0.7)
            g.setColorAt(0, QColor("#2B5C9E")); g.setColorAt(1, QColor("#0E2440"))
            p.setBrush(QBrush(g)); p.setPen(Qt.NoPen)
            p.drawRoundedRect(0, 0, s, s, r, r)
            if self._letter:
                p.setPen(QPen(QColor(255, 255, 255, 220), 1.5))
                p.setFont(QFont(FFD, int(s*0.32), QFont.Bold))
                p.drawText(QRectF(0, 0, s, s), Qt.AlignCenter, self._letter)
            else:
                p.setPen(QPen(QColor(255, 255, 255, 50), 1.5))
                p.setFont(QFont("Arial", int(s*0.2)))
                p.drawText(QRectF(0, 0, s, s), Qt.AlignCenter, "\u266b")

class AudioVis(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bars = 48
        self._cur = [0.0] * self._bars
        self._tgt = [0.0] * self._bars
        self._seed = [random.random() for _ in range(self._bars)]
        self._act = False
        self._real = None
        self._real_t = 0.0
        self._phase = 0.0
        self._grad = None
        self._grad_h = -1
        self.setMouseTracking(False)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background:transparent")
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def feed(self, levels):
        if levels:
            self._real = levels
            self._real_t = time.monotonic()

    def set_active(self, v):
        self._act = v
        if v:
            if not self._timer.isActive():
                self._timer.start(50)
        else:
            if self._timer.isActive():
                self._timer.stop()
            for i in range(self._bars):
                self._cur[i] = 0.0
                self._tgt[i] = 0.0
            self.update()

    def _ensure_grad(self, h):
        if self._grad is not None and self._grad_h == h:
            return self._grad
        grad = QLinearGradient(0, h, 0, 0)
        grad.setColorAt(0.0, QColor(120, 180, 255, 90))
        grad.setColorAt(0.5, QColor(180, 150, 255, 200))
        grad.setColorAt(1.0, QColor(255, 170, 200, 230))
        self._grad = grad
        self._grad_h = h
        return grad

    def _resample(self, src, n):
        L = len(src)
        if L == n:
            return list(src)
        out = [0.0] * n
        for i in range(n):
            idx = i * L / float(n)
            lo = int(idx); hi = min(L - 1, lo + 1); f = idx - lo
            out[i] = src[lo] * (1 - f) + src[hi] * f
        return out

    def _tick(self):
        if not self._act:
            return
        now = time.monotonic()
        has_real = self._real is not None and (now - self._real_t) < 0.5
        if has_real:
            self._phase += 0.10
            raw = self._resample(self._real, self._bars)
            half = self._bars // 2
            for i in range(self._bars):
                src = raw[i] if i < half else raw[self._bars - 1 - i]
                fn = i / float(self._bars - 1) if self._bars > 1 else 0.5
                dist = abs(fn - 0.5) * 2.0
                boost = 1.35 - 0.4 * dist
                ripple = 0.05 * math.sin(self._phase * 0.8 + i * 0.45)
                self._tgt[i] = max(0.0, min(1.0, src * boost + ripple))
        else:
            energy = 0.30 + 0.25 * (0.5 + 0.5 * math.sin(now * 1.8)) + 0.12 * math.sin(now * 3.2 + 1.0)
            energy = max(0.15, min(0.95, energy))
            t = now * 9.0
            for i in range(self._bars):
                fn = i / float(self._bars - 1) if self._bars > 1 else 0.5
                dist = abs(fn - 0.5) * 2.0
                base = 0.55 * math.exp(-dist * 1.4) + 0.10
                jitter = 0.5 + 0.5 * math.sin(t + self._seed[i] * 6.283)
                pulse = 0.5 + 0.5 * math.sin(t * 0.7 + self._seed[i] * 12.0)
                self._tgt[i] = max(0.0, min(1.0, base * jitter * pulse * (0.4 + energy * 1.3)))
        for i in range(self._bars):
            d = self._tgt[i] - self._cur[i]
            if d > 0:
                self._cur[i] += d * 0.45
            else:
                self._cur[i] += d * 0.08
            if self._cur[i] < 0.002:
                self._cur[i] = 0.0
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if w < 10 or h < 10:
            return
        N = self._bars
        spacing = w / float(N)
        bw = max(1.8, spacing * 0.38)
        gap = spacing - bw
        base_y = h - 1.0
        usable = h - 3.0
        grad = self._ensure_grad(h)
        p.setPen(Qt.NoPen)
        rad = bw * 0.5
        for i in range(N):
            bh = max(1.2, self._cur[i] * usable)
            x = i * spacing + gap / 2
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(QRectF(x, base_y - bh, bw, bh), rad, rad)

class CoverWave(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._act = False; self._ph = 0.0; self._hover = False
        self._bars = 3; self._cur = [0.0] * self._bars
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    def set_active(self, v):
        self._act = v
        if v and not self._timer.isActive(): self._timer.start(90)
        elif not v: self._timer.stop(); self._cur = [0.0] * self._bars; self.update()

    def set_hover(self, v): self._hover = v; self.update()

    def _tick(self):
        self._ph += 0.30
        for i in range(self._bars):
            self._cur[i] = 0.35 + 0.65 * abs(math.sin(self._ph + i * 1.3))
        self.update()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        path = QPainterPath(); path.addRoundedRect(0, 0, w, h, R["sm"], R["sm"])
        p.setClipPath(path)
        if self._hover and not self._act:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(0, 0, 0, 100))
            p.drawRoundedRect(0, 0, w, h, R["sm"], R["sm"])
            tri = QPolygonF([
                QPointF(w * 0.42, h * 0.32),
                QPointF(w * 0.42, h * 0.68),
                QPointF(w * 0.70, h * 0.50)])
            p.setBrush(QColor(255, 255, 255, 235))
            p.drawPolygon(tri)
        elif self._act:
            bw = max(2.5, w / 9.0)
            gap = bw * 1.5
            total = self._bars * (bw + gap) - gap
            x0 = (w - total) / 2
            cy = h / 2.0
            g = QLinearGradient(0, cy - h * 0.3, 0, cy + h * 0.3)
            g.setColorAt(0, QColor(15, 108, 189, 240))
            g.setColorAt(1, QColor(124, 200, 255, 240))
            p.setPen(Qt.NoPen); p.setBrush(QBrush(g))
            for i in range(self._bars):
                bh = max(3.0, self._cur[i] * (h * 0.55))
                x = x0 + i * (bw + gap)
                p.drawRoundedRect(QRectF(x, cy - bh / 2, bw, bh), bw / 2, bw / 2)

class SeekBar(QSlider):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setFixedHeight(14); self.setCursor(Qt.PointingHandCursor)
        self._hv = False; self.setMouseTracking(True); self._set(self._n())

    def _n(self):
        return (f"QSlider::groove:horizontal{{background:transparent;height:4px}}"
                f"QSlider::handle:horizontal{{background:transparent;width:0;height:0;margin:0}}"
                f"QSlider::sub-page:horizontal{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 {C['pr']},stop:1 {C['cy']});border-radius:2px}}"
                f"QSlider::add-page:horizontal{{background:{C['bd']};border-radius:2px}}")

    def _h(self):
        return (f"QSlider::groove:horizontal{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 {rgba(C['pr'],0.12)},stop:1 {rgba(C['cy'],0.12)});"
                f"height:6px;border-radius:3px}}"
                f"QSlider::handle:horizontal{{background:white;width:13px;height:13px;margin:-5px 0;"
                f"border-radius:7px;border:2px solid {C['pr']};}}"
                f"QSlider::sub-page:horizontal{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 {C['pr']},stop:1 {C['cy']});border-radius:3px}}"
                f"QSlider::add-page:horizontal{{background:{C['bd']};border-radius:3px}}")

    def enterEvent(self, e): self._hv = True; self._set(self._h())
    def leaveEvent(self, e): self._hv = False; self._set(self._n())
    def _set(self, s): self.setStyleSheet(s)

class FlowLayout(QWidget):
    def __init__(self, h=12, v=12, parent=None):
        super().__init__(parent)
        self._h, self._v, self._items = h, v, []
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def addWidget(self, w):
        w.setParent(self); self._items.append(w)
        self.updateGeometry(); self._lay(QRectF(self.rect()))

    def clear(self):
        for it in self._items: it.hide(); it.deleteLater()
        self._items.clear(); self.updateGeometry()

    def hasHeightForWidth(self): return True
    def heightForWidth(self, w): return int(self._calc(w))
    def _calc(self, w):
        if not self._items: return 0
        m = self.contentsMargins(); x, y, rh = m.left(), m.top(), 0
        a = w - m.left() - m.right()
        for it in self._items:
            iw, ih = it.sizeHint().width(), it.sizeHint().height()
            if x + iw > a and x > m.left(): x = m.left(); y += rh + self._v; rh = 0
            x += iw + self._h; rh = max(rh, ih)
        return y + rh + m.bottom()

    def _lay(self, rect):
        if not self._items: return
        m = self.contentsMargins(); x, y, rh = m.left(), m.top(), 0
        a = rect.width() - m.left() - m.right()
        for it in self._items:
            iw, ih = it.sizeHint().width(), it.sizeHint().height()
            if x + iw > a and x > m.left(): x = m.left(); y += rh + self._v; rh = 0
            it.setGeometry(int(x), int(y), int(iw), int(ih)); it.show()
            x += iw + self._h; rh = max(rh, ih)

    def resizeEvent(self, e):
        super().resizeEvent(e); self._lay(QRectF(self.rect()))
    def minimumSizeHint(self): return QSize(0, int(self._calc(self.width() or 800)))

class RespGrid(QWidget):
    def __init__(self, cols=4, h=12, v=12, parent=None):
        super().__init__(parent)
        self._cols, self._h, self._v, self._items = cols, h, v, []
        self._cur_cols = 0
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._gl = QGridLayout(self); self._gl.setContentsMargins(0, 0, 0, 0)
        self._gl.setHorizontalSpacing(h); self._gl.setVerticalSpacing(v)
    def addWidget(self, w):
        self._items.append(w); w.setParent(self); self._cur_cols = 0; self._relay()
    def clear(self):
        for it in self._items: it.hide(); it.deleteLater()
        self._items.clear(); self._cur_cols = 0; self._relay()
    def showEvent(self, e):
        super().showEvent(e); self._cur_cols = 0; self._relay()
    def _cols_for(self, cw):
        return max(2, min(self._cols, (cw or 700) // 160))
    def _relay(self):
        cw = self.width() or 700
        cols = self._cols_for(cw)
        if cols == self._cur_cols and self._gl.count() == len(self._items):
            return
        for i in reversed(range(self._gl.count())):
            self._gl.takeAt(i)
        for i, it in enumerate(self._items):
            r, c = divmod(i, cols)
            self._gl.addWidget(it, r, c)
        for c in range(cols):
            self._gl.setColumnStretch(c, 1)
        self._cur_cols = cols
        self.updateGeometry()
    def resizeEvent(self, e):
        super().resizeEvent(e); self._relay()

class Thumb(QLabel):
    def __init__(self, sz=40, rad=R["sm"], parent=None):
        super().__init__(parent); self._sz, self._rad = sz, rad
        self.setFixedSize(sz, sz); self.setStyleSheet("background:transparent;border:none"); self._mk()

    def _mk(self):
        s = self._sz; px = QPixmap(s, s); px.fill(QColor(0, 0, 0, 0))
        p = QPainter(px); p.setRenderHint(QPainter.Antialiasing); p.setPen(Qt.NoPen)
        g = QRadialGradient(s*0.35, s*0.3, s*0.75)
        g.setColorAt(0, QColor("#3A3A5C")); g.setColorAt(1, QColor("#1D1D2E"))
        p.setBrush(QBrush(g)); p.drawRoundedRect(QRectF(0, 0, s, s), int(self._rad), int(self._rad))
        p.setPen(QPen(QColor(255, 255, 255, 50))); p.setFont(QFont("Arial", max(8, int(s*0.3))))
        p.drawText(QRectF(0, 0, s, s), Qt.AlignCenter, "\u266a")
        p.end(); self.setPixmap(px)

    def set_pix(self, px):
        if px and not px.isNull():
            s = self._sz; n = QPixmap(s, s); n.fill(QColor(0, 0, 0, 0))
            p = QPainter(n); p.setRenderHint(QPainter.Antialiasing)
            pt = QPainterPath(); pt.addRoundedRect(QRectF(0, 0, s, s), int(self._rad), int(self._rad))
            p.setClipPath(pt)
            p.drawPixmap(0, 0, s, s, px.scaled(s, s, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            p.end(); self.setPixmap(n)

class CoverArt(QWidget):
    def __init__(self, sz=200, rad=R["lg"], parent=None):
        super().__init__(parent)
        self._sz, self._rad, self._px = sz, rad, None
        self.setFixedSize(sz, sz)

    def set_pix(self, px):
        if px and not px.isNull():
            s = self._sz; r = QPixmap(s, s); r.fill(QColor(0, 0, 0, 0))
            p = QPainter(r); p.setRenderHint(QPainter.Antialiasing)
            pt = QPainterPath(); pt.addRoundedRect(QRectF(0, 0, s, s), int(self._rad), int(self._rad))
            p.setClipPath(pt)
            p.drawPixmap(0, 0, s, s, px.scaled(s, s, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            p.end(); self._px = r; self.update()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        s = self._sz; r = QRectF(0, 0, s, s)
        rp = QPainterPath(); rp.addRoundedRect(r, int(self._rad), int(self._rad)); p.setClipPath(rp)
        if self._px: p.drawPixmap(0, 0, self._px)
        else:
            g = QRadialGradient(s*0.35, s*0.3, s*0.75)
            g.setColorAt(0, QColor("#2B5C9E")); g.setColorAt(1, QColor("#0E2440"))
            p.setBrush(QBrush(g)); p.setPen(Qt.NoPen)
            p.drawRoundedRect(r, int(self._rad), int(self._rad))
        p.end()

class ElideLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._full = text or ""
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setWordWrap(False)
    def setText(self, t):
        self._full = t or ""
        super().setText(t)
    def paintEvent(self, e):
        if self._full and self.width() > 4:
            el = self.fontMetrics().elidedText(self._full, Qt.ElideRight, self.width() - 2)
            if el and el != self.text():
                super().setText(el)
        super().paintEvent(e)


class MarqueeLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._full = text or ""; self._offset = 0; self._hov = False; self._scroll = False
        self.setWordWrap(False); self.setTextInteractionFlags(Qt.NoTextInteraction)
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick)
    def setText(self, t):
        self._full = t or ""; self._offset = 0; super().setText(t); self._check()
    def _check(self):
        if not self._full or self.width() <= 4: return
        tw = self.fontMetrics().horizontalAdvance(self._full)
        self._scroll = tw > self.width() - 2
    def enterEvent(self, e):
        self._hov = True; self._offset = 0
        if self._scroll and not self._timer.isActive(): self._timer.start(40)
        super().enterEvent(e)
    def leaveEvent(self, e):
        self._hov = False; self._offset = 0; self._timer.stop(); self.update()
        super().leaveEvent(e)
    def resizeEvent(self, e):
        super().resizeEvent(e); self._check()
    def _tick(self):
        self._offset += 1
        tw = self.fontMetrics().horizontalAdvance(self._full)
        if self._offset > tw + 20: self._offset = -self.width() + 10
        self.update()
    def paintEvent(self, e):
        if not self._scroll or not self._hov:
            if self._full and self.width() > 4:
                el = self.fontMetrics().elidedText(self._full, Qt.ElideRight, self.width() - 2)
                super().setText(el)
            super().paintEvent(e); return
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        clip = QPainterPath(); clip.addRect(QRectF(0, 0, self.width(), self.height())); p.setClipPath(clip)
        p.setPen(self.palette().windowText().color())
        p.setFont(self.font())
        p.drawText(-self._offset, self.fontMetrics().ascent() + (self.height() - self.fontMetrics().height()) // 2, self._full)


class SongRow(QFrame):
    play = pyqtSignal(dict, list, int)
    fav = pyqtSignal(dict)
    dl = pyqtSignal(dict)
    delete = pyqtSignal(dict)
    open_folder = pyqtSignal(dict)
    remove = pyqtSignal(dict)

    def __init__(self, song, songs, idx, si=False, show_remove=False, parent=None):
        super().__init__(parent)
        self.song, self.songs, self.index = song, songs, idx
        self._pl = False; self._hv = False
        self._card_bg = "rgba(255,255,255,0.55)"; self._card_bd = "rgba(15,108,189,0.10)"
        self.setMouseTracking(True)
        self.setFixedHeight(52); self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"SongRow{{background:{self._card_bg};border:1px solid {self._card_bd};border-radius:14px}}")
        lo = QHBoxLayout(self); lo.setContentsMargins(14, 5, 14, 5); lo.setSpacing(10)
        if si:
            self._lx = QWidget(); self._lx.setFixedWidth(22)
            lxl = QHBoxLayout(self._lx); lxl.setContentsMargins(0, 0, 0, 0); lxl.setSpacing(0)
            lxl.setAlignment(Qt.AlignCenter)
            self._ix = QLabel(str(idx + 1)); self._ix.setFixedWidth(22)
            self._ix.setAlignment(Qt.AlignCenter)
            self._ix.setStyleSheet(f"color:{C['tx3']};font-family:{FF};font-size:12px;background:transparent;border:none")
            lxl.addWidget(self._ix)
            lo.addWidget(self._lx)
        else:
            self._lx = None; self._ix = None
        self._wv = QWidget(); self._wv.setFixedSize(42, 42)
        self._wv.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._wvl = QVBoxLayout(self._wv); self._wvl.setContentsMargins(0, 0, 0, 0)
        self._cv = Thumb(42, R["sm"]); self._wvl.addWidget(self._cv)
        self._cv.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._cw = CoverWave(self._wv); self._cw.setGeometry(0, 0, 42, 42); self._cw.raise_()
        lo.addWidget(self._wv)
        inf = QVBoxLayout(); inf.setContentsMargins(0, 0, 0, 0); inf.setSpacing(2)
        self._nm = ElideLabel(song.get("name", ""))
        self._nm.setStyleSheet(f"color:{C['tx']};font-family:{FF};font-size:13px;font-weight:500;background:transparent;border:none")
        self._nm.setTextFormat(Qt.PlainText); self._nm.setTextInteractionFlags(Qt.NoTextInteraction)
        inf.addWidget(self._nm)
        self._ar = ElideLabel(song.get("singer", ""))
        self._ar.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:11px;background:transparent;border:none")
        self._ar.setTextFormat(Qt.PlainText); self._ar.setTextInteractionFlags(Qt.NoTextInteraction)
        inf.addWidget(self._ar); lo.addLayout(inf, 1)
        self._du = QLabel(fmt(song.get("duration", 0)))
        self._du.setStyleSheet(f"color:{C['tx3']};font-family:{FF};font-size:11px;background:transparent;border:none"); lo.addWidget(self._du)
        self._fb = QPushButton(); self._fb.setFixedSize(28, 28); self._fb.setCursor(Qt.PointingHandCursor)
        self._fb.setIcon(QIcon(render("heart", 13, C["tx3"]))); self._fb.setStyleSheet(_btn_ss(14))
        self._fb.clicked.connect(lambda: self.fav.emit(self.song)); lo.addWidget(self._fb)
        self._db = QPushButton(); self._db.setFixedSize(28, 28); self._db.setCursor(Qt.PointingHandCursor)
        self._db.setIcon(QIcon(render("download", 13, C["tx3"]))); self._db.setStyleSheet(_btn_ss(14))
        self._db.clicked.connect(lambda: self.dl.emit(self.song)); lo.addWidget(self._db)
        self._ofb = QPushButton(); self._ofb.setFixedSize(28, 28); self._ofb.setCursor(Qt.PointingHandCursor)
        self._ofb.setIcon(QIcon(render("folder", 13, C["blu"]))); self._ofb.setStyleSheet(_btn_ss(14))
        self._ofb.clicked.connect(lambda: self.open_folder.emit(self.song)); lo.addWidget(self._ofb)
        self._dlb = QPushButton(); self._dlb.setFixedSize(28, 28); self._dlb.setCursor(Qt.PointingHandCursor)
        self._dlb.setIcon(QIcon(render("delete", 13, C["red"]))); self._dlb.setStyleSheet(_btn_ss(14))
        self._dlb.clicked.connect(lambda: self.delete.emit(self.song)); lo.addWidget(self._dlb)
        self._ofb.hide(); self._dlb.hide()
        self._rmb = QPushButton(); self._rmb.setFixedSize(28, 28); self._rmb.setCursor(Qt.PointingHandCursor)
        self._rmb.setIcon(QIcon(render("close", 12, C["tx3"]))); self._rmb.setStyleSheet(_btn_ss(14))
        self._rmb.clicked.connect(lambda: self.remove.emit(self.song)); lo.addWidget(self._rmb)
        self._rmb.setVisible(show_remove)
        self._dlp = QProgressBar(self); self._dlp.setFixedHeight(3); self._dlp.setTextVisible(False)
        self._dlp.setRange(0, 100); self._dlp.setValue(0); self._dlp.hide()
        self._dlp.setStyleSheet(f"QProgressBar{{background:transparent;border:none}}QProgressBar::chunk{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {C['pr']},stop:1 {C['cy']});border-radius:1px}}")

    def set_dl_progress(self, pct):
        self._dlp.show()
        self._dlp.setValue(max(0, min(100, int(pct))))
        self._dlp.setGeometry(0, self.height() - 3, self.width(), 3)

    def set_dl_done(self):
        self._dlp.hide()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._dlp.isVisible():
            self._dlp.setGeometry(0, self.height() - 3, self.width(), 3)

    def set_playing(self, v):
        self._pl = v
        if v:
            self._nm.setStyleSheet(f"color:{C['pr']};font-family:{FF};font-size:13px;font-weight:600;background:transparent;border:none")
            self.setStyleSheet(f"SongRow{{background:{C['sba']};border:1px solid {C['pr']};border-radius:14px}}")
        else:
            self._nm.setStyleSheet(f"color:{C['tx']};font-family:{FF};font-size:13px;font-weight:500;background:transparent;border:none")
            bg = "rgba(255,255,255,0.95)" if self._hv else self._card_bg
            bd = C['pr'] if self._hv else self._card_bd
            self.setStyleSheet(f"SongRow{{background:{bg};border:1px solid {bd};border-radius:14px}}")
        self._cw.set_active(v)

    def set_cover(self, px): self._cv.set_pix(px)
    def set_fav(self, v):
        ic, cl = ("heart_filled", C["red"]) if v else ("heart", C["tx3"]); self._fb.setIcon(QIcon(render(ic, 13, cl)))
    def set_dled(self, v):
        if v:
            self._db.setIcon(QIcon(render("check", 13, C["grn"])))
            self._ofb.show(); self._dlb.show()

    def enterEvent(self, e):
        self._hv = True
        local = self._wv.mapFromGlobal(self.mapToGlobal(e.pos()))
        if self._wv.rect().contains(local):
            self._cw.set_hover(True)
        if not self._pl:
            self.setStyleSheet(f"SongRow{{background:rgba(255,255,255,0.95);border:1px solid {C['pr']};border-radius:14px}}")
    def leaveEvent(self, e):
        self._hv = False
        self._cw.set_hover(False)
        if not self._pl:
            self.setStyleSheet(f"SongRow{{background:{self._card_bg};border:1px solid {self._card_bd};border-radius:14px}}")
    def focusInEvent(self, e):
        pass
    def mouseMoveEvent(self, e):
        local = self._wv.mapFromGlobal(self.mapToGlobal(e.pos()))
        self._cw.set_hover(self._wv.rect().contains(local))
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            local = self._wv.mapFromGlobal(self.mapToGlobal(e.pos()))
            if self._wv.rect().contains(local):
                e.accept(); self.play.emit(self.song, self.songs, self.index); return
        super().mousePressEvent(e)
    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton: e.accept(); self.play.emit(self.song, self.songs, self.index)

class Banner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setFixedHeight(130)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"Banner{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {C['pr']},stop:0.55 {C['tea']},stop:1 {C['cy']});border-radius:{R['lg']}px}}")
        lo = QVBoxLayout(self); lo.setContentsMargins(28, 0, 28, 0); lo.setSpacing(6)
        lo.addStretch()
        t = QLabel("\u5343\u5343\u52a8\u542c")
        t.setStyleSheet(f"color:#FFFFFF;font-family:{FFD};font-size:22px;font-weight:700;background:transparent;border:none")
        lo.addWidget(t)
        s = QLabel("\u8046\u542c\u7f8e\u597d\uff0c\u611f\u53d7\u97f3\u4e50\u7684\u529b\u91cf")
        s.setStyleSheet(f"color:rgba(255,255,255,0.85);font-family:{FF};font-size:11px;background:transparent;border:none")
        lo.addWidget(s)
        lo.addStretch()

class HotCard(QFrame):
    clicked = pyqtSignal(str, str)
    def __init__(self, hl, parent=None):
        super().__init__(parent); self._hid = hl.get("id", "")
        self._hv = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        lo = QVBoxLayout(self); lo.setContentsMargins(10, 10, 10, 12); lo.setSpacing(8)
        self._cv = SquareCover(124); self._cv.setFixedSize(124, 124)
        lo.addWidget(self._cv, 0, Qt.AlignCenter)
        cover_url = hl.get("cover", "")
        if cover_url:
            cl = CoverLoader.instance()
            cl.load(cover_url, [lambda pix, w=self._cv: w.set_pix(pix) if (pix and not pix.isNull()) else w.set_letter(hl.get("name", ""))])
        else:
            self._cv.set_letter(hl.get("name", ""))
        self._t = QLabel(hl.get("name", ""))
        self._t.setStyleSheet(f"color:{C['tx']};font-family:{FF};font-size:12px;font-weight:600;background:transparent;border:none")
        self._t.setAlignment(Qt.AlignCenter); self._t.setTextFormat(Qt.PlainText)
        self._t.setTextInteractionFlags(Qt.NoTextInteraction); self._t.setWordWrap(True)
        self._t.setFixedHeight(32); lo.addWidget(self._t)
        sub = hl.get("singer", "") or hl.get("sub", "")
        if sub:
            self._sub = QLabel(sub)
            self._sub.setStyleSheet(f"color:{C['tx3']};font-family:{FF};font-size:10px;background:transparent;border:none")
            self._sub.setAlignment(Qt.AlignCenter); self._sub.setTextFormat(Qt.PlainText)
            self._sub.setTextInteractionFlags(Qt.NoTextInteraction); self._sub.setWordWrap(True)
            lo.addWidget(self._sub)
        self._cv.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._t.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        if hasattr(self, "_sub"):
            self._sub.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._ref()
    def _ref(self):
        bd = C['pr'] if self._hv else C['bd']
        bg = C['sf'] if self._hv else C['bg2']
        self.setStyleSheet(f"HotCard{{background:{bg};border:1px solid {bd};border-radius:{R['lg']}px}}")
    def sizeHint(self): return QSize(144, 184)
    def enterEvent(self, e):
        self._hv = True; self._ref()
    def leaveEvent(self, e):
        self._hv = False; self._ref()
    def focusInEvent(self, e):
        pass
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            e.accept()
            self.clicked.emit(self._hid, self._t.text())
        else:
            e.ignore()

class PlaylistCard(QFrame):
    clicked = pyqtSignal(str, str)
    renamed = pyqtSignal(str, str)
    deleted = pyqtSignal(str)
    def __init__(self, pl, parent=None):
        super().__init__(parent); self._pl = pl; self._pid = pl.get("id", "")
        self._hv = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        lo = QVBoxLayout(self); lo.setContentsMargins(10, 10, 10, 12); lo.setSpacing(6)
        cv_row = QHBoxLayout(); cv_row.setContentsMargins(0, 0, 0, 0)
        self._cv = SquareCover(108); self._cv.setFixedSize(108, 108)
        cv_row.addWidget(self._cv, 0, Qt.AlignCenter)
        lo.addLayout(cv_row)
        cover_url = pl.get("cover", "")
        if cover_url:
            CoverLoader.instance().load(cover_url, [lambda pix, w=self._cv: w.set_pix(pix) if (pix and not pix.isNull()) else w.set_letter(pl.get("name", ""))])
        else:
            self._cv.set_letter(pl.get("name", ""))
        self._t = QLabel(pl.get("name", "歌单"))
        self._t.setStyleSheet(f"color:{C['tx']};font-family:{FF};font-size:12px;font-weight:600;background:transparent;border:none")
        self._t.setAlignment(Qt.AlignCenter); self._t.setTextFormat(Qt.PlainText)
        self._t.setWordWrap(True); self._t.setFixedHeight(32); lo.addWidget(self._t)
        self._cnt = QLabel(f"{len(pl.get('songs', []))} 首")
        self._cnt.setStyleSheet(f"color:{C['tx3']};font-family:{FF};font-size:10px;background:transparent;border:none")
        self._cnt.setAlignment(Qt.AlignCenter); lo.addWidget(self._cnt)
        btn_row = QHBoxLayout(); btn_row.setContentsMargins(0, 0, 0, 0); btn_row.setSpacing(4)
        self._rn = QPushButton(); self._rn.setFixedSize(24, 24); self._rn.setCursor(Qt.PointingHandCursor)
        self._rn.setFocusPolicy(Qt.NoFocus)
        self._rn.setIcon(QIcon(render("settings", 12, C["tx2"]))); self._rn.setStyleSheet(_btn_ss(12))
        self._rn.clicked.connect(self._do_rename); btn_row.addWidget(self._rn)
        self._dl = QPushButton(); self._dl.setFixedSize(24, 24); self._dl.setCursor(Qt.PointingHandCursor)
        self._dl.setFocusPolicy(Qt.NoFocus)
        self._dl.setIcon(QIcon(render("delete", 12, C["red"]))); self._dl.setStyleSheet(_btn_ss(12))
        self._dl.clicked.connect(lambda: self.deleted.emit(self._pid)); btn_row.addWidget(self._dl)
        lo.addLayout(btn_row)
        for w in (self._cv, self._t, self._cnt): w.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._ref()
    def _do_rename(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("重命名歌单")
        dlg.setFixedSize(320, 130)
        dlg.setStyleSheet(f"QDialog{{background:{C['bg2']};border-radius:12px}}")
        dl = QVBoxLayout(dlg); dl.setContentsMargins(20, 20, 20, 16); dl.setSpacing(10)
        lb = QLabel("歌单名称:"); lb.setStyleSheet(f"color:{C['tx']};font-family:{FF};font-size:13px;font-weight:600;background:transparent;border:none")
        dl.addWidget(lb)
        le = QLineEdit(self._t.text()); le.setFixedHeight(32)
        le.setStyleSheet(f"QLineEdit{{background:{C['sf']};border:1px solid {C['bd']};border-radius:6px;padding:0 10px;color:{C['tx']};font-family:{FF};font-size:12px}}QLineEdit:focus{{border-color:{C['pr']}}}")
        le.selectAll(); dl.addWidget(le)
        bl = QHBoxLayout(); bl.setSpacing(8); bl.addStretch()
        ok = QPushButton("确定"); ok.setFixedSize(64, 30); ok.setCursor(Qt.PointingHandCursor)
        ok.setStyleSheet(f"QPushButton{{background:{C['pr']};color:white;border:none;border-radius:6px;font-family:{FF};font-size:12px;font-weight:600}}QPushButton:hover{{background:{C['prh']}}}")
        cancel = QPushButton("取消"); cancel.setFixedSize(64, 30); cancel.setCursor(Qt.PointingHandCursor)
        cancel.setStyleSheet(f"QPushButton{{background:{C['sf']};color:{C['tx']};border:1px solid {C['bd']};border-radius:6px;font-family:{FF};font-size:12px}}QPushButton:hover{{background:{C['sfh']}}}")
        ok.clicked.connect(dlg.accept); cancel.clicked.connect(dlg.reject)
        bl.addWidget(cancel); bl.addWidget(ok); dl.addLayout(bl)
        le.returnPressed.connect(dlg.accept)
        if dlg.exec_() == QDialog.Accepted:
            new = le.text().strip()
            if new:
                self._t.setText(new)
                self.renamed.emit(self._pid, new)
    def _ref(self):
        bd = C['pr'] if self._hv else C['bd']
        bg = C['sf'] if self._hv else C['bg2']
        self.setStyleSheet(f"PlaylistCard{{background:{bg};border:1px solid {bd};border-radius:{R['lg']}px}}")
    def sizeHint(self): return QSize(140, 200)
    def enterEvent(self, e):
        self._hv = True; self._ref()
    def leaveEvent(self, e):
        self._hv = False; self._ref()
    def focusInEvent(self, e):
        pass
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            e.accept()
            self.clicked.emit(self._pid, self._t.text())
        else:
            e.ignore()

class StatsCard(QFrame):
    clicked = pyqtSignal()
    def __init__(self, title, value, icon, color, parent=None):
        super().__init__(parent); self.setFixedHeight(76)
        self._hv = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_StyledBackground, True)
        lo = QHBoxLayout(self); lo.setContentsMargins(14, 10, 14, 10); lo.setSpacing(10)
        ic = QLabel(); ic.setPixmap(render(icon, 18, color)); ic.setFixedSize(34, 34)
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        ic.setStyleSheet(f"background:rgba({r},{g},{b},0.10);border-radius:17px;border:none"); lo.addWidget(ic)
        inf = QVBoxLayout(); inf.setContentsMargins(0, 0, 0, 0); inf.setSpacing(2)
        self._v = QLabel(str(value))
        self._v.setStyleSheet(f"color:{C['tx']};font-family:{FFD};font-size:18px;font-weight:700;background:transparent;border:none")
        inf.addWidget(self._v)
        tl = QLabel(title)
        tl.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:11px;background:transparent;border:none")
        inf.addWidget(tl); lo.addLayout(inf, 1)
        for _w in (ic, self._v, tl):
            _w.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._ref()

    def set_value(self, v):
        self._v.setText(str(v))
    def _ref(self):
        bd = C['pr'] if self._hv else C['bd']
        self.setStyleSheet(f"StatsCard{{background:{C['bg2']};border:1px solid {bd};border-radius:{R['lg']}px}}")
    def enterEvent(self, e):
        self._hv = True; self._ref()
    def leaveEvent(self, e):
        self._hv = False; self._ref()
    def focusInEvent(self, e):
        pass
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: e.accept(); self.clicked.emit()
        else: e.ignore()

class Empty(QWidget):
    def __init__(self, icon="music", title="", sub="", parent=None):
        super().__init__(parent)
        lo = QVBoxLayout(self); lo.setAlignment(Qt.AlignCenter); lo.setSpacing(12)
        ic = QLabel(); ic.setPixmap(render(icon, 36, C["tx3"])); ic.setFixedSize(60, 60)
        ic.setAlignment(Qt.AlignCenter); ic.setStyleSheet(f"background:{C['sf']};border-radius:30px;border:none")
        lo.addWidget(ic, 0, Qt.AlignCenter)
        tl = QLabel(title)
        tl.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:13px;font-weight:600;background:transparent")
        tl.setAlignment(Qt.AlignCenter); lo.addWidget(tl, 0, Qt.AlignCenter)
        if sub:
            st = QLabel(sub)
            st.setStyleSheet(f"color:{C['tx3']};font-family:{FF};font-size:12px;background:transparent")
            st.setAlignment(Qt.AlignCenter); lo.addWidget(st, 0, Qt.AlignCenter)
        lo.addStretch()

class LyricBox(QWidget):
    FONTS = ["微软雅黑", "苹方", "PingFang SC", "宋体", "黑体", "楷体", "等线", "思源黑体"]
    seekRequested = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent); self._ci, self._lbs = -1, []
        self._times: list = []
        self._ff = f'"{self.FONTS[0]}"'; self._fs = 10
        self._cur_col = C["tx"]; self._nor_col = C["tx3"]
        self.setStyleSheet("background:transparent;border:none")

    def set_colors(self, cur: str, nor: str):
        self._cur_col, self._nor_col = cur, nor
        for i, lb in enumerate(self._lbs):
            lb.setStyleSheet(f"color:{self._cur_col if i == self._ci else self._nor_col};"
                             f"font-family:{self._ff};"
                             f"font-size:{self._fs+4 if i == self._ci else self._fs}px;"
                             f"{'font-weight:700;' if i == self._ci else ''}padding:"
                             f"{12 if i == self._ci else 10}px 0")
        self._sc = QScrollArea(self); self._sc.setWidgetResizable(True)
        self._sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._sc.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._sc.setStyleSheet(f"QScrollArea{{background:transparent;border:none}}"
                               f"QScrollBar:vertical{{background:transparent;width:8px;border-radius:4px;margin:0}}"
                               f"QScrollBar::handle:vertical{{background:transparent;border-radius:4px;min-height:30px}}"
                               f"QScrollArea:hover QScrollBar::handle:vertical{{background:#C7C7CC}}"
                               f"QScrollBar::handle:vertical:hover{{background:#AEAEB2}}"
                               f"QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;background:transparent}}")
        self._bx = QWidget(); self._bx.setStyleSheet("background:transparent")
        self._vl = QVBoxLayout(self._bx); self._vl.setContentsMargins(20, 120, 20, 200); self._vl.setSpacing(0); self._vl.addStretch()
        self._sc.setWidget(self._bx); QVBoxLayout(self).setContentsMargins(0, 0, 0, 0); self.layout().addWidget(self._sc)

    def set_font_size(self, fs):
        self._fs = max(10, min(34, fs))
        for i, lb in enumerate(self._lbs):
            if i == self._ci:
                lb.setStyleSheet(f"color:{self._cur_col};font-family:{self._ff};font-size:{self._fs+4}px;font-weight:700;padding:12px 0")
            else:
                lb.setStyleSheet(f"color:{self._nor_col};font-family:{self._ff};font-size:{self._fs}px;padding:10px 0")

    def set_font_family(self, ff):
        self._ff = ff
        for i, lb in enumerate(self._lbs):
            if i == self._ci:
                lb.setStyleSheet(f"color:{self._cur_col};font-family:{ff};font-size:{self._fs+4}px;font-weight:700;padding:12px 0")
            else:
                lb.setStyleSheet(f"color:{self._nor_col};font-family:{ff};font-size:{self._fs}px;padding:10px 0")

    def set_lyrics(self, lyrics):
        self._lbs.clear(); self._ci = -1; self._times = []
        while self._vl.count() > 1:
            it = self._vl.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        if not lyrics:
            no = QLabel("\u6682\u65e0\u6b4c\u8bcd")
            no.setStyleSheet(f"color:{self._nor_col};font-family:{self._ff};font-size:{self._fs}px;background:transparent")
            no.setAlignment(Qt.AlignCenter); self._vl.insertWidget(self._vl.count()-1, no); return
        for line in lyrics:
            if isinstance(line, dict):
                t = line.get("line", ""); ms = int(line.get("time", 0))
            elif isinstance(line, (list, tuple)) and len(line) >= 2:
                t = str(line[1]); ms = int(line[0])
            else:
                t = str(line); ms = 0
            lb = QLabel(t)
            lb.setStyleSheet(f"color:{self._nor_col};font-family:{self._ff};font-size:{self._fs}px;padding:10px 0")
            lb.setWordWrap(True); lb.setTextFormat(Qt.PlainText)
            lb.setAlignment(Qt.AlignCenter); lb.setCursor(Qt.PointingHandCursor)
            lb.installEventFilter(self)
            self._vl.insertWidget(self._vl.count()-1, lb); self._lbs.append(lb); self._times.append(ms)

    def eventFilter(self, obj, ev):
        if ev.type() == ev.MouseButtonPress and ev.button() == Qt.LeftButton:
            try:
                idx = self._lbs.index(obj)
            except ValueError:
                idx = -1
            if 0 <= idx < len(self._times) and self._times[idx] >= 0:
                self.seekRequested.emit(self._times[idx])
                return True
        return super().eventFilter(obj, ev)

    def set_current(self, idx):
        if idx == self._ci: return
        self._ci = idx
        for i, lb in enumerate(self._lbs):
            if i == idx: lb.setStyleSheet(f"color:{self._cur_col};font-family:{self._ff};font-size:{self._fs+4}px;font-weight:700;padding:12px 0")
            else: lb.setStyleSheet(f"color:{self._nor_col};font-family:{self._ff};font-size:{self._fs}px;padding:10px 0")
        if 0 <= idx < len(self._lbs):
            lb = self._lbs[idx]; sp = self._sc.viewport().height()
            self._sc.verticalScrollBar().setValue(lb.y() - sp // 2 + lb.height() // 2)

class LyricOverlay(QWidget):
    req_toggle = pyqtSignal()
    seekRequested = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("LyricOverlay{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #EAF1FF,stop:0.5 #F1ECFB,stop:1 #FFEFF7);border:none}")
        lo = QVBoxLayout(self); lo.setContentsMargins(0, 0, 0, 0); lo.setSpacing(0)

        hdr = QWidget(); hdr.setFixedHeight(48)
        hdr.setStyleSheet("background:transparent")
        hlo = QHBoxLayout(hdr); hlo.setContentsMargins(16, 0, 16, 0); hlo.setSpacing(8)
        hlo.addStretch()
        self._btn_toggle = QPushButton("\u5168")
        self._btn_toggle.setFixedSize(40, 28); self._btn_toggle.setCursor(Qt.PointingHandCursor)
        self._btn_toggle.setStyleSheet(f"QPushButton{{color:rgba(26,27,31,0.30);font-family:{FFD};font-size:11px;font-weight:400;background:rgba(255,255,255,0.30);border:none;border-radius:14px;padding:0 8px}}"
                                       f"QPushButton:hover{{background:#FFFFFF;color:{C['pr']}}}"
                                       f"QPushButton:pressed{{background:rgba(255,255,255,0.85)}}")
        self._btn_toggle.clicked.connect(self.req_toggle.emit); hlo.addWidget(self._btn_toggle)
        lo.addWidget(hdr)

        mid = QHBoxLayout(); mid.setContentsMargins(40, 10, 40, 20); mid.setSpacing(40)

        lp = QVBoxLayout(); lp.setAlignment(Qt.AlignCenter); lp.setSpacing(12)
        self._cover = SquareCover(200)
        lp.addWidget(self._cover, 0, Qt.AlignCenter)
        self._sn = QLabel(""); self._sn.setAlignment(Qt.AlignCenter)
        self._sn.setStyleSheet(f"color:{C['tx']};font-family:{FFD};font-size:16px;font-weight:700;background:transparent;border:none")
        lp.addWidget(self._sn)
        self._sa = QLabel(""); self._sa.setAlignment(Qt.AlignCenter)
        self._sa.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:13px;background:transparent;border:none")
        lp.addWidget(self._sa)

        self._lb = LyricBox()
        self._lb.seekRequested.connect(self.seekRequested)
        self._lb.set_colors("#0EA5E9", "#8B909A")

        fp = QHBoxLayout(); fp.setAlignment(Qt.AlignCenter); fp.setSpacing(10)
        self._lb_sm = QPushButton("\u2013")
        self._lb_sm.setFixedSize(30, 26); self._lb_sm.setCursor(Qt.PointingHandCursor)
        self._lb_sm.setStyleSheet(f"QPushButton{{color:{C['tx2']};font-family:{FF};font-size:13px;font-weight:600;background:transparent;border:1px solid {C['bd']};border-radius:8px}}"
                                  f"QPushButton:hover{{background:{rgba(C['sfh'],0.5)}}}"
                                  f"QPushButton:pressed{{background:{rgba(C['sfa'],0.5)}}}")
        self._lb_sm.clicked.connect(self._dec_font); fp.addWidget(self._lb_sm)
        self._ff_btn = QPushButton(self._lb.FONTS[0])
        self._ff_btn.setCursor(Qt.PointingHandCursor)
        self._ff_btn.setStyleSheet(f"QPushButton{{color:{C['tx2']};font-family:{FF};font-size:11px;background:transparent;border:none}}"
                                   f"QPushButton:hover{{color:{C['pr']}}}")
        self._ff_btn.clicked.connect(self._cycle_font); fp.addWidget(self._ff_btn)
        self._lb_lg = QPushButton("+")
        self._lb_lg.setFixedSize(30, 26); self._lb_lg.setCursor(Qt.PointingHandCursor)
        self._lb_lg.setStyleSheet(f"QPushButton{{color:{C['tx2']};font-family:{FF};font-size:13px;font-weight:600;background:transparent;border:1px solid {C['bd']};border-radius:8px}}"
                                  f"QPushButton:hover{{background:{rgba(C['sfh'],0.5)}}}"
                                  f"QPushButton:pressed{{background:{rgba(C['sfa'],0.5)}}}")
        self._lb_lg.clicked.connect(self._inc_font); fp.addWidget(self._lb_lg)
        lp.addLayout(fp)

        mid.addLayout(lp)

        mid.addWidget(self._lb, 1)

        lo.addLayout(mid, 1)

    def _dec_font(self):
        self._lb.set_font_size(self._lb._fs - 2)

    def _inc_font(self):
        self._lb.set_font_size(self._lb._fs + 2)

    def _cycle_font(self):
        from PyQt5.QtWidgets import QMenu
        m = QMenu(self)
        m.setStyleSheet(f"QMenu{{background:{C['sf']};border:1px solid {C['bd']};border-radius:8px;padding:6px}}"
                        f"QMenu::item{{padding:8px 24px;color:{C['tx']};font-size:12px;border-radius:4px}}"
                        f"QMenu::item:selected{{background:{rgba(C['pr'],0.12)}}}")
        for fn in self._lb.FONTS:
            a = m.addAction(fn)
            a.triggered.connect(lambda checked, f=fn: self._set_font(f))
        m.exec_(self._ff_btn.mapToGlobal(QPoint(0, self._ff_btn.height())))

    def _set_font(self, fn):
        self._lb.set_font_family(f'"{fn}"')
        self._ff_btn.setText(fn)

    def set_song(self, s):
        self._sn.setText(s.get("name", "") if s else "")
        self._sa.setText(s.get("singer", "") if s else "")
    def set_full(self, v):
        self._btn_toggle.setText("\u663e" if v else "\u5168")
        self._cover.setVisible(not v)
        self._sn.setVisible(not v)
        self._sa.setVisible(not v)
        self._lb_sm.setVisible(not v)
        self._ff_btn.setVisible(not v)
        self._lb_lg.setVisible(not v)
    def set_cover(self, px): self._cover.set_pix(px)
    def set_lyrics(self, ly): self._lb.set_lyrics(ly)
    def set_current(self, idx): self._lb.set_current(idx)

class HomePage(QWidget):
    play_song = pyqtSignal(dict, list, int); toggle_fav = pyqtSignal(dict); download_song = pyqtSignal(dict)
    open_hot = pyqtSignal(str, str); nav_to = pyqtSignal(int)
    def __init__(self, core, parent=None):
        super().__init__(parent); self.core = core; self._hl = []; self._rs = []
        self.setStyleSheet(f"background:{C['bg']}")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        sc = _sc(); c = QWidget(); c.setStyleSheet("background:transparent")
        cl = QVBoxLayout(c); cl.setContentsMargins(28, 20, 28, 28); cl.setSpacing(18)
        cl.addWidget(Banner())
        cl.addWidget(_hd("\u70ed\u95e8\u699c\u5355"))
        self._hg = RespGrid(cols=4, h=12, v=12); cl.addWidget(self._hg)
        self._he = Empty("hot", "\u6682\u65e0\u70ed\u699c", "\u52a0\u8f7d\u4e2d..."); cl.addWidget(self._he)
        st = QHBoxLayout(); st.setSpacing(10)
        self._sc_fav = StatsCard("\u6536\u85cf", "0", "heart", C["red"]); self._sc_fav.clicked.connect(lambda: self.nav_to.emit(IX["fav"])); st.addWidget(self._sc_fav, 1)
        self._sc_rec = StatsCard("\u6700\u8fd1", "0", "clock", C["blu"]); self._sc_rec.clicked.connect(lambda: self.nav_to.emit(IX["clock"])); st.addWidget(self._sc_rec, 1)
        self._sc_dl = StatsCard("\u4e0b\u8f7d", "0", "download", C["grn"]); self._sc_dl.clicked.connect(lambda: self.nav_to.emit(IX["download"])); st.addWidget(self._sc_dl, 1)
        cl.addLayout(st)
        cl.addWidget(_hd("\u6b63\u5728\u64ad\u653e"))
        self._plw = QVBoxLayout(); self._plw.setContentsMargins(0, 0, 0, 0); self._plw.setSpacing(6)
        cl.addLayout(self._plw)
        self._pe = Empty("play", "\u6682\u65e0\u64ad\u653e", "\u9009\u62e9\u6b4c\u66f2\u5f00\u59cb\u64ad\u653e")
        cl.addWidget(self._pe)
        cl.addStretch(); sc.setWidget(c); root.addWidget(sc, 1)
    def refresh(self):
        self._sc_fav.set_value(len(self.core.favorites))
        self._sc_rec.set_value(len(self.core.recent))
        self._sc_dl.set_value(len(self.core.downloaded_songs))
        _clear_rows(self._rs)
        pl = self.core.current_playlist
        if pl and self.core.current_song:
            self._pe.hide()
            for i, s in enumerate(pl):
                card = SongRow(s, pl, i); card.play.connect(self.play_song.emit)
                card.fav.connect(self.toggle_fav.emit); card.dl.connect(self.download_song.emit)
                card.set_fav(self.core.is_fav(s.get("mid", "")))
                lp = s.get("local_path", ""); card.set_dled(bool(lp and os.path.isfile(lp)))
                self._plw.addWidget(card); self._rs.append(card)
            _lc(pl, self._rs)
            key = song_key(self.core.current_song or {})
            for r in self._rs: r.set_playing(song_key(r.song) == key)
            _fade_in(self._rs)
        else: self._pe.show()
    def set_hot_lists(self, ls):
        self._hl = ls; self._hg.clear()
        for hl in ls[:8]: cd = HotCard(hl); cd.clicked.connect(self.open_hot.emit); self._hg.addWidget(cd)
        self._he.hide() if ls else self._he.show()

class SearchPage(QWidget):
    play_song = pyqtSignal(dict, list, int); toggle_fav = pyqtSignal(dict); download_song = pyqtSignal(dict)
    def __init__(self, core, parent=None):
        super().__init__(parent); self.core = core; self._rs = []; self._lw = None
        self.setStyleSheet(f"background:{C['bg']}")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        self._ct = QLabel(""); self._ct.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:12px;background:transparent")
        root.addWidget(_hd("\u641c\u7d22\u7ed3\u679c", self._ct))
        sc = _sc(); lc = QWidget(); lc.setStyleSheet("background:transparent")
        self._lo = QVBoxLayout(lc); self._lo.setContentsMargins(28, 8, 28, 20); self._lo.setSpacing(6)
        self._em = Empty("search", "\u641c\u7d22\u6b4c\u66f2\u3001\u6b4c\u624b", "\u5728\u9876\u90e8\u641c\u7d22\u6846\u8f93\u5165\u5173\u952e\u8bcd")
        self._lo.addWidget(self._em); sc.setWidget(lc); root.addWidget(sc, 1)

    def clear(self):
        _clear_rows(self._rs)
        if self._lw is not None:
            self._lw.hide(); self._lw.deleteLater(); self._lw = None

    def set_loading(self):
        self.clear(); self._em.hide(); self._ct.setText("\u641c\u7d22\u4e2d...")
        self._lw = Empty("search", "\u6b63\u5728\u641c\u7d22...", "")
        self._lo.addWidget(self._lw)

    def set_error(self, msg: str):
        self.clear(); self._ct.setText("")
        self._lo.addWidget(Empty("search", "\u641c\u7d22\u5931\u8d25", msg))

    def set_results(self, songs):
        self.clear()
        if songs:
            self._em.hide(); self._ct.setText(f"\u5171 {len(songs)} \u9996")
            for i, s in enumerate(songs):
                card = SongRow(s, songs, i); card.play.connect(self.play_song.emit)
                card.fav.connect(self.toggle_fav.emit); card.dl.connect(self.download_song.emit)
                card.set_fav(self.core.is_fav(s.get("mid", "")))
                self._lo.addWidget(card); self._rs.append(card)
            _lc(songs, self._rs)
            key = song_key(self.core.current_song or {})
            for r in self._rs: r.set_playing(song_key(r.song) == key)
        else:
            self._em.show(); self._ct.setText("")

class FavoritesPage(QWidget):
    play_song = pyqtSignal(dict, list, int); toggle_fav = pyqtSignal(dict); download_song = pyqtSignal(dict)
    def __init__(self, core, parent=None):
        super().__init__(parent); self.core = core; self._rs = []
        self.setStyleSheet(f"background:{C['bg']}")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        root.addWidget(_hd("\u6536\u85cf"))
        sc = _sc(); lc = QWidget(); lc.setStyleSheet("background:transparent")
        self._lo = QVBoxLayout(lc); self._lo.setContentsMargins(28, 8, 28, 20); self._lo.setSpacing(6)
        self._em = Empty("heart", "\u6682\u65e0\u6536\u85cf", "\u70b9\u51fb\u6b4c\u66f2\u65c1\u8fb9\u7684\u7231\u5fc3\u6536\u85cf")
        self._lo.addWidget(self._em); self._lo.addStretch(); sc.setWidget(lc); root.addWidget(sc, 1)
    def refresh(self):
        _clear_rows(self._rs)
        favs = self.core.favorites
        if favs:
            self._em.hide()
            for i, s in enumerate(favs):
                card = SongRow(s, favs, i); card.play.connect(self.play_song.emit)
                card.fav.connect(self.toggle_fav.emit); card.dl.connect(self.download_song.emit); card.set_fav(True)
                self._lo.insertWidget(self._lo.count()-1, card); self._rs.append(card)
            _lc(favs, self._rs)
            _fade_in(self._rs)
        else: self._em.show()

class RecentPage(QWidget):
    play_song = pyqtSignal(dict, list, int); toggle_fav = pyqtSignal(dict); download_song = pyqtSignal(dict)
    remove_song = pyqtSignal(dict)
    def __init__(self, core, parent=None):
        super().__init__(parent); self.core = core; self._rs = []
        self.setStyleSheet(f"background:{C['bg']}")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        root.addWidget(_hd("最近播放"))
        sc = _sc(); lc = QWidget(); lc.setStyleSheet("background:transparent")
        self._lo = QVBoxLayout(lc); self._lo.setContentsMargins(28, 8, 28, 20); self._lo.setSpacing(6)
        self._em = Empty("clock", "暂无播放记录", "快去听歌吧")
        self._lo.addWidget(self._em); self._lo.addStretch(); sc.setWidget(lc); root.addWidget(sc, 1)
    def refresh(self):
        _clear_rows(self._rs)
        rec = self.core.recent[:50]
        if rec:
            self._em.hide()
            for i, s in enumerate(rec):
                card = SongRow(s, rec, i, show_remove=True); card.play.connect(self.play_song.emit)
                card.fav.connect(self.toggle_fav.emit); card.dl.connect(self.download_song.emit)
                card.remove.connect(self.remove_song.emit)
                card.set_fav(self.core.is_fav(s.get("mid", "")))
                self._lo.insertWidget(self._lo.count()-1, card); self._rs.append(card)
            _lc(rec, self._rs)
        else: self._em.show()

class DownloadsPage(QWidget):
    play_song = pyqtSignal(dict, list, int); toggle_fav = pyqtSignal(dict)
    download_song = pyqtSignal(dict); delete_song = pyqtSignal(dict); open_folder = pyqtSignal(dict)
    def __init__(self, core, parent=None):
        super().__init__(parent); self.core = core; self._rs = []
        self.setStyleSheet(f"background:{C['bg']}")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        root.addWidget(_hd("\u4e0b\u8f7d\u7ba1\u7406"))
        sc = _sc(); lc = QWidget(); lc.setStyleSheet("background:transparent")
        self._lo = QVBoxLayout(lc); self._lo.setContentsMargins(28, 8, 28, 20); self._lo.setSpacing(6)
        self._em = Empty("download", "\u6682\u65e0\u4e0b\u8f7d")
        self._lo.addWidget(self._em); self._lo.addStretch(); sc.setWidget(lc); root.addWidget(sc, 1)
    def refresh(self):
        _clear_rows(self._rs)
        dl = self.core.downloaded_songs
        if dl:
            self._em.hide()
            for i, s in enumerate(dl):
                card = SongRow(s, dl, i); card.play.connect(self.play_song.emit)
                card.fav.connect(self.toggle_fav.emit); card.dl.connect(self.download_song.emit)
                card.set_fav(self.core.is_fav(s.get("mid", ""))); card.set_dled(True)
                card.delete.connect(self.delete_song.emit); card.open_folder.connect(self.open_folder.emit)
                self._lo.insertWidget(self._lo.count()-1, card); self._rs.append(card)
            _lc(dl, self._rs)
        else: self._em.show()

class HotListPage(QWidget):
    open_hot = pyqtSignal(str, str)
    def __init__(self, core, parent=None):
        super().__init__(parent); self.core = core; self._hl = []
        self.setStyleSheet(f"background:{C['bg']}")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        root.addWidget(_hd("\u70ed\u95e8\u699c\u5355"))
        sc = _sc(); c = QWidget(); c.setStyleSheet("background:transparent")
        self._g = RespGrid(cols=4, h=14, v=14)
        cl = QVBoxLayout(c); cl.setContentsMargins(28, 20, 28, 28); cl.addWidget(self._g)
        self._em = Empty("hot", "\u6682\u65e0\u70ed\u699c", "\u52a0\u8f7d\u4e2d..."); cl.addWidget(self._em)
        sc.setWidget(c); root.addWidget(sc, 1)
    def set_hot_lists(self, ls):
        self._hl = ls; self._g.clear()
        for hl in ls: cd = HotCard(hl); cd.clicked.connect(self.open_hot.emit); self._g.addWidget(cd)
        self._em.hide() if ls else self._em.show()
    def refresh(self): self.core.load_hot_list()

class HotDetailPage(QWidget):
    go_back = pyqtSignal(); play_song = pyqtSignal(dict, list, int)
    toggle_fav = pyqtSignal(dict); download_song = pyqtSignal(dict)
    def __init__(self, core, parent=None):
        super().__init__(parent); self.core = core; self._ss = []; self._ti = ""; self._rs = []
        self.setStyleSheet(f"background:{C['bg']}")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        hd = QWidget(); hd.setFixedHeight(48); hd.setStyleSheet(f"background:transparent;border-bottom:1px solid {C['bd']}")
        hlo = QHBoxLayout(hd); hlo.setContentsMargins(20, 0, 28, 0); hlo.setSpacing(8)
        bk = QPushButton(); bk.setFixedSize(32, 32); bk.setCursor(Qt.PointingHandCursor)
        bk.setIcon(QIcon(render("back", 16, C["tx"])))
        bk.setStyleSheet(_btn_ss(16)); bk.clicked.connect(self.go_back.emit); hlo.addWidget(bk)
        self._ht = QLabel(""); self._ht.setStyleSheet(f"color:{C['tx']};font-family:{FFD};font-size:16px;font-weight:700;background:transparent")
        hlo.addWidget(self._ht); hlo.addStretch()
        self._ct = QLabel(""); self._ct.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:12px;background:transparent"); hlo.addWidget(self._ct)
        root.addWidget(hd)
        sc = _sc(); lc = QWidget(); lc.setStyleSheet("background:transparent")
        self._lo = QVBoxLayout(lc); self._lo.setContentsMargins(28, 8, 28, 20); self._lo.setSpacing(6)
        self._em = Empty("hot", "\u52a0\u8f7d\u4e2d..."); self._lo.addWidget(self._em); self._lo.addStretch()
        sc.setWidget(lc); root.addWidget(sc, 1)
    def set_songs(self, songs, title=""):
        self._ss = songs; self._ti = title; self._ht.setText(title)
        _clear_rows(self._rs)
        if songs:
            self._em.hide(); self._ct.setText(f"\u5171 {len(songs)} \u9996")
            for i, s in enumerate(songs):
                card = SongRow(s, songs, i, si=True); card.play.connect(self.play_song.emit)
                card.fav.connect(self.toggle_fav.emit); card.dl.connect(self.download_song.emit)
                card.set_fav(self.core.is_fav(s.get("mid", "")))
                self._lo.insertWidget(self._lo.count()-1, card); self._rs.append(card)
            _lc(songs, self._rs)
            _fade_in(self._rs)
        else: self._em.show(); self._ct.setText("")

class ImportPage(QWidget):
    import_playlist = pyqtSignal(str)
    open_playlist = pyqtSignal(str, str, list)
    rename_playlist = pyqtSignal(str, str)
    delete_playlist = pyqtSignal(str)
    def __init__(self, core, parent=None):
        super().__init__(parent); self.core = core; self._cards = []
        self.setStyleSheet(f"background:{C['bg']}")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        root.addWidget(_hd("导入歌单"))
        inp = QWidget(); inp.setStyleSheet(f"background:transparent;border-bottom:1px solid {C['bd']}")
        inp.setFixedHeight(44)
        ilo = QHBoxLayout(inp); ilo.setContentsMargins(24, 4, 24, 4); ilo.setSpacing(8)
        self._url = QLineEdit(); self._url.setPlaceholderText("粘贴酷狗、QQ音乐、网易云歌单链接...")
        self._url.setFixedHeight(32)
        self._url.setStyleSheet(f"QLineEdit{{background:{C['sf']};border:1px solid {C['bd']};border-radius:{R['sm']}px;padding:0 10px;color:{C['tx']};font-family:{FF};font-size:11px}}QLineEdit:focus{{border-color:{C['pr']}}}")
        self._url.returnPressed.connect(self._go)
        ilo.addWidget(self._url, 1)
        btn = QPushButton("导入"); btn.setFixedSize(52, 32); btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"QPushButton{{background:{C['pr']};color:white;border:none;border-radius:{R['sm']}px;font-family:{FF};font-size:11px;font-weight:600}}QPushButton:hover{{background:{C['prh']}}}QPushButton:pressed{{background:{C['prp']}}}")
        btn.clicked.connect(self._go); ilo.addWidget(btn)
        root.addWidget(inp)
        sc = _sc(); c = QWidget(); c.setStyleSheet("background:transparent")
        self._lo = QVBoxLayout(c); self._lo.setContentsMargins(28, 16, 28, 28); self._lo.setSpacing(12)
        self._hdr = _hd("我的歌单")
        self._lo.addWidget(self._hdr)
        self._grid = RespGrid(cols=5, h=12, v=12); self._lo.addWidget(self._grid)
        self._em = Empty("import", "暂无导入歌单", "在上方粘贴歌单链接进行导入")
        self._lo.addWidget(self._em)
        self._lo.addStretch()
        sc.setWidget(c); root.addWidget(sc, 1)
    def _go(self):
        u = self._url.text().strip()
        if u: self.import_playlist.emit(u); self._url.clear()
    def refresh(self):
        for cd in self._cards: cd.hide(); cd.deleteLater()
        self._cards.clear(); self._grid.clear()
        pls = self.core.imported_playlists
        if pls:
            self._em.hide(); self._hdr.show()
            for pl in pls:
                cd = PlaylistCard(pl, self._grid)
                pid = pl.get("id", ""); name = pl.get("name", ""); songs = pl.get("songs", [])
                cd.clicked.connect(lambda a=pid, b=name, c=songs: self.open_playlist.emit(a, b, c))
                cd.renamed.connect(self.rename_playlist.emit)
                cd.deleted.connect(self.delete_playlist.emit)
                self._grid.addWidget(cd); self._cards.append(cd)
        else:
            self._em.show()


class DetailPage(QWidget):
    def __init__(self, core, parent=None):
        super().__init__(parent); self.core = core; self._song = {}
        self.setStyleSheet(f"background:{C['bg']}")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        sc = _sc(); c = QWidget(); c.setStyleSheet("background:transparent")
        clo = QVBoxLayout(c); clo.setContentsMargins(40, 32, 40, 32); clo.setSpacing(24)
        top = QHBoxLayout(); top.setSpacing(32)
        self._cv = CoverArt(200, R["lg"])
        top.addWidget(self._cv, 0, Qt.AlignTop)
        inf = QVBoxLayout(); inf.setContentsMargins(0, 0, 0, 0); inf.setSpacing(6)
        self._nm = QLabel("\u672a\u64ad\u653e")
        self._nm.setStyleSheet(f"color:{C['tx']};font-family:{FFD};font-size:24px;font-weight:700;background:transparent")
        inf.addWidget(self._nm)
        self._ar = QLabel("")
        self._ar.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:14px;background:transparent")
        inf.addWidget(self._ar); inf.addSpacing(10)
        self._ly = LyricBox(); inf.addWidget(self._ly, 1)
        top.addLayout(inf, 1); clo.addLayout(top, 1); clo.addStretch()
        sc.setWidget(c); root.addWidget(sc, 1)
    def set_song(self, s): self._song = s or {}; self._nm.setText(self._song.get("name", "")); self._ar.setText(self._song.get("singer", ""))
    def set_cover(self, px): px and not px.isNull() and self._cv.set_pix(px)
    def set_lyrics(self, ly): self._ly.set_lyrics(ly)
    def set_current_lyric(self, idx): self._ly.set_current(idx)

NAV = [("home", "推荐"), ("hot", "排行榜"), ("fav", "我的收藏"),
       ("import", "音乐歌单"), ("clock", "最近播放"), ("download", "下载管理")]
IX = {k: i for i, (k, _) in enumerate(NAV)}
IX["hot_detail"] = 6; IX["detail"] = 7; IX["search"] = 8

class NavBtn(QWidget):
    clicked = pyqtSignal(int)
    _ICON = {"home": "home", "hot": "hot", "fav": "heart",
             "clock": "clock", "download": "download", "import": "import"}
    def __init__(self, key, text, idx, parent=None):
        super().__init__(parent); self._idx = idx; self._act = False; self._hv = False
        self._key = key
        self.setFixedHeight(42); self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_StyledBackground, True)
        lo = QHBoxLayout(self); lo.setContentsMargins(12, 0, 12, 0); lo.setSpacing(10)
        self._ic = QLabel(); self._ic.setFixedSize(18, 18); self._ic.setAlignment(Qt.AlignCenter)
        lo.addWidget(self._ic)
        self._lb = QLabel(text); lo.addWidget(self._lb); lo.addStretch()
        self._ref()

    def _ref(self):
        if self._act:
            self.setStyleSheet(f"NavBtn{{background:{C['prs']};border-radius:10px;border:none}}")
            col = C['pr']
            self._lb.setStyleSheet(f"color:{C['pr']};font-family:{FFD};font-size:13px;font-weight:400;background:transparent;border:none")
        else:
            bg = C['sbh'] if self._hv else "transparent"
            self.setStyleSheet(f"NavBtn{{background:{bg};border-radius:10px;border:none}}")
            col = C['pr'] if self._hv else C['tx2']
            self._lb.setStyleSheet(f"color:{C['tx']};font-family:{FFD};font-size:13px;font-weight:400;background:transparent;border:none")
        self._ic.setPixmap(render(self._ICON.get(self._key, "list"), 18, col))

    def set_active(self, v): self._act = v; self._ref()
    def enterEvent(self, e): self._hv = True; self._ref()
    def leaveEvent(self, e): self._hv = False; self._ref()
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self.clicked.emit(self._idx)

class SideBar(QWidget):
    nav = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent); self.setFixedWidth(S["sb"])
        self._active = -1
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"SideBar{{background:transparent;border-right:1px solid {C['bd']}}}")
        root = QVBoxLayout(self); root.setContentsMargins(12, 16, 12, 16); root.setSpacing(8)
        root.addSpacing(4)
        self._bs = []
        for i, (key, txt) in enumerate(NAV):
            b = NavBtn(key, txt, i); b.clicked.connect(self.nav.emit)
            root.addWidget(b); self._bs.append(b)
        root.addStretch()

    def setActive(self, idx):
        self._active = idx
        for i, b in enumerate(self._bs): b.set_active(i == idx)

class TrafficLight(QWidget):
    clicked = pyqtSignal()
    def __init__(self, color, glyph, parent=None):
        super().__init__(parent); self.setFixedSize(18, 18)
        self._c = color; self.setCursor(Qt.PointingHandCursor)
        self._lb = QLabel(glyph); self._lb.setFixedSize(18, 18); self._lb.setAlignment(Qt.AlignCenter)
        self._lb.setFont(QFont(FF, 11, QFont.Bold))
        self._lb.setStyleSheet("color:rgba(0,0,0,0);background:transparent;border:none")
        lo = QHBoxLayout(self); lo.setContentsMargins(0, 0, 0, 0); lo.addWidget(self._lb)
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(self._c)); p.setPen(Qt.NoPen); p.drawEllipse(1, 1, 16, 16)
    def enterEvent(self, e):
        self._lb.setStyleSheet("color:rgba(0,0,0,0.55);background:transparent;border:none"); super().enterEvent(e)
    def leaveEvent(self, e):
        self._lb.setStyleSheet("color:rgba(0,0,0,0);background:transparent;border:none"); super().leaveEvent(e)
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self.clicked.emit()


class TitleBar(QWidget):
    search = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent); self.setFixedHeight(S["tp"])
        self.setStyleSheet(f"TitleBar{{background:{GP};border-bottom:1px solid rgba(255,255,255,0.55)}}")
        lo = QHBoxLayout(self); lo.setContentsMargins(14, 0, 14, 0); lo.setSpacing(8)
        brand = QWidget(); blo = QHBoxLayout(brand); blo.setContentsMargins(0, 0, 0, 0); blo.setSpacing(8)
        blogo = QLabel(); blogo.setFixedSize(24, 24); blogo.setAlignment(Qt.AlignCenter)
        blogo.setStyleSheet("background:transparent;border-radius:7px")
        _pm = QPixmap(_res("icon.ico"))
        if not _pm.isNull():
            blogo.setPixmap(_pm.scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            blogo.setStyleSheet(f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {C['pr']},stop:1 {C['cy']});border-radius:7px")
            blogo.setPixmap(render("cd", 14, "#FFFFFF"))
        blo.addWidget(blogo)
        bt = QLabel("\u5343\u5343\u52a8\u542c")
        bt.setStyleSheet(f"color:{C['tx']};font-family:{FFD};font-size:14px;font-weight:700;background:transparent;border:none")
        blo.addWidget(bt); lo.addWidget(brand)
        lo.addSpacing(48)
        self._ed = AnimLineEdit(110); self._ed.setFixedHeight(26)
        self._ed.setPlaceholderText("\u641c\u7d22\u6b4c\u66f2\u3001\u6b4c\u624b...")
        self._ed.setStyleSheet(f"QLineEdit{{background:rgba(255,255,255,0.7);border:1px solid {C['bd']};border-radius:13px;color:{C['tx']};font-family:{FF};font-size:11px;padding:0 12px}}"
                               f"QLineEdit:focus{{border:1px solid {C['pr']};background:#FFFFFF}}")
        self._ed.returnPressed.connect(self._go); lo.addWidget(self._ed)
        self._sb = QPushButton("\u641c\u7d22"); self._sb.setFixedHeight(22); self._sb.setCursor(Qt.PointingHandCursor)
        self._sb.setStyleSheet(f"QPushButton{{color:{C['txi']};font-family:{FF};font-size:10px;font-weight:600;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {C['pr']},stop:1 {C['cy']});border:none;border-radius:10px;padding:0 6px}}"
                               f"QPushButton:hover{{background:{C['prh']}}}"
                               f"QPushButton:pressed{{background:{C['prp']}}}")
        self._sb.clicked.connect(self._go); lo.addWidget(self._sb)
        lo.addStretch(1)
        lights = QWidget(); ll = QHBoxLayout(lights); ll.setContentsMargins(0, 0, 0, 0); ll.setSpacing(10)
        lg = TrafficLight("#28C840", "\u2212"); lg.clicked.connect(self._minimize); ll.addWidget(lg)
        lw = TrafficLight("#FF5F57", "\u00d7"); lw.clicked.connect(self._close); ll.addWidget(lw)
        lo.addWidget(lights)
        self._parent = parent

    def _go(self): kw = self._ed.text().strip(); kw and self.search.emit(kw)
    def _minimize(self):
        if self._parent: self._parent.showMinimized()
    def _maximize(self):
        if self._parent:
            if self._parent.isMaximized(): self._parent.showNormal()
            else: self._parent.showMaximized()
    def _close(self):
        if self._parent: self._parent.close()

class HoverButton(QPushButton):
    entered = pyqtSignal(); left = pyqtSignal()
    def enterEvent(self, e):
        self.entered.emit(); super().enterEvent(e)
    def leaveEvent(self, e):
        self.left.emit(); super().leaveEvent(e)


class ModePopup(QWidget):
    entered = pyqtSignal(); left = pyqtSignal()
    _MODES = {"repeat": "列表循环", "repeat_one": "单曲循环", "shuffle": "随机播放"}
    def __init__(self, parent=None):
        super().__init__(parent, Qt.ToolTip)
        self.setFixedHeight(32)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet(f"ModePopup{{background:{C['glass_pl']};border:1px solid {C['glass_pl_border']};border-radius:8px}}")
        lo = QHBoxLayout(self); lo.setContentsMargins(10, 0, 10, 0); lo.setSpacing(6)
        self._ic = QLabel(); lo.addWidget(self._ic)
        self._lb = QLabel()
        self._lb.setStyleSheet(f"color:{C['tx']};font-family:{FF};font-size:12px;font-weight:600;background:transparent;border:none")
        lo.addWidget(self._lb)
    def enterEvent(self, e): self.entered.emit(); super().enterEvent(e)
    def leaveEvent(self, e): self.left.emit(); super().leaveEvent(e)
    def set_mode(self, mode):
        self._lb.setText(self._MODES.get(mode, "列表循环"))
        self._ic.setPixmap(render(mode, 14, C["pr"]))
        self.adjustSize()


class VolumePopup(QWidget):
    volume_changed = pyqtSignal(int)
    entered = pyqtSignal(); left = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup)
        self.setFixedSize(236, 50)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setStyleSheet(f"VolumePopup{{background:{C['glass_pl']};border:1px solid {C['glass_pl_border']};border-radius:12px}}")
        lo = QHBoxLayout(self); lo.setContentsMargins(12, 0, 12, 0); lo.setSpacing(10)
        self._icon = QPushButton(); self._icon.setFixedSize(26, 26)
        self._icon.setCursor(Qt.PointingHandCursor); self._icon.setStyleSheet(_btn_ss(13))
        self._icon.clicked.connect(self._toggle_mute); lo.addWidget(self._icon)
        self._slider = QSlider(Qt.Horizontal); self._slider.setRange(0, 100)
        self._slider.setStyleSheet(f"""
            QSlider::groove:horizontal{{background:rgba(0,0,0,0.08);height:4px;border-radius:2px}}
            QSlider::handle:horizontal{{background:{C['pr']};width:14px;height:14px;margin:-5px 0;border-radius:7px;border:2px solid white}}
            QSlider::sub-page:horizontal{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {C['pr']},stop:1 {C['cy']});border-radius:2px}}
            QSlider::add-page:horizontal{{background:rgba(0,0,0,0.08);border-radius:2px}}
        """)
        self._slider.valueChanged.connect(self._on_val); lo.addWidget(self._slider, 1)
        self._lbl = QLabel("80%"); self._lbl.setFixedWidth(34)
        self._lbl.setAlignment(Qt.AlignCenter)
        self._lbl.setStyleSheet(f"color:{C['tx']};font-family:{FF};font-size:11px;font-weight:600;background:transparent;border:none")
        lo.addWidget(self._lbl)
        self._muted = False; self._last = 80
    def enterEvent(self, e): self.entered.emit(); super().enterEvent(e)
    def leaveEvent(self, e): self.left.emit(); super().leaveEvent(e)
    def set_volume(self, v):
        v = max(0, min(100, v))
        self._slider.blockSignals(True); self._slider.setValue(v); self._slider.blockSignals(False)
        self._lbl.setText(f"{v}%")
        if v > 0: self._last = v
        ic = "volume_mute" if v == 0 else ("volume_low" if v < 40 else "volume_high")
        self._icon.setIcon(QIcon(render(ic, 14, C["pr"])))
    def _toggle_mute(self):
        if self._slider.value() > 0:
            self._slider.setValue(0)
        else:
            self._slider.setValue(self._last or 80)
    def _on_val(self, v):
        self._lbl.setText(f"{v}%")
        if v > 0: self._last = v
        ic = "volume_mute" if v == 0 else ("volume_low" if v < 40 else "volume_high")
        self._icon.setIcon(QIcon(render(ic, 14, C["pr"])))
        self.volume_changed.emit(v)

class PlayCtrl(QWidget):
    tog = pyqtSignal(); nxt = pyqtSignal(); prv = pyqtSignal(); seek = pyqtSignal(int)
    cd_clicked = pyqtSignal(); volume_changed = pyqtSignal(int); mode_changed = pyqtSignal(str)
    fav_clicked = pyqtSignal(); dl_clicked = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent); self.setFixedHeight(74)
        self._play = False; self._mode = "repeat"; self._song = {}; self._dur = 0
        self.setStyleSheet(f"PlayCtrl{{background:{GP};border-top:1px solid rgba(255,255,255,0.55);border-radius:16px}}")

        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        ctrl = QWidget(self); ctrl.setStyleSheet("background:transparent")
        ch = QHBoxLayout(ctrl); ch.setContentsMargins(0, 4, 0, 4); ch.setSpacing(0)
        ch.setAlignment(Qt.AlignVCenter)

        left = QWidget(); left.setStyleSheet("background:transparent")
        left.setFixedWidth(170)
        ll = QHBoxLayout(left); ll.setContentsMargins(16, 0, 8, 0); ll.setSpacing(10)
        self._cd = CDDisc(52); self._cd.setCursor(Qt.PointingHandCursor)
        self._cd.clicked.connect(self.cd_clicked.emit); ll.addWidget(self._cd)
        inf = QVBoxLayout(); inf.setContentsMargins(0, 0, 0, 0); inf.setSpacing(1)
        self._ti = MarqueeLabel("未播放"); self._ti.setMaximumWidth(105)
        self._ti.setStyleSheet(f"color:{C['tx']};font-family:{FF};font-size:12px;font-weight:600;background:transparent;border:none")
        inf.addWidget(self._ti)
        self._ar = MarqueeLabel(""); self._ar.setMaximumWidth(105)
        self._ar.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:11px;background:transparent;border:none")
        self._ar.setTextFormat(Qt.PlainText); self._ar.setTextInteractionFlags(Qt.NoTextInteraction)
        inf.addWidget(self._ar); ll.addLayout(inf)
        ch.addWidget(left)

        mid = QWidget(); mid.setStyleSheet("background:transparent")
        midl = QVBoxLayout(mid); midl.setContentsMargins(0, 0, 0, 0); midl.setSpacing(3)
        midl.setAlignment(Qt.AlignVCenter)

        ctr = QHBoxLayout(); ctr.setContentsMargins(0, 0, 0, 0); ctr.setSpacing(10)
        ctr.addStretch()
        self._mb = HoverButton(); self._mb.setFixedSize(32, 32); self._mb.setCursor(Qt.PointingHandCursor)
        self._mb.setIcon(QIcon(render("repeat", 16, C["tx"]))); self._mb.setStyleSheet(_btn_ss(16))
        self._mb.clicked.connect(self._tm); ctr.addWidget(self._mb)
        self._pb = QPushButton(); self._pb.setFixedSize(36, 36); self._pb.setCursor(Qt.PointingHandCursor)
        self._pb.setIcon(QIcon(render("prev", 18, C["tx"]))); self._pb.setIconSize(QSize(18, 18)); self._pb.setStyleSheet(_btn_ss(16))
        self._pb.clicked.connect(self.prv.emit); ctr.addWidget(self._pb)
        self._pp = QPushButton(); self._pp.setFixedSize(30, 30); self._pp.setCursor(Qt.PointingHandCursor)
        self._pp.setIcon(QIcon(render("play", 15, C["txi"]))); self._pp.setIconSize(QSize(15, 15))
        self._pp.setStyleSheet(f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {C['pr']},stop:1 {C['cy']});border:none;border-radius:15px}}"
                               f"QPushButton:hover{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {C['prh']},stop:1 {C['cy']})}}"
                               f"QPushButton:pressed{{background:{C['prp']}}}")
        self._pp.clicked.connect(self.tog.emit)
        self._pp.setContextMenuPolicy(Qt.CustomContextMenu)
        self._pp.customContextMenuRequested.connect(lambda: self._tm())
        ctr.addWidget(self._pp)
        self._nb = QPushButton(); self._nb.setFixedSize(36, 36); self._nb.setCursor(Qt.PointingHandCursor)
        self._nb.setIcon(QIcon(render("next", 18, C["tx"]))); self._nb.setIconSize(QSize(18, 18)); self._nb.setStyleSheet(_btn_ss(16))
        self._nb.clicked.connect(self.nxt.emit); ctr.addWidget(self._nb)
        self._vb = HoverButton(); self._vb.setFixedSize(32, 32); self._vb.setCursor(Qt.PointingHandCursor)
        self._vb.setIcon(QIcon(render("volume", 15, C["tx"]))); self._vb.setStyleSheet(_btn_ss(16))
        self._vb.clicked.connect(self._show_vol); ctr.addWidget(self._vb)
        ctr.addStretch()
        midl.addLayout(ctr)

        bar_box = QWidget(); bar_box.setStyleSheet("background:transparent")
        bar_box.setFixedHeight(20); self._bar_box = bar_box
        bbl = QVBoxLayout(bar_box); bbl.setContentsMargins(0, 0, 0, 0); bbl.setSpacing(0)
        bar_inner = QWidget(); bar_inner.setStyleSheet("background:transparent")
        bil = QVBoxLayout(bar_inner); bil.setContentsMargins(10, 3, 10, 5)
        bil.setSpacing(0); bil.setAlignment(Qt.AlignVCenter)
        bar_row = QHBoxLayout(); bar_row.setContentsMargins(0, 0, 0, 0); bar_row.setSpacing(10)
        self._tm_label = QLabel("00:00")
        self._tm_label.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:10px;background:transparent;border:none")
        self._tm_label.setFixedWidth(40); self._tm_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bar_row.addWidget(self._tm_label)
        self._bar = SeekBar(); self._bar.setRange(0, 0)
        self._bar.sliderMoved.connect(lambda v: self.seek.emit(v))
        bar_row.addWidget(self._bar, 1)
        self._tm_total = QLabel("00:00")
        self._tm_total.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:10px;background:transparent;border:none")
        self._tm_total.setFixedWidth(40); self._tm_total.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        bar_row.addWidget(self._tm_total)
        bil.addLayout(bar_row)
        bbl.addWidget(bar_inner)
        midl.addWidget(bar_box)

        self._viz = AudioVis(self)
        self._viz.lower()
        self._viz.setVisible(False)

        ch.addWidget(mid, 1)

        right = QWidget(); right.setStyleSheet("background:transparent")
        right.setFixedWidth(160)
        rl = QHBoxLayout(right); rl.setContentsMargins(8, 0, 16, 0); rl.setSpacing(4)
        rl.addStretch()
        self._fav = QPushButton(); self._fav.setFixedSize(28, 28); self._fav.setCursor(Qt.PointingHandCursor)
        self._fav.setIcon(QIcon(render("heart", 13, C["tx3"]))); self._fav.setStyleSheet(_btn_ss(14))
        self._fav.clicked.connect(self._on_fav); rl.addWidget(self._fav)
        self._dl = QPushButton(); self._dl.setFixedSize(26, 26); self._dl.setCursor(Qt.PointingHandCursor)
        self._dl.setIcon(QIcon(render("download", 13, C["tx3"]))); self._dl.setStyleSheet(_btn_ss(14))
        self._dl.clicked.connect(self._on_dl); rl.addWidget(self._dl)
        ch.addWidget(right)

        root.addWidget(ctrl, 1)

        self._vol_pop = VolumePopup(self)
        self._vol_pop.volume_changed.connect(self.volume_changed.emit)
        self._mode_pop = ModePopup(self)

        self._vol_hide = QTimer(self); self._vol_hide.setSingleShot(True)
        self._vol_hide.timeout.connect(self._vol_pop.hide)
        self._mode_hide = QTimer(self); self._mode_hide.setSingleShot(True)
        self._mode_hide.timeout.connect(self._mode_pop.hide)
        self._vb.entered.connect(self._show_vol)
        self._vb.left.connect(self._schedule_hide_vol)
        self._vol_pop.entered.connect(self._vol_hide.stop)
        self._vol_pop.left.connect(self._schedule_hide_vol)
        self._mb.entered.connect(self._show_mode)
        self._mb.left.connect(self._schedule_hide_mode)
        self._mode_pop.entered.connect(self._mode_hide.stop)
        self._mode_pop.left.connect(self._schedule_hide_mode)

    def _show_vol(self):
        self._vol_pop.set_volume(self._vol_pop._slider.value())
        r = self._vb.mapToGlobal(QPoint(0, 0))
        x = r.x() + self._vb.width() // 2 - self._vol_pop.width() // 2
        y = r.y() - self._vol_pop.height() - 8
        self._vol_pop.move(max(4, x), max(4, y)); self._vol_pop.show(); self._vol_hide.stop()
    def _schedule_hide_vol(self):
        self._vol_hide.start(180)
    def _show_mode(self):
        self._mode_pop.set_mode(self._mode)
        r = self._mb.mapToGlobal(QPoint(0, 0))
        x = r.x() + self._mb.width() // 2 - self._mode_pop.width() // 2
        y = r.y() - self._mode_pop.height() - 8
        self._mode_pop.move(max(4, x), max(4, y)); self._mode_pop.show(); self._mode_hide.stop()
    def _schedule_hide_mode(self):
        self._mode_hide.start(180)

    def set_playing(self, v):
        self._play = v
        self._pp.setIcon(QIcon(render("pause" if v else "play", 15, C["txi"])))
        self._cd.set_spin(v); self._viz.set_active(v); self._viz.setVisible(v)
    def set_song(self, s):
        self._song = s or {}
        self._ti.setText(self._song.get("name", "")); self._ar.setText(self._song.get("singer", ""))
        self.set_fav_state(False)
    def feed_levels(self, levels):
        self._viz.feed(levels)
    def set_fav_state(self, v):
        ic, cl = ("heart_filled", C["red"]) if v else ("heart", C["tx3"])
        self._fav.setIcon(QIcon(render(ic, 13, cl)))
    def _on_fav(self): self.fav_clicked.emit()
    def _on_dl(self): self.dl_clicked.emit()
    def set_cover(self, px): px and not px.isNull() and self._cd.set_pix(px)
    def set_duration(self, v):
        self._dur = v; self._bar.setRange(0, v); self._tm_total.setText(fmt(v))
    def set_position(self, v):
        if not self._bar.isSliderDown(): self._bar.setValue(v)
        self._tm_label.setText(fmt(v))
    def set_volume(self, v): self._vol_pop.set_volume(v)
    def _tm(self):
        m = ["repeat", "repeat_one", "shuffle"]; i = m.index(self._mode) if self._mode in m else 0
        self._mode = m[(i+1)%3]
        self._mb.setIcon(QIcon(render(self._mode, 16, C["tx"])))
        self._mode_pop.set_mode(self._mode)
        self.mode_changed.emit(self._mode)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        QTimer.singleShot(0, self._place_viz)

    def _place_viz(self):
        if hasattr(self, "_viz") and hasattr(self, "_bar"):
            bar_pos = self._bar.mapTo(self, QPoint(0, 0))
            x = bar_pos.x()
            y_top = 0
            self._viz.setGeometry(x, y_top, self._bar.width(), bar_pos.y() - y_top + 2)

class MainWindow(QWidget):
    def __init__(self, player, parent=None):
        super().__init__(parent); self.core = player; self.player = player
        self.setWindowTitle("\u5343\u5343\u52a8\u542c"); self.setMinimumSize(760, 540)
        self.resize(880, 620)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._lyr_mode = False; self._full = False
        self._drag_pos = None; self._back_target = 0
        self._tray = None; self._tray_hinted = False
        self._ui(); self._bind(); QTimer.singleShot(200, self._init)
        self._apply_mask()

    def _ui(self):
        self.setStyleSheet(f"background:{C['bg']}")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        self._tp = TitleBar(self); root.addWidget(self._tp)
        mid = QHBoxLayout(); mid.setContentsMargins(0, 0, 0, 0); mid.setSpacing(0)
        self._sb = SideBar(); mid.addWidget(self._sb)
        self._st = QStackedWidget(); self._st.setStyleSheet("QStackedWidget{background:transparent;border:none}")
        mid.addWidget(self._st, 1); root.addLayout(mid, 1)
        self._pl = PlayCtrl(); self._pl.cd_clicked.connect(self._toggle_lyrics)
        root.addWidget(self._pl)
        self._hp = HomePage(self.core); self._st.addWidget(self._hp)
        self._htl = HotListPage(self.core); self._st.addWidget(self._htl)
        self._page_factories = {
            2: ("_fp", FavoritesPage), 3: ("_ip", ImportPage),
            4: ("_rp", RecentPage), 5: ("_dp", DownloadsPage),
            6: ("_hdt", HotDetailPage), 7: ("_det", DetailPage),
            8: ("_sp", SearchPage),
        }
        self._pages = {0: self._hp, 1: self._htl}
        self._st.setCurrentIndex(0); self._sb.setActive(0)
        self._lyr = LyricOverlay(self)
        self._lyr.hide()

    def _toggle_lyrics(self):
        if self._lyr_mode or self._full:
            self._exit_full_lyric()
            return
        self._lyr_mode = True
        self._full = False
        self._sb.hide(); self._st.hide()
        tp_h = self._tp.height(); pl_h = self._pl.height()
        self._lyr.setGeometry(0, tp_h, self.width(), self.height() - tp_h - pl_h)
        self._lyr.show(); self._lyr.raise_()
        self._lyr._lb.set_current(self._lyr._lb._ci)
        self._lyr.set_full(False)

    def _enter_full_lyric(self):
        if self._full:
            return
        self._full = True
        self._lyr_mode = True
        self._sb.hide(); self._st.hide()
        tp_h = self._tp.height(); pl_h = self._pl.height()
        self._lyr.setGeometry(0, tp_h, self.width(), self.height() - tp_h - pl_h)
        self._lyr.show(); self._lyr.raise_()
        self._lyr._lb.set_current(self._lyr._lb._ci)
        self._lyr.set_full(True)

    def _exit_full_lyric(self):
        was = self._lyr_mode or self._full
        self._full = False
        self._lyr_mode = False
        self._sb.show(); self._st.show()
        self._lyr.hide()
        self._lyr.set_full(False)
        if was and self.width() < 560:
            self._sb.hide()

    def _toggle_full_lyric(self):
        if self._full:
            self._full = False
            self._lyr.set_full(False)
        else:
            self._full = True
            self._lyr.set_full(True)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._lyr_mode or self._full:
            tp_h = self._tp.height(); pl_h = self._pl.height()
            self._lyr.setGeometry(0, tp_h, self.width(), self.height() - tp_h - pl_h)
        w = self.width()
        if not self._full and not self._lyr_mode:
            if w < 560:
                self._sb.hide()
            else:
                self._sb.show()
        QTimer.singleShot(30, self._apply_mask)

    def _apply_mask(self):
        rect = self.rect()
        r = 16
        if self.isMaximized() or self.isFullScreen():
            self.setMask(QRegion(rect))
        else:
            path = QPainterPath()
            path.addRoundedRect(QRectF(rect), r, r)
            self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0.0, QColor("#EAF1FF"))
        g.setColorAt(0.45, QColor("#F1ECFF"))
        g.setColorAt(1.0, QColor("#FFEFF7"))
        p.fillRect(self.rect(), g)
        hl = QLinearGradient(0, 0, 0, 130)
        hl.setColorAt(0.0, QColor(255, 255, 255, 95))
        hl.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.fillRect(self.rect().adjusted(0, 0, 0, 130), hl)

    def _init(self):
        self._pl.set_volume(self.core.volume)
        self.core.hotListReady.connect(lambda ls: [self._hp.set_hot_lists(ls), self._htl.set_hot_lists(ls)])
        self.core.load_hot_list()
        self.core.songChanged.connect(self._on_song)
        self.core.playStateChanged.connect(self._on_play)
        self.core.positionChanged.connect(self._on_pos)
        self.core.durationChanged.connect(self._on_dur)
        self.core.coverReady.connect(self._on_cover)
        self.core.lyricsLoaded.connect(self._on_lyrics)
        self.core.lyricIndexChanged.connect(self._on_lyric_idx)
        self.core.searchFinished.connect(lambda s: [self._st.setCurrentIndex(self._st.indexOf(self._sp)), self._sb.setActive(-1), self._sp.set_results(s)])
        self.core.searchError.connect(lambda m: [self._st.setCurrentIndex(self._st.indexOf(self._sp)), self._sb.setActive(-1), self._sp.set_error(m)])
        self.core.needRefreshFavorites.connect(lambda: [self._pages.get(IX['fav']) and self._fp.refresh(), self._hp.refresh()])
        self.core.needRefreshRecent.connect(lambda: [self._pages.get(IX['clock']) and self._rp.refresh(), self._hp.refresh()])
        self.core.needRefreshDownloads.connect(lambda: [self._pages.get(IX['download']) and self._dp.refresh(), self._hp.refresh()])
        self.core.favChanged.connect(self._on_fav_changed)
        self.core.audioLevels.connect(self._pl.feed_levels)
        self.core.hotDetailReady.connect(self._on_hot_detail)
        self.core.errorMsg.connect(self._on_error)
        self.core.playlistImported.connect(self._on_playlist_imported)
        self.core.playlistsChanged.connect(self._on_playlists_changed)
        self.core.downloadProgress.connect(self._on_dl_progress)
        self.core.downloadFinished.connect(self._on_dl_finished)
        self._setup_tray()
        QTimer.singleShot(300, self._preload_pages)

    def _preload_pages(self):
        for idx in range(2, 6):
            p = self._ensure_page(idx)
            if hasattr(p, 'refresh'): p.refresh()

    def _on_error(self, msg):
        if msg:
            self._toast(msg, ok=False)

    def _toast(self, msg, ok=True, duration=2500):
        if not hasattr(self, '_toast_lbl') or self._toast_lbl is None:
            self._toast_lbl = QLabel(self)
            self._toast_lbl.setAlignment(Qt.AlignCenter)
            self._toast_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self._toast_timer = QTimer(self)
            self._toast_timer.setSingleShot(True)
            self._toast_timer.timeout.connect(self._toast_lbl.hide)
        bg = rgba(C['grn'], 0.92) if ok else rgba(C['red'], 0.92)
        self._toast_lbl.setStyleSheet(
            f"QLabel{{background:{bg};color:white;border-radius:8px;"
            f"padding:8px 20px;font-family:{FF};font-size:12px;font-weight:600}}")
        self._toast_lbl.setText(msg)
        self._toast_lbl.adjustSize()
        w = self._toast_lbl.width() + 40
        h = self._toast_lbl.height() + 16
        self._toast_lbl.setGeometry((self.width() - w) // 2, 16, w, h)
        self._toast_lbl.raise_(); self._toast_lbl.show()
        self._toast_timer.start(duration)

    def _find_rows(self, name):
        for p in self._pages.values():
            if hasattr(p, '_rs'):
                for r in p._rs:
                    if r.song.get("name", "") == name:
                        yield r

    def _on_dl_progress(self, name, got, total):
        pct = int(got * 100 / total) if total > 0 else 0
        for r in self._find_rows(name):
            r.set_dl_progress(pct)

    def _on_dl_finished(self, name, ok, path):
        for r in self._find_rows(name):
            r.set_dl_done()
            if ok:
                r.set_dled(True)
        if ok:
            QMessageBox.information(self, "下载完成", f"「{name}」已下载完成")
        else:
            QMessageBox.warning(self, "下载失败", f"「{name}」下载失败")

    def _bind(self):
        self._sb.nav.connect(self._nav); self._tp.search.connect(self._srch)
        self._hp.nav_to.connect(self._nav)
        self._lyr.req_toggle.connect(self._toggle_full_lyric)
        self._lyr.seekRequested.connect(self.player.seek)
        self._pl.tog.connect(lambda: self.player.toggle())
        self._pl.nxt.connect(lambda: self.player.next())
        self._pl.prv.connect(lambda: self.player.prev())
        self._pl.seek.connect(self.player.seek)
        self._pl.volume_changed.connect(self.player.set_volume)
        self._pl.mode_changed.connect(self.player.set_play_mode)
        self._pl.fav_clicked.connect(self._pl_fav)
        self._pl.dl_clicked.connect(self._pl_dl)
        for p in [self._hp]:
            p.play_song.connect(self._play)
            p.toggle_fav.connect(lambda s: self.core.toggle_fav(s))
            p.download_song.connect(self._dl)
            if hasattr(p, 'delete_song'):
                p.delete_song.connect(self._del)
                p.open_folder.connect(self._of)
        self._hp.open_hot.connect(self._oh)
        self._htl.open_hot.connect(self._oh)

    def _ensure_page(self, idx):
        p = self._pages.get(idx)
        if p is not None:
            return p
        f = self._page_factories.get(idx)
        if not f:
            return None
        attr, cls = f
        p = cls(self.core)
        setattr(self, attr, p)
        self._st.insertWidget(idx, p)
        self._pages[idx] = p
        self._wire_page(p)
        self._refresh_play_indicators()
        return p

    def _wire_page(self, p):
        if hasattr(p, 'play_song'):
            p.play_song.connect(self._play)
        if hasattr(p, 'toggle_fav'):
            p.toggle_fav.connect(lambda s: self.core.toggle_fav(s))
        if hasattr(p, 'download_song'):
            p.download_song.connect(self._dl)
        if hasattr(p, 'delete_song'):
            p.delete_song.connect(self._del); p.open_folder.connect(self._of)
        if hasattr(p, 'remove_song'):
            p.remove_song.connect(lambda s: self.core.remove_from_recent(s))
        if isinstance(p, HomePage):
            p.nav_to.connect(self._nav); p.open_hot.connect(self._oh)
        if isinstance(p, HotListPage):
            p.open_hot.connect(self._oh)
        if isinstance(p, HotDetailPage):
            p.go_back.connect(self._bk)
        if isinstance(p, ImportPage):
            p.import_playlist.connect(self._imp)
            p.open_playlist.connect(self._open_playlist)
            p.rename_playlist.connect(self.core.rename_playlist)
            p.delete_playlist.connect(self._del_playlist)

    def _nav(self, idx):
        if self._lyr_mode: self._toggle_lyrics()
        p = self._ensure_page(idx)
        self._st.setCurrentIndex(idx); self._sb.setActive(idx)
        if p is not None and hasattr(p, 'refresh'): p.refresh()
        self._refresh_play_indicators()
    def _srch(self, kw):
        if self._full: self._exit_full_lyric()
        elif self._lyr_mode: self._toggle_lyrics()
        sp = self._ensure_page(IX["search"])
        self._st.setCurrentIndex(self._st.indexOf(sp))
        self._sb.setActive(-1)
        sp.set_loading()
        self.core.search(kw)
    def _oh(self, hid, title):
        self.core.load_hot_detail(hid, title)
        if self._full: self._exit_full_lyric()
        elif self._lyr_mode: self._toggle_lyrics()
        self._back_target = IX["hot"]
        hdt = self._ensure_page(IX["hot_detail"])
        self._st.setCurrentIndex(self._st.indexOf(hdt)); self._sb.setActive(-1)
    def _bk(self):
        if self._full: self._exit_full_lyric()
        elif self._lyr_mode: self._toggle_lyrics()
        self._nav(getattr(self, '_back_target', 0))
    def _play(self, song, songs, idx): self.core.play_song(song, songs, idx)

    def _on_hot_detail(self, songs, title=""):
        hdt = self._ensure_page(IX["hot_detail"])
        hdt.set_songs(songs, title)
        self._refresh_play_indicators()

    def _on_playlist_imported(self, pl):
        n = len(pl.get("songs", []))
        ip = getattr(self, "_ip", None)
        if ip is not None: ip.refresh()
        if n > 0:
            self._toast(f"已导入「{pl.get('name','')}」{n} 首", ok=True)
        else:
            self._toast("歌单为空或解析失败", ok=False)

    def _on_playlists_changed(self):
        ip = getattr(self, "_ip", None)
        if ip is not None: ip.refresh()

    def _open_playlist(self, pid, name, songs):
        if self._full: self._exit_full_lyric()
        elif self._lyr_mode: self._toggle_lyrics()
        self._back_target = IX["import"]
        hdt = self._ensure_page(IX["hot_detail"])
        hdt.set_songs(songs, name)
        self._st.setCurrentIndex(self._st.indexOf(hdt)); self._sb.setActive(-1)
        self._refresh_play_indicators()

    def _del_playlist(self, pid):
        r = QMessageBox.question(self, "删除歌单", "确认删除该歌单？",
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r == QMessageBox.Yes:
            self.core.delete_playlist(pid)

    def _on_fav_changed(self, mid, is_fav):
        for name in ("_hp", "_sp", "_fp", "_rp", "_dp", "_hdt"):
            page = getattr(self, name, None)
            if page is None:
                continue
            for row in getattr(page, '_rs', []):
                if row.song.get("mid") == mid:
                    row.set_fav(is_fav)
        cs = self.core.current_song or {}
        if cs.get("mid") == mid:
            self._pl.set_fav_state(is_fav)

    def _on_song(self, s):
        self._pl.set_song(s); self._lyr.set_song(s)
        self._pl.set_fav_state(bool(s) and self.core.is_fav(s.get("mid", "")))
        self._hp.refresh()
        QTimer.singleShot(60, self._refresh_play_indicators)
    def _on_play(self, v):
        self._pl.set_playing(v)
        self._refresh_play_indicators()
    def _refresh_play_indicators(self):
        key = song_key(self.core.current_song or {})
        for name in ("_hp", "_sp", "_fp", "_rp", "_dp", "_hdt"):
            page = getattr(self, name, None)
            if page is None: continue
            for r in getattr(page, "_rs", []):
                r.set_playing(song_key(r.song) == key)
    def _on_pos(self, pos): self._pl.set_position(pos)
    def _on_dur(self, dur): self._pl.set_duration(dur)
    def _on_cover(self, px):
        self._pl.set_cover(px); self._lyr.set_cover(px)
        det = getattr(self, "_det", None)
        if det is not None: det.set_cover(px)
    def _on_lyrics(self, ly):
        if isinstance(ly, list):
            cl = []
            for l in ly:
                if isinstance(l, tuple): cl.append({"time": l[0], "line": l[1]})
                else: cl.append(l)
            self._lyr.set_lyrics(cl)
            det = getattr(self, "_det", None)
            if det is not None: det.set_lyrics(cl)
    def _on_lyric_idx(self, idx):
        self._lyr.set_current(idx)
        det = getattr(self, "_det", None)
        if det is not None: det.set_current_lyric(idx)
    def _dl(self, song):
        if not song: return
        dlg = QDialog(self)
        dlg.setWindowTitle("下载歌曲")
        dlg.setFixedSize(360, 230)
        dlg.setStyleSheet(f"QDialog{{background:{C['bg2']};border-radius:12px}}")
        dl = QVBoxLayout(dlg); dl.setContentsMargins(24, 20, 24, 16); dl.setSpacing(10)
        for label, val in [("歌曲", song.get("name", "")), ("歌手", song.get("singer", ""))]:
            row = QHBoxLayout(); row.setSpacing(8)
            lb = QLabel(label + ":"); lb.setFixedWidth(40)
            lb.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:12px;background:transparent;border:none")
            vl = ElideLabel(val); vl.setStyleSheet(f"color:{C['tx']};font-family:{FF};font-size:12px;font-weight:600;background:transparent;border:none")
            row.addWidget(lb); row.addWidget(vl, 1); dl.addLayout(row)
        fmt_row = QHBoxLayout(); fmt_row.setSpacing(8)
        fmt_lb = QLabel("格式:"); fmt_lb.setFixedWidth(40)
        fmt_lb.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:12px;background:transparent;border:none")
        from PyQt5.QtWidgets import QComboBox
        fmt_cb = QComboBox(); fmt_cb.addItems(["MP3", "FLAC"]); fmt_cb.setFixedHeight(30)
        fmt_cb.setStyleSheet(f"QComboBox{{background:{C['sf']};border:1px solid {C['bd']};border-radius:6px;padding:0 8px;color:{C['tx']};font-family:{FF};font-size:12px}}QComboBox::drop-down{{border:none;width:20px}}QComboBox QAbstractItemView{{background:{C['sf']};color:{C['tx']};selection-background-color:{C['prs']};border:1px solid {C['bd']}}}")
        fmt_row.addWidget(fmt_lb); fmt_row.addWidget(fmt_cb, 1); dl.addLayout(fmt_row)
        dir_row = QHBoxLayout(); dir_row.setSpacing(8)
        dir_lb = QLabel("位置:"); dir_lb.setFixedWidth(40)
        dir_lb.setStyleSheet(f"color:{C['tx2']};font-family:{FF};font-size:12px;background:transparent;border:none")
        last_dir = config.load_settings().get("download_dir", "") or config.get_download_dir()
        dir_le = QLineEdit(last_dir); dir_le.setFixedHeight(30)
        dir_le.setStyleSheet(f"QLineEdit{{background:{C['sf']};border:1px solid {C['bd']};border-radius:6px;padding:0 8px;color:{C['tx']};font-family:{FF};font-size:11px}}")
        browse = QPushButton("..."); browse.setFixedSize(30, 30); browse.setCursor(Qt.PointingHandCursor)
        browse.setStyleSheet(f"QPushButton{{background:{C['sf']};border:1px solid {C['bd']};border-radius:6px;color:{C['tx']};font-family:{FF};font-size:12px}}QPushButton:hover{{background:{C['sfh']}}}")
        browse.clicked.connect(lambda: (lambda d: d and dir_le.setText(d))(QFileDialog.getExistingDirectory(dlg, "选择目录", dir_le.text())))
        dir_row.addWidget(dir_lb); dir_row.addWidget(dir_le, 1); dir_row.addWidget(browse); dl.addLayout(dir_row)
        dl.addStretch()
        bl = QHBoxLayout(); bl.setSpacing(8); bl.addStretch()
        ok = QPushButton("下载"); ok.setFixedSize(72, 32); ok.setCursor(Qt.PointingHandCursor)
        ok.setStyleSheet(f"QPushButton{{background:{C['pr']};color:white;border:none;border-radius:6px;font-family:{FF};font-size:12px;font-weight:600}}QPushButton:hover{{background:{C['prh']}}}")
        cancel = QPushButton("取消"); cancel.setFixedSize(72, 32); cancel.setCursor(Qt.PointingHandCursor)
        cancel.setStyleSheet(f"QPushButton{{background:{C['sf']};color:{C['tx']};border:1px solid {C['bd']};border-radius:6px;font-family:{FF};font-size:12px}}QPushButton:hover{{background:{C['sfh']}}}")
        ok.clicked.connect(dlg.accept); cancel.clicked.connect(dlg.reject)
        bl.addWidget(cancel); bl.addWidget(ok); dl.addLayout(bl)
        if dlg.exec_() == QDialog.Accepted:
            d = dir_le.text().strip()
            if d:
                s = config.load_settings(); s["download_dir"] = d; config.save_settings(s)
                fmt = "flac" if fmt_cb.currentText() == "FLAC" else "mp3"
                self.core.download_song(song, d, fmt=fmt)
    def _pl_fav(self):
        s = self.core.current_song
        if s: self.core.toggle_fav(s)
    def _pl_dl(self):
        s = self.core.current_song
        if s: self._dl(s)
    def _del(self, song):
        lp = song.get("local_path", "")
        if lp and os.path.isfile(lp):
            try: os.remove(lp)
            except Exception: pass
        self.core.downloaded_songs = [s for s in self.core.downloaded_songs if s.get("local_path") != lp]
        config.save_downloads(self.core.downloaded_songs)
        dp = getattr(self, "_dp", None)
        if dp is not None: dp.refresh()
    def _of(self, song):
        lp = song.get("local_path", "")
        if lp:
            d = os.path.dirname(lp)
            if os.path.isdir(d): os.startfile(d)
    def _imp(self, url): self.core.import_playlist(url)
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and e.pos().y() < 40:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()
            e.accept()
    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() & Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)
            e.accept()
    def mouseReleaseEvent(self, e): self._drag_pos = None
    def mouseDoubleClickEvent(self, e):
        if e.pos().y() < 40:
            if self.isMaximized(): self.showNormal()
            else: self.showMaximized()
    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self._tray = None
            return
        self._tray = QSystemTrayIcon(self)
        ip = _res("icon.ico")
        if os.path.exists(ip):
            self._tray.setIcon(QIcon(ip))
        elif not self.windowIcon().isNull():
            self._tray.setIcon(self.windowIcon())
        ver = QApplication.applicationVersion() or "1.0.3"
        self._tray.setToolTip(f"\u5343\u5343\u52a8\u542c v{ver}")
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {C['bg2']};
                border: 1px solid {C['bd']};
                border-radius: 6px;
                padding: 4px 2px;
            }}
            QMenu::item {{
                color: {C['tx']};
                font-family: {FF};
                font-size: 12px;
                padding: 5px 22px 5px 16px;
                margin: 1px 3px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background: {C['prs']};
                color: {C['pr']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {C['bd']};
                margin: 3px 10px;
            }}
        """)
        menu.addAction("\u663e\u793a\u4e3b\u754c\u9762").triggered.connect(self._show_from_tray)
        menu.addAction(f"\u7248\u672c\u4fe1\u606f v{ver}").triggered.connect(
            lambda: QMessageBox.information(self, "\u5173\u4e8e \u5343\u5343\u52a8\u542c", f"\u5343\u5343\u52a8\u542c\n\u7248\u672c v{ver}"))
        menu.addAction("\u68c0\u67e5\u66f4\u65b0").triggered.connect(
            lambda: self._check_update())
        menu.addSeparator()
        menu.addAction("\u9000\u51fa").triggered.connect(self._quit_app)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._tray_activated)
        self._tray.show()

    def _check_update(self):
        try:
            import updater
            updater.check_and_show(self, auto=False)
        except Exception as e:
            QMessageBox.information(self, "\u68c0\u67e5\u66f4\u65b0", f"\u68c0\u67e5\u5931\u8d25\uff1a{e}")

    def _tray_activated(self, reason):
        if reason in (QSystemTrayIcon.DoubleClick, QSystemTrayIcon.Trigger):
            self._show_from_tray()

    def _show_from_tray(self):
        self.showNormal(); self.activateWindow(); self.raise_()

    def _quit_app(self):
        if self._tray: self._tray.hide()
        self.core.shutdown()
        QApplication.quit()

    def closeEvent(self, e):
        if getattr(self, "_tray", None) and self._tray.isVisible():
            e.ignore(); self.hide()
            if not self._tray_hinted:
                self._tray.showMessage("\u5343\u5343\u52a8\u542c",
                                       "\u5df2\u6700\u5c0f\u5316\u5230\u7cfb\u7edf\u6258\u76d8\uff0c\u53cc\u51fb\u56fe\u6807\u6062\u590d\u4e3b\u754c\u9762",
                                       QSystemTrayIcon.Information, 2500)
                self._tray_hinted = True
        else:
            self.core.shutdown(); super().closeEvent(e)
