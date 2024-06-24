import sounddevice as sd

print("Lista de dispositivos de audio:")
dispositivos = sd.query_devices()
for i, dispositivo in enumerate(dispositivos):
    print(f"{i}: {dispositivo['name']}")
