# write_sin_02
# 
# Make a wave file (.wav) consisting of a sine wave

# 8 bits per sample

from struct import pack
from math import sin, pi
import wave

Fs = 8000

# Write a mono wave file 

wf = wave.open('hw1-q5-sin8bit.wav', 'w')		# wf : wave file
wf.setnchannels(1)			# one channel (mono)
wf.setsampwidth(1)			# 1 byte per sample (8 bits per sample)
wf.setframerate(Fs)			# samples per second
A = 2**7 - 1.0 			# amplitude
f = 261.6					# frequency in Hz (note A3)
N = int(0.5*Fs)				# half-second in samples

for n in range(0, N):	    # half-second loop 
	x = A * sin(2*pi*f/Fs*n)
	byte_string = pack('B', int(x + 128)) 
	# 'i' stands for 'integer' (8 bits)
	wf.writeframesraw(byte_string)
wf.close()
