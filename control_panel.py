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

# État des projets
project_states = {}

def load_config():
    if not os.path.exists(config_path):
        print(f"Fichier de configuration introuvable : {config_path}")
        exit(1)
    with open(config_path, "r") as file:
        return json.load(file)

def get_icon(state, is_project=True):
    paths = project_icon_paths if is_project else icon_paths
    return QIcon(paths[state])

def start_project(project_name):
    config = load_config()
    project = next((p for p in config['projects'] if p['name'] == project_name), None)
    if project and os.path.exists(project["start_script"]):
        subprocess.run([project["start_script"]], check=True)
        return True
    return False

def stop_project(project_name):
    config = load_config()
    project = next((p for p in config['projects'] if p['name'] == project_name), None)
    if project and os.path.exists(project["stop_script"]):
        subprocess.run([project["stop_script"]], check=True)
        return True
    return False

def update_menu_and_icon(tray_icon, menu):
    global project_states
    config = load_config()

    # Déterminer l'état global de l'app
    app_state = 2 if any(state == 2 for state in project_states.values()) else 0
    tray_icon.setIcon(get_icon(app_state, is_project=False))

    # Mettre à jour le menu
    menu.clear()
    quit_action = QAction("Quitter", tray_icon)
    quit_action.triggered.connect(lambda: quit_program(tray_icon, menu))
    menu.addAction(quit_action)

    for project in config['projects']:
        project_name = project["name"]
        state = project_states.get(project_name, 0)
        icon = get_icon(state)
        text = {
            0: f"Start {project_name}",
            1: f"Stopping {project_name}...",
            2: f"Stop {project_name}",
        }[state]

        action = QAction(icon, text, tray_icon)
        action.setData(project_name)
        if state == 0:  # Projet arrêté
            action.triggered.connect(
                lambda checked, name=project_name: start_and_update(name, tray_icon, menu)
            )
        elif state == 2:  # Projet actif
            action.triggered.connect(
                lambda checked, name=project_name: stop_and_update(name, tray_icon, menu)
            )

        menu.addAction(action)

def start_and_update(project_name, tray_icon, menu):
    global project_states
    if start_project(project_name):
        project_states[project_name] = 2
        update_menu_and_icon(tray_icon, menu)

def stop_and_update(project_name, tray_icon, menu):
    global project_states
    project_states[project_name] = 1  # Standby
    update_menu_and_icon(tray_icon, menu)

    # Arrêter le projet après un délai pour simuler le standby
    QTimer.singleShot(1000, lambda: finalize_stop(project_name, tray_icon, menu))

def finalize_stop(project_name, tray_icon, menu):
    global project_states
    if stop_project(project_name):
        project_states[project_name] = 0
        update_menu_and_icon(tray_icon, menu)

def quit_program(tray_icon, menu):
    global project_states
    tray_icon.setIcon(get_icon(1, is_project=False))  # Standby pour l'application
    QTimer.singleShot(1000, lambda: finalize_quit(tray_icon, menu))

def finalize_quit(tray_icon, menu):
    global project_states
    active_projects = [name for name, state in project_states.items() if state == 2]
    for project_name in active_projects:
        stop_project(project_name)
        project_states[project_name] = 0

    QApplication.quit()

def start_icon():
    global project_states
    config = load_config()
    project_states = {p["name"]: 0 for p in config["projects"]}

    app = QApplication(sys.argv)
    tray_icon = QSystemTrayIcon(get_icon(0, is_project=False), app)
    tray_icon.setToolTip("Gestion des projets Docker")

    menu = QMenu()
    tray_icon.setContextMenu(menu)
    update_menu_and_icon(tray_icon, menu)
    tray_icon.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start_icon()

