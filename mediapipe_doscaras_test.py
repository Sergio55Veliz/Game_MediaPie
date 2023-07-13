import cv2
import mediapipe as mp
from math import sqrt
import time
from webcam import *

# Inicializar el objeto de detección de rostros
mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1,  # Máximo de 1 cara a detectar
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


def distance_nose(nostril_l, nostril_r, nose, verbose=False):
    n_x, n_y = nose
    nl_x, nl_y = nostril_l
    nr_x, nr_y = nostril_r

    # ax + by + c = 0
    m = (nr_y - nl_y) / (nr_x - nl_x)
    a, b, c = -m, 1, -nr_y + m * nr_x
    if verbose: print("pendiente: ", m)
    distance = (a * n_x + b * n_y + c) / sqrt(a ** 2 + b ** 2)

    if m == 0:
        y2 = nr_y
    else:
        y2 = -(a * n_x + c) / b
    q_point = (int(n_x), int(y2))

    return -distance, q_point


def get_points(face_landmarks, image_shape):
    # ---------------------------- Puntos para movimiento de nave -----------------------------
    # Obtener los puntos de la frente y la barbilla
    height, width = image_shape
    top_point = (int(face_landmarks.landmark[10].x * width),
                 int(face_landmarks.landmark[10].y * height))
    bottom_point = (int(face_landmarks.landmark[152].x * width),
                    int(face_landmarks.landmark[152].y * height))

    # Obtener los puntos de nariz y fosas nazales
    nose_point = (int(face_landmarks.landmark[1].x * width),
                  int(face_landmarks.landmark[1].y * height))
    nostril_l_point = (int(face_landmarks.landmark[203].x * width),
                       int(face_landmarks.landmark[203].y * height))
    nostril_r_point = (int(face_landmarks.landmark[423].x * width),
                       int(face_landmarks.landmark[423].y * height))

    # --------------------------------- Cuadrado del rostro -----------------------------------
    # Obtener coordenadas del 'cuadrado' de la cara para poder mostrarlo en la pantalla despues
    # Las coordenadas obtenidas aquí son absolutas. Entre 0 y 1.
    #   - 0 es el primer pixel a la izquierdo
    #   - 1 es el último pixel a la derecha
    #   - Los valores negativos implican que el rostro está fuera de la pantalla
    face_left_x = face_landmarks.landmark[234].x
    face_right_x = face_landmarks.landmark[454].x
    face_top_y = face_landmarks.landmark[10].y
    face_bottom_y = face_landmarks.landmark[152].y

    # Dejar algo de espacio alrededor
    border = 0.1*abs(face_right_x-face_left_x)
    face_left_x -= border
    face_right_x += border
    face_top_y -= border*2
    face_bottom_y += border*0.5
    # Obtener valores escalados
    face_left_x = int(face_left_x * width)
    face_right_x = int(face_right_x * width)
    face_top_y = int(face_top_y * height)
    face_bottom_y = int(face_bottom_y * height)

    height_ROI, width_ROI = (face_bottom_y-face_top_y, face_right_x-face_left_x)
    center_h, center_w = (face_top_y + height_ROI/2, face_left_x + width_ROI/2)
    #print("----- Dimensión ROI:", height_ROI, width_ROI)
    # Creamos un ROI cuadrado escogiendo el eje más grande
    if height_ROI < width_ROI:
        #print("ancho >>>>> alto")
        face_top_y = int(center_h - width_ROI/2)
        face_bottom_y = int(center_h + width_ROI/2)
    elif height_ROI > width_ROI:
        #print("ancho <<<<< alto")
        face_left_x = int(center_w - height_ROI/2)
        face_right_x = int(center_w + height_ROI/2)

    height_ROI, width_ROI = (face_bottom_y - face_top_y, face_right_x - face_left_x)
    center_h, center_w = (face_top_y + height_ROI/2, face_left_x + width_ROI/2)
    # Mitigamos el hecho de que una cara esté fuera de cuadro
    if face_left_x < 0:
        face_right_x += (-1*face_left_x)
        face_left_x = 0
    if face_right_x > width:
        face_left_x -= face_right_x-width
        face_right_x = width
    if face_top_y < 0:
        face_bottom_y += (-1*face_top_y)
        face_top_y = 0
    if face_bottom_y > height:
        face_top_y -= face_bottom_y-height
        face_bottom_y = height

    height_ROI, width_ROI = (face_bottom_y - face_top_y, face_right_x - face_left_x)
    center_h, center_w = (face_top_y + height_ROI/2, face_left_x + width_ROI/2)
    # en caso de que la cara esté muy cerca simplemente recortamos el alto y perderemos parte de la imagen a presentar
    if face_left_x <= 0 and face_right_x >= width:
        #print("Puntos anchura:", face_left_x, face_right_x, width)
        face_left_x, face_right_x = 0, width
        face_top_y = int(center_h - width/2)
        face_bottom_y = int(center_h + width/2)

    # Limpiar coordenadas del cuadro de la cara
    # Nos aseguramos de que el ROI no seleccione algo fuera del frame
    if face_left_x < 0: face_left_x = 0
    if face_right_x > width: face_right_x = width
    if face_top_y < 0: face_top_y = 0
    if face_bottom_y > height: face_bottom_y = height

    return (nostril_l_point, nostril_r_point, nose_point, top_point, bottom_point), \
           (face_left_x, face_right_x, face_top_y, face_bottom_y)


def add_points_to_image(image, movement_points, face_rectangle_points):
    nostril_l_point, nostril_r_point, nose_point, q_point, top_point, bottom_point = movement_points
    face_left_x, face_right_x, face_top_y, face_bottom_y = face_rectangle_points
    thikness_factor = (face_right_x - face_left_x)/image.shape[1] # ancho de cara / ancho de imagen, este es un factor de cercanía
    thikness_factor = 0.5 if thikness_factor<=0.5 else thikness_factor

    cv2.line(image, nostril_l_point, nostril_r_point, (0, 255, 0), 2)
    cv2.circle(image,
               nose_point, round(5*thikness_factor),
               (0, 0, 255), -1)
    cv2.circle(image,
               q_point, round(5*thikness_factor),
               (0, 0, 255), -1)

    cv2.circle(image,
               top_point, round(5*thikness_factor),
               (255, 0, 0), -1)
    cv2.circle(image,
               bottom_point, round(5*thikness_factor),
               (255, 0, 0), -1)

    cv2.line(image, (face_left_x, face_top_y), (face_right_x, face_top_y), (150, 255, 0), round(2*thikness_factor))
    cv2.line(image, (face_left_x, face_bottom_y), (face_right_x, face_bottom_y), (150, 255, 0), round(2*thikness_factor))
    cv2.line(image, (face_left_x, face_top_y), (face_left_x, face_bottom_y), (150, 255, 0), round(2*thikness_factor))
    cv2.line(image, (face_right_x, face_top_y), (face_right_x, face_bottom_y), (150, 255, 0), round(2*thikness_factor))


def detect_face(image,
                verbose=False
                ):
    height, width, _ = image.shape
    # Convertir la imagen de BGR a RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Detectar rostros en la imagen
    results = mp_face_mesh.process(image_rgb)
    if results.multi_face_landmarks:
        #print("Número de caras detectadas: {}".format(len(results.multi_face_landmarks)))
        for face_landmarks in results.multi_face_landmarks:
            movement_points, face_rectangle_points = get_points(face_landmarks, (height, width))
            nostril_l_point, nostril_r_point, nose_point, top_point, bottom_point = movement_points

            distance, q_point = distance_nose(nostril_l=nostril_l_point,
                                              nostril_r=nostril_r_point,
                                              nose=nose_point,
                                              verbose=verbose
                                              )
            if verbose: print("\ndistance:", distance)
            length_head = sqrt((top_point[0] - bottom_point[0]) ** 2 + (top_point[1] - bottom_point[1]) ** 2)
            absolute_distance = round(distance / length_head, 3)
            if verbose: print("\tdistance absolute:", absolute_distance)

            if abs(distance) >= 0 and verbose:
                print("nose: {}  -  {}".format(nose_point[0], nose_point[1]))
                print("nostril L: {}  -  {}".format(nostril_l_point[0], nostril_l_point[1]))
                print("nostril R: {}  -  {}".format(nostril_r_point[0], nostril_r_point[1]))
                print("Q: {}  -  {}".format(q_point[0], q_point[1]))

            # Dibujar la línea que conecta los puntos
            add_points_to_image(image=image,
                                movement_points=(nostril_l_point, nostril_r_point, nose_point, q_point, top_point, bottom_point),
                                face_rectangle_points=face_rectangle_points)

            # Selección del ROI de la cara
            face_left_x, face_right_x, face_top_y, face_bottom_y = face_rectangle_points
            height_ROI, width_ROI = (face_bottom_y - face_top_y, face_right_x - face_left_x)
            #print("----- NEW Dimensión ROI:", height_ROI, width_ROI)
            roi = image[face_top_y: face_bottom_y,
                        face_left_x: face_right_x,
                        :]
            resized_image = cv2.resize(roi, (width, width)) # Garantizamos una imagen cuadrada del mismo tamaño constante
            return resized_image

    # ROI por defecto sin imagen detectada
    return image[int(height*4/10-width/2): int(height*4/10+width/2), :, :]


def main():
    # Inicializar la captura de video desde la cámara
    webcam = Webcam().start()
    time.sleep(1)  # Darle tiempo a que se inicialice

    while True:
        # Leer un frame del video
        frame = webcam.read()

        # Comprobar si se ha podido leer el frame correctamente
        if frame is None:
            print("Cámara no detectada")
            break

        frame = cv2.flip(frame, 1)

        # Obtener el ancho y alto del frame
        height, width, _ = frame.shape

        # Dividir el frame en dos mitades
        half_width = width // 2
        left_frame = frame[:, :half_width, :]
        right_frame = frame[:, half_width:, :]

        # Detección de rostros y puntos
        left_frame_ROI = detect_face(left_frame, verbose=False)
        right_frame_ROI = detect_face(right_frame, verbose=False)

        # Mostrar las dos mitades del frame
        #cv2.imshow('Video LEFT', left_frame)
        #cv2.imshow('Video RIGHT', right_frame)
        cv2.imshow('Video LEFT', left_frame_ROI)
        cv2.imshow('Video RIGHT', right_frame_ROI)

        # Salir del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) == ord('q'):
            break

    # Liberar los recursos
    #webcam.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

