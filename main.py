from tkinter import *
import pygame
from tkinter import filedialog
import tkinter.ttk as ttk
from tkinter import messagebox

import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf

import pyaudio
import struct
import wave
from matplotlib import pyplot
from os import path
import os
from pathlib import Path
import time
import psutil

root = Tk()
root.title('Vocal Extractor')

pygame.mixer.init()

'''
on_closing
	clears GUI and processes running inside it to 
	exit the application in a clean manner
'''
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
    	pygame.mixer.music.unload()
    	root.destroy()
    	root.quit()
    	os._exit(0)
    	

'''
	loads user-selected song
'''
def add_song():
	song = filedialog.askopenfilename(initialdir='songs/', title="Choose a song", filetypes=(("WAV Files", "*.wav"), ))
	song = song.split('/')[-1]
	
	if song not in listbox.get(0, "end"):
		listbox.insert(END, song)

'''
	loads multiple user-selected songs
'''
def add_mul_song():
	songs = filedialog.askopenfilenames(initialdir='songs/', title="Choose a song", filetypes=(("WAV Files", "*.wav"), ))
	for song in songs:
		song = song.split('/')[-1]
		if song not in listbox.get(0, "end"):
			listbox.insert(END, song)

'''
	plays user-selected song
'''
def play():
	song = listbox.get(ACTIVE)
	song = f'songs/{song}'

	try:
		pygame.mixer.music.load(song)
		pygame.mixer.music.play(loops=0)
	except FileNotFoundError:
		print("Song not added")

'''
	stops playing currently playing song
'''
def stop():
	pygame.mixer.music.stop()
	listbox.selection_clear(ACTIVE)

'''
	runs audio processor on the user-selected song;
	extracts vocal and instrumental music separately and
	saves it to different files in the "songs/" directory
'''
def extract():
	song = listbox.get(ACTIVE)
	song = f'songs/{song}'

	y, sr = librosa.load(song)
	S_full, phase = librosa.magphase(librosa.stft(y))

	S_filter = librosa.decompose.nn_filter(S_full,
                                       aggregate=np.median,
                                       metric='cosine',
                                       width=int(librosa.time_to_frames(2, sr=sr)))
	S_filter = np.minimum(S_full, S_filter)

	margin_i, margin_v = 2, 10
	power = 2

	mask_i = librosa.util.softmask(S_filter,
	                               margin_i * (S_full - S_filter),
	                               power=power)

	mask_v = librosa.util.softmask(S_full - S_filter,
	                               margin_v * S_filter,
	                               power=power)

	S_foreground = mask_v * S_full
	S_background = mask_i * S_full

	y_foreground = librosa.istft(S_foreground * phase)
	y_background = librosa.istft(S_background * phase)


	vocal_file =  song[:-4] + '_vocals' +'.wav'
	print(vocal_file)
	sf.write(vocal_file, y_foreground, sr)

	instr_file =  song[:-4] + '_instrumentals' + '.wav'
	print(instr_file)
	sf.write(instr_file, y_background, sr)

	stop()

	# load the processed audio files in the application
	vocal_file = vocal_file.split('/')[-1]
	instr_file = instr_file.split('/')[-1]
	# listbox.insert(END, vocal_file)
	# listbox.insert(END, instr_file)
	if vocal_file not in listbox.get(0, "end"):
		listbox.insert(END, vocal_file)
	
	if instr_file not in listbox.get(0, "end"):
		listbox.insert(END, instr_file)

global paused
paused = False

'''
	pauses the currenly playing song
'''
def pause(is_paused):
	global paused
	paused = is_paused

	if paused:
		pygame.mixer.music.unpause()
		paused = False
	else:
		pygame.mixer.music.pause()
		paused = True

'''
	handles update in volume using volume-slider
'''
def volume(x):
	pygame.mixer.music.set_volume(1 - volume_slider.get())
	current_vol = pygame.mixer.music.get_volume()

'''
	plot the selected sound track in real-time
'''
def graph():
	songname = listbox.get(ACTIVE)
	song = f'songs/{songname}'

	if song[-4:] == '.mp3':
		return

	

	wavfile = f'songs/graph_{songname}'
	print('Name of wave file: %s' % wavfile)

	y, sr = librosa.load(song)
	sf.write(wavfile, y, sr)

	# Open wave file
	wf = wave.open( wavfile, 'rb')

	# Read wave file properties
	RATE        = wf.getframerate()     # Frame rate (frames/second)
	WIDTH       = wf.getsampwidth()     # Number of bytes per sample
	LEN         = wf.getnframes()       # Signal length
	CHANNELS    = wf.getnchannels()     # Number of channels

	print('The file has %d channel(s).'         % CHANNELS)
	print('The file has %d frames/second.'      % RATE)
	print('The file has %d frames.'             % LEN)
	print('The file has %d bytes per sample.'   % WIDTH)

	BLOCKLEN = 2000    # Blocksize

	# Set up plotting...

	pyplot.ion()           # Turn on interactive mode so plot gets updated

	fig = pyplot.figure(1)

	[g1] = pyplot.plot([], [])

	g1.set_xdata(range(BLOCKLEN))
	pyplot.ylim(-20000, 20000)
	pyplot.xlim(0, BLOCKLEN)

	# Open the audio output stream
	p = pyaudio.PyAudio()

	PA_FORMAT = p.get_format_from_width(WIDTH)
	stream = p.open(
	    format = PA_FORMAT,
	    channels = CHANNELS,
	    rate = RATE,
	    input = False,
	    output = True,
	    frames_per_buffer = 256)      # low latency so that plot and output audio are synchronized

	# Get block of samples from wave file
	input_bytes = wf.readframes(BLOCKLEN)

	while len(input_bytes) >= BLOCKLEN * WIDTH:

	    # Convert binary data to number sequence (tuple)
	    signal_block = struct.unpack('h' * BLOCKLEN, input_bytes)

	    g1.set_ydata(signal_block)
	    pyplot.pause(0.001)

	    # Write binary data to audio output stream
	    stream.write(input_bytes, BLOCKLEN)

	    # Get block of samples from wave file
	    input_bytes = wf.readframes(BLOCKLEN)

	stream.stop_stream()
	stream.close()
	p.terminate()

	wf.close()

	pyplot.ioff()           # Turn off interactive mode
	pyplot.show()           # Keep plot showing at end of program
	pyplot.close()
	print('* Finished')

# initialize GUI roo
master_frame = Frame(root)
master_frame.pack(pady=20)

# add song list panel
listbox = Listbox(master_frame, bg = "black", fg = "green", width = 60, selectbackground="gray", selectforeground="black")
listbox.grid(row=0, column=0)

# load assets
play_btn_img = PhotoImage(file='images/rsz_play.png')
pause_btn_img = PhotoImage(file='images/rsz_pause.png')
stop_btn_img = PhotoImage(file='images/rsz_stop.png')
vol_btn_img = PhotoImage(file='images/rsz_vol.png')
vocal_btn_img = PhotoImage(file='images/rsz_mic.png')
graph_btn_img = PhotoImage(file='images/rsz_graph.png')

# add volume slider
volume_frame = LabelFrame(master_frame, text="Volume")
volume_frame.grid(row = 0, column=1, padx = 20)

# add audio control panel
controls_frame = Frame(master_frame)
controls_frame.grid(row=1, column=0)

# add buttons in audio control panel
# play button
play_btn = Button(controls_frame, image = play_btn_img, borderwidth = 0, command=play)
play_btn.grid(row=0, column=0, padx=10)

# pause button
pause_btn = Button(controls_frame, image = pause_btn_img, borderwidth = 0, command = lambda: pause(paused))
pause_btn.grid(row=0, column=1, padx=10)

# stop button
stop_btn = Button(controls_frame, image = stop_btn_img, borderwidth = 0, command = stop)
stop_btn.grid(row=0, column=2, padx=10)

# vocal extraction button
vocal_btn = Button(controls_frame, image = vocal_btn_img, borderwidth = 0, command = extract)
vocal_btn.grid(row=0, column=3, padx=10)

# audio visualizer button
graph_btn = Button(controls_frame, image = graph_btn_img, borderwidth=0, command = graph)
graph_btn.grid(row=0, column=4, padx=10)

# add application menu
my_menu = Menu(root)
root.config(menu=my_menu)

# add song menu
add_song_menu = Menu(my_menu)
my_menu.add_cascade(label= "Add songs", menu = add_song_menu)
add_song_menu.add_command(label="Add a song", command=add_song)
add_song_menu.add_command(label="Add multiple songs", command=add_mul_song)

# configure volume slider
volume_slider = ttk.Scale(volume_frame, from_ = 0, to = 1, orient= VERTICAL, value = 0.5, command=volume, length=125)
volume_slider.pack(pady=10)



root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
for p in Path("songs/").glob("graph*.wav"):
	p.unlink()