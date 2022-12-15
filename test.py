from tkinter import *
import pygame
from tkinter import filedialog
import tkinter.ttk as ttk

root = Tk()
root.title('Vocal Extractor')

pygame.mixer.init()

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
	pygame.mixer.music.set_volume(volume_slider.get())
	current_vol = pygame.mixer.music.get_volume()

master_frame = Frame(root)
master_frame.pack(pady=20)

listbox = Listbox(master_frame, bg = "black", fg = "green", width = 60, selectbackground="gray", selectforeground="black")
listbox.grid(row=0, column=0)

play_btn_img = PhotoImage(file='images/rsz_play.png')
pause_btn_img = PhotoImage(file='images/rsz_pause.png')
stop_btn_img = PhotoImage(file='images/rsz_stop.png')
vol_btn_img = PhotoImage(file='images/rsz_vol.png')

volume_frame = LabelFrame(master_frame, text="Volume")
volume_frame.grid(row = 0, column=1, padx = 20)

controls_frame = Frame(master_frame)
controls_frame.grid(row=1, column=0)


play_btn = Button(controls_frame, image = play_btn_img, borderwidth = 0, command=play)
pause_btn = Button(controls_frame, image = pause_btn_img, borderwidth = 0, command = lambda: pause(paused))
stop_btn = Button(controls_frame, image = stop_btn_img, borderwidth = 0, command = stop)

play_btn.grid(row=0, column=0, padx=10)
pause_btn.grid(row=0, column=1, padx=10)
stop_btn.grid(row=0, column=2, padx=10)

my_menu = Menu(root)
root.config(menu=my_menu)

add_song_menu = Menu(my_menu)
my_menu.add_cascade(label= "Add songs", menu = add_song_menu)
add_song_menu.add_command(label="Add a song", command=add_song)
add_song_menu.add_command(label="Add multiple songs", command=add_mul_song)

volume_slider = ttk.Scale(volume_frame, from_ = 0, to = 1, orient= VERTICAL, value = 1, command=volume, length=125)
volume_slider.pack(pady=10)
root.mainloop()