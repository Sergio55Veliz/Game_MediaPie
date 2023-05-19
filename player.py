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

    def __init__(self, name, type, face_mesh):
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

        self.speed_y = 0

        # Bullets
        self.bullets = pygame.sprite.Group()

        # LIVE
        self.live = Live(BarPosition.RIGHT) if type == TypePlayer.RIGHT else Live(BarPosition.LEFT)

        # CAMARA
        self.face_mesh = face_mesh
        self.webcam = Webcam().start()
        self.tiempoFace = 0
        self.tiempoBoca = 0
        self.mouthWasOpen = False
        # for render camera
        self.max_face_surf_height = 0
        self.face_left_x = 0
        self.face_right_x = 0
        self.face_top_y = 0
        self.face_bottom_y = 0

    def update(self):
        self.process_camera()
        '''
        self.speed_y = 0
        keystate = pygame.key.get_pressed()
        if self.type == TypePlayer.LEFT:
            if keystate[pygame.K_w]:
                self.speed_y = -5
            if keystate[pygame.K_s]:
                self.speed_y = 5
        elif self.type == TypePlayer.RIGHT:
            if keystate[pygame.K_UP]:
                self.speed_y = -5
            if keystate[pygame.K_DOWN]:
                self.speed_y = 5
        '''

        self.rect.y += self.speed_y
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.y > HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
        if self.rect.y < 0:
            self.rect.y = 0
        # self.update_mask()

    def detec_head_top_down(self, top_point, bottom_point, nostril_l_point, nostril_r_point, nose_point):
        distance = self.distance_nose(nostril_l=nostril_l_point,
                                      nostril_r=nostril_r_point,
                                      nose=nose_point
                                      )
        print("distance:", distance)
        length_head = sqrt((top_point[0] - bottom_point[0]) ** 2 + (top_point[1] - bottom_point[1]) ** 2)
        absolute_distance = round(distance / length_head, 3)

        if self.tiempoFace > 40:
            if absolute_distance > 0.08:
                print("ARRIBA", absolute_distance)
                self.speed_y = - 5
                self.tiempoFace = 0
            elif absolute_distance < -0.04:
                print("ABAJO", absolute_distance)
                self.speed_y = + 5
                self.tiempoFace = 0
            else:
                self.speed_y = 0

        self.tiempoFace += 1

    def process_camera(self):
        image = self.webcam.read()

        if image is not None:
            image.flags.writeable = False
            image = cv2.flip(image, 1)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            results = self.face_mesh.process(image)
            self.webcam_image = image
            cv2.imshow("camara", image)
            if results.multi_face_landmarks is not None:
                for face_landmarks in results.multi_face_landmarks:
                    (top, bottom), (nose_point, nostril_l_point, nostril_r_point), relative_distance = self.drawLines(
                        face_landmarks)

                    if self.tiempoBoca > 10:
                        if not self.mouthWasOpen and relative_distance > 10:
                            pygame.event.post(pygame.event.Event(MOUTH_OPENED))

                            print("abierta", self.tiempoBoca)
                            '''
                            laser = Laser()
                            # posicion  de nave con el cohete
                            laser.rect.x = self.player.rect.x
                            laser.rect.y = self.player.rect.y
                            self.laser.add(laser)
                            '''
                            # Ejecutamos el disparo
                            self.shoot()
                            self.mouthWasOpen = True
                        elif self.mouthWasOpen and relative_distance < 6:
                            pygame.event.post(pygame.event.Event(MOUTH_CLOSED))

                            print("Cerrado", self.tiempoBoca)
                            self.mouthWasOpen = False
                        self.tiempoBoca = 0
                    self.tiempoBoca += 1

                    # Deteccion de angulo
                    # self.detect_head_movement(top, bottom)

                    # Detección Mover arriba abajo
                    self.detec_head_top_down(top, bottom, nose_point, nostril_l_point, nostril_r_point)

    def drawLines(self, face_landmarks):
        # Obtener los puntos de la frente y barbilla
        top = (int(face_landmarks.landmark[10].x * self.webcam.width()),
               int(face_landmarks.landmark[10].y * self.webcam.height()))
        bottom = (int(face_landmarks.landmark[152].x * self.webcam.width()),
                  int(face_landmarks.landmark[152].y * self.webcam.height()))

        topmouth = (int(face_landmarks.landmark[13].x * self.webcam.width()),
                    int(face_landmarks.landmark[13].y * self.webcam.height()))
        downmouth = (int(face_landmarks.landmark[14].x * self.webcam.width()),
                     int(face_landmarks.landmark[14].y * self.webcam.height()))

        # Obtener los puntos de nariz y fosas nazales
        nose_point = (int(face_landmarks.landmark[1].x * self.webcam.width()),
                      int(face_landmarks.landmark[1].y * self.webcam.height()))
        nostril_l_point = (int(face_landmarks.landmark[203].x * self.webcam.width()),
                           int(face_landmarks.landmark[203].y * self.webcam.height()))
        nostril_r_point = (int(face_landmarks.landmark[423].x * self.webcam.width()),
                           int(face_landmarks.landmark[423].y * self.webcam.height()))

        # Obtener coordenadas del 'cuadrado' de la cara para poder mostrarlo en la pantalla despues
        self.face_left_x = face_landmarks.landmark[234].x
        self.face_right_x = face_landmarks.landmark[454].x
        self.face_top_y = face_landmarks.landmark[10].y
        self.face_bottom_y = face_landmarks.landmark[152].y

        # Dejar algo de espacio alrededor
        self.face_left_x = self.face_left_x - .1
        self.face_right_x = self.face_right_x + .1
        self.face_top_y = self.face_top_y - .1
        self.face_bottom_y = self.face_bottom_y + .1

        '''
        # Linea media
        cv2.line(
            self.webcam_image,
            top, bottom,
            (0, 255, 0), 3
        )
        '''

        # Draw frente y barbilla
        cv2.circle(self.webcam_image,
                   top, 8,
                   (0, 0, 255), -1)
        cv2.circle(self.webcam_image,
                   bottom, 8,
                   (0, 0, 255), -1)
        # nariz
        cv2.line(self.webcam_image, nostril_l_point, nostril_r_point, (0, 255, 0), 2)
        cv2.circle(self.webcam_image,
                   nose_point, 5,
                   (0, 0, 255), -1)

        # boca Abierta
        distanceBetweenMouthPoints = sqrt(
            pow(int(topmouth[0]) - int(downmouth[0]), 2) +
            pow(int(topmouth[1]) - int(downmouth[1]), 2)
        )
        face_height = (int(bottom[1]) - int(top[1]))

        # Obtener la distancia real de la boca dividida entre la cara
        # para que sea mas 'relativamente constante'
        real_distance = int(distanceBetweenMouthPoints) * self.webcam.height()
        relative_distance = int(real_distance) / int(face_height)

        return (top, bottom), (nose_point, nostril_l_point, nostril_r_point), relative_distance

    def distance_nose(self, nostril_l, nostril_r, nose):
        n_x, n_y = nose
        nl_x, nl_y = nostril_l
        nr_x, nr_y = nostril_r

        # ax + by + c = 0
        m = (nr_y - nl_y) / (nr_x - nl_x)
        a, b, c = -m, 1, -nr_y + m * nr_x
        #print("pendiente: ", m)
        distance = (a * n_x + b * n_y + c) / sqrt(a ** 2 + b ** 2)

        return distance

    def shoot(self):
        direction = BulletDirection.RIGHT if self.type == TypePlayer.LEFT else BulletDirection.LEFT
        bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
        self.bullets.add(bullet)

        # Agregamos sonido
        Bullet.sound_play()
