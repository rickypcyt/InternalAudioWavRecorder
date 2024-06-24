import tkinter as tk
from tkinter import messagebox, Canvas
import sounddevice as sd
import numpy as np
import wave
import threading
import os
from pydbus import SessionBus

# Global Variables
recording = False
fs = 48000  # Sampling rate, compatible with AirPods Pro
audio_buffer = []
buffer_size = fs  # 1-second buffer
elapsed_time = 0
current_title = ""
current_artists = ""
current_filename = ""

# Function to get song title and artist information
def get_song_info():
    global current_title, current_artists, recording

    bus = SessionBus()
    try:
        player = bus.get('org.mozilla.firefox.ZGVmYXVsdC1yZWxlYXNl', '/org/mpris/MediaPlayer2')
        metadata = player.Metadata
        if metadata:
            title = metadata.get('xesam:title', 'N/A')
            artists = metadata.get('xesam:artist', ['N/A'])
            artists_str = ', '.join(artists)
            if title != current_title or artists_str != current_artists:
                current_title = title
                current_artists = artists_str
                if recording:
                    stop_recording()
                    start_recording()
            return title, artists_str
        else:
            return "N/A", "N/A"
    except Exception as e:
        print(f"Error retrieving player information: {e}")
        return "N/A", "N/A"


# Function to handle new song detection
def new_song_detected(title, artists):
    # Optionally update song_label here
    # song_label.config(text=f"Song Name: {title}\nArtist: {artists}")
    pass

# Function to update window title with song title and artist
def update_song_title():
    global current_title, current_artists
    title, artists = get_song_info()
    window.title(f"WAV Recorder - {title} - {artists}")
    song_label.config(text=f"Song Name: {title}\nArtist: {artists}")
    current_title = title
    current_artists = artists
    window.after(1000, update_song_title)

def record_audio(filename):
    global recording, audio_buffer, elapsed_time
    elapsed_time = 0

    audio_data = []

    def callback(indata, frames, time, status):
        global audio_buffer
        if recording:
            audio_data.append(indata.copy())
            audio_buffer.extend(indata.copy())
            if len(audio_buffer) > buffer_size:
                audio_buffer = audio_buffer[-buffer_size:]

    # Find desired input device by name
    devices = sd.query_devices()
    device_index = None
    for i, device in enumerate(devices):
        if "Firefox" in device['name']:
            device_index = i
            break

    if device_index is None:
        messagebox.showerror("Error", "Desired input device not found")
        return

    output_filename = filename

    with sd.InputStream(samplerate=fs, device=device_index, channels=2, callback=callback, dtype='int16'):
        while recording:
            sd.sleep(100)

    audio_data_np = np.concatenate(audio_data, axis=0)
    save_audio(audio_data_np, output_filename)

def save_audio(audio, filename):
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(fs)
        wav_file.writeframes(audio.tobytes())

def clean_filename(name):
    # Invalid characters in filenames
    invalid_chars = '/\\:*?"<>|'
    for char in invalid_chars:
        name = name.replace(char, '-')
    return name

def start_recording():
    global recording, current_filename
    if not recording:
        title, artists = get_song_info()
        current_filename = clean_filename(f"{artists} - {title}.wav")
        threading.Thread(target=record_audio, args=(current_filename,)).start()
        update_elapsed_time()
        recording = True
        update_record_indicator()  # Update recording indicator
        print("Recording started...")

def stop_recording():
    global recording
    if recording:
        recording = False
        update_record_indicator()  # Update recording indicator
        print("Recording stopped")

def update_elapsed_time():
    global elapsed_time
    if recording:
        elapsed_time += 1
        time_label.config(text=f"Recording time: {elapsed_time} s")
        window.after(1000, update_elapsed_time)

def update_record_indicator():
    if recording:
        canvas.itemconfig(recording_indicator, fill='green')
    else:
        canvas.itemconfig(recording_indicator, fill='red')

# Create the main window
window = tk.Tk()
window.title("WAV Recorder")
window.geometry("600x200")  # Window size

# Label to display current song information
song_label = tk.Label(window, text="Song Name: \nArtist: ")
song_label.pack(pady=10)

# Label to display elapsed recording time
time_label = tk.Label(window, text="Recording time: 0 s")
time_label.pack(pady=10)

# Canvas to draw recording indicator
canvas = Canvas(window, width=20, height=20)
canvas.pack(pady=10)
recording_indicator = canvas.create_oval(5, 5, 20, 20, fill='red')  # Red circle initially

# Function to update song label with current song information
def update_song_label():
    title, artists = get_song_info()
    song_label.config(text=f"Song Name: {title}\nArtist: {artists}")
    window.after(1000, update_song_label)

# Call function to update label initially
update_song_label()

# Frame for recording buttons
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

# Buttons to start and stop recording
start_button = tk.Button(button_frame, text="Start Recording", command=start_recording)
start_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(button_frame, text="Stop Recording", command=stop_recording)
stop_button.pack(side=tk.RIGHT, padx=10)

# Run the main GUI loop
window.mainloop()
