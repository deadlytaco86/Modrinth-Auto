from bs4 import BeautifulSoup
import customtkinter as ctk
import threading
import requests
import queue
import time
import json
import sys
import os

#################################
##### define and set things #####
#################################

# Set the working directory to the script's directory. I think its needed for compiling.
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

VERSION = '1.2.0'
ctk.set_appearance_mode("dark")
checkboxes = []
links = []
mod_names = []

###################################
##### define helper functions #####
###################################

def save(dict, name):
    json_object = json.dumps(dict, indent=4)
    with open(name, 'w') as writer:
        writer.write(json_object)

def on_load():
    savepath = f'{os.path.expanduser("~")}\\Documents\\Modrinth Auto\\'
    if not os.path.isdir(savepath):
        os.mkdir(f'{savepath}')
    if not os.path.isfile(f'{savepath}savefile.json'):
        save({'default mods':[]},f'{savepath}savefile.json')

def load_links() -> list[str]:
    links_path = os.path.join(base_path, 'base_links.json')
    with open(links_path, 'r') as f:
        link_dict = json.load(f)
        return link_dict["links"]

def just_mod_names(links: list[str]) -> list[str]:
    names_list = [name.split('/')[4] for name in links]
    return names_list

def get_download_links(url: str) -> list[str]:
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        all_download_buttons = soup.find_all('a', {'aria-label':'Download'})
        return [button['href'] for button in all_download_buttons]
    else:
        return []
    
links = load_links()
mod_names = just_mod_names(links)

def download_mod(mod_to_download, filter_extension, out_dir, q):
    mod_download_links = get_download_links(f'{mod_to_download}{filter_extension}')
    if len(mod_download_links) == 0:
        q.put(f'-> no valid version exists for {mod_to_download.split("/")[4]}')
    else:
        mod = mod_download_links[0]
        response = requests.get(mod)
        if response.status_code == 200:
            with open(f'{out_dir}{mod.split("/")[-1]}', 'wb') as f:
                f.write(response.content)
            q.put(f'-> downloaded {mod_to_download.split("/")[4]}')
        else:
            q.put(f'-> Failed to download {mod_to_download.split("/")[4]}')
    
###################################
##### define button functions #####
###################################

def read_checkboxes():
    button1.configure(state='disabled')
    button2.configure(state='disabled')
    checked_options = [i for i, checkbox in enumerate(checkboxes) if checkbox.get()]
    mods_to_download = [link for i, link in enumerate(links) if i in checked_options]
    total_mods = len(mods_to_download)

    savepath = f'{os.path.expanduser("~")}\\Documents\\Modrinth Auto\\'
    checked_mods_for_save = [mod for i, mod in enumerate(mod_names) if i in checked_options]
    save({'default mods':checked_mods_for_save},f'{savepath}savefile.json')

    v = version_entry.get()
    p = platform_entry.get()

    if v == '':
        print('please specify a version number')
        button1.configure(state='normal')
        button2.configure(state='normal')
        return
    if len(mods_to_download) == 0:
        print('you have not selected any mods for download')
        button1.configure(state='normal')
        button2.configure(state='normal')
        return
    filter_extension = f'?g={v}&l={p}'

    out_dir = output_entry.get()
    if not out_dir.endswith('\\'):
        out_dir = out_dir + '\\'
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    q = queue.Queue()
    threads = []
    counter = 0

    for mod_to_download in mods_to_download:
        # Start each download in a separate thread
        t = threading.Thread(target=download_mod, args=(mod_to_download, filter_extension, out_dir, q))
        threads.append(t)
        t.start()
        t.join()
        counter += 1

        while not q.empty():
            print(q.get())

        if counter != total_mods:
            for i in range(10):
                time.sleep(0.5)
                root.update_idletasks()
                root.update()

    print('-> downloads complete!')
    button1.configure(state='normal')
    button2.configure(state='normal')
    
def load_previous():
    savepath = f'{os.path.expanduser("~")}\\Documents\\Modrinth Auto\\'
    with open(f'{savepath}savefile.json') as f:
        previously_checked = json.load(f)['default mods']
    mods_in_order = [mod for i, mod in enumerate(mod_names)]
    for i, checkbox in enumerate(checkboxes):
        if mods_in_order[i] in previously_checked:
            checkbox.select()
        else:
            checkbox.deselect()

def close_program():
    sys.exit()

################################
##### create the UI window #####
################################

# Create the main application window
root = ctk.CTk()
root.geometry("400x720")
root.title(f"Modrinth Auto v{VERSION}")
root.resizable(False, False)


# create large font for labels
title_font = ctk.CTkFont('',24)

# create scrollable frame label
mod_label = ctk.CTkLabel(root, text="default mods:", font=title_font)
mod_label.grid(row=0, column=0, padx=10, pady=0, sticky='nw')

# Create a scrollable frame
scrollable_frame = ctk.CTkScrollableFrame(root, width=380, height=150)
scrollable_frame.columnconfigure(0, weight=9, minsize=360)
scrollable_frame.columnconfigure(1, weight=1)
scrollable_frame.grid(row=1, column=0, padx=10, pady=2, sticky="new")

# Populate the scrollable frame with widgets
for i in range(len(mod_names)):  # Adjust the range for more or fewer items
    label = ctk.CTkLabel(scrollable_frame, text=mod_names[i])
    label.grid(row=i, column=0, padx=5, pady=2, sticky="w")

    checkbox = ctk.CTkCheckBox(scrollable_frame, text='')
    checkbox.grid(row=i, column=1, padx=5, pady=2, sticky="e")
    checkboxes.append(checkbox)

# create output directory entry
text_frame = ctk.CTkFrame(root, width=380, height=200)
text_frame.columnconfigure(0, weight=1)
text_frame.columnconfigure(1, weight=5)
text_frame.grid(row=2, column=0, padx=10, pady=5, sticky='new')

version_label = ctk.CTkLabel(text_frame, text="Game Version: ")
version_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
version_entry = ctk.CTkEntry(text_frame)
version_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

version_label = ctk.CTkLabel(text_frame, text="Platform: ")
version_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
platform_entry = ctk.CTkComboBox(text_frame, values=['fabric', 'forge', 'neoforge', 'quilt'])
platform_entry.grid(row=1, column=1, padx=5,pady=5, sticky="ew")

output_label = ctk.CTkLabel(text_frame, text="Output Folder: ")
output_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
output_entry = ctk.CTkEntry(text_frame)
output_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
output_entry.insert(0, f'C:\\Desktop\\mods\\')

button1 = ctk.CTkButton(root, text="Download Checked Mods", command=read_checkboxes)
button1.grid(row=3, column=0, padx=80, pady=(15,5), sticky="ew")
button2 = ctk.CTkButton(root, text="Load Previous Options", command=load_previous)
button2.grid(row=4, column=0, padx=80, pady=5, sticky="ew")

console = ctk.CTkTextbox(root, width=380, height=180)
console.grid(row=5, column=0, padx=10, pady=(20,5), sticky="ew")
console.configure(state="disabled")

button3 = ctk.CTkButton(root, text="Close Program", fg_color="red",hover_color="#cc0000", command = close_program)
button3.grid(row=6, column=0, padx=80, pady=(20,5), sticky="ew")

# Ensure the main window expands to fill the space, but only in width in order to look nice
root.columnconfigure(0, weight=1)

class TextRedirector:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, text):
        self.textbox.configure(state="normal")  # Enable text box for writing
        self.textbox.insert("end", text)
        self.textbox.yview("end")  # Scroll to the end to keep the latest output visible
        self.textbox.configure(state="disabled")  # Disable text box after writing
        self.textbox.update_idletasks()  # Force UI update for immediate rendering

    def flush(self):
        self.textbox.update_idletasks()

sys.stdout = TextRedirector(console)

#################################
##### Start the application #####
#################################

if __name__ == "__main__":
    try:
        on_load()
        root.mainloop()
    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(str(e))


# seems like a good resource for customtkinter: https://www.youtube.com/@freepythoncode/videos

# pyinstaller "Modrinth Auto.spec"
# pyinstaller Modrinth_Auto_1.0.0.py --onefile --name "Modrinth Auto" --hidden-import=bs4 --hidden-import=customtkinter --hidden-import=requests --hidden-import=time --hidden-import=json --hidden-import=sys --add-data="c:/Desktop/Modrinth Auto/base_links.json":.
# https://drive.google.com/drive/folders/1t1P_gaPoAfe1jQdN0OYJotwfsnxcrJpo?usp=sharing
