import cv2

# Capturar el flujo de video de la cámara
cap = cv2.VideoCapture(0)

while True:
    # Leer el fotograma actual
    ret, frame = cap.read()

    # Dividir la imagen en dos mitades
    height, width, _ = frame.shape
    half_width = width // 2
    left_half = frame[:, :half_width]
    right_half = frame[:, half_width:]

    # Realizar análisis en la mitad izquierda
    # ...

    # Realizar análisis en la mitad derecha
    # ...

    # Mostrar los resultados en una ventana
    cv2.imshow('Left Half', left_half)
    cv2.imshow('Right Half', right_half)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar los recursos
cap.release()
cv2.destroyAllWindows()