import requests
import os
import subprocess
import psutil

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint, QRunnable
from PyQt5.QtWidgets import QMainWindow

def launch_duckstation(duckstation_path, patched_file_path, fast_boot = "0", fullscreen = "0",):
    try:
        process = f'start "" "{duckstation_path}" {patched_file_path}{" -fullscreen" if fullscreen == "1" else ""}{" -fastboot" if fast_boot == "1" else ""}'
        subprocess.Popen(process, shell=True)
        return True

    except Exception as e:
        print(e)
        return False

def patch_game(xdelta_file_path, patched_file_path, rom_file_path, root_folder):
    xdelta_path = os.path.join(root_folder, "_XDELTA", "xdelta3.exe")
    if os.path.exists(patched_file_path):
        os.remove(patched_file_path)
    command = f'"{xdelta_path}" -d -s "{rom_file_path}" "{xdelta_file_path}" "{patched_file_path}"'
    subprocess.run(command, shell=True)

def check_for_updates():
    try:
        local_version = get_local_version()
        version = get_current_patch()
        if version != local_version:
            return True, version
        else:
            return False, version
    except Exception as e:
        print(e)
        return False, None

def download_file(url, destination):
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
    
        with open(destination, "wb") as file:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                downloaded_size += len(data)
                progress = int(100 * downloaded_size / total_size)
                yield progress

    except Exception as e:
        print(e)
        yield None

def get_local_version():
    try:
        with open("version", "r") as file:
            version = file.read()
            return version
    except Exception as e:
        print(e)
        return "1"

def get_current_patch():
    url = "https://online-ctr.com/wp-content/uploads/onlinectr_patches/build.txt"
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        return content
    else:
        return "1"

def write_version_file(version):
    try:
        with open("version", "w") as file:
            file.write(version)
    except Exception as e:
        print(e)

def check_for_patched_game(patched_file_path):
    if os.path.exists(patched_file_path):
        return True
    else:
        return False

def kill_process():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in ['client.exe', 'duckstation-qt-x64-ReleaseLTCG.exe']:
            proc.kill()

class MovableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.m_drag = False
        self.m_DragPosition = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.m_drag:
            self.move(event.globalPos() - self.m_DragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_drag = False