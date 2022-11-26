# Procedures/functions used by other Python files for M4B processing
# Built with Python 3.8.1
# -----------------------------------------------------------------------------
# module imports

import codecs
import datetime
import html
import json
import math
import os
import re
import shutil
import subprocess
import time

from pathlib import *
from tkinter import *
from tkinter import Tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter.filedialog import askopenfilenames


# -----------------------------------------------------------------------------
# global variables

helperProg = 'variables.txt'

# -----------------------------------------------------------------------------
# procedures and functions
# -----------------------------------------------------------------------------
# get external program details and variables from text file

def getFileVariable():

  fn = open(helperProg, 'r', encoding='utf8')

  fileVar = {}
  for var in fn:
    if var[:1] != '#' and var != '\n':
      pair = var.split('=')
      key = pair[0]
      value = pair[1].rstrip()
      fileVar[key] = value

  fn.close()

  return fileVar

# -----------------------------------------------------------------------------
#  does file exist? if yes, rename to .old. If .old already exists, delete it

def fileExists(fn):
  oldfn = str(fn.parents[0].joinpath(fn.stem + fn.suffix + '.old'))

  if os.path.exists(oldfn):
    os.remove(oldfn)
    
  if os.path.exists(fn):
    os.rename(fn, oldfn)

# -----------------------------------------------------------------------------
# does directory exists? if yes, rename to .old. If .old already exists, delete it

def dirExists(fd):
  if os.path.exists(fd + '.old'):
    shutil.rmtree(fd + '.old')
    
  if os.path.exists(fd):
    os.rename(fd, fd + '.old')

# -----------------------------------------------------------------------------
# select M4B file(s)

def selectFiles(defaultdir):
  Tk().withdraw()
  fn = askopenfilenames(filetypes=[("Audiobook File(s)", "*.m4b"), ("All Files", "*.*")], title="Select audiobook file(s)", initialdir = defaultdir)
#  fn = askopenfilenames(filetypes=[("Audiobook Files(s)", "*.m4b"), ("All Files", "*.*")], title="Select audiobook file(s)")

  if fn:
    return fn
  else:
    return None


# -----------------------------------------------------------------------------
# concatenate command line elements stored in list

def concat_args(*args):
  return ''.join(*args)


# -----------------------------------------------------------------------------
# launch 'command' windowless - for text output and progress feedback via scrolling textbox

def launchWithoutConsoleWin(cmd):
  log = []
  counter = 0
  
  # create scrolling text box for command output
  root = Tk()
  root.title('Detecting silence')
  textbox = scrolledtext.ScrolledText(root, height=50, width=100)
  textbox.config(wrap='word')
  textbox.pack()

  # run command windowless (text output)
  startupinfo = subprocess.STARTUPINFO()
  startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
  p = subprocess.Popen(cmd, startupinfo=startupinfo, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)

  # send each line of output to a scrolling textbox

  for line in p.stdout:
    # add output to log file - only for the start/end of each detected silence (in seconds)
    if line.startswith('lavfi.silence_start=') or line.startswith('lavfi.silence_end='):
      log.append(float(line.split('=')[1].rstrip()))
      counter += 1
      textbox.insert(END, line)     # add output to end of textbox content
      textbox.see(END)              # move cursor to end of textbox content
      Tk.update(textbox)            # update textbox with new content

      if counter > 1000:
        textbox.delete("1.0", END)
        Tk.update(textbox)
        counter = 0

  p.wait()                        # wait for process to finish
  root.destroy()                  # close textbox

  return log


# -----------------------------------------------------------------------------
# launch 'command' windowless - for text output

def launchWithoutConsoleText(cmd):
  startupinfo = subprocess.STARTUPINFO()
  startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

  return subprocess.Popen(cmd, startupinfo=startupinfo, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)


# -----------------------------------------------------------------------------
# launch 'command' windowless - for binary output

def launchWithoutConsole(cmd):
  startupinfo = subprocess.STARTUPINFO()
  startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

  return subprocess.Popen(cmd, startupinfo=startupinfo, stderr=subprocess.PIPE, stdout=subprocess.PIPE)


# -----------------------------------------------------------------------------
# run command and grab stdout and stderr (default for Windows)
# type = 'b' for binary output, 'w' for feedback in textbox, else assume text output
# stderr = p[0]; stdout = p[1]; all output = p
# ffprobe, exiftool -> stderr; ffmpeg -> stdout

def runCommand(args, type):
  if type == 'w':
    return launchWithoutConsoleWin(concat_args(args))   # output to scrolling textbox
  elif type == 't':
    p = launchWithoutConsoleText(concat_args(args))     # text output
    return p.communicate()
  else:
    p = launchWithoutConsole(concat_args(args))         # binary output
    return p.communicate()


# -----------------------------------------------------------------------------
# replace UTF-8 characters with ASCII equivalent

def badChar(str):
  transFrom = '’‘ ꞉“”—–‒‐'
  transTo = '\'\' :""----'
  trans_table = str.maketrans(transFrom, transTo)
  return str.translate(trans_table)


# -----------------------------------------------------------------------------
# rename file with characters that Exiftool can't read (i.e. UTF-8)
# invalid filename characters in Windows: <>:"/\|?*

##def badFn(fn):
##  transFrom = '’‘ “”—–‒‐'
##  transTo =   "'' ''----"
##  transDelete = '꞉〈〉⁄∕ǀ？⃰'
##  trans_table = str.maketrans(transFrom, transTo, transDelete)
##  newstem = fn.stem.translate(trans_table)
##
##  if newstem != fn.stem:
##    newfn = fn.parents[0].joinpath(newstem + fn.suffix)
##    os.rename(fn, newfn)
##  else:
##    newfn = fn
##
##  return newfn


# -----------------------------------------------------------------------------
