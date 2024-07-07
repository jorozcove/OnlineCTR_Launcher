import os
import re
import shutil
import subprocess
import threading
import time
import zipfile

from src.utils import *


URL_CLIENT = "https://online-ctr.com/wp-content/uploads/onlinectr_patches/client.zip"
URL_XDELTA_30 = "https://online-ctr.com/wp-content/uploads/onlinectr_patches/ctr-u_Online30.xdelta"
URL_XDELTA_60 = "https://online-ctr.com/wp-content/uploads/onlinectr_patches/ctr-u_Online60.xdelta"

class GameLauncher:
    def __init__(self, root_folder, gui, settings):
        self.root_folder = root_folder
        self.xdelta60_file = "ctr-u_Online60.xdelta"
        self.xdelta30_file = "ctr-u_Online30.xdelta"
        self.rom_file_path = settings.game_rom  
        #os.path.join(root_folder, "_ROM", "CTR.bin")
        self.patched60_file_path = os.path.join(self.root_folder, "_ROM", "CTR_Online60.bin")
        self.patched30_file_path = os.path.join(self.root_folder, "_ROM", "CTR_Online30.bin")
        self.client_path = os.path.join(self.root_folder, "_CTRClient", "client.exe")
        self.fast_boot = settings.fast_boot
        self.fullscreen = settings.fullscreen
        self.duckstation_path = settings.duckstation
        self.frame_rate = settings.frame_rate
        self.name = settings.name
        self.gui = gui
        self.patched_file = None

        if int(self.frame_rate) == 0:
            self.xdelta_file = self.xdelta30_file
            self.patched_file = self.patched30_file_path
        elif int(self.frame_rate) == 1:
            self.xdelta_file = self.xdelta60_file
            self.patched_file = self.patched60_file_path

        self.xdelta_file_path = os.path.join(self.root_folder, "_XDELTA", self.xdelta_file)

    def print_logs(self, text, format=0):
        # format 0 = normal; 1 = red
        # I hope someone will make this better
        if format == 0:
            self.gui.logs_text.append(text)
            self.gui.update()
            
        elif format == 1:
            self.gui.logs_text.append("<div style=\"background-color: red; color:white\">{}</div>".format(text))
            self.gui.update()
        
        
    def _download_file(self, url, destination):
        self.gui.progress_bar.show()
        for progress in download_file(url, destination):
            if progress is not None:
                self.gui.progress_bar.setValue(progress)
            else:
                print("Download failed or interrupted")
        self.gui.progress_bar.hide()

    def _patch_game(self):
        try:
            patch_game(self.xdelta_file_path, self.patched_file, self.rom_file_path, self.root_folder)
            self.print_logs("Game patched successfully")
        except Exception as e:
            self.print_logs("Error patching the game", 1)
            self.print_logs(str(e), 1)
    
    def download_and_extract_zip(self, url, extract_to, new_file_name):
        temp_zip_path = "temp.zip"
        self._download_file(url, temp_zip_path)
    
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall("temp_folder")
    
        for root, dirs, files in os.walk("temp_folder"):
            for file in files:
                if file.endswith(".exe"):
                    source_file_path = os.path.join(root, file)
                    destination_file_path = os.path.join(extract_to, new_file_name)
                    shutil.move(source_file_path, destination_file_path)
    
        os.remove(temp_zip_path)
        shutil.rmtree("temp_folder")

    def download_updated_files(self, version):
        self.print_logs("Downloading updated files...")
        self.print_logs("Downloading ctr-u_Online30.xdelta")
        self._download_file(URL_XDELTA_30, "_XDELTA/ctr-u_Online30.xdelta")
        self.print_logs("Downloading ctr-u_Online60.xdelta")
        self._download_file(URL_XDELTA_60, "_XDELTA/ctr-u_Online60.xdelta")
        self.print_logs("Downloading client.exe")
        self.download_and_extract_zip(URL_CLIENT, "_CTRClient", "client.exe")

    def check_for_files(self):
        check = True
        if not os.path.exists(self.duckstation_path):
            self.print_logs("DuckStation not found. Check the path in settings...", 1)
            check = False
        if not os.path.exists(self.rom_file_path):
            self.print_logs("Game ROM not found. Check the path in settings...", 1)
            check = False
        return check

    def check_for_patch_files(self):
        check = True
        if not os.path.exists(self.xdelta_file_path) or not os.path.exists(self.client_path):
            check = False
        return check
        
    def launch_game(self):
        #Check for duckstation and ROM
        if not self.check_for_files():
            return
        
        self.print_logs("Checking for updates...")
        is_update, version = check_for_updates()
        self.print_logs(f"OnlineCTR version: {version}")
        if not self.check_for_patch_files() or is_update:
            self.download_updated_files(version)
            write_version_file(version)
            self._patch_game()
        else:
            self.print_logs("No updates found...")
            
        if not check_for_patched_game(self.patched_file):
            self.print_logs("Patched game not found...")
            self._patch_game()
        
        #Launch DuckStation
        self.print_logs("Launching DuckStation...")
        if not launch_duckstation(self.duckstation_path, self.patched_file, self.fast_boot, self.fullscreen):
            self.print_logs("Error launching DuckStation", 1)
            return
        
        #Launch CTRClient
        self.print_logs("Launching CTRClient...")
        threading.Thread(target=self.launch_game_thread).start()
    
    
    def launch_game_thread(self):
        try:
            os.environ['netname'] = self.name
    
            # 5 seconds delay before launching the client
            command1 = 'timeout /t 5 /nobreak > NUL'
            
            netname = os.environ['netname'].strip()
            command2 = 'echo ' + netname + ' | "' + self.client_path + '"'
            subprocess.call(command1, shell=True)
    
            process = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            while True:
                output = process.stdout.readline()
                if output:
                    output = output.decode('utf-8', errors='replace').strip()
                    # Trying to make the logs look better ¯\_(ツ)_/¯
                    output = re.sub(r'[^a-zA-Z0-9: "().@]', '', output)
                    
                    if output.strip() == 'Enter Server IPV4 Address:':
                        self.print_logs("Private lobbies are not supported", 1)
                        self.print_logs("Exiting in 5 seconds...")
                        time.sleep(5)
                        LauncherGUI.kill_process(self)
                        break
                        
                    elif output.strip() != '':
                        self.gui.logs_text.append(output)
        except Exception as e:
            self.print_logs("Error launching CTRClient")
            self.print_logs(str(e))
