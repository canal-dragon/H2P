#!/usr/bin/env python
"""
Class to contain a hymn
Class to contain the whole hymn book once compiled from all available hymns.

Part of H2P source code
CJCJ 06/12/2025
"""
import H2P_cfg as cfg

class HYMN():
    """
    Store a hymn as
    verse[] # list of verses, each verse is a list of verseLine strings
    chorus  # only one allowed per hymn
    sourceBook # eg STF, MP, Other
    hymnNumber
    firstLine
    """
    
    def __init__(self, filename, hBlog): # filename here is the one from the running subdirectory, i.e. from ./H2P/ 

        # first read the hymn from its text file
        tag, bookCode, hymnNumber = self.makeTag(filename, hBlog)
        success = True
        
        if hymnNumber == 0:
            hBlog.write("** Problem with file: " + stemname + ". There should not be a file for hymn number 0.<br/>\n")
            success = False
        else:
            [success, verse, chorus, attribution, rCode, firstLine, longestLine, \
            mostLines, hasChorus, bookVerseNumber, chorusFirst] = self.readhymn(filename, hBlog)
        
        self.verse = verse # is a list of verses, each one being a list of lines
        self.chorus = chorus
        self.hasChorus = hasChorus
        self.chorusFirst = chorusFirst
        self.longestLine = longestLine
        self.mostLines = mostLines
        self.attribution = attribution
        self.rCode = rCode
        self.firstLine = firstLine
        self.tag = tag
        self.bookCode = bookCode
        self.hymnNumber = hymnNumber
        self.bookVerseNumber = bookVerseNumber
        self.topBookVerseNumber = 0
        if bool(self.bookVerseNumber): # forced numbering (assume ascending order)
            topKey = max(self.bookVerseNumber, key = self.bookVerseNumber.get)
            self.topBookVerseNumber = int(''.join(char for char in self.bookVerseNumber[topKey] if char.isdigit()))
        else: 
            self.topBookVerseNumber = len(self.verse)

        return 


    def __str__(self):
        """
        When hymn object is printed ..
        """

        return self.tag + ":  " + self.firstLine +" : " + str(self.topBookVerseNumber) + " verses, |Lines|  = " + str(self.mostLines) + " |characters| = " + str(self.longestLine)

    def readhymn(self, filen, hBlog):
        """
        Read a file containing the wqords of a hymn into a Hymn object.
        filen is either a string containing a path/filename or a posixPath object.
        
        """

        import os
        import re # regex methods

        ABS_MAX_CHARS = 62
        ABS_MAX_LINES = 12
    
        stemname = os.path.split(filen)[-1]

        success = True
        with open(filen, "r",encoding="utf-8") as file:
            data = file.read()
        vStartIndex = [i for i, c in enumerate(data) if c == '{'] # verses
        vEndIndex = [i for i, c in enumerate(data) if c == '}']
        cStartIndex = [i for i, c in enumerate(data) if c == chr(92)] # chorus \o/
        cEndIndex = [i for i, c in enumerate(data) if c == chr(47)]
        aStartIndex = [i for i, c in enumerate(data) if c == '['] # attribution
        aEndIndex = [i for i, c in enumerate(data) if c == ']']
        rStartIndex = [i for i, c in enumerate(data) if c == '<'] # rights code
        rEndIndex = [i for i, c in enumerate(data) if c == '>']

        # Check for errors in the hymn file that we can notice so far.
        # Just throw all errors out so that the user is forced to correct files.
        if len(vEndIndex) == 0 and len(vStartIndex) == 0 and len(cStartIndex) == 0 and len(cEndIndex) == 0:
            hBlog.write("** Problem with file: " + stemname + ". There are no verses or even a chorus.<br/>\n")
            success = False 
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]
            
        if len(vEndIndex) <  len(vStartIndex):
            hBlog.write("** Problem with file: " + stemname + ". More starts of verses '{' are found than ends of verses '}'.<br/>\n")
            success = False 
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]
        elif len(vEndIndex) >  len(vStartIndex):
            hBlog.write("** Problem with file: " + stemname + " More ends of verses '{' are found than ends of verses '}'.<br/>\n")
            success = False 
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]
        if len(cStartIndex) > 1: # could be 0 choruses, but no more than 1
            hBlog.write("** Problem with file: " + stemname + ". More than 1 start of chorus (backward slash) is found.<br/>\n")
            success = False
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]
        if len(cEndIndex) > 1:
            hBlog.write("** Problem with file: " + stemname + ". More than 1 end of chorus (forward slash) is found.<br/>\n")
            success = False 
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]
        if len(cEndIndex) != len(cStartIndex):
            hBlog.write("** Problem with file: " + stemname + ". Chorus brackets (backwards and forwards slash) not balanced.<br/>\n")
            success = False 
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]
        if len(aStartIndex) > 1: # allow no rights code, but not more than 1
            hBlog.write("** Problem with file: " + stemname + ". More than 1 start of attribution '[' is found.<br/>\n")
            success = False 
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]
        if len(aEndIndex) > 1:
            hBlog.write("** Problem with file: " + stemname + ". More than 1 end of attribution ']' is found.<br/>\n")
            success = False 
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]
        if len(aEndIndex) != len(aStartIndex):
            hBlog.write("** Problem with file: " + stemname + ". Attribution brackets not balanced.<br/>\n")
            success = False 
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]
        if len(rStartIndex) > 1: # allow no rights code, but not more than 1
            hBlog.write("** Problem with file: " + stemname + ". More than 1 start of rights code '<' is found.<br/>\n")
            success = False 
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]
        if len(rEndIndex) > 1:
            hBlog.write("** Problem with file: " + stemname + ". More than 1 end of rights code '>' is found.<br/>\n")
            success = False 
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]

        # read verses
        verse = []
        longestLine = 0
        mostLines = 0
        bookVerseNumber = {}
        
        for iverse in range(0,len(vStartIndex)):
            verse_strings = []
            for string in data[vStartIndex[iverse]+1:vEndIndex[iverse]].splitlines():
                string = string.strip()
                verse_strings.append(string)
            while '' in verse_strings: # need to remove all empty lines
                verse_strings.remove('')
            
            longest = []
            for s in verse_strings:
                longest.append(len(s))
            mostLines = max(mostLines, len(longest))
            longestLine = max(longestLine, max(longest))
            verse.append(verse_strings)

            # look for option bookVerseNumbers
            # between the verse demilimiters.
            
            if iverse == 0:
                iStart = 0
                iEnd = vStartIndex[0]
            else:
                iStart = vEndIndex[iverse-1]+1
                iEnd = vStartIndex[iverse]
            nstr = data[iStart: iEnd].strip()
            isChorus = False
            if nstr.find('c') > 0:
                isChorus = True
                nstr.replace('c', '')
            nstr = ''.join(char for char in nstr if char.isdigit()) # extracts only digits
            if bool(nstr):
                if int(nstr) == 0: # no numbering
                    set_str = ''
                else:
                    set_str = ' v ' + nstr.strip()
                if isChorus:
                    set_str = set_str + ' c'
                bookVerseNumber.update({iverse: set_str})
                
            # leave bookVerseNumber epmty if no numbers found, but allow
            # some numbers between }{ to be missing.
           
        # read chorus

        chorusFirst = False
        if len(cStartIndex) == 1: # there is a chorus
            hasChorus = True
            if cEndIndex[0] < vStartIndex[0]: # chorus is stated before any of the verses
                chorusFirst = True
            chorus_strings = []
            for string in data[cStartIndex[0]+1:cEndIndex[0]].splitlines():
                string.strip()
                chorus_strings.append(string)
            if '' in chorus_strings:
                chorus_strings.remove('')
            
            longest = []
            for s in chorus_strings:
                longest.append(len(s))
            mostLines = max(mostLines, len(longest))
            longestLine = max(longestLine, max(longest))
            chorus = chorus_strings
        else:
            chorus = ""
            hasChorus = False
            
        if chorusFirst:
            firstLine = chorus[0]
        else:
            firstLine = verse[0][0]
            
        if firstLine[0] == "#": # just to tidy up presentation of firstLine
            firstLine = firstLine.replace("#", "") 
        if firstLine[0] == '~': 
            firstLine = firstLine.replace("~", "") 
        if firstLine[0] == '*': 
            firstLine = firstLine.replace("*", "") 
        if firstLine[0] == '$':
            firstLine = firstLine.replace("$", "")

           
        # read attribution
        if len(aStartIndex) == 1:
            attribution = data[aStartIndex[0]+1:aEndIndex[0]]
        else:
            attribution = ""

        # read rights code
        if len(rStartIndex) == 1:
            rCode = data[rStartIndex[0]+1:rEndIndex[0]]
        else:
            rCode =""

        # check if a verse might be too big
        if mostLines >= ABS_MAX_LINES:
            hBlog.write("** Problem with file: " + stemname + ". More than " + str(ABS_MAX_LINES) + " lines found in a verse.<br/>\n")
            success = False
        if longestLine >= ABS_MAX_CHARS:
            hBlog.write("** Problem with file: " + stemname + ". More than " + str(ABS_MAX_CHARS) + " characters found ina line.<br/>\n")
            success = False
        if success:
            return [success, verse, chorus, attribution, rCode, firstLine, longestLine, mostLines, hasChorus, bookVerseNumber, chorusFirst]
        else:
            print("*** Failure to read hymn file: ", filen)
            return [success, [], [], "bad hymn file", "bad hymn file", "bad hymn file", 0, 0, False, {}, False]
      
         # end of readhymn

    def makeTag(self, filename, hBlog):
        """
        Make a tag from the filename to be used as the key in a dict structure for the hymnbook.
        We expect files to have names like  ./hymns/.. path ../STF_010.txt
        """
        from pathlib import Path

        success = True

        # lop off the stem of the filename from the path
        
        basename = Path(filename).name.split('.')[0] # this still includes the filename extension
        tag = basename.upper()

        x = []
        if tag.find('_') > 0:
            x=tag.split('_', 1)
        elif tag.find('-') > 0:
            x=tag.split('-', 1)
        else:
            print("*** txt file found that is not named correctly for a hymn file: ",filename)
            hBlog.write("File name: " + filename + " filename not correctly formed.<br/>\n")
            success = False
        if len(x) < 2:
            print("*** txt file found that is not named correctly for a hymn file: ",filename)
            hBlog.write("File name: " + filename + " filename not correctly formed.<br/>\n")
            success = False

        if success:    
            bookCode = x[0].upper()
            bookCode.strip()
            hymnNumber = int(x[1])
            
            if not isinstance(hymnNumber, int):
                print("*** File name: " + filename + " does not have a hymn number\n.")
                print("*** txt file found that is not named correctly for a hymn file: ",filename)
                hBlog.write("File name: " + filename + " filename not correctly formed.<br/>\n")
                success = False

        if success:
            tag, book, number  = cfg.make_tag_from_num(bookCode,hymnNumber)
        else:
            tag = "XXX 0"
            bookCode = "XXX"
            hymnNumber = -1
        
        return tag, bookCode, hymnNumber
        
        

    
