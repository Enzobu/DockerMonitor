import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
import os
import json

# Chemins des icônes
icon_paths = {
    0: "/opt/dockerExtension/dockerIcon.png",       # Rouge : application arrêtée
    1: "/opt/dockerExtension/dockerIconStandBy.png",# Orange : standby (uniquement en quittant)
    2: "/opt/dockerExtension/dockerIconRun.png"     # Vert : application démarrée
}
project_icon_paths = {
    0: "/opt/dockerExtension/icon_inactive.png",    # Rouge : projet arrêté
    1: "/opt/dockerExtension/icon_standBy.png",     # Orange : standby
    2: "/opt/dockerExtension/icon_active.png"       # Vert : projet démarré
}
config_path = "/home/enzo/Dev/config.json"
