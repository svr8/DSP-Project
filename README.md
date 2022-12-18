<div id="top"></div>
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a>
    <img src="https://s3.dualstack.us-east-2.amazonaws.com/pythondotorg-assets/media/community/logos/python-logo-only.png" alt="Logo" width="80" height="80">
    <img src="https://librosa.org/doc/latest/_static/librosa_logo_text.svg" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Vocal Extractor: A DSP Project</h3>
  <p align="center">
    Extract vocals and instrumentals of a song at the click of a button
    <br />
    <!-- TODO update demo link -->
    <a href="https://docs.rehost.in/#/getting-started/quickstart"><strong><u>View Live Demo »</u></strong></a>
    <br />
    <a href="mailto:si2152@nyu.edu">Siddhanth Iyer (si2152)</a>
    ·
    <a href="mailto:sv2270@nyu.edu">Shikhar Vaish (sv2270)</a>
  </p>
</div>

<p align="center">
    <img src="images/demo.png" alt="Logo" width="400" height="300">
</p>

## About The Project

This is a submission to the course Digital Signal Processing Laboratory ECE-GY 6183 as the final project. The goal was to use signal processing techniques learned in the course and build something real-life oriented out of it. The appliction presented here exectues predefined audio processing algrotihms to extract vocal and instrumental audio signals from a song. It assumes that the input audio file provided is a musical audio with human voices.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

Dependency | Link |
--- | --- |
Python | [Official Page](https://www.python.org/downloads/)

### Installation

1. Download and extract the project zip.
2. Run the following command to install project dependencies:
`pip install -r requirements.txt`

### Run Application

1. Start the application using:
`python main.py`

<p align="right">(<a href="#top">back to top</a>)</p>

## Usage

### Load Songs

<p align="center">
    <img src="images/load-song.png" alt="Logo" width="300" height="250">
</p>
In the application menu, go to `Add Songs > Add a song` to open the file chooser pop-up. Select the file present on your computer to load it in the application. Intuitively, you can choose `Add Songs > Add multiple songs` to load multiple audio files.

### Audio Control

<p align="center">
    <img src="images/play-song.png" alt="Logo" width="300" height="250">
</p>
You can use the intuitive control buttons to play, pause, and, stop playing the songs. The slider on the right can be used to adjust the playback volume.

### Extract Vocals and Instrumentals

<p align="center">
    <img src="images/extract-song.png" alt="Logo" width="300" height="250">
</p>
First, click on the audio track that you want to process. Next, click on the microphone icon to extract vocals and instrumentals of the selected audio file in separate files.

It takes a few seconds to process the audo file, depending on the length of audio track. Finally, you will see 2 new audio files saved as `<audio file name>_instrumentals.wav` and `<audio file name>_vocals.wav` in the `songs/` directory. 

These audio tracks would be loaded in the application directly after processing. You can see listen to them directly through the application.

### Real-Time Audio Visualization

<p align="center">
    <img src="images/plot-song.png" alt="Logo" width="300" height="250">
</p>
Click the wave icon to visualize audio frequency in real-time.

## How It Works

### Audio Extraction

The application uses `librosa` library and apply 2 different softmask filters the on the audio data, for instrumental and vocals respectively.

The final output is processed and saved in different files.

### Real-Time Audio Visualization

The application uses `matplotlib` and simple sliding window algorithm to load the binary data in blocks of fix sizes. These batches are passed to `pyaudio` stream connected that plays the audio to the output device meanwhile we get matplotlib to read the audio data and plot the signals in real-time.


## Authors

* Siddhanth Iyer - si2152
* Shikhar Vaish - sv2270
