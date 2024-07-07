from src.utils import MovableWindow

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QFileDialog

class SettingsWindow(MovableWindow):
    def __init__(self, launcher_settings, game_launcher):
        super().__init__()
        self.launcher_settings = launcher_settings
        self.setWindowTitle("CTR Launcher Settings")
        self.setWindowIcon(QIcon('assets/icon.ico'))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.resize(300, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint & ~Qt.WindowMinimizeButtonHint)
        layout = QVBoxLayout(central_widget)

        self.create_name_input(layout)
        self.create_frame_rate_input(layout)
        self.create_fast_boot_input(layout)
        self.create_fullscreen_input(layout)
        self.create_duckstation_input(layout)
        self.create_game_rom_input(layout)
        self.create_save_button(layout)

        self.game_launcher = game_launcher

    def create_name_input(self, layout):
        self.name_label = QLabel("Player Name:")
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        self.name_input.setText(self.launcher_settings.get_player_name())

    def create_frame_rate_input(self, layout):
        self.frame_rate_label = QLabel("Frame Rate:")
        self.frame_rate_input = QComboBox()
        self.frame_rate_input.addItem("30fps")
        self.frame_rate_input.addItem("60fps")
        self.frame_rate_input.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.frame_rate_label)
        layout.addWidget(self.frame_rate_input)
        if self.launcher_settings.get_frame_rate() == "0":
            self.frame_rate_input.setCurrentIndex(0)
        else:
            self.frame_rate_input.setCurrentIndex(1)

    def create_fast_boot_input(self, layout):
        self.fast_boot_label = QLabel("Fast Boot:")
        self.fast_boot_input = QComboBox()
        self.fast_boot_input.addItem("Disabled")
        self.fast_boot_input.addItem("Enabled")
        self.fast_boot_input.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.fast_boot_label)
        layout.addWidget(self.fast_boot_input)
        if self.launcher_settings.get_fast_boot() == "0":
            self.fast_boot_input.setCurrentIndex(0)
        else:
            self.fast_boot_input.setCurrentIndex(1)

    def create_fullscreen_input(self, layout):
        self.fullscreen_label = QLabel("Fullscreen:")
        self.fullscreen_input = QComboBox()
        self.fullscreen_input.addItem("Disabled")
        self.fullscreen_input.addItem("Enabled")
        self.fullscreen_input.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.fullscreen_label)
        layout.addWidget(self.fullscreen_input)
        if self.launcher_settings.get_fullscreen() == "0":
            self.fullscreen_input.setCurrentIndex(0)
        else:
            self.fullscreen_input.setCurrentIndex(1)

    def create_duckstation_input(self, layout):
        self.duckstation_label = QLabel("Duckstation Path:")
        self.duckstation_input = QLineEdit()
        self.duckstation_button = QPushButton("Browse for Duckstation")
        self.duckstation_button.setCursor(Qt.PointingHandCursor)
        self.duckstation_button.clicked.connect(self.browse_duckstation)
        layout.addWidget(self.duckstation_label)
        layout.addWidget(self.duckstation_input)
        layout.addWidget(self.duckstation_button)
        self.duckstation_input.setDisabled(True)
        self.duckstation_input.setText(self.launcher_settings.get_duckstation_path())

    def create_game_rom_input(self, layout):
        self.game_rom_label = QLabel("Game ROM Path:")
        self.game_rom_input = QLineEdit()
        self.game_rom_button = QPushButton("Browse for CTR ROM")
        self.game_rom_button.setCursor(Qt.PointingHandCursor)
        self.game_rom_button.clicked.connect(self.browse_game_rom)
        layout.addWidget(self.game_rom_label)
        layout.addWidget(self.game_rom_input)
        layout.addWidget(self.game_rom_button)
        self.game_rom_input.setDisabled(True)
        self.game_rom_input.setText(self.launcher_settings.get_game_rom_path())

    def create_save_button(self, layout):
        layout.addSpacing(10)
        save_button = QPushButton("Save and Close")
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 10px 24px; text-align: center; text-decoration: none; font-size: 16px; margin: 4px 2px;")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

    def save_settings(self):
        self.launcher_settings.name = self.name_input.text()
        self.launcher_settings.frame_rate = str(self.frame_rate_input.currentIndex())
        self.launcher_settings.fast_boot = str(self.fast_boot_input.currentIndex())
        self.launcher_settings.fullscreen = str(self.fullscreen_input.currentIndex())
        self.launcher_settings.duckstation = self.duckstation_input.text()
        self.launcher_settings.game_rom = self.game_rom_input.text()
        self.launcher_settings.save_settings()
        self.game_launcher.load_settings()
        self.close()

    def browse_duckstation(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Duckstation", filter="duckstation-qt-x64-ReleaseLTCG.exe")
        if file:
            self.duckstation_input.setText(file)

    def browse_game_rom(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Game ROM", filter="*.bin")
        if file:
            self.game_rom_input.setText(file)