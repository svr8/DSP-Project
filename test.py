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

root = Tk()
root.title('Vocal Extractor')

pygame.mixer.init()

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        root.quit()
        os._exit(0)

def add_song():
	song = filedialog.askopenfilename(initialdir='songs/', title="Choose a song", filetypes=(("WAV Files", "*.wav"), ))
	song = song.split('/')[-1]
	
	if song not in listbox.get(0, "end"):
		listbox.insert(END, song)

def add_mul_song():
	songs = filedialog.askopenfilenames(initialdir='songs/', title="Choose a song", filetypes=(("WAV Files", "*.wav"), ))
	for song in songs:
		song = song.split('/')[-1]
		if song not in listbox.get(0, "end"):
			listbox.insert(END, song)

def play():
	song = listbox.get(ACTIVE)
	song = f'songs/{song}'

	try:
		pygame.mixer.music.load(song)
		pygame.mixer.music.play(loops=0)
	except FileNotFoundError:
		print("Song not added")

def stop():
	pygame.mixer.music.stop()
	listbox.selection_clear(ACTIVE)

def extract():
	song = listbox.get(ACTIVE)
	song = f'songs/{song}'

	y, sr = librosa.load(song)
	S_full, phase = librosa.magphase(librosa.stft(y))

	sf.write(song, y, sr)

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

	vocal_file = vocal_file.split('/')[-1]
	instr_file = instr_file.split('/')[-1]
	listbox.insert(END, vocal_file)
	listbox.insert(END, instr_file)

global paused
paused = False

def pause(is_paused):
	global paused
	paused = is_paused

	if paused:
		pygame.mixer.music.unpause()
		paused = False
	else:
		pygame.mixer.music.pause()
		paused = True

def volume(x):
	pygame.mixer.music.set_volume(volume_slider.get())
	current_vol = pygame.mixer.music.get_volume()

def graph():
	songname = listbox.get(ACTIVE)
	song = f'songs/{songname}'


	if song[-4:] == '.mp3':
		return

	wavfile = f'songs/{songname}'
	print('Name of wave file: %s' % wavfile)

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

master_frame = Frame(root)
master_frame.pack(pady=20)

listbox = Listbox(master_frame, bg = "black", fg = "green", width = 60, selectbackground="gray", selectforeground="black")
listbox.grid(row=0, column=0)

play_btn_img = PhotoImage(file='images/rsz_play.png')
pause_btn_img = PhotoImage(file='images/rsz_pause.png')
stop_btn_img = PhotoImage(file='images/rsz_stop.png')
vol_btn_img = PhotoImage(file='images/rsz_vol.png')
vocal_btn_img = PhotoImage(file='images/rsz_mic.png')
graph_btn_img = PhotoImage(file='images/rsz_graph.png')


volume_frame = LabelFrame(master_frame, text="Volume")
volume_frame.grid(row = 0, column=1, padx = 20)

controls_frame = Frame(master_frame)
controls_frame.grid(row=1, column=0)


play_btn = Button(controls_frame, image = play_btn_img, borderwidth = 0, command=play)
pause_btn = Button(controls_frame, image = pause_btn_img, borderwidth = 0, command = lambda: pause(paused))
stop_btn = Button(controls_frame, image = stop_btn_img, borderwidth = 0, command = stop)
vocal_btn = Button(controls_frame, image = vocal_btn_img, borderwidth = 0, command = extract)
graph_btn = Button(controls_frame, image = graph_btn_img, borderwidth=0, command = graph)

play_btn.grid(row=0, column=0, padx=10)
pause_btn.grid(row=0, column=1, padx=10)
stop_btn.grid(row=0, column=2, padx=10)
vocal_btn.grid(row=0, column=3, padx=10)
graph_btn.grid(row=0, column=4, padx=10)

my_menu = Menu(root)
root.config(menu=my_menu)

add_song_menu = Menu(my_menu)
my_menu.add_cascade(label= "Add songs", menu = add_song_menu)
add_song_menu.add_command(label="Add a song", command=add_song)
add_song_menu.add_command(label="Add multiple songs", command=add_mul_song)

volume_slider = ttk.Scale(volume_frame, from_ = 0, to = 1, orient= VERTICAL, value = 1, command=volume, length=125)
volume_slider.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
