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

# This version 06/12/2025 


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

def show_summary(parent, message):
    """
    Show summary from reading hymn files
    """
    dlg = QMessageBox(parent)
    dlg.setWindowTitle("H2P starting")
    dlg.setFont(QFont(cfg.families[0],14))
    dlg.setText(message)
    button = dlg.exec()
    return


def main(args):

    # retreive persistent settings from two files in private data
    
    cfg.black_between, cfg.ccliNumber, cfg.CCLIList, cfg.desktop = cfg.retrieveSettings() 

    # Start App interface starts here

    app = QApplication(sys.argv)
    
    # read hymnbook.pickled or load AAA_NNN.txt files otherwise
    # needs app to have been started to post message box
    
    picklePath = Path('H2P-private-data', 'hymnbook.pickled')
    if picklePath.exists():
        dbfile = open(picklePath, 'rb')
        db = pickle.load(dbfile)
        cfg.hymnBook = db[0]
        cfg.bookCodeList = db[1]
        message = db[2]
        message = "Using previously saved hymnbook.\n\n" + message
        message = message + "\n\nThe CCLI number is currently set to \n" + cfg.CCLIList[0] + "."
        dbfile.close()
    else:
        cfg.hymnBook, cfg.bookCodeList, message = cfg.load_hymns()

    panel = MainWindow()
    panel.show()
    show_summary(panel, message)
    
    app.exec() # start the event loop

    # sys.exit(app.exec()) # this should be the last line of the code before the return 0
    
    return 0

if __name__ == '__main__':

    sys.exit(main(sys.argv[1:]))

