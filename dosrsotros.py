import time
import cv2
import mediapipe as mp
from math import sqrt

def distance_nose(nostril_l, nostril_r, nose):
    n_x, n_y = nose
    nl_x, nl_y = nostril_l
    nr_x, nr_y = nostril_r

    # ax + by + c = 0
    m = (nr_y - nl_y) / (nr_x - nl_x)
    a, b, c = -m, 1, -nr_y + m * nr_x
    print("pendiente: ", m)
    distance = (a * n_x + b * n_y + c) / sqrt(a ** 2 + b ** 2)

    if m == 0:
        y2 = nr_y
    else:
        y2 = -(a * n_x + c) / b
    q_point = (int(n_x), int(y2))

    return -distance, q_point

draw_all = False

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

    face1 = None
    face2 = None

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

            for i, face_landmarks in enumerate(results.multi_face_landmarks):
                if i == 0:
                    height, width, _ = image.shape
                    top_point = (int(face_landmarks.landmark[10].x * width),
                                 int(face_landmarks.landmark[10].y * height))
                    bottom_point = (int(face_landmarks.landmark[152].x * width),
                                    int(face_landmarks.landmark[152].y * height))
                    nose_point = (int(face_landmarks.landmark[1].x * width),
                                  int(face_landmarks.landmark[1].y * height))
                    nostril_l_point = (int(face_landmarks.landmark[203].x * width),
                                       int(face_landmarks.landmark[203].y * height))
                    nostril_r_point = (int(face_landmarks.landmark[423].x * width),
                                       int(face_landmarks.landmark[423].y * height))

                    distance, q_point = distance_nose(nostril_l=nostril_l_point,
                                                      nostril_r=nostril_r_point,
                                                      nose=nose_point)

                    print("distance:", distance)
                    length_head = sqrt((top_point[0] - bottom_point[0]) ** 2 + (top_point[1] - bottom_point[1]) ** 2)
                    absolute_distance = round(distance / length_head, 3)
                    print("\tdistance absolute:", absolute_distance)

                    if abs(distance) >= 0:
                        print("nose: {}  -  {}".format(nose_point[0], nose_point[1]))
                        print("nostril L: {}  -  {}".format(nostril_l_point[0], nostril_l_point[1]))
                        print("nostril R: {}  -  {}".format(nostril_r_point[0], nostril_r_point[1]))
                        print("Q: {}  -  {}".format(q_point[0], q_point[1]))

                    cv2.line(image, nostril_l_point, nostril_r_point, (0, 255, 0), 2)
                    cv2.circle(image, nose_point, 5, (0, 0, 255), -1)
                    cv2.circle(image, q_point, 5, (0, 0, 255), -1)
                    cv2.circle(image, top_point, 5, (255, 0, 0), -1)
                    cv2.circle(image, bottom_point, 5, (255, 0, 0), -1)

                    # Guardar los puntos del rostro en una variable
                    face1 = {
                        'top_point': top_point,
                        'bottom_point': bottom_point,
                        'nose_point': nose_point,
                        'nostril_l_point': nostril_l_point,
                        'nostril_r_point': nostril_r_point,
                        'distance': distance,
                        'q_point': q_point,
                        'absolute_distance': absolute_distance
                    }

                elif i == 1:
                    height, width, _ = image.shape
                    top_point = (int(face_landmarks.landmark[10].x * width),
                                 int(face_landmarks.landmark[10].y * height))
                    bottom_point = (int(face_landmarks.landmark[152].x * width),
                                    int(face_landmarks.landmark[152].y * height))
                    nose_point = (int(face_landmarks.landmark[1].x * width),
                                  int(face_landmarks.landmark[1].y * height))
                    nostril_l_point = (int(face_landmarks.landmark[203].x * width),
                                       int(face_landmarks.landmark[203].y * height))
                    nostril_r_point = (int(face_landmarks.landmark[423].x * width),
                                       int(face_landmarks.landmark[423].y * height))

                    distance, q_point = distance_nose(nostril_l=nostril_l_point,
                                                      nostril_r=nostril_r_point,
                                                      nose=nose_point)

                    print("distance:", distance)
                    length_head = sqrt((top_point[0] - bottom_point[0]) ** 2 + (top_point[1] - bottom_point[1]) ** 2)
                    absolute_distance = round(distance / length_head, 3)
                    print("\tdistance absolute:", absolute_distance)

                    if abs(distance) >= 0:
                        print("nose: {}  -  {}".format(nose_point[0], nose_point[1]))
                        print("nostril L: {}  -  {}".format(nostril_l_point[0], nostril_l_point[1]))
                        print("nostril R: {}  -  {}".format(nostril_r_point[0], nostril_r_point[1]))
                        print("Q: {}  -  {}".format(q_point[0], q_point[1]))

                    cv2.line(image, nostril_l_point, nostril_r_point, (0, 255, 0), 2)
                    cv2.circle(image, nose_point, 5, (0, 0, 255), -1)
                    cv2.circle(image, q_point, 5, (0, 0, 255), -1)
                    cv2.circle(image, top_point, 5, (255, 0, 0), -1)
                    cv2.circle(image, bottom_point, 5, (255, 0, 0), -1)

                    # Guardar los puntos del rostro en una variable
                    face2 = {
                        'top_point': top_point,
                        'bottom_point': bottom_point,
                        'nose_point': nose_point,
                        'nostril_l_point': nostril_l_point,
                        'nostril_r_point': nostril_r_point,
                        'distance': distance,
                        'q_point': q_point,
                        'absolute_distance': absolute_distance
                    }

        # Mostrar la imagen con las líneas dibujadas
        cv2.imshow('Face Mesh', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()