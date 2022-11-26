# Audiobook_NFO
Create NFO file for audiobooks

CUE_TXT_JPG_FILES.EXE

This program will produce .cue, .jpg and .txt (info) files for any selected .m4b audiobook files. You can select one, or more, files in the dialog box. Press the "Cancel" button to exit the program.

Existing files are renamed .old

===============================================================================

SPLIT_AUDIOBOOK.EXE

Note. All user options are specified in the file VARIABLES.TXT (see below for details)

This file will split an m4b audiobook file into smaller files by either a specified number of minutes or by chapter. Output files can be in m4a or mp3 format.

After a file is selected in the dialog box, it is checked for periods of silence that are at least as long as specified in the user options. Then the nearest silence points to the selected minutes are used to break the audiobook into smaller audio files. It is also possible to break by the chapters defined in the m4b file.

A window will open to advise that the silence detection is in progress and will take some time. No user input is required and this is just a reminder that the program is still running.

While the output files are being created, another window will open showing the files being written to disk. This is for user feedback to show what is happening.

Note. m4a files are effectively copied so this transformation is faster than mp3 which requires transcoding. In all cases, the original m4b file is untouched.

If a silence log is required, update the user options. This program will then generate a text log file with details of all silence intervals detected by FFMPEG. It also adds the actual split points at the end of the log file so these can be checked.

Check the <filename>.log file for each selected m4b file to see if any silence points are detected. If no silence points are detected, adjust the user options and re-run the program until split points are detected correctly.

A good starting point for splitting a typical audiobook:
-30dB to identify silence
1.0 seconds for length of silence

Once the split points are calculated, writing to m4a files is relatively quick.
e.g. 2h35m audiobook in 15 seconds; 24h32m audiobook in 2m46s

===============================================================================

VARIABLES.TXT

This file is where file locations and user options are stored. Each option is described and a suitable default is included for most options. However, file locations and start up directory will need to be updated for each installation.

User options available include:

* Location (on your system) of the following executable files:
  ffmpeg.exe, ffprobe.exe, exiftool.exe

* defaultdir - starting directory for file selection
* minutes - split into files that are "minutes" long (e.g. 10 minutes long)
* db - silence threshold in dB (e.g. below -30dB is considered silence)
* silencelength - minimum silence length in seconds (e.g. 1.0 seconds)
* ext - file extension for output ("m4a" or "mp3")
* splitby - split by minutes OR chapters
* split - split the audiobook OR generate a silence log

===============================================================================

Notepad++ tip: Find all non-ASCII characters

1. Ctrl-F
2. Search for: [^\x00-\x7F]+
3. Select search mode as 'Regular expression'

===============================================================================

Last updated: 11 Oct 2022
