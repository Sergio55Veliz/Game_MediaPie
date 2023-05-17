from bullet import *
from live import *
from constants import *
from enum import Enum


class TypePlayer(Enum):  # enum class
    RIGHT = 0
    LEFT = 1


class Player(pygame.sprite.Sprite):

    def __init__(self, type):
        super().__init__()
        self.type = type

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

        # LIVE
        self.live = Live(BarPosition.RIGHT) if type == TypePlayer.RIGHT else Live(BarPosition.LEFT)

    def update(self):
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

        self.rect.y += self.speed_y
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.y > HEIGHT-self.rect.height:
            self.rect.y = HEIGHT-self.rect.height
        if self.rect.y < 0:
            self.rect.y = 0
        # self.update_mask()

    def shoot(self):
        direction = BulletDirection.RIGHT if self.type == TypePlayer.LEFT else BulletDirection.LEFT
        bullet = Bullet(self.rect.centerx, self.rect.centery, direction)

        # Agregamos sonido
        Bullet.sound_play()

        return bullet

    '''
    def update_mask(self):
        # Mascara tiene un 80% del tamano para 'perdonar' al jugador en ciertas colisiones
        maskSurface = self.surf
        maskSurface = pygame.transform.scale(maskSurface, (WIDTH * .8, HEIGHT * .8))
        self.mask = pygame.mask.from_surface(maskSurface)
    '''
