import cv2
import mediapipe as mp

# Inicializar el objeto de detección de rostros
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

# Configurar la captura de video desde la cámara
cap = cv2.VideoCapture(0)  # Cambiar el índice si tienes varias cámaras
face_mesh_global = None
with mp_face_mesh.FaceMesh(
    max_num_faces=2,  # Máximo de 2 caras
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:
    face_mesh_global = face_mesh
    print("Previo al loop")

    while cap.isOpened():
        success, image = cap.read()
        image = cv2.flip(image, 1)
        if not success:
            break

        # Convertir la imagen de BGR a RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Detectar rostros en la imagen
        results = face_mesh_global.process(image_rgb)

        if results.multi_face_landmarks:
            print("Número de caras detectadas: {}".format(len(results.multi_face_landmarks)))
            for face_landmarks in results.multi_face_landmarks:
                # Obtener los puntos de la frente y la barbilla
                forehead_point = face_landmarks.landmark[10]
                chin_point = face_landmarks.landmark[152]

                # Obtener las coordenadas en píxeles
                height, width, _ = image.shape
                forehead_x = int(forehead_point.x * width)
                forehead_y = int(forehead_point.y * height)
                chin_x = int(chin_point.x * width)
                chin_y = int(chin_point.y * height)

                # Dibujar la línea que conecta los puntos
                cv2.line(image, (forehead_x, forehead_y), (chin_x, chin_y), (0, 255, 0), 2)

        # Mostrar la imagen con las líneas dibujadas
        cv2.imshow('Face Mesh', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
