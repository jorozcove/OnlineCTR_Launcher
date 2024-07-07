import configparser

class LauncherSettings:
    def __init__(self):
        self.config = configparser.ConfigParser(inline_comment_prefixes=";")
        self.read_settings()
    
    def read_settings(self):
        try:
            self.config.read("settings.ini")
            self.name = self.config["SETTINGS"]["name"].strip('"')
            self.frame_rate = self.config["SETTINGS"]["frame_rate"].strip('"')
            self.duckstation = self.config["PATHS"]["duckstation"].strip('"')
            self.game_rom = self.config["PATHS"]["game_rom"].strip('"')
            self.fullscreen = self.config["SETTINGS"]["fullscreen"].strip('"')
            self.fast_boot = self.config["SETTINGS"]["fast_boot"].strip('"')
        except Exception as e:
            self.name = "YourName"
            self.frame_rate = "0"
            self.duckstation = r"C:\Users\[yourUserName]\[remaining path to duckstation folder]\duckstation-qt-x64-ReleaseLTCG.exe"
            self.game_rom = r"C:\Users\[yourUserName]\[remaining path to game rom]\CTR.bin"
            self.fullscreen = "0"
            self.fast_boot = "0"
            self.save_settings()
            
    def save_settings(self):
        self.config["SETTINGS"] = {
            "name": f'"{self.name}" ; Your name in the game',
            "frame_rate": f'{self.frame_rate} ; 0 = 30fps, 1 = 60fps',
            "fullscreen": f'{self.fullscreen} ; 0 = disabled, 1 = enabled',
            "fast_boot": f'{self.fast_boot} ; 0 = disabled, 1 = enabled'
        }
        self.config["PATHS"] = {
            "duckstation": f'"{self.duckstation}"',
            "game_rom": f'"{self.game_rom}"'
        }
        with open("settings.ini", "w") as file:
            self.config.write(file)
    
    def get_player_name(self):
        return self.name

    def get_frame_rate(self):
        return self.frame_rate

    def get_fast_boot(self):
        return self.fast_boot

    def get_fullscreen(self):
        return self.fullscreen

    def get_duckstation_path(self):
        return self.duckstation

    def get_game_rom_path(self):
        return self.game_rom
