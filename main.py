import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import numpy as np
import wave
import threading
from pydbus import SessionBus

# Variables globales
grabando = False
fs = 48000  # Frecuencia de muestreo, compatible con AirPods Pro
nombre_archivo = 'output.wav'
segundos_transcurridos = 0

# Función para obtener el título de la canción
def obtener_titulo_cancion():
    bus = SessionBus()
    try:
        player = bus.get('org.mpris.MediaPlayer2.firefox.instance_1_97', '/org/mpris/MediaPlayer2')
        metadata = player.Metadata
        if metadata:
            return metadata['xesam:title']
        else:
            return "N/A"
    except Exception as e:
        print(f"Error al obtener información del reproductor: {e}")
        return "N/A"

# Función para actualizar el título de la ventana con el nombre de la canción actual
def actualizar_titulo_cancion():
    titulo = obtener_titulo_cancion()
    ventana.title(f"Spotify WAV Recorder - {titulo}")

def grabar_audio():
    global grabando, segundos_transcurridos
    grabando = True
    segundos_transcurridos = 0
    audio_data = []

    def callback(indata, frames, time, status):
        global segundos_transcurridos
        nonlocal audio_data
        if grabando:
            audio_data.append(indata.copy())
            segundos_transcurridos += 0.1  # Aumenta en 0.1 segundos (ajuste según necesidad)
            etiqueta_tiempo.config(text=f"Tiempo transcurrido: {segundos_transcurridos:.1f} segundos")

    # Encuentra el dispositivo de entrada deseado (por nombre)
    dispositivos = sd.query_devices()
    indice_dispositivo = None
    for i, dispositivo in enumerate(dispositivos):
        if "Ricky Munoz’s AirPods Pro" in dispositivo['name']:
            indice_dispositivo = i
            break

    if indice_dispositivo is None:
        messagebox.showerror("Error", "No se encontró el dispositivo de entrada adecuado")
        return

    with sd.InputStream(samplerate=fs, device=indice_dispositivo, channels=2, callback=callback, dtype='int16'):
        while grabando:
            sd.sleep(100)

    audio_data_np = np.concatenate(audio_data, axis=0)
    guardar_audio(audio_data_np)

def guardar_audio(audio):
    with wave.open(nombre_archivo, 'w') as archivo_wav:
        archivo_wav.setnchannels(2)
        archivo_wav.setsampwidth(2)
        archivo_wav.setframerate(fs)
        archivo_wav.writeframes(audio.tobytes())
    messagebox.showinfo("Información", f"Grabación completada y guardada como '{nombre_archivo}'")

def iniciar_grabacion():
    global grabando
    print("Grabando...")
    if not grabando:
        threading.Thread(target=grabar_audio).start()

def detener_grabacion():
    global grabando
    grabando = False
    print("Grabación terminada")
    etiqueta_tiempo.config(text="Tiempo transcurrido: 0.0 segundos")  # Reinicia el contador

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Spotify WAV Recorder")
ventana.geometry("600x200")  # Tamaño de la ventana

# Etiqueta para mostrar el nombre de la canción actual
etiqueta_cancion = tk.Label(ventana, text="Nombre de la canción: ")
etiqueta_cancion.pack(pady=10)

# Función para actualizar la etiqueta con el nombre de la canción actual
def actualizar_etiqueta_cancion():
    titulo = obtener_titulo_cancion()
    etiqueta_cancion.config(text=f"Nombre de la canción: {titulo}")
    ventana.after(1000, actualizar_etiqueta_cancion)

# Llamar a la función para actualizar la etiqueta inicialmente
actualizar_etiqueta_cancion()

# Etiqueta para mostrar el tiempo transcurrido
etiqueta_tiempo = tk.Label(ventana, text="Tiempo transcurrido: 0.0 segundos")
etiqueta_tiempo.pack()

# Botones para iniciar y detener la grabación
boton_grabar = tk.Button(ventana, text="Iniciar Grabación", command=iniciar_grabacion)
boton_grabar.pack(side=tk.LEFT, padx=10)

boton_detener = tk.Button(ventana, text="Detener Grabación", command=detener_grabacion)
boton_detener.pack(side=tk.LEFT, padx=10)

# Ejecutar el bucle principal de la interfaz gráfica
ventana.mainloop()
