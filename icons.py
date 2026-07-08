"""千千动听 - 矢量图标库"""
from __future__ import annotations
import math
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QIcon, QPolygonF, QPainterPath, QFont


def _stroke(p, w):
    pen = p.pen()
    pen.setWidthF(w)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)


def _fill(p):
    c = p.pen().color()
    p.setPen(Qt.NoPen)
    p.setBrush(c)


def _home(p, s):
    _stroke(p, s * 0.085)
    path = QPainterPath()
    path.moveTo(s * 0.18, s * 0.54)
    path.lineTo(s * 0.5, s * 0.22)
    path.lineTo(s * 0.82, s * 0.54)
    p.drawPath(path)
    p.drawLine(QPointF(s * 0.29, s * 0.49), QPointF(s * 0.29, s * 0.82))
    p.drawLine(QPointF(s * 0.71, s * 0.49), QPointF(s * 0.71, s * 0.82))
    p.drawLine(QPointF(s * 0.29, s * 0.82), QPointF(s * 0.71, s * 0.82))
    p2 = QPainterPath()
    p2.moveTo(s * 0.42, s * 0.82)
    p2.lineTo(s * 0.42, s * 0.62)
    p2.lineTo(s * 0.58, s * 0.62)
    p2.lineTo(s * 0.58, s * 0.82)
    p.drawPath(p2)


def _hot(p, s):
    _stroke(p, s * 0.07)
    path = QPainterPath()
    path.moveTo(s * 0.5, s * 0.16)
    path.cubicTo(s * 0.33, s * 0.36, s * 0.30, s * 0.54, s * 0.40, s * 0.68)
    path.cubicTo(s * 0.44, s * 0.58, s * 0.50, s * 0.56, s * 0.50, s * 0.48)
    path.cubicTo(s * 0.50, s * 0.56, s * 0.57, s * 0.60, s * 0.60, s * 0.70)
    path.cubicTo(s * 0.71, s * 0.52, s * 0.62, s * 0.34, s * 0.5, s * 0.16)
    path.closeSubpath()
    p2 = QPainterPath()
    p2.moveTo(s * 0.5, s * 0.50)
    p2.cubicTo(s * 0.45, s * 0.58, s * 0.45, s * 0.66, s * 0.5, s * 0.76)
    p2.cubicTo(s * 0.55, s * 0.68, s * 0.55, s * 0.60, s * 0.5, s * 0.50)
    p2.closeSubpath()
    p.drawPath(path)
    p.drawPath(p2)


def _heart(p, s, filled=False):
    path = QPainterPath()
    path.moveTo(s * 0.5, s * 0.84)
    path.cubicTo(s * 0.12, s * 0.56, s * 0.20, s * 0.22, s * 0.5, s * 0.42)
    path.cubicTo(s * 0.80, s * 0.22, s * 0.88, s * 0.56, s * 0.5, s * 0.84)
    path.closeSubpath()
    if filled:
        _fill(p)
        p.fillPath(path, p.brush().color())
    else:
        _stroke(p, s * 0.085)
        p.drawPath(path)


def _clock(p, s):
    _stroke(p, s * 0.085)
    p.drawEllipse(QPointF(s * 0.5, s * 0.5), s * 0.32, s * 0.32)
    p.drawLine(QPointF(s * 0.5, s * 0.5), QPointF(s * 0.5, s * 0.32))
    p.drawLine(QPointF(s * 0.5, s * 0.5), QPointF(s * 0.66, s * 0.56))


def _download(p, s):
    _stroke(p, s * 0.085)
    p.drawLine(QPointF(s * 0.5, s * 0.18), QPointF(s * 0.5, s * 0.62))
    path = QPainterPath()
    path.moveTo(s * 0.34, s * 0.46)
    path.lineTo(s * 0.5, s * 0.64)
    path.lineTo(s * 0.66, s * 0.46)
    p.drawPath(path)
    p.drawLine(QPointF(s * 0.26, s * 0.80), QPointF(s * 0.74, s * 0.80))


def _file_download(p, s):
    _stroke(p, s * 0.078)
    path = QPainterPath()
    path.moveTo(s * 0.30, s * 0.18)
    path.lineTo(s * 0.52, s * 0.18)
    path.lineTo(s * 0.70, s * 0.36)
    path.lineTo(s * 0.70, s * 0.82)
    path.lineTo(s * 0.30, s * 0.82)
    path.closeSubpath()
    p.drawPath(path)
    p.drawLine(QPointF(s * 0.5, s * 0.44), QPointF(s * 0.5, s * 0.68))
    p2 = QPainterPath()
    p2.moveTo(s * 0.38, s * 0.56)
    p2.lineTo(s * 0.5, s * 0.70)
    p2.lineTo(s * 0.62, s * 0.56)
    p.drawPath(p2)


def _delete(p, s):
    _stroke(p, s * 0.082)
    path = QPainterPath()
    path.moveTo(s * 0.30, s * 0.32)
    path.lineTo(s * 0.70, s * 0.32)
    path.lineTo(s * 0.66, s * 0.82)
    path.lineTo(s * 0.34, s * 0.82)
    path.closeSubpath()
    p.drawPath(path)
    p.drawLine(QPointF(s * 0.40, s * 0.32), QPointF(s * 0.39, s * 0.24))
    p.drawLine(QPointF(s * 0.60, s * 0.32), QPointF(s * 0.61, s * 0.24))
    p.drawLine(QPointF(s * 0.45, s * 0.44), QPointF(s * 0.44, s * 0.72))
    p.drawLine(QPointF(s * 0.55, s * 0.44), QPointF(s * 0.56, s * 0.72))


def _play_pause(p, s, mode):
    _fill(p)
    if mode == "play":
        path = QPainterPath()
        path.moveTo(s * 0.36, s * 0.26)
        path.lineTo(s * 0.36, s * 0.74)
        path.lineTo(s * 0.72, s * 0.5)
        path.closeSubpath()
        p.drawPath(path)
    else:
        bw, bh = s * 0.13, s * 0.5
        y0 = (s - bh) / 2
        r = s * 0.04
        p.drawRoundedRect(QRectF(s * 0.3, y0, bw, bh), r, r)
        p.drawRoundedRect(QRectF(s * 0.57, y0, bw, bh), r, r)


def _prev(p, s):
    _fill(p)
    bw, bh = s * 0.12, s * 0.5
    y0 = (s - bh) / 2
    p.drawRoundedRect(QRectF(s * 0.2, y0, bw, bh), s * 0.02, s * 0.02)
    path = QPainterPath()
    path.moveTo(s * 0.78, s * 0.26)
    path.lineTo(s * 0.78, s * 0.74)
    path.lineTo(s * 0.42, s * 0.5)
    path.closeSubpath()
    p.drawPath(path)


def _next(p, s):
    _fill(p)
    bw, bh = s * 0.12, s * 0.5
    y0 = (s - bh) / 2
    p.drawRoundedRect(QRectF(s * 0.68, y0, bw, bh), s * 0.02, s * 0.02)
    path = QPainterPath()
    path.moveTo(s * 0.22, s * 0.26)
    path.lineTo(s * 0.22, s * 0.74)
    path.lineTo(s * 0.58, s * 0.5)
    path.closeSubpath()
    p.drawPath(path)


def _shuffle(p, s):
    _stroke(p, s * 0.075)
    p.drawLine(QPointF(s * 0.18, s * 0.30), QPointF(s * 0.40, s * 0.30))
    p.drawLine(QPointF(s * 0.48, s * 0.30), QPointF(s * 0.82, s * 0.30))
    p.drawLine(QPointF(s * 0.18, s * 0.70), QPointF(s * 0.40, s * 0.70))
    p.drawLine(QPointF(s * 0.48, s * 0.70), QPointF(s * 0.82, s * 0.70))
    p.drawLine(QPointF(s * 0.40, s * 0.30), QPointF(s * 0.60, s * 0.70))
    p.drawLine(QPointF(s * 0.40, s * 0.70), QPointF(s * 0.60, s * 0.30))
    _fill(p)
    p.drawPolygon(QPolygonF([QPointF(s * 0.82, s * 0.30), QPointF(s * 0.72, s * 0.24), QPointF(s * 0.72, s * 0.36)]))
    p.drawPolygon(QPolygonF([QPointF(s * 0.82, s * 0.70), QPointF(s * 0.72, s * 0.64), QPointF(s * 0.72, s * 0.76)]))


def _repeat(p, s):
    _stroke(p, s * 0.075)
    p.drawArc(QRectF(s * 0.22, s * 0.22, s * 0.56, s * 0.56), 30 * 16, 120 * 16)
    p.drawArc(QRectF(s * 0.22, s * 0.22, s * 0.56, s * 0.56), 210 * 16, 120 * 16)
    _fill(p)
    p.drawPolygon(QPolygonF([QPointF(s * 0.68, s * 0.22), QPointF(s * 0.78, s * 0.30), QPointF(s * 0.62, s * 0.32)]))
    p.drawPolygon(QPolygonF([QPointF(s * 0.32, s * 0.78), QPointF(s * 0.22, s * 0.70), QPointF(s * 0.38, s * 0.68)]))


def _repeat_one(p, s):
    _repeat(p, s)
    col = p.brush().color()
    p.setPen(col)
    p.setBrush(Qt.NoBrush)
    f = QFont()
    f.setPixelSize(int(s * 0.28))
    f.setBold(True)
    p.setFont(f)
    p.drawText(QRectF(s * 0.30, s * 0.30, s * 0.40, s * 0.40), Qt.AlignCenter, "1")


def _order(p, s):
    _stroke(p, s * 0.085)
    for y in (s * 0.32, s * 0.52, s * 0.72):
        p.drawLine(QPointF(s * 0.22, y), QPointF(s * 0.56, y))
    _fill(p)
    p.drawPolygon(QPolygonF([QPointF(s * 0.66, s * 0.30), QPointF(s * 0.82, s * 0.52), QPointF(s * 0.66, s * 0.74)]))


def _vol_base(p, s):
    _stroke(p, s * 0.08)
    return QPolygonF([QPointF(s * 0.16, s * 0.4), QPointF(s * 0.32, s * 0.4),
                      QPointF(s * 0.46, s * 0.26), QPointF(s * 0.46, s * 0.74),
                      QPointF(s * 0.32, s * 0.6), QPointF(s * 0.16, s * 0.6)])


def _volume(p, s):
    p.drawPolygon(_vol_base(p, s))
    p.drawArc(QRectF(s * 0.52, s * 0.34, s * 0.16, s * 0.32), -55 * 16, 110 * 16)


def _volume_high(p, s):
    p.drawPolygon(_vol_base(p, s))
    p.drawArc(QRectF(s * 0.52, s * 0.34, s * 0.14, s * 0.32), -55 * 16, 110 * 16)
    p.drawArc(QRectF(s * 0.62, s * 0.26, s * 0.18, s * 0.48), -55 * 16, 110 * 16)


def _volume_low(p, s):
    p.drawPolygon(_vol_base(p, s))
    p.drawArc(QRectF(s * 0.52, s * 0.34, s * 0.14, s * 0.32), -55 * 16, 110 * 16)


def _volume_mute(p, s):
    p.drawPolygon(_vol_base(p, s))
    p.drawLine(QPointF(s * 0.58, s * 0.38), QPointF(s * 0.82, s * 0.62))
    p.drawLine(QPointF(s * 0.82, s * 0.38), QPointF(s * 0.58, s * 0.62))


def _search(p, s):
    _stroke(p, s * 0.09)
    p.drawEllipse(QPointF(s * 0.38, s * 0.38), s * 0.28, s * 0.28)
    p.drawLine(QPointF(s * 0.60, s * 0.60), QPointF(s * 0.85, s * 0.85))


def _close(p, s):
    _stroke(p, s * 0.085)
    p.drawLine(QPointF(s * 0.24, s * 0.24), QPointF(s * 0.76, s * 0.76))
    p.drawLine(QPointF(s * 0.76, s * 0.24), QPointF(s * 0.24, s * 0.76))


def _minimize(p, s):
    _stroke(p, s * 0.085)
    p.drawLine(QPointF(s * 0.24, s * 0.5), QPointF(s * 0.76, s * 0.5))


def _maximize(p, s):
    _stroke(p, s * 0.08)
    p.drawRoundedRect(QRectF(s * 0.24, s * 0.24, s * 0.52, s * 0.52), s * 0.06, s * 0.06)


def _lyrics(p, s):
    _stroke(p, s * 0.085)
    p.drawLine(QPointF(s * 0.18, s * 0.30), QPointF(s * 0.82, s * 0.30))
    p.drawLine(QPointF(s * 0.18, s * 0.50), QPointF(s * 0.64, s * 0.50))
    p.drawLine(QPointF(s * 0.18, s * 0.70), QPointF(s * 0.74, s * 0.70))


def _chevron_left(p, s):
    _stroke(p, s * 0.09)
    path = QPainterPath()
    path.moveTo(s * 0.64, s * 0.2)
    path.lineTo(s * 0.32, s * 0.5)
    path.lineTo(s * 0.64, s * 0.8)
    p.drawPath(path)


def _settings(p, s):
    cx, cy = s * 0.5, s * 0.5
    r_out = s * 0.36
    _stroke(p, s * 0.075)
    for i in range(8):
        a = i * 45 * math.pi / 180
        p.drawLine(QPointF(cx + r_out * 0.78 * math.cos(a), cy + r_out * 0.78 * math.sin(a)),
                   QPointF(cx + r_out * math.cos(a), cy + r_out * math.sin(a)))
    p.drawEllipse(QPointF(cx, cy), r_out * 0.62, r_out * 0.62)
    _fill(p)
    p.drawEllipse(QPointF(cx, cy), r_out * 0.22, r_out * 0.22)


def _folder(p, s):
    _stroke(p, s * 0.08)
    path = QPainterPath()
    path.moveTo(s * 0.12, s * 0.34)
    path.lineTo(s * 0.12, s * 0.82)
    path.lineTo(s * 0.88, s * 0.82)
    path.lineTo(s * 0.88, s * 0.34)
    path.lineTo(s * 0.48, s * 0.34)
    path.lineTo(s * 0.38, s * 0.22)
    path.lineTo(s * 0.12, s * 0.22)
    path.closeSubpath()
    p.drawPath(path)


def _import(p, s):
    _stroke(p, s * 0.085)
    p.drawLine(QPointF(s * 0.5, s * 0.82), QPointF(s * 0.5, s * 0.26))
    path = QPainterPath()
    path.moveTo(s * 0.5, s * 0.26)
    path.lineTo(s * 0.30, s * 0.46)
    path.lineTo(s * 0.42, s * 0.46)
    path.lineTo(s * 0.42, s * 0.18)
    path.lineTo(s * 0.58, s * 0.18)
    path.lineTo(s * 0.58, s * 0.46)
    path.lineTo(s * 0.70, s * 0.46)
    path.lineTo(s * 0.5, s * 0.26)
    p.drawPath(path)
    p.drawLine(QPointF(s * 0.25, s * 0.82), QPointF(s * 0.75, s * 0.82))


def _wave(p, s):
    w = max(1.6, s * 0.08)
    gap = s * 0.20
    x0 = s * 0.18
    heights = [s * 0.34, s * 0.66, s * 0.48, s * 0.80, s * 0.42]
    r = w / 2
    for i, h in enumerate(heights):
        x = x0 + i * (w + gap)
        y = (s - h) / 2
        p.drawRoundedRect(QRectF(x, y, w, h), r, r)


def _check(p, s):
    _stroke(p, s * 0.09)
    path = QPainterPath()
    path.moveTo(s * 0.22, s * 0.52)
    path.lineTo(s * 0.42, s * 0.74)
    path.lineTo(s * 0.80, s * 0.28)
    p.drawPath(path)


def _back(p, s):
    _stroke(p, s * 0.085)
    path = QPainterPath()
    path.moveTo(s * 0.62, s * 0.2)
    path.lineTo(s * 0.30, s * 0.5)
    path.lineTo(s * 0.62, s * 0.8)
    p.drawPath(path)
    p.drawLine(QPointF(s * 0.30, s * 0.5), QPointF(s * 0.82, s * 0.5))


def _list(p, s):
    _stroke(p, s * 0.08)
    for y in (s * 0.26, s * 0.5, s * 0.74):
        p.drawEllipse(QPointF(s * 0.22, y), s * 0.06, s * 0.06)
        p.drawLine(QPointF(s * 0.38, y), QPointF(s * 0.82, y))


def _cd(p, s):
    cx, cy = s * 0.5, s * 0.5
    r = s * 0.42
    _stroke(p, s * 0.07)
    p.drawEllipse(QPointF(cx, cy), r, r)
    p.drawEllipse(QPointF(cx, cy), r * 0.6, r * 0.6)
    _fill(p)
    p.drawEllipse(QPointF(cx, cy), r * 0.16, r * 0.16)


_DRAWERS = {
    'home': _home, 'hot': _hot, 'heart': _heart,
    'heart_filled': lambda p, s: _heart(p, s, True),
    'clock': _clock, 'download': _download, 'file_download': _file_download,
    'delete': _delete, 'play': lambda p, s: _play_pause(p, s, "play"),
    'pause': lambda p, s: _play_pause(p, s, "pause"),
    'prev': _prev, 'next': _next, 'shuffle': _shuffle,
    'repeat': _repeat, 'repeat_one': _repeat_one, 'order': _order,
    'volume_high': _volume_high, 'volume_low': _volume_low,
    'volume_mute': _volume_mute, 'volume': _volume_high,
    'search': _search, 'close': _close, 'minimize': _minimize,
    'maximize': _maximize, 'lyrics': _lyrics, 'chevron_left': _chevron_left,
    'settings': _settings, 'folder': _folder, 'import': _import,
    'wave': _wave, 'check': _check, 'back': _back, 'list': _list, 'cd': _cd,
}

_cache: dict = {}
_CACHE_MAX = 256


def render(name: str, size: int = 14, color: str = None) -> QPixmap:
    key = (name, size, color)
    cached = _cache.get(key)
    if cached is not None and not cached.isNull():
        return cached
    drawer = _DRAWERS.get(name)
    if not drawer:
        return QPixmap()
    dpr = 2
    pm = QPixmap(size * dpr, size * dpr)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.SmoothPixmapTransform)
    c = QColor(color) if color else QColor("#000000")
    p.setPen(QPen(c, max(1.5, size * 0.12), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(QBrush(c))
    p.scale(dpr, dpr)
    drawer(p, size)
    p.end()
    pm.setDevicePixelRatio(dpr)
    if len(_cache) >= _CACHE_MAX:
        try:
            _cache.pop(next(iter(_cache)))
        except (StopIteration, KeyError):
            pass
    _cache[key] = pm
    return pm


def make_icon(name: str, size: int = 14, color: str = None) -> QIcon:
    return QIcon(render(name, size, color))
