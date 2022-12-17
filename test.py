from tkinter import *
import pygame
from tkinter import filedialog
import tkinter.ttk as ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import wave
import numpy as np
import matplotlib.pyplot as plt

import librosa
import librosa.display
import soundfile as sf
import pyaudio


plt.ion()

root = Tk()
root.title('Vocal Extractor')

pygame.mixer.init()

def clip16( x ):    
  # Clipping for 16 bits
  if x > 32767:
    x = 32767
  elif x < -32768:
    x = -32768
  else:
    x = x        
  return (x)


class FilteredSignal:
	def __init__(self, signal, sample_rate, label):
		self.sig = signal

		filename = f'output/{label}.wav'
		sf.write(f'output/{label}.wav', signal, sample_rate, 'PCM_24')

		self.RATE = sample_rate

		wf = wave.open(filename, 'rb')
		self.WIDTH = wf.getsampwidth()
		self.LEN = wf.getnframes()
		self.CHANNELS = wf.getnchannels()
		self.label = label

		wf.close()
	
def filter_audio(filename):
	y, sr = librosa.load(filename, duration=120)

	start = 0
	end = 25

	# And compute the spectrogram magnitude and phase
	S_full, phase = librosa.magphase(librosa.stft(y))

	# Play back a 5-second excerpt with vocals
	# Audio(data=y[start*sr:end*sr], rate=sr)

	idx = slice(*librosa.time_to_frames([start, end], sr=sr))
	# fig, ax = plt.subplots()
	# img = librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
							#  y_axis='log', x_axis='time', sr=sr, ax=ax)
	# fig.colorbar(img, ax=ax)

	# We'll compare frames using cosine similarity, and aggregate similar frames
	# by taking their (per-frequency) median value.
	#
	# To avoid being biased by local continuity, we constrain similar frames to be
	# separated by at least 2 seconds.
	#
	# This suppresses sparse/non-repetetitive deviations from the average spectrum,
	# and works well to discard vocal elements.
	S_filter = librosa.decompose.nn_filter(S_full,
										aggregate=np.median,
										metric='cosine',
										width=int(librosa.time_to_frames(2, sr=sr)))

	# The output of the filter shouldn't be greater than the input
	# if we assume signals are additive.  Taking the pointwise minimum
	# with the input spectrum forces this.
	S_filter = np.minimum(S_full, S_filter)

	# We can also use a margin to reduce bleed between the vocals and instrumentation masks.
	# Note: the margins need not be equal for foreground and background separation
	margin_i, margin_v = 2, 10
	power = 2

	mask_i = librosa.util.softmask(S_filter,
								margin_i * (S_full - S_filter),
								power=power)

	mask_v = librosa.util.softmask(S_full - S_filter,
								margin_v * S_filter,
								power=power)

	# Once we have the masks, simply multiply them with the input spectrum
	# to separate the components

	S_foreground = mask_v * S_full
	S_background = mask_i * S_full

	y_foreground = librosa.istft(S_foreground * phase)
	# Play back a 5-second excerpt with vocals
	# Audio(data=y_foreground[start*sr:end*sr], rate=sr)

	y_background = librosa.istft(S_background * phase)
	# Play back a 5-second excerpt with instrumentals
	# Audio(data=y_background[start*sr:end*sr], rate=sr)

	background_signal = FilteredSignal(y_background, sr, 'background')
	foreground_signal = FilteredSignal(y_foreground, sr, 'foreground')

	return foreground_signal, background_signal

def generate_audio_plot(sig, sample_rate):

	fig = plt.figure(1)

	# adding the energy subplot
	plot_a = fig.add_subplot(211)
	plot_a.plot(sig)
	plot_a.set_xlabel('sample rate * time')
	plot_a.set_ylabel('energy')

	# adding the frequency subplot
	plot_b = plt.subplot(212)
	plot_b.specgram(sig, NFFT=1024, Fs=sample_rate, noverlap=900)
	plot_b.set_xlabel('Time')
	plot_b.set_ylabel('Frequency')

	# create wrapper frame
	wrapper_frame = Frame(root)
	wrapper_frame.pack(pady=20)

	# creating the Tkinter canvas
	# containing the Matplotlib figure
	canvas = FigureCanvasTkAgg(fig,
							master = wrapper_frame)
	
	canvas.draw()

	# placing the toolbar on the Tkinter window
	canvas.get_tk_widget().grid(row=0, column=0)

	plt.ioff()

def plot_and_play_filteredaudio(filteredAudio):

	BLOCKLEN = 1000
	fig = plt.figure(1)
	plot_sig = fig.add_subplot(211)
	[g1] = plot_sig.plot([], [])

	g1.set_xdata(range(BLOCKLEN))
	plt.ylim(-32000, 32000)
	plt.xlim(0, BLOCKLEN)

	# Open the audio output stream
	p = pyaudio.PyAudio()

	PA_FORMAT = p.get_format_from_width(filteredAudio.WIDTH)
	stream = p.open(
		format = PA_FORMAT,
		channels = filteredAudio.CHANNELS,
		rate = filteredAudio.RATE,
		input = False,
		output = True,
		frames_per_buffer = 256)      # low latency so that plot and output audio are synchronized

	sliding_window_start = 0
	sliding_window_end = BLOCKLEN
	audio_output_format = 'h'*BLOCKLEN
	while sliding_window_end < filteredAudio.LEN:
		
		block_data = filteredAudio.sig[sliding_window_start:sliding_window_end]
		g1.set_ydata(block_data)
		plt.pause(0.0001)
		
		outputList = []
		for i in range(BLOCKLEN):
			outputList.append(block_data[i])
		output_bytes = struct.pack('h'*BLOCKLEN, *outputList)
		stream.write(audio_output_format, output_bytes)

		sliding_window_start += BLOCKLEN
		sliding_window_end += BLOCKLEN
	
	stream.stop_stream()
	stream.close()
	p.terminate()


def add_song():
	song = filedialog.askopenfilename(initialdir='songs/', title="Choose a song", filetypes=(("mp3 Files", "*.mp3"), ("WAV Files", "*.wav")))
	song = song.split('/')[-1]
	
	if song not in listbox.get(0, "end"):
		listbox.insert(END, song)

def add_mul_song():
	songs = filedialog.askopenfilenames(initialdir='songs/', title="Choose a song", filetypes=(("mp3 Files", "*.mp3"), ("WAV Files", "*.wav")))
	for song in songs:
		song = song.split('/')[-1]
		if song not in listbox.get(0, "end"):
			listbox.insert(END, song)

def play():
	song = listbox.get(ACTIVE)
	song = f'songs/{song}'

	try:
		foreground_sig, background_sig = filter_audio(song)
		
		filtered_filename = f'output/{foreground_sig.label}.wav'
		# pygame.mixer.music.load(filtered_filename)
		# pygame.mixer.music.play(loops=0)
		# generate_audio_plot(foreground_sig.sig, foreground_sig.RATE)
		plot_and_play_filteredaudio(foreground_sig)

	except FileNotFoundError:
		print("Song not added")

def stop():
	pygame.mixer.music.stop()
	listbox.selection_clear(ACTIVE)

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
	pygame.mixer.music.set_volume(1 - volume_slider.get())
	current_vol = pygame.mixer.music.get_volume()

# initialize GUI root
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

# add volume slider
volume_frame = LabelFrame(master_frame, text="Volume")
volume_frame.grid(row = 0, column=1, padx = 20)

# add audio control panel
controls_frame = Frame(master_frame)
controls_frame.grid(row=1, column=0)

# add buttons in audio control panel
play_btn = Button(controls_frame, image = play_btn_img, borderwidth = 0, command=play)
play_btn.grid(row=0, column=0, padx=10)

pause_btn = Button(controls_frame, image = pause_btn_img, borderwidth = 0, command = lambda: pause(paused))
pause_btn.grid(row=0, column=1, padx=10)

stop_btn = Button(controls_frame, image = stop_btn_img, borderwidth = 0, command = stop)
stop_btn.grid(row=0, column=2, padx=10)

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
root.mainloop()