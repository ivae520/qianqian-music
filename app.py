"""千千动听 - 入口"""
import sys, os, traceback

_LOG = os.path.join(os.path.expanduser("~"), "qianqian_crash.log")


def _log(msg: str) -> None:
    try:
        with open(_LOG, "w", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def _excepthook(t, v, tb):
    s = "".join(traceback.format_exception(t, v, tb))
    _log(s)
    sys.stderr.write(s)


sys.excepthook = _excepthook
os.environ.setdefault('QT_QPA_FONTDIR', 'C:/Windows/Fonts')


def main():
    _log("=== Starting ===")
    try:
        import updater
        updater.cleanup_old_files()
    except Exception:
        pass
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
    from PyQt5.QtWidgets import QApplication
    from ui import C, FF, MainWindow
    import version

    app = QApplication(sys.argv)
    app.setApplicationName("千千动听")
    app.setApplicationDisplayName("千千动听")
    app.setApplicationVersion(version.__version__)
    app.setOrganizationName("Qianqian")

    fam = FF.split(",")[0].strip('"')
    app.setFont(QFont(fam, 12))
    app.setStyleSheet(f"""
        * {{ font-family: {FF}; }}
        *:focus {{ outline: none; }}
        QToolTip {{ background: {C['bg2']}; color: {C['tx']}; border: 1px solid {C['bd']}; border-radius: 6px; padding: 4px 8px; font-size: 11px; }}
        QMessageBox {{ background: {C['bg2']}; }}
        QMessageBox QLabel {{ color: {C['tx']}; font-size: 12px; }}
        QMessageBox QPushButton {{ background: {C['sf']}; color: {C['tx']}; border: 1px solid {C['bd']}; border-radius: 6px; padding: 6px 18px; min-width: 60px; }}
        QMessageBox QPushButton:hover {{ background: {C['sfh']}; }}
    """)

    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base, "icon.ico")
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
    else:
        pm = QPixmap(64, 64)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(C["pr"]))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, 64, 64, 14, 14)
        p.setBrush(QColor("white"))
        p.drawEllipse(14, 28, 10, 10)
        p.drawEllipse(36, 22, 10, 10)
        p.drawRect(26, 12, 6, 22)
        p.end()
        icon = QIcon(pm)
    app.setWindowIcon(icon)

    _log("App configured")
    from core import PlayerCore
    player = PlayerCore()
    _log("PlayerCore OK")
    w = MainWindow(player)
    w.setWindowIcon(icon)
    w.show()
    _log("show() OK")

    try:
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: _auto_check_update(w))
    except Exception:
        pass

    return app.exec_()


def _auto_check_update(parent):
    try:
        import updater
        updater.check_and_show(parent, auto=True)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        _log(f"FATAL: {e}\n{traceback.format_exc()}")
        raise
