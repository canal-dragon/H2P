# H2P
Ceate a pptx presentation file of hymns for presentation at a church service

H2p is written in Python 3. It uses the python-pptx module from Github and pyside6. 

Important files required by H2P are kept in the H2P-private-data subdirectory.
A pdf file H2P-help-Text.pdf contains more information about the program.
H2P uses 4 base pptx files, kept in the provate data directory, to modify by 
injecting the requred hymns.

The hymns are stored as text files in the 'hymns' subdirectory.
There is some very simple mark up in the text files to format how the hymn will appear 
on the slides of the presentation.
I have the whole of the British Methodist Hymn book in my hymns directory but 
for Git-hub, for copyright compliance, I have just given three out-of-copyright hymns 
as examples. 

H2P uses two alternative fonts, one sans serif, the other serif. These should be 
installed both on the computer on which the presentation is prepared and on the one from 
which it is projected. The fonts are both licenced under the SIL open font licence.
The font files are in this repository for convenience. In addtion there is a copy
of the Andika regualr sans serif font in the private data directory that is used for the interface.

File in the H2P-private-data directory should not be altered or deleted. H2P needs to access them.

Copyright exists on written works from the time of authorship to 70 years
after the authors death. Churches using H2P should own hymn books with the hymns 
they are using along with a CCLI Licence that extends the right to project copyrighted 
hymns for the purpose of a church service. 

The CCLI licence number is managed inside H2P and shown along with the author attribution
at the bottom of copyrighted hymns. 

There are 3 simple steps (1) Choose up to 7 hymns in the main panel,
(2) Choose dark or light background, serif or sans serif.
(3) Press 'make presentation' .. and a file called hymn-words.pptx will appear on the 
desktop. 


