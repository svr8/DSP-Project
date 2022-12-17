from tkinter import *
import pygame
from tkinter import filedialog
import tkinter.ttk as ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

root = Tk()
root.title('Vocal Extractor')

pygame.mixer.init()

def generate_audio_plot():
	# the figure that will contain the plot
	fig = Figure(figsize = (5, 5),
				dpi = 100)

	# list of squares
	y = [i**2 for i in range(101)]

	# adding the subplot
	plot1 = fig.add_subplot(111)

	# plotting the graph
	plot1.plot(y)

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
		pygame.mixer.music.load(song)
		pygame.mixer.music.play(loops=0)
		generate_audio_plot()
		
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