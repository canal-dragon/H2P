#!/usr/bin/env python3

#
#  H2P_main.py
#  
#  Copyright 2025 Chris <chris@chris-desktop>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# This version 13/03/2026

import sys
import os
from pathlib import Path
import pickle

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMessageBox,
    QApplication)

from H2P_panel import MainWindow

import H2P_Classes # from local source file

import H2P_cfg as cfg

def show_summary(title, parent, message):
    """
    Show summary from reading hymn files
    """
    dlg = QMessageBox(parent)
    dlg.setWindowTitle(title)
    dlg.setFont(QFont(cfg.families[0],14))
    dlg.setText(message)
    button = dlg.exec()
    return


def find_first_subdirectory(target_name: str) -> Path | None:
    """
    Gemini generated function
    Path module must be imported in domain above this def.
    i.e. from pathlib import Path
    
    Searches the user's home directory for the first sub-directory matching target_name.
    
    - Excludes iCloud and OneDrive directories.
    - Does not follow symbolic links.
    
    Returns:
        Path: A PosixPath object of the found directory, or None if not found.
    """
    home = Path.home()
    
    # Define directories to skip (case-insensitive check handled below)
    skip_dirs = {"iclouddrive", "onedrive"}
    
    # rglob("*") yields all files and directories recursively
    for path in home.rglob("*"):
        # Skip symbolic links immediately to avoid infinite loops or lifting restrictions
        if path.is_symlink():
            continue
            
        # Check if the path is a directory and matches our target name
        if path.is_dir() and path.name == target_name:
            
            # Check the parts of the path to see if it lives inside iCloud or OneDrive
            # path.parts breaks the path into a tuple (e.g., ('/', 'Users', 'username', 'OneDrive', 'Documents'))
            path_parts_lower = [part.lower() for part in path.parts]
            
            if any(skip in path_parts_lower for skip in skip_dirs):
                continue  # Skip it if it's inside an ignored cloud directory
                
            return path  # Return the first match found as a PosixPath object
            
    return None

# Example Usage of the above routine:
# result = find_first_subdirectory("ProjectX")
# if result:
#     print(f"Found it at: {result}")
# else:
#     print("Directory not found.")



def main(args):

    # Start App interface starts here

    app = QApplication(sys.argv)
    panel = MainWindow()
    schemeStr = str(app.styleHints().colorScheme())
    if "Light" in schemeStr:
        cfg.colStr = "color: maroon"
    elif "Dark" in schemeStr:
        cfg.colStr = "color: gold"
    else:
        print("Colour scheme not determined to be Light or Dark.")


    # set useful directories -
    # When compiled with pyinstaller, finding the intended working directory,
    # (wehre H2P is launched from) may be a bit of a game.

    if Path(Path.cwd(), "H2P-private-data").is_dir(): # The simple case in which Path.cwd() works
        cfg.pwd = Path.cwd().resolve() # abs path, works in Windows but not in pyinstaller-compiled case for macos or linux
    else: # for compiled cases on linux or macos
        if Path(Path.home(),".h2p.dat").exists(): # path has been saved before
            f = open(Path(Path.home(),".h2p.dat"),"rt")
            firstLine = f.readline()
            print("Read saved directory as >"+firstLine.strip())
            cfg.pwd = Path(firstLine.strip()) # only take first line.
            f.close()
        else: # go looking for it
            message = "Looking for H2P-private-data directory.\nThis may take some time.\n"
            message = message +"We only have to do this once.\n"
            message = message + "Starting search from \n" + str(Path.home())
            show_summary("H2P finding data directory", panel, message)
            possibleLocation = find_first_subdirectory("H2P-private-data") 
            if  possibleLocation:
                fsave = open(Path(Path.home(),".h2p.dat"),"wt")
                fsave.write(str(possibleLocation.parent)+"\n")
                fsave.close()
            else:
                print("***ERROR could not find H2P's home diectory - please provide in user's home/.h2p.dat")
                return -1
            cfg.pwd = Path(possibleLocation.parent)
            show_summary("Found H2P's directory", panel, "Found cwr as " + str(cfg.pwd))

    cfg.desktop = cfg.get_desktop_path() # for output
    
    # retreive persistent settings from two files in private data
    
    cfg.black_between, cfg.ccliNumber, cfg.CCLIList, cfg.desktop = cfg.retrieveSettings() 

    # read hymnbook.pickled or load AAA_NNN.txt files otherwise
    # needs app to have been started to post message box

    if Path(cfg.pwd, 'H2P-private-data').is_dir(): 
        picklePath = Path(cfg.pwd,'H2P-private-data', 'hymnbook.pickled')
        if picklePath.is_file():
            dbfile = open(picklePath, 'rb')
            db = pickle.load(dbfile)
            cfg.hymnBook = db[0]
            cfg.bookCodeList = db[1]
            message = db[2]
            message = "Using previously saved hymnbook.\n\n" + message
            message = message + "\n\nThe CCLI number is currently set to \n" + cfg.CCLIList[0] + "."
            dbfile.close()
        else: # compile a new pickled hymn book
            cfg.hymnBook, cfg.bookCodeList, message = cfg.load_hymns()
    else:
        message = "There is no subdirectory\n"
        message = message + "H2P-private-data.\n"
        message = message + "H2P-private-data must be present\n"
        message = message + "and contain certain files,\n"
        message = message + "otherwise H2P cannot run.\n"
        message = message + "Please see H2P-help-text.pdf\n" 
        message = message + str(cfg.pwd) +"\n"
        message = message + str(Path.home()) +"\n"
    panel = MainWindow()
    panel.show()
    show_summary("H2P starting", panel, message)
    
    app.exec() # start the event loop

    # sys.exit(app.exec()) # this should be the last line of the code before the return 0
    
    return 0

if __name__ == '__main__':

    sys.exit(main(sys.argv[1:]))

