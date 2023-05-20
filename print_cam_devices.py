# Enumerar los dispositivos de captura de video
import cv2


devices = []
for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        devices.append(f"Device {i}")
        cap.release()

# Mostrar los dispositivos disponibles
for device in devices:
    print(device)