# Split .m4b to multiple files
# -----------------------------------------------------------------------------
# module imports

from common import *

# -----------------------------------------------------------------------------
# add split points to end of log file in human-readable format
# for checking only

def printSpltPts(logDict, spltPts, fn):
  # filenames for each filetype accessed
  fileLog = fn.parents[0].joinpath(fn.stem + '.log')
      
  sf = open(fileLog, 'w')

  for key in logDict:
    sf.write('Start time = ' + str(key) + ', End time = ' + str(logDict[key]) + '\n')

  sf.write('\n===============================================================================\n\n')
  sf.write('SPLIT POINTS\n')

  for pt in spltPts:
    sf.write(str(pt) + ' secs - ' + str(datetime.timedelta(seconds=pt)) + '\n')

  sf.close()
  
  return


# -----------------------------------------------------------------------------
# split by chapters

def splitByChapters(fn, fileVar):
  # handle existing files/directories
  splitDir = str(fn.parents[0].joinpath(fileVar['ext'].upper()))
  dirExists(splitDir)
  os.mkdir(splitDir)
  os.chdir(splitDir)

  counter = 1

  # command line for ffprobe chapter data
  a = []
  a.append('"' + fileVar['ffprobe'] + '"')
  a.append(' -show_chapters -print_format json ')
  a.append('"' + str(fn) + '"')

  # extract chapter data from M4B file using FFPROBE
  p = runCommand(concat_args(a), None)
  chapterData = json.loads(p[0])

  # zeroes needed to pad file number
  sp = len(chapterData['chapters'])
  result = 10 ** (math.floor(math.log10(sp)))
  digits = len(str(result))

  # create scrolling text box for command output
  root = Tk()
  root.title('Writing audio files')
  textbox = scrolledtext.ScrolledText(root, height=30, width=80)
  textbox.config(wrap='word')
  textbox.pack()
  textbox.insert(END, 'Writing audio files\n\n')   # add output to end of textbox content
  textbox.see(END)                                    # move cursor to end of textbox content
  Tk.update(textbox)                                  # update textbox

  # split by chapter start/end times
  for i in chapterData['chapters']:
    first, last = splitCmd(fn, i['start_time'], i['end_time'], counter, digits, sp)
    textbox.insert(END, 'Writing... ' + str(fn.stem) + ' - ' + str(counter).zfill(digits) + '.' + fileVar['ext'].lower() + '\n')
    textbox.see(END)
    Tk.update(textbox)
    # run external command
    p = runCommand(concat_args(first), None)
    counter += 1

  root.destroy()                  # close textbox


# -----------------------------------------------------------------------------
# split to M4A/MP3

def splitCmd(fn, startTime, secs, counter, digits, maxtrk):
 
  # create cmd line for file export from time1 to time2
  a = []
  a.append('"' + fileVar['ffmpeg'] + '"')
  a.append(' -i ')
  a.append('"' + str(fn) + '"')
  a.append(' -map_metadata 0 -metadata track="')
  a.append(str(counter) + '/' + str(maxtrk) + '"')
  if fileVar['ext'] == 'm4a':
    a.append(' -vn -acodec copy -ss ' + str(startTime))
  else:   # assume mp3
    a.append(' -vn -vsync 0 -acodec libmp3lame -q 3 -ss ' + str(startTime))
  a.append('s -to ' + str(secs) + 's ')  
  a.append('"' + str(fn.stem) + ' - ' + str(counter).zfill(digits) + '.' + fileVar['ext'].lower() + '"')

  # create cmd line for file export from time1 to EOF
  b = []
  b.append('"' + fileVar['ffmpeg'] + '"')
  b.append(' -i ')
  b.append('"' + str(fn) + '"')
  b.append(' -map_metadata 0 -metadata track="')
  b.append(str(counter) + '/' + str(maxtrk) + '"')
  if fileVar['ext'] == 'm4a':
    b.append(' -vn -acodec copy -ss ' + str(startTime))
  else:   # assume mp3
    b.append(' -vn -vsync 0 -acodec libmp3lame -q 3 -ss ' + str(startTime))
  b.append('s ')
  b.append('"' + str(fn.stem) + ' - ' + str(counter).zfill(digits) + '.' + fileVar['ext'].lower() + '"')

  return a, b


# -----------------------------------------------------------------------------
# get duration of audio file

def duration(fn):
  # command line for ffprobe - audio duration
  a = []
  a.append('"' + fileVar['ffprobe'] + '"')
  a.append(' -hide_banner -show_entries format=duration -of default=noprint_wrappers=1 ')
  a.append('"' + str(fn) + '"')

  # extract chapter data from M4B file using FFPROBE
  p = runCommand(concat_args(a), 't')
  durSecs = float(p[0].split('=')[1])
  
  return durSecs


# -----------------------------------------------------------------------------
# split into X minute files (.m4b to .m4a)
# - need to add metadata (incl image) and track number to output files

## start time to end time:
##   ffmpeg -i input.mp3 -vn -acodec copy -ss 00:00:00 -to 00:01:32 output.mp3
## start time + duration time:
##   ffmpeg -i input.mp3 -vn -acodec copy -ss 00:00:00 -t 00:01:32 output.mp3
## start of audio to end time:
##   ffmpeg -i input.mp3 -vn -acodec copy -to 00:01:32 output.mp3
## start time till end of audio:
##   ffmpeg -i input.mp3 -vn -acodec copy -ss 00:01:32 output.mp3


def splitByMinutes(spltPts, fn):
  # handle existing files/directories
  splitDir = str(fn.parents[0].joinpath(fileVar['ext'].upper()))
  dirExists(splitDir)
  os.mkdir(splitDir)
  os.chdir(splitDir)

  counter = 1
  startTime = 0
  # get length of m4b file in seconds
  maxSecs = duration(fn)
  # add length to end of spltPts list (ensures that last file is always produced)
  spltPts.append(maxSecs)
  
  # zeroes needed to pad file number
  sp = max(len(spltPts) - 1, 1)
  result = 10 ** (math.floor(math.log10(sp)))
  digits = len(str(result))

  # create scrolling text box for command output
  root = Tk()
  root.title('Writing audio files')
  textbox = scrolledtext.ScrolledText(root, height=30, width=80)
  textbox.config(wrap='word')
  textbox.pack()
  textbox.insert(END, 'Writing audio files\n\n')   # add output to end of textbox content
  textbox.see(END)                                 # move cursor to end of textbox content
  Tk.update(textbox)                               # update textbox

# split files
  secs = spltPts[counter-1]
  while True:
    # 3 minutes minimum size for last file
    if maxSecs - secs > 180:
      # create file from time1 to time2
      first, last = splitCmd(fn, startTime, secs, counter, digits, len(spltPts))

      textbox.insert(END, 'Writing... ' + str(fn.stem) + ' - ' + str(counter).zfill(digits) + '.' + fileVar['ext'].lower() + '\n')
      textbox.see(END)
      Tk.update(textbox)

      # run external command
      p = runCommand(concat_args(first), None)

      counter += 1
      startTime = secs
      secs = spltPts[counter-1]
    else:
      # create file from time1 to EOF
      first, last = splitCmd(fn, startTime, secs, counter, digits, len(spltPts))

      textbox.insert(END, 'Writing... ' + str(fn.stem) + ' - ' + str(counter).zfill(digits) + '.' + fileVar['ext'].lower() + '\n')
      textbox.see(END)
      Tk.update(textbox)

      # run external command
      p = runCommand(concat_args(last), None)

      root.destroy()                  # close textbox
      break


# -----------------------------------------------------------------------------
# identify nearest silence point to required cut-off point (e.g. 10 minutes)

def splitPoints(ld, minutes, lastSilence):
  # convert minutes to seconds
  fileLen = float(minutes * 60)
  fileSecs = fileLen
  splitPoints = []

  # calculate the nearest silence to cut-off point and set split point to middle of silence
  while True:
    # returns ld.result_key and ld.result_value
    startTime, endTime = min(ld.items(), key=lambda x: abs(fileSecs - x[1]))
    splitPoints.append(round(startTime + (endTime - startTime) / 2, 3))
    fileSecs += fileLen

    if fileSecs > lastSilence:
      break

  return splitPoints


# -----------------------------------------------------------------------------
# detect silence in audio file (parameters defined in text file)

def silenceDetect(fn, fileVar):
  logDict = {}

  # command line for ffmpeg silence detection
  a = []
  a.append('"' + fileVar['ffmpeg'] + '"')
  a.append(' -i')
  a.append(' "' + str(fn) + '"')
  a.append(' -loglevel quiet -af silencedetect=n=')
  a.append(fileVar['db'])
  a.append('dB:d=')
  a.append(fileVar['silencelength'])
  a.append(",ametadata=mode=print:direct=1:file='-' -f null -")   # direct=1 - prints continuously; file='-' - prints to stdout

  # extract chapter data from M4B file using FFPROBE (grab stdout for this dataset)
  logList = runCommand(concat_args(a), 'w')

  # create dictionary with start and end as key/value pairs
  for start, end in zip(logList[::2], logList[1::2]):
    logDict[start] = end
    lastSilence = end

  return logDict, lastSilence


# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":

# get variables from external file
  fileVar = getFileVariable()

# iterate over selected files to produce output

  fileNames = selectFiles(fileVar['defaultdir'])

  while fileNames:
    for fn in fileNames:
      fn = Path(fn)

      if fileVar['split'] == 'Y':
        if fileVar['splitby'] == 'minutes':
          # detect silence
          logDict, lastSilence = silenceDetect(fn, fileVar)
          # calculate split points
          spltPts = splitPoints(logDict, int(fileVar['minutes']), lastSilence)
          # split into X minutes file
          splitByMinutes(spltPts, fn)
        else:   # assume chapters
          splitByChapters(fn, fileVar)
      else:   # assume silence log
        # detect silence
        logDict, lastSilence = silenceDetect(fn, fileVar)
        # calculate split points
        spltPts = splitPoints(logDict, int(fileVar['minutes']), lastSilence)
        # print split points to log file
        printSpltPts(logDict, spltPts, fn)


    fileNames = selectFiles(fileVar['defaultdir'])
    if not fileNames:
      break


# -----------------------------------------------------------------------------
# exit program
# -----------------------------------------------------------------------------
