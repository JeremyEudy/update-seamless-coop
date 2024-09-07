import tkinter as tk
from tkinter import filedialog,Toplevel
import requests
import configparser
import os
import win32com.client
import zipfile

# Constants
MOD_URL = "https://api.github.com/repos/LukeYui/EldenRingSeamlessCoopRelease/releases/latest"
DEFAULT_GAME_DIR = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\ELDEN RING\\Game"

def select_directory():
    # Opens a file dialog to select the game directory
    directory = filedialog.askdirectory()
    if directory:
        game_dir_entry.delete(0, tk.END)
        game_dir_entry.insert(0, directory)

def perform_update():
    # Fetches and updates the game mod from GitHub
    game_dir = game_dir_entry.get()
    config_path = f"{game_dir}\\SeamlessCoop\\ersc_settings.ini"
    old_config = configparser.ConfigParser()
    old_config.read(config_path)
    old_config_dict = {section: dict(old_config.items(section)) for section in old_config.sections()}

    try:
        response = requests.get(MOD_URL)
        response.raise_for_status()
        latest_release = response.json()
        zip_url = next((asset["browser_download_url"] for asset in latest_release["assets"] if asset["name"].endswith(".zip")), None)

        if zip_url:
            download = requests.get(zip_url)
            zip_file_path = f"{game_dir}\\SeamlessCoop.zip"
            with open(zip_file_path, "wb") as file:
                file.write(download.content)

            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(game_dir)

            new_config = configparser.ConfigParser()
            new_config.read(config_path)
            for section in new_config.sections():
                for key in new_config[section]:
                    if key in old_config_dict.get(section, {}):
                        new_config[section][key] = old_config_dict[section][key]

            with open(config_path, "w") as config_file:
                new_config.write(config_file)

        # After update, ask for creating a shortcut
        create_shortcut_dialog(game_dir)

    except Exception as e:
        print(f"Error: {e}")

def create_shortcut_dialog(game_dir):
    dialog = Toplevel(root)
    dialog.title("Create Shortcut?")
    dialog.geometry("800x150")
    tk.Label(dialog, text="Would you like to add a shortcut to the Smellingtons Thing launcher?").pack(pady=10)

    def on_yes():
        create_shortcut(game_dir)
        dialog.destroy()

    def on_no():
        dialog.destroy()

    # Buttons now stacked vertically
    yes_button = tk.Button(dialog, text="Yupperino and I'm super thankful lord shortcut maker.", command=on_yes)
    yes_button.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)  # Fill the X axis and provide padding

    no_button = tk.Button(dialog,
                          text="No I don't want your dumb shortcut, you dumb dumb potato dumb, why would even ask me that.",
                            command=on_no)
    no_button.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)  # Fill the X axis and provide padding

def create_shortcut(game_dir):
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    path = os.path.join(desktop, "Elden Ring SC Launcher.lnk")
    target = f"{game_dir}\\ersc_launcher.exe"

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = game_dir
    shortcut.IconLocation = target
    shortcut.save()

# Main window setup
root = tk.Tk()
root.title("Update Oldman Circle's Magical Seam")
root.geometry("650x400")  # Adjusted size to fit ASCII art and other elements comfortably

# ASCII Art display using a Label
ascii_art = """\
     (   (            )   (   (       )
     )\ ))\ )      ( /(   )\ ))\ ) ( /( (
 (  (()/(()/(  (   )\()) (()/(()/( )\()))\ )
 )\  /(_))(_)) )\ ((_)\   /(_))(_)|(_)\(()/
((_)(_))(_))_ ((_) _((_) (_))(_))  _((_)/(_))_
| __| |  |   \| __| \| | | _ \_ _|| \| (_)) __|
| _|| |__| |) | _|| .` | |   /| | | .` | | (_ |
|___|____|___/|___|_|\_| |_|_\___||_|\_|  \___|"""
ascii_art_label = tk.Label(root, text=ascii_art, justify=tk.LEFT, font=('Courier', 10), bg='SystemButtonFace')
ascii_art_label.pack()

# UI for game directory entry
tk.Label(root, text="Put your Elden Ring game folder here:").pack()
game_dir_frame = tk.Frame(root)
game_dir_frame.pack(fill=tk.X, padx=5)
game_dir_entry = tk.Entry(game_dir_frame, width=65)
game_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
game_dir_entry.insert(0, DEFAULT_GAME_DIR)

# Button with three dots for directory selection
browse_button = tk.Button(game_dir_frame, text="...", command=select_directory, width=3)
browse_button.pack(side=tk.LEFT, padx=(2, 0))

# Button for initiating update
update_button = tk.Button(root, text="Update", command=perform_update)
update_button.pack(side=tk.TOP, fill=tk.X, padx=50, pady=20)  # Centered and made larger with padding

# Start the GUI event loop
root.mainloop()