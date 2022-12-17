import wave

def displayWAVFileInfo(filename):

  wf = wave.open(filename, 'rb')

  # number of channels
  num_channel = wf.getnchannels()

  # frame rate (number of frames per second)
  fs = wf.getframerate()

  # total number of frames (length of signal)
  length_signal = wf.getnframes()

  # number of bytes per sample
  width = wf.getsampwidth() 

  print('number of channels:', num_channel)
  print('frame rate        :', fs)
  print('signal length     :', length_signal)
  print('bytes per sample  :', width)

displayWAVFileInfo('output/background.wav')
displayWAVFileInfo('output/foreground.wav')