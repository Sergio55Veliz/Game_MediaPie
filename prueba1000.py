import cv2

class FaceRegistration:
    def __init__(self):
        self.webcam = cv2.VideoCapture(0)

    def register_faces(self):
        # Cargar el clasificador pre-entrenado de detección de rostros
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Variables para almacenar los rostros registrados
        registered_faces = []

        while True:
            # Leer el fotograma actual de la cámara
            ret, frame = self.webcam.read()

            # Convertir a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detectar rostros en la imagen
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            for (x, y, w, h) in faces:
                # Dibujar un rectángulo alrededor del rostro detectado
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Extraer el rostro de la imagen en escala de grises
                face = gray[y:y + h, x:x + w]

                # Agregar el rostro a la lista de rostros registrados
                registered_faces.append(face)

            # Mostrar la imagen en una ventana
            cv2.imshow('Face Registration', frame)

            # Salir del bucle si se presiona la tecla 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Liberar los recursos
        self.webcam.release()
        cv2.destroyAllWindows()

        return registered_faces

# Ejemplo de uso
face_registration = FaceRegistration()
registered_faces = face_registration.register_faces()
print(f"Se registraron {len(registered_faces)} rostros.")
