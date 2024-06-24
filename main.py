import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import numpy as np
import wave
import threading
import os
from pydbus import SessionBus

# Variables globales
grabando = False
fs = 48000  # Frecuencia de muestreo, compatible con AirPods Pro
nombre_archivo = 'output.wav'
audio_buffer = []
buffer_size = fs  # Buffer de 1 segundo
tiempo_transcurrido = 0
titulo_actual = ""
artistas_actual = ""

# Función para obtener el título y artista de la canción
def obtener_info_cancion():
    global titulo_actual, artistas_actual
    bus = SessionBus()
    try:
        player = bus.get('org.mpris.MediaPlayer2.firefox.instance_1_83', '/org/mpris/MediaPlayer2')
        metadata = player.Metadata
        if metadata:
            titulo = metadata.get('xesam:title', 'N/A')
            artistas = metadata.get('xesam:artist', ['N/A'])
            artistas_str = ', '.join(artistas)
            if titulo != titulo_actual or artistas_str != artistas_actual:
                titulo_actual = titulo
                artistas_actual = artistas_str
                nueva_cancion_detectada(titulo, artistas_str)
            return titulo, artistas_str
        else:
            return "N/A", "N/A"
    except Exception as e:
        print(f"Error al obtener información del reproductor: {e}")
        return "N/A", "N/A"

# Función para manejar la detección de una nueva canción
def nueva_cancion_detectada(titulo, artistas):
    global grabando
    if grabando:
        detener_grabacion()
    iniciar_grabacion()

# Función para actualizar el título y artista de la ventana
def actualizar_titulo_cancion():
    global titulo_actual, artistas_actual
    titulo, artistas = obtener_info_cancion()
    ventana.title(f"WAV Recorder - {titulo} - {artistas}")
    etiqueta_cancion.config(text=f"Nombre de la canción: {titulo}\nArtista: {artistas}")
    titulo_actual = titulo
    artistas_actual = artistas
    ventana.after(1000, actualizar_titulo_cancion)

def grabar_audio():
    global grabando, audio_buffer, tiempo_transcurrido
    grabando = True
    tiempo_transcurrido = 0

    audio_data = []

    def callback(indata, frames, time, status):
        global audio_buffer
        if grabando:
            audio_data.append(indata.copy())
            audio_buffer.extend(indata.copy())
            if len(audio_buffer) > buffer_size:
                audio_buffer = audio_buffer[-buffer_size:]

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

    titulo, artistas = obtener_info_cancion()
    nombre_archivo_salida = limpiar_nombre_archivo(f"{artistas} - {titulo}.wav")

    with sd.InputStream(samplerate=fs, device=indice_dispositivo, channels=2, callback=callback, dtype='int16'):
        while grabando:
            sd.sleep(100)

    audio_data_np = np.concatenate(audio_data, axis=0)
    guardar_audio(audio_data_np, nombre_archivo_salida)

def guardar_audio(audio, nombre_archivo):
    with wave.open(nombre_archivo, 'w') as archivo_wav:
        archivo_wav.setnchannels(2)
        archivo_wav.setsampwidth(2)
        archivo_wav.setframerate(fs)
        archivo_wav.writeframes(audio.tobytes())
    messagebox.showinfo("Información", f"Grabación completada y guardada como '{nombre_archivo}'")

def limpiar_nombre_archivo(nombre):
    # Caracteres no permitidos en nombres de archivos
    caracteres_no_permitidos = '/\\:*?"<>|'
    for caracter in caracteres_no_permitidos:
        nombre = nombre.replace(caracter, '-')
    return nombre

def iniciar_grabacion():
    global grabando
    actualizar_tiempo_transcurrido()
    print("Grabando...")
    if not grabando:
        threading.Thread(target=grabar_audio).start()
        

def detener_grabacion():
    global grabando
    grabando = False
    print("Grabación terminada")

def actualizar_tiempo_transcurrido():
    global tiempo_transcurrido
    if grabando:
        tiempo_transcurrido += 1
        etiqueta_tiempo.config(text=f"Tiempo de grabación: {tiempo_transcurrido} s")
        ventana.after(1000, actualizar_tiempo_transcurrido)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("WAV Recorder")
ventana.geometry("600x200")  # Tamaño de la ventana

# Etiqueta para mostrar el nombre de la canción actual
etiqueta_cancion = tk.Label(ventana, text="Nombre de la canción: \nArtista: ")
etiqueta_cancion.pack(pady=10)

# Etiqueta para mostrar el tiempo de grabación transcurrido
etiqueta_tiempo = tk.Label(ventana, text="Tiempo de grabación: 0 s")
etiqueta_tiempo.pack(pady=10)

# Función para actualizar la etiqueta con el nombre de la canción actual
def actualizar_etiqueta_cancion():
    titulo, artistas = obtener_info_cancion()
    etiqueta_cancion.config(text=f"Nombre de la canción: {titulo}\nArtista: {artistas}")
    ventana.after(1000, actualizar_etiqueta_cancion)

# Llamar a la función para actualizar la etiqueta inicialmente
actualizar_etiqueta_cancion()

# Frame para los botones de grabación
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=10)

# Botones para iniciar y detener la grabación
boton_grabar = tk.Button(frame_botones, text="Iniciar Grabación", command=iniciar_grabacion)
boton_grabar.pack(side=tk.LEFT, padx=10)

boton_detener = tk.Button(frame_botones, text="Detener Grabación", command=detener_grabacion)
boton_detener.pack(side=tk.RIGHT, padx=10)

# Ejecutar el bucle principal de la interfaz gráfica
ventana.mainloop()
