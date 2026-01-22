"""
H2P component

Module to help cart 'global' variables about

CJCJ 30/11/2025
"""

import sys
import os
from pathlib import Path


import H2P_Classes # from local source file

# Variable declared here become global variables
# anywhere this file is imported

vers = "Jan 2026"

# settings

darkOrLight = 1 # default dark theme with white text
black_between = True
hymnBook = {}
families = '' # for fonts
fontName = 'Source Serif Pro' # or fontName = 'Andika' for san serif
CCLIList = ['Hollingworth MC 610406', 'Add a new church name and CCLI No. here.']
ccliNumber = '0'

desktop = "Not set yet"

# initialise list of differnt book codes found
bookCodeList = []
bookCodeChoice = "XXX" # for make index menu item

# the following list have to be initialised with len() = 7
# because they relate to the 7 hymns it is possible to set

tagList = ['STF 0', 'STF 0', 'STF 0', 'STF 0', 'STF 0', 'STF 0', 'STF 0'] # tags inserted into this list by UpdateBook and UpdateNumber callbacks.
hymnNumbers = [0,0,0,0,0,0,0]
hymnBCode = ["STF", "STF", "STF", "STF", "STF", "STF", "STF"] # to be updated with first in the hymnBookCode list before presenting interface.

def make_tag_from_num(book, num):
    """Make the tag which becomes the key to the hymn in the hymnBook dict.
    """
    book = book.strip().upper()
    tag = book + " " + str(int(num))
    return tag, book, num


def get_num_from_tag(tag):

    if len(tag.strip()) > 0: # check is a valid tag (only slightly)
        i = tag.find(' ')
        book = tag[0: i]
        num_str = tag[i+1: len(tag)]
        num = int(num_str)
    return [num, book]
    

def get_desktop_path():
    home_dir = Path.home()
    os_name = sys.platform
 
    if os_name == "win32": # returns this even when is 64 bit
        # Looking up in windows registry caters for the (unusual?) case where the user has moved their Deskop directory.
        import winreg # Odd here but only runs on a Windows system
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
                0,
                winreg.KEY_READ
            )
            desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
            winreg.CloseKey(key)
            return Path(desktop_path)
        except (FileNotFoundError, OSError):
            return home_dir / "Desktop"  # Path concatenation with /
    
    elif os_name == "darwin":
        return home_dir / "Desktop"
    
    elif os_name.startswith("linux"):
        xdg_desktop = os.environ.get("XDG_DESKTOP_DIR")
        if xdg_desktop:
            return Path(xdg_desktop).expanduser()
        return home_dir / "Desktop"
    
    else:
        raise NotImplementedError(f"Unsupported OS: {os_name}")

def load_hymns():
    """
    1) Obtain list of all hymn-file names.
    ======================================
    
    Read them into HYMN objects to make dict cfg.hymnBook.
    """

    import pickle
    
    p = Path('.','hymns')
    
    filenameList = list(p.glob('**/*.txt'))
    stemnameList = filenameList.copy()
    # filenameList is a list of posixPath objects pointing to each of the hymn 'txt' files in the subdirectory tree.
    hBLog = open(Path(".","H2P-private-data","hymnBook_reading_log.html"),"wt")
    hBLog.write('<b>Log of reading hymn files</b><br/>\n')
    hBLog.write('=======================<br/>\n')
    hBLog.write(' <br/>\n')
    hBLog.write("Files are not read in hymn-number order - see index in file menu.<br>\n")
    hBLog.write(' <br/>\n')
    
    bookCodeDict= {}
    
    for i in range(0,len(filenameList)):
        # it is convenient to have paths as strings for the sake of reporting errors etc.
        stemnameList[i] = os.path.split(filenameList[i])[-1]
        filenameList[i] = str(filenameList[i])
        hymn = H2P_Classes.HYMN(filenameList[i], hBLog) # hymn is a HYMN object
        print(hymn)
        
        hBLog.write(("<pre>File: " + stemnameList[i]).ljust(25) + hymn.firstLine.ljust(54) + str(hymn.topBookVerseNumber).ljust(3) + "verses  " + str(hymn.longestLine).rjust(2) + "  " + str(hymn.mostLines).rjust(2) + "</pre>\n") # <br/> not needed
        if hymn.firstLine == "bad hymn file":
            print("Could not read hymn file : "+stemnameList[i]+" -- hymn not added to hymnbook. Please check the file.")
            hBLog.write("Could not read hymn file : "+stemnameList[i]+" -- hymn not added to hymnbook. Please check the file.<br/>\n")
            # print("If this message is always printed there is a error in the file reading routine, not in an occaisional file.")
        else:
            if hymn.tag in hymnBook:
                print("There is more than one file for: ", hymn.tag)
                hBLog.write("There is more than one file for: " + hymn.tag+ "<br/>/n")
            else:
                hymnBook.update({hymn.tag: hymn})
            if hymn.bookCode in bookCodeDict:
                freq = bookCodeDict.get(hymn.bookCode)
                bookCodeDict.update({hymn.bookCode: freq+1})
            else:
                bookCodeDict.update({hymn.bookCode: 1})

        bookCodeUsage = list(sorted(bookCodeDict.items(), key=lambda item: item[1]))
        bookCodeUsage.reverse()
        bookCodeList = []
        for i in range(0,len(bookCodeUsage)):
            bookCodeList.append(bookCodeUsage[i][0])
         
    hBLog.close() 
      
    message = "H2P has found "+str(len(filenameList))+" hymn files."
    message  = message + "\nThe hymnBook contains "+str(len(hymnBook))+" hymns."
    
    dudHymnFiles = len(filenameList) - len(hymnBook)
    if dudHymnFiles > 0:
        message = message + "\n\nThere are " + str(int(dudHymnFiles)) + " \nhymn files that were not read properly."
        message = message + "\nPlease see file menu, show log."

    # pickle a copy of the hymnbook
    db = [hymnBook, bookCodeList, message]
    picklePath = Path('H2P-private-data', 'hymnbook.pickled')
    dbfile = open(picklePath, 'wb')
    pickle.dump(db, dbfile)
    dbfile.close()

    return  hymnBook, bookCodeList, message

def retrieveSettings():

    # read CCLI number from file
    # The selection from this list will be handled by CCLIDialog in H2P_panel.py
    # On conclusion CCLIDialog should update this file.

    if Path('.', 'H2P-private-data', 'ccli_number.txt').exists():
        ccliFile = open(Path('.', 'H2P-private-data', 'ccli_number.txt'), 'r', encoding = 'utf-8')
        ccliData = ccliFile.read()
        ccliFile.close()
    else:
        ccliData = "Add a new church name and CCLI No. here."

    CCLIList = ccliData.splitlines()
    for i in range(0,len(CCLIList)):
        CCLIList[i] = CCLIList[i].strip()
    if '' in CCLIList:
        CCLIList.remove('')

    # set default CCLI number as first in the saved list - this for convenience as most users will revert to one church.
    ccliNumber = ''.join(char for char in CCLIList[0] if char.isdigit())
    if ccliNumber == '':
        ccliNumber = '0'
    if int(ccliNumber) == 0 :
        ccliNumber = '0'

    if Path('.', 'H2P-private-data', 'black_between.txt').exists():
        blackFile = open(Path('.', 'H2P-private-data', 'black_between.txt'),"r", encoding = 'utf-8')
        dividerData = blackFile.read()
        blackFile.close()
        
        if dividerData.find("Black") >= 0:
            black_between = True
        else:
            black_between = False
    else:
        black_between = False
       
    desktop = get_desktop_path() # to be passed on

    return black_between, ccliNumber, CCLIList, desktop


