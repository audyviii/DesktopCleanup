import os
import sys
import time
import shutil
from collections import Counter
import tkinter as tk
from tkinter import ttk

# Windows DPI adjustment for GUI 
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

FULL_PATH_TO_DESIGNATED_FOLDER = 'You put full path of folder you want to file(s) to.'

                  # Word Processing
file_extensions = {'.txt' : 'FULL_PATH_TO_DESIGNATED_FOLDER',
                   '.doc' : 'FULL_PATH_TO_DESIGNATED_FOLDER',
                  # Image Formats
                   '.jpg' : 'FULL_PATH_TO_DESIGNATED_FOLDER',
                   '.png' : 'FULL_PATH_TO_DESIGNATED_FOLDER',
                   }

def scan_files(main_dir):
        global files, extensions, full_file_names
        files = os.listdir(main_dir) 
        if 'desktop.ini' in files: 
                files.remove('desktop.ini')  # Prevents .ini file deletion
        elif 'downloads.ini' in files:
                files.remove('downloads.ini') # Prevents .ini file deletion
        else:
                pass
        extensions = [] 
        full_file_names = []
        file_count = 0 
        for file in files:
                full_file_names.append(f"{main_dir}\{file}")
                extensions.append(os.path.splitext(files[file_count])[1]) 
                file_count += 1

def organize_files():
        global extension_List, duplicates_list, dest_folder
        duplicates_list = dict(enumerate(extensions)) 
        extension_List = [] 
        dest_folder = []
        for keys in duplicates_list:
                extension_List.append(keys)
                for v in extension_List:
                        a = file_extensions.get(v)
                        dest_folder.append(a)
        def file_handle():                
                for k in full_file_names: 
                        criteria = os.path.splitext(k)[1] # takes item in list, stores variable with extension split from full path name
                        try:
                                if criteria in file_extensions:
                                        path_to = file_extensions.get(criteria) 
                                        shutil.move(k, path_to) # moves file to location based on 'criteria' (criteria = extension keys in dictionary)
                        except shutil.Error:
                                shutil.move(k, "PATH_TO_DUPLICATES FOLDER")
                        except FileNotFoundError:
                                print('You need to add this extension pre-defined dictionary structure. \n')
                                print(criteria)

        file_handle()


def clean_downloads():
        scan_files('C:\\Users\\User\\Type_USER_Here\\Admin\\Downloads\\')
        organize_files()
        root.destroy()


def clean_desktop():
        scan_files('C:\\Users\\Type_USER_Here\\Admin\\Desktop\\')
        organize_files()
        root.destroy()


root = tk.Tk()
root.resizable(False, False)
root.columnconfigure(0, weight=1)

main = ttk.Frame(root, padding=(30, 15))
main.grid()

downloads = ttk.Button(main, text='Downloads', command=clean_downloads)
downloads.grid(column=1, row=2, sticky="EW", padx=5, pady=5)

desktop = ttk.Button(main, text="Desktop", command=clean_desktop)
desktop.grid(column=0, row=1, columnspan=2, sticky="EW", padx=5, pady=5)

root.mainloop()
