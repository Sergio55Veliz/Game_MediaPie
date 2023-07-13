from bullet import *
from live import *
from constants import *
from events import *

from webcam import *
import mediapipe as mp
from math import sqrt

from enum import Enum


class TypePlayer(Enum):  # enum class
    RIGHT = 0
    LEFT = 1


class Player(pygame.sprite.Sprite):

    def __init__(self, name, type, face_mesh=None):
        super().__init__()
        self.type = type
        self.name = name

        self.original_surf = pygame.image.load("assets/player.png").convert()
        self.original_surf.set_colorkey(BLACK)

        # Cual es la diferencia entre convert y convert_alpha ??

        self.rect = self.original_surf.get_rect()
        self.rect.centerx = WIDTH // 2

        if self.type == TypePlayer.LEFT:
            self.rect.left = 0
            self.image = pygame.transform.rotate(self.original_surf, -90)
        elif self.type == TypePlayer.RIGHT:
            self.rect.right = WIDTH
            self.image = pygame.transform.rotate(self.original_surf, 90)

        # Modo de control
        control_mode = input(f"\n{self.name} elija su preferencia de control:"
                             f"\t1. Control por teclado"
                             f"\t2. Control "
                             f"por Gestos\n\tELIJE (1 ó 2): ")
        while control_mode not in ["1", "2"]:
            print("\nXXXXX Elije solo entre los valores de 1 y 2 XXXXX")
            control_mode = input(
                f"\n{self.name} elija su preferencia de control:"
                f"\t1. Control por teclado"
                f"\t2. Control "
                f"Gestos\n\tELIJE (1 ó 2): ")
        if control_mode == "1":
            face_mesh = None

        self.speed_y = 0

        # Bullets
        self.bullets = pygame.sprite.Group()

        # LIVE
        self.live = Live(BarPosition.RIGHT) if type == TypePlayer.RIGHT else Live(BarPosition.LEFT)
        
        # CAMARA
        self.face_mesh = face_mesh
        if self.face_mesh is not None:
            self.init_camera_detection()

    def init_camera_detection(self):
        # CAMARA
        self.image_width = webcam.read()[self.type.value].shape[1]
        self.image_height = webcam.read()[self.type.value].shape[0]
        self.tiempoFace = 0
        self.tiempoBoca = 0
        # for render camera
        self.max_face_surf_height = 0
        # coor position ROI
        self.face_left_x = 0
        self.face_right_x = self.image_width
        self.face_top_y = int(self.image_height * 4 / 10 - self.image_width / 2)
        self.face_bottom_y = int(self.image_height * 4 / 10 + self.image_width / 2)

    def update(self):
        if self.face_mesh is not None:
            self.process_camera()
        else:
            self.speed_y = 0
            keystate = pygame.key.get_pressed()
            if self.type == TypePlayer.LEFT:
                if keystate[pygame.K_w]:
                    self.speed_y = -5
                if keystate[pygame.K_s]:
                    self.speed_y = 5
                if keystate[pygame.K_d]:
                    self.shoot()
                    print("Izquierda dispara")
            elif self.type == TypePlayer.RIGHT:
                if keystate[pygame.K_UP]:
                    self.speed_y = -5
                if keystate[pygame.K_DOWN]:
                    self.speed_y = 5
                if keystate[pygame.K_LEFT]:
                    self.shoot()
                    print("Derecha dispara")

        self.rect.y += self.speed_y
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.y > HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
        if self.rect.y < 0:
            self.rect.y = 0

    def detec_head_top_down(self, top_point, bottom_point, nostril_l_point, nostril_r_point, nose_point):
        distance = self.distance_nose(nostril_l=nostril_l_point,
                                      nostril_r=nostril_r_point,
                                      nose=nose_point
                                      )
        print("distance:", distance)
        length_head = sqrt((top_point[0] - bottom_point[0]) ** 2 + (top_point[1] - bottom_point[1]) ** 2)
        absolute_distance = round(distance / length_head, 3)

        if self.tiempoFace > 40:
            if absolute_distance > 0.14:
                print("ARRIBA", absolute_distance)
                self.speed_y = - 5
                self.tiempoFace = 0
            elif absolute_distance < -0.03:
                print("ABAJO", absolute_distance)
                self.speed_y = + 5
                self.tiempoFace = 0
            else:
                self.speed_y = 0

        self.tiempoFace += 1

    def process_camera(self):
        image = webcam.read()[self.type.value]
        self.webcam_image = image

        if image is not None:
            image.flags.writeable = True
            results = self.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            if results.multi_face_landmarks is not None:
                for face_landmarks in results.multi_face_landmarks:
                    movement_points, mouth_lenght = self.drawLines(face_landmarks)
                    (top, bottom), (nose_point, nostril_l_point, nostril_r_point) = movement_points

                    if self.tiempoBoca > 18:
                        if mouth_lenght > 30:
                            pygame.event.post(pygame.event.Event(MOUTH_OPENED))
                            print("abierta", self.tiempoBoca)
                            # Ejecutamos el disparo
                            self.shoot()

                        self.tiempoBoca = 0
                    self.tiempoBoca += 1

                    # Deteccion de angulo
                    # self.detect_head_movement(top, bottom)

                    # Detección Mover arriba abajo
                    self.detec_head_top_down(top, bottom, nose_point, nostril_l_point, nostril_r_point)

            # Mostrar en pantalla ROI
            # Si no se detecta rostro, el cuadro sigue de la misma dimensión que antes de que dejara de detectarlo
            roi = self.webcam_image[self.face_top_y: self.face_bottom_y,
                                    self.face_left_x: self.face_right_x,
                                    :]
            resized_image = cv2.resize(roi, (self.image_width, self.image_width))  # Garantizamos una imagen cuadrada del mismo tamaño constante
            cv2.imshow(self.name, resized_image)

    def drawLines(self, face_landmarks):
        # ---------------------------- Puntos para movimiento de nave -----------------------------
        # Obtener los puntos de la frente y barbilla
        top = (int(face_landmarks.landmark[10].x * self.image_width),
               int(face_landmarks.landmark[10].y * self.image_height))
        bottom = (int(face_landmarks.landmark[152].x * self.image_width),
                  int(face_landmarks.landmark[152].y * self.image_height))

        # Obtener los puntos de nariz y fosas nazales
        nose_point = (int(face_landmarks.landmark[1].x * self.image_width),
                      int(face_landmarks.landmark[1].y * self.image_height))
        nostril_l_point = (int(face_landmarks.landmark[203].x * self.image_width),
                           int(face_landmarks.landmark[203].y * self.image_height))
        nostril_r_point = (int(face_landmarks.landmark[423].x * self.image_width),
                           int(face_landmarks.landmark[423].y * self.image_height))

        # ---------------------------- Puntos para disparo de la nave -----------------------------
        # Obtener los puntos de la boca
        topmouth = (int(face_landmarks.landmark[13].x * self.image_width),
                    int(face_landmarks.landmark[13].y * self.image_height))
        downmouth = (int(face_landmarks.landmark[14].x * self.image_width),
                     int(face_landmarks.landmark[14].y * self.image_height))

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
        border = 0.1 * abs(face_right_x - face_left_x)
        face_left_x -= border
        face_right_x += border
        face_top_y -= border * 2
        face_bottom_y += border * 0.5
        # Obtener valores escalados
        face_left_x = int(face_left_x * self.image_width)
        face_right_x = int(face_right_x * self.image_width)
        face_top_y = int(face_top_y * self.image_height)
        face_bottom_y = int(face_bottom_y * self.image_height)

        height_ROI, width_ROI = (face_bottom_y - face_top_y, face_right_x - face_left_x)
        center_h, center_w = (face_top_y + height_ROI / 2, face_left_x + width_ROI / 2)
        # print("----- Dimensión ROI:", height_ROI, width_ROI)
        # Creamos un ROI cuadrado escogiendo el eje más grande
        if height_ROI < width_ROI:
            # print("ancho >>>>> alto")
            face_top_y = int(center_h - width_ROI / 2)
            face_bottom_y = int(center_h + width_ROI / 2)
        elif height_ROI > width_ROI:
            # print("ancho <<<<< alto")
            face_left_x = int(center_w - height_ROI / 2)
            face_right_x = int(center_w + height_ROI / 2)

        height_ROI, width_ROI = (face_bottom_y - face_top_y, face_right_x - face_left_x)
        center_h, center_w = (face_top_y + height_ROI / 2, face_left_x + width_ROI / 2)
        # Mitigamos el hecho de que una cara esté fuera de cuadro en uno de los lados
        if face_left_x < 0:
            face_right_x += (-1 * face_left_x)
            face_left_x = 0
        if face_right_x > self.image_width:
            face_left_x -= face_right_x - self.image_width
            face_right_x = self.image_width
        if face_top_y < 0:
            face_bottom_y += (-1 * face_top_y)
            face_top_y = 0
        if face_bottom_y > self.image_width:
            face_top_y -= face_bottom_y - self.image_width
            face_bottom_y = self.image_width

        height_ROI, width_ROI = (face_bottom_y - face_top_y, face_right_x - face_left_x)
        center_h, center_w = (face_top_y + height_ROI / 2, face_left_x + width_ROI / 2)
        # en caso de que la cara esté muy cerca simplemente recortamos el alto y perderemos parte de la imagen a presentar
        if face_left_x <= 0 and face_right_x >= self.image_width:
            # print("Puntos anchura:", face_left_x, face_right_x, self.image_width)
            face_left_x, face_right_x = 0, self.image_width
            face_top_y = int(center_h - self.image_width / 2)
            face_bottom_y = int(center_h + self.image_width / 2)

        # Limpiar coordenadas del cuadro de la cara
        # Nos aseguramos de que el ROI no seleccione algo fuera del frame
        if face_left_x < 0: face_left_x = 0
        if face_right_x > self.image_width: face_right_x = self.image_width
        if face_top_y < 0: face_top_y = 0
        if face_bottom_y > self.image_width: face_bottom_y = self.image_width

        # Actualizamos el valor aplicando la función de suavizado
        self.face_left_x = int(self.lerp(self.face_left_x, face_left_x, 0.3))
        self.face_right_x = int(self.lerp(self.face_right_x, face_right_x, 0.3))
        self.face_top_y = int(self.lerp(self.face_top_y, face_top_y, 0.5))
        self.face_bottom_y = int(self.lerp(self.face_bottom_y, face_bottom_y, 0.3))

        # -------------------------------- Draw LINES and POINTS ----------------------------------
        thikness_factor = (self.face_right_x - self.face_left_x) / self.image_width  # ancho de cara / ancho de imagen, este es un factor de cercanía
        thikness_factor = 0.5 if thikness_factor <= 0.5 else thikness_factor
        # Boca
        cv2.circle(self.webcam_image,
                   topmouth, round(6 * thikness_factor),
                   (0, 150, 150), -1)
        cv2.circle(self.webcam_image,
                   downmouth, round(6 * thikness_factor),
                   (0, 150, 150), -1)
        # nariz
        cv2.line(self.webcam_image, nostril_l_point, nostril_r_point, (0, 255, 0), round(2*thikness_factor))
        cv2.circle(self.webcam_image,
                   nose_point, round(5 * thikness_factor),
                   (0, 0, 255), -1)
        # Recuadro de rostro
        cv2.line(self.webcam_image,
                 (self.face_left_x, self.face_top_y), (self.face_right_x, self.face_top_y),
                 (150, 255, 0), round(2*thikness_factor))
        cv2.line(self.webcam_image,
                 (self.face_left_x, self.face_bottom_y), (self.face_right_x, self.face_bottom_y),
                 (150, 255, 0), round(2*thikness_factor))
        cv2.line(self.webcam_image,
                 (self.face_left_x, self.face_top_y), (self.face_left_x, self.face_bottom_y),
                 (150, 255, 0), round(2*thikness_factor))
        cv2.line(self.webcam_image,
                 (self.face_right_x, self.face_top_y), (self.face_right_x, self.face_bottom_y),
                 (150, 255, 0), round(2*thikness_factor))

        # -----------------------------------------------------------------------------------------
        # ----------------------------- Apertura de boca para disparo -----------------------------
        # boca Abierta
        distance_between_mouthPoints = sqrt(
            pow(int(topmouth[0]) - int(downmouth[0]), 2) +
            pow(int(topmouth[1]) - int(downmouth[1]), 2)
        )
        face_height = (int(bottom[1]) - int(top[1]))

        # Obtener la distancia real de la boca dividida entre la cara
        # para que sea mas 'relativamente constante'
        real_distance = int(distance_between_mouthPoints) * self.image_height
        relative_distance = int(real_distance) / int(face_height)  # Solucionado problema de lejanía
                                                                   # de que la distancia varía con qué tan lejos se está

        return ((top, bottom), (nose_point, nostril_l_point, nostril_r_point)), relative_distance

    def distance_nose(self, nostril_l, nostril_r, nose) -> float:
        # Ecuación de distancia de punto a la recta
        n_x, n_y = nose  # El punto
        nl_x, nl_y = nostril_l  # recta
        nr_x, nr_y = nostril_r  # recta

        # ax + by + c = 0  <- La recta
        m = (nr_y - nl_y) / (nr_x - nl_x)  # pendiente de la recta
        a, b, c = -m, 1, -nr_y + m * nr_x

        distance = (a * n_x + b * n_y + c) / sqrt(a ** 2 + b ** 2)

        return distance

    def lerp(self, a: float, b: float, t: float) -> float:
        #Funcion para suavizado de movimiento
        return (1 - t) * a + t * b

    def shoot(self):
        direction = BulletDirection.RIGHT if self.type == TypePlayer.LEFT else BulletDirection.LEFT
        bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
        self.bullets.add(bullet)

        # Agregamos sonido
        Bullet.sound_play()
