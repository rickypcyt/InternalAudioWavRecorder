# WAV Recorder

WAV Recorder is a Python GUI application built with Tkinter that allows you to record audio from a specified input device and save it as a WAV file. It integrates with media players to automatically detect and record the currently playing song.

## Features

- Record audio from a specified input device (e.g., AirPods Pro) at a sampling rate of 48000 Hz.
- Automatically detects and records the currently playing song's title and artist.
- Displays real-time information such as song metadata and recording duration.
- Saves recorded audio as a WAV file with the format "Artist - Song Title.wav".

## Requirements

- Python 3.x
- tkinter (for GUI)
- sounddevice (for audio recording)
- numpy (for audio data handling)
- pydbus (for interfacing with D-Bus services)
- wave (for WAV file handling)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/wav-recorder.git
   ```

2. Install dependencies:
   ```
   pip install sounddevice numpy pydbus
   ```

3. Run the application:
   ```
   python wav_recorder.py
   ```

## Usage

- Launch the application (`python wav_recorder.py`).
- Click on "Start Recording" to begin recording audio.
- The application will automatically detect the currently playing song and display its title and artist.
- Click on "Stop Recording" to finish recording and save the audio as a WAV file in the current directory.

## Screenshots

[Include screenshots of your application in action if available]

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
