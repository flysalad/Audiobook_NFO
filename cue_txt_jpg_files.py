# Create cue, nfo (.txt) and jpeg files for m4b file(s)
# -----------------------------------------------------------------------------
# module imports

from common import *

# -----------------------------------------------------------------------------
# convert seconds into cue file format (minutes:seconds:frames)
# 60 secs/min; 75 frames/sec

def timeConvert(seconds):
  seconds = float(seconds)
  min, sec = divmod(seconds, 60)
  frame = int((sec % 1) * 75)
  return "%d:%02d:%d" % (min, sec, frame)


# -----------------------------------------------------------------------------
# calculate length of each chapter and convert to human-readable format for NFO file

def Duration(startTime, endTime):
  startTime = float(startTime)
  endTime = float(endTime)
  
  chapterLen = endTime - startTime
  chapterLen = str(datetime.timedelta(seconds=int(chapterLen)))
  
  startTime = str(datetime.timedelta(seconds=int(startTime)))
  endTime = str(datetime.timedelta(seconds=int(endTime)))
  
  return startTime, endTime, chapterLen


# -----------------------------------------------------------------------------
# create cue file

def createCueFile(fn, fileVar):
  fileCue = fn.parents[0].joinpath(fn.stem + '.cue')

  # command line for ffprobe chapter data
  a = []
  a.append('"' + fileVar['ffprobe'] + '"')
  a.append(' -show_chapters -print_format json ')
  a.append('"' + str(fn) + '"')

  # extract chapter data from M4B file using FFPROBE
  p = runCommand(concat_args(a), None)
  chapterData = json.loads(p[0])

  # write cue file
  fileExists(fileCue)
  cue = open(fileCue, 'w', encoding='utf8')

  # write file header
  cue.write('FILE "' + fn.name + '" MP3\n')

  # write out chapter details to cue file
  for i in chapterData['chapters']:

    # convert sequencial chapter titles to text (e.g. "001" to "Chapter 1")
    title = str(i['tags']['title'])
    if len(title) == 3:
      try:
        title = int(title)
        title = 'Chapter ' + str(title)
      except ValueError:
        pass
    
    startTime, endTime, chapterLen = Duration(i['start_time'], i['end_time'])
    cue.write('TRACK ' + str(int(i['id']) + 1) + ' AUDIO\n')
    cue.write('  TITLE "' + title + '"\n')
    cue.write('  INDEX 01 ' + timeConvert(i['start_time']) + '\n')

  # clean up
  cue.close()
  return chapterData


# -----------------------------------------------------------------------------
# create nfo text file

def createNfoFile(fn, fileVar):
  fileNfo = fn.parents[0].joinpath(fn.stem + '.txt')

  titlesInt = 0

  # command line for ffprobe chapter data
  a = []
  a.append('"' + fileVar['exiftool'] + '"')
  a.append(' "' + str(fn) + '"')
  a.append(' -j -f -Title -Album -Artist -Narrator -Composer -Copyright -ReleaseDate -ContentCreateDate -Genre -Publisher')
  a.append(' -Duration -ProductID -FileType -AudioSampleRate -AudioChannels -AudioBitsPerSample -AvgBitrate -Description')

  # extract metadata from M4B file using Exiftool.exe
  # as Exiftool can't handle filenames with some UTF characters, throw error dialog to user
  p = runCommand(concat_args(a), None)
  try:
    metaData = json.loads(p[0])
  except json.decoder.JSONDecodeError:
    messagebox.showerror('Exiftool error', 'Invalid filename.\n\nPlease remove invalid characters for your language and try again.')
    # sys.exit(1)
    return

  fileExists(fileNfo)
  nfo = open(fileNfo, 'w', encoding='utf8')

  for i in metaData:
    # get whichever field exists
    lst = [i['Narrator'], i['Composer']]
    narrator = next(filter(lambda l: l != '-', lst), '')

    lst = [i['Title'], i['Album']]
    title = next(filter(lambda l: l != '-', lst), '')

    lst = [i['Copyright'], i['ContentCreateDate']]
    copyright = next(filter(lambda l: l != '-', lst), '')
    copyright = html.unescape(str(copyright))

    # deal with unescaped HTML characters in metadata
    desc = html.unescape(i['Description'])
    desc = badChar(desc)
    desc = desc.replace('\\n', '\n\n')

    # write metadata to cue file
    nfo.write('AUDIOBOOK DETAILS\n=================\n')
    nfo.write('Title:\n  ' + str(title) + '\n')
    nfo.write('Author:\n  ' + i['Artist'] + '\n')
    nfo.write('Narrator(s):\n  ' + narrator + '\n')
    nfo.write('Duration:\n  ' + i['Duration'] + '\n')
    nfo.write('Copyright:\n  ' + str(copyright) + '\n')
    nfo.write('Release Date:\n  ' + i['ReleaseDate'] + '\n')
    nfo.write('Genre:\n  ' + i['Genre'] + '\n')
    nfo.write('Publisher:\n  ' + i['Publisher'] + '\n')
    nfo.write('Product ID:\n  ' + i['ProductID'] + '\n')
    nfo.write('\n\nAUDIO DETAILS\n=============\n')
    nfo.write('File Type:\n  ' + i['FileType'] + '\n')
    nfo.write('Average Bitrate:\n  ' + i['AvgBitrate'] + '\n')
    nfo.write('Audio SampleRate :\n  ' + str(i['AudioSampleRate']) + ' Hz\n')
    nfo.write('Audio Channels:\n  ' + str(i['AudioChannels']) + '\n')
    nfo.write('Audio Bits Per Sample:\n  ' + str(i['AudioBitsPerSample']) + '\n')
    nfo.write('\n\nBOOK DESCRIPTION\n================\n' + desc + '\n')

  # write chapter details to cue file
  nfo.write('\n\nCHAPTERS\n========\n')
  for i in chapterData['chapters']:

    # convert sequencial chapter titles to text (e.g. "001" to "Chapter 1")
    title = str(i['tags']['title'])
    if len(title) == 3:
      try:
        title = int(title)
        title = 'Chapter ' + str(title)
      except ValueError:
        pass
    
    startTime, endTime, chapterLen = Duration(i['start_time'], i['end_time'])
    nfo.write('Chapter ' + str(int(i['id']) + 1) + '\n')
    nfo.write('  "' + title + '"\n')
    nfo.write('  Start time       ' + startTime + '\n')
    nfo.write('  End time         ' + endTime + '\n')
    nfo.write('  Chapter length   ' + chapterLen + '\n')

  nfo.close()


# -----------------------------------------------------------------------------
# extract cover art from M4B using Exiftool (create jpeg file)

def createJpegFile(fn, fileVar):
  fileJpeg = fn.parents[0].joinpath(fn.stem + '.jpg')

  if not os.path.exists(fileJpeg):
    a = []
    a.append('"' + fileVar['exiftool'] + '"')
    a.append(' "' + str(fn) + '"')
    a.append(' -CoverArt -b')

    # extract cover art from M4B file using Exiftool.exe
    p = runCommand(concat_args(a), None)

    # create jpeg file from binary stderr output
    f = open(fileJpeg ,'w+b')
    f.write(p[0])
    f.close()


# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":

# get external program details and set variables
  fileVar = getFileVariable()

# iterate over selected file(s) to produce output

  fileNames = selectFiles(fileVar['defaultdir'])

  while fileNames:
    for fn in fileNames:
      fn = Path(fn)

      chapterData = createCueFile(fn, fileVar)
      createNfoFile(fn, fileVar)
      createJpegFile(fn, fileVar)

    fileNames = selectFiles(fileVar['defaultdir'])
    if not fileNames:
      break


# -----------------------------------------------------------------------------
# exit program
# -----------------------------------------------------------------------------
