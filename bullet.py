import pygame
from constants import *
from enum import Enum

sound = pygame.mixer.Sound("assets/laser5.ogg")


class BulletDirection(Enum):  # enum class
    RIGHT = 1
    LEFT = -1


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.direction = direction
        self.original_surf = pygame.image.load("assets/laser1.png")
        self.original_surf.set_colorkey(BLACK)

        if self.direction == BulletDirection.LEFT:
            self.image = pygame.transform.rotate(self.original_surf, 90)
        elif self.direction == BulletDirection.RIGHT:
            self.image = pygame.transform.rotate(self.original_surf, -90)

        self.rect = self.image.get_rect()
        self.rect.y = y - self.rect.height/2
        self.rect.centerx = x
        self.speedx = 10 * direction.value

    def update(self):
        self.rect.x += self.speedx
        print(self.rect.left, "-", self.rect.right)
        if self.direction == BulletDirection.LEFT and self.rect.left < 0:
            self.kill()
        elif self.direction == BulletDirection.RIGHT and self.rect.right > WIDTH:
            self.kill()

    @staticmethod
    def sound_play():
        sound.play()
