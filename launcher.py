import os
import sys
import warnings
import psutil

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.utils import MovableWindow, kill_process
from src.SettingsWindow import SettingsWindow
from src.LauncherSettings import LauncherSettings 
from src.GameLauncher import GameLauncher

warnings.filterwarnings('ignore')

LAUNCHER_VERSION = "1.3b2"

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    application_path = os.path.dirname(__file__)


#Kill launcher.exe if already running
current_pid = os.getpid()
for proc in psutil.process_iter(['pid', 'name']):
    if proc.info['name'] in ['launcher.exe', 'client.exe', 'duckstation-qt-x64-ReleaseLTCG.exe'] and proc.info['pid'] != current_pid:
        proc.kill()

class LauncherGameRunnable(QRunnable):
    def __init__(self, game_launcher):
        super().__init__()
        self.game_launcher = game_launcher

    def run(self):
        self.game_launcher.launch_game()        


class LauncherGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.window = self.create_main_window()
        self.logs_text = self.create_logs_textbox()
        self.create_launch_button()
        self.create_settings_button()
        self.create_exit_button()
        self.progress_bar = self.create_progress_bar()

    def create_main_window(self):
        window = MovableWindow()
        window.setAttribute(Qt.WA_TranslucentBackground, True)
        window.setAttribute(Qt.WA_NoSystemBackground, True)
        window.setWindowFlags(Qt.FramelessWindowHint)
        window.setWindowIcon(QIcon('assets/icon.ico'))

        label = QLabel(window)
        pixmap = QPixmap('assets/launcher.png')
        label.setPixmap(pixmap)
        label.setGeometry(0, 0, pixmap.width(), pixmap.height())

        window.label = label
        window.resize(pixmap.width(), pixmap.height())

        return window

    def create_logs_textbox(self):
        logs_textbox = QTextEdit(self.window)
        logs_textbox.setGeometry(315, 70, 450, 260)
        logs_textbox.setText(f"Launcher Version: {LAUNCHER_VERSION}\n")
        logs_textbox.setReadOnly(True)
        logs_textbox.setLineWrapMode(QTextEdit.WidgetWidth)
        logs_textbox.setStyleSheet("background-color: black; color: white; font-family: Arial; font-size: 12px; border-radius: 10px; padding: 10px;")

        return logs_textbox

    def create_launch_button(self):
        button_launch = QPushButton(self.window)
        button_launch.setGeometry(50, 255, 190, 30)
        button_launch.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        button_launch.setCursor(Qt.PointingHandCursor)
        #debugpy.debug_this_thread()
        button_launch.clicked.connect(self.launch_game_in_thread)

    def create_settings_button(self):
        button_settings = QPushButton(self.window)
        button_settings.setGeometry(65, 300, 170, 30)
        button_settings.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        button_settings.setCursor(Qt.PointingHandCursor)
        
        launcher_settings = LauncherSettings()
        self.second_window = SettingsWindow(launcher_settings)
        button_settings.clicked.connect(self.second_window.show)

    def create_exit_button(self):
        button_exit = QPushButton(self.window)
        button_exit.setGeometry(80, 338, 140, 30)
        button_exit.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        button_exit.setCursor(Qt.PointingHandCursor)
        button_exit.clicked.connect(self.close)

    def create_progress_bar(self):
        progress_bar = QProgressBar(self.window)
        progress_bar.setGeometry(315, 348, 450, 20)
        progress_bar.setValue(0)
        progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: white;
                text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    }""")
        progress_bar.setRange(0, 100)
        progress_bar.hide()
        
        return progress_bar

    def launch_game_in_thread(self):
        runnable = LauncherGameRunnable(GameLauncher(root_folder, self, settings))
        QThreadPool.globalInstance().start(runnable)

    def show(self):
        self.window.show()

    def close(self):
        kill_process()
        self.destroy()
        sys.exit(0)
        
if __name__ == "__main__":
    root_folder = application_path
    settings = LauncherSettings()
    app = QApplication(sys.argv)
    launcher = LauncherGUI()
    launcher.show()
    sys.exit(app.exec_())