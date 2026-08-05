
import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtCore import QMimeData, QSharedMemory
from PySide6.QtGui import QIcon, QAction
import logging
from monitor import Monitor
from notifier import Notifier
from logger import setup_logger
from utils import get_resource_path

APP_ID = "esun.ClipMonitor"
DISPLAY_NAME = "Clip Monitor"
ICON_PATH = get_resource_path(os.path.join("assets", "icon.ico"))

if __name__ == "__main__":

    app = QApplication([])

    app_logger = setup_logger(
        display_name=DISPLAY_NAME,
        log_level=logging.INFO,
    )

    shm = QSharedMemory("ClipMonitor_SingleInstance")
    if not shm.create(1):
        app_logger.error("Another instance of Clip Monitor is already running. Exiting.")
        sys.exit(0)

    app.setQuitOnLastWindowClosed(False)

    tray = QSystemTrayIcon(QIcon(str(ICON_PATH)), app, toolTip=DISPLAY_NAME)
    menu = QMenu()
    quit_action = QAction("Quit", app)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.show()

    notifier = Notifier(
        aumid=APP_ID,
        display_name=DISPLAY_NAME,
        icon_path=ICON_PATH,
        parent=app,
    )

    monitor = Monitor(notifier=notifier)

    app.exec()