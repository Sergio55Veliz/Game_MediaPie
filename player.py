from bullet import *
from live import *
from constants import *
from events import *

from webcam import *
import mediapipe as mp
import math

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

    def detec_head_top_down(self, topMov, bottomMov):
        pointTop = topMov[1]
        pointDown = bottomMov[1]
        pointCor = round(pointDown, 3) - round(pointTop, 3)

        if self.tiempoFace > 40:

            if pointCor > 0.30:
                print("abajo")
                self.speed_y = + 1

            else:
                print("arriba")
                self.speed_y = - 1
                self.tiempoFace = 0

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
            if results.multi_face_landmarks is not None:
                for face_landmarks in results.multi_face_landmarks:
                    topMov, bottomMov, relative_distance = self.drawLines(face_landmarks)

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
                    #self.detect_head_movement(top, bottom)

                    # Detección Mover arriba abajo
                    self.detec_head_top_down(topMov, bottomMov)
                    # print((topMov[1], (bottomMov[1])))

    def drawLines(self, face_landmarks):
        # coordenadas de la cara (arriba y abajo)
        topMov = (face_landmarks.landmark[10].x, face_landmarks.landmark[10].y)
        bottomMov = (face_landmarks.landmark[152].x, face_landmarks.landmark[152].y)
        # codigo extra

        top = (int(face_landmarks.landmark[10].x * self.webcam.width()),
               int(face_landmarks.landmark[10].y * self.webcam.height()))
        bottom = (int(face_landmarks.landmark[152].x * self.webcam.width()),
                  int(face_landmarks.landmark[152].y * self.webcam.height()))

        topmouth = (int(face_landmarks.landmark[13].x * self.webcam.width()),
                    int(face_landmarks.landmark[13].y * self.webcam.height()))
        downmouth = (int(face_landmarks.landmark[14].x * self.webcam.width()),
                     int(face_landmarks.landmark[14].y * self.webcam.height()))

        # topmouth=(face_landmarks.landmark[13].x, face_landmarks.landmark[13].y)
        # downmouth=(face_landmarks.landmark[14].x, face_landmarks.landmark[14].y)

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

        cv2.line(
            self.webcam_image,
            (int(top[0] * self.webcam.width()), int(top[1] * self.webcam.height())),
            (int(bottom[0] * self.webcam.width()), int(bottom[1] * self.webcam.height())),
            (0, 255, 0), 3
        )

        # cordenadas circulo
        cv2.circle(self.webcam_image,
                   (int(topMov[0] * self.webcam.width()), int(topMov[1] * self.webcam.height())), 8,
                   (0, 0, 255), -1)
        cv2.circle(self.webcam_image,
                   (int(bottomMov[0] * self.webcam.width()), int(bottomMov[1] * self.webcam.height())), 8,
                   (0, 0, 255), -1)

        cv2.circle(self.webcam_image,
                   (int(top[0] * self.webcam.width()), int(top[1] * self.webcam.height())), 8, (0, 0, 255),
                   -1)
        cv2.circle(self.webcam_image,
                   (int(bottom[0] * self.webcam.width()), int(bottom[1] * self.webcam.height())), 8,
                   (0, 0, 255), -1)
        # extra
        cv2.circle(self.webcam_image,
                   (int(topmouth[0] * self.webcam.width()), int(topmouth[1] * self.webcam.height())), 8,
                   (255, 0, 0), -1)
        cv2.circle(self.webcam_image,
                   (int(downmouth[0] * self.webcam.width()), int(downmouth[1] * self.webcam.height())), 8,
                   (255, 0, 0), -1)

        # boca Abierta
        distanceBetweenMouthPoints = math.sqrt(
            pow(int(topmouth[0]) - int(downmouth[0]), 2) +
            pow(int(topmouth[1]) - int(downmouth[1]), 2)
        )
        face_height = (int(bottom[1]) - int(top[1]))

        # Obtener la distancia real de la boca dividida entre la cara
        # para que sea mas 'relativamente constante'
        real_distance = int(distanceBetweenMouthPoints) * self.webcam.height()

        relative_distance = int(real_distance) / int(face_height)

        return topMov, bottomMov, relative_distance

    def shoot(self):
        direction = BulletDirection.RIGHT if self.type == TypePlayer.LEFT else BulletDirection.LEFT
        bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
        self.bullets.add(bullet)

        # Agregamos sonido
        Bullet.sound_play()

