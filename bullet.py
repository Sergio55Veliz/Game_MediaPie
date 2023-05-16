import pygame
from constants import*
from player import TypePlayer


sound = pygame.mixer.Sound("assets/laser5.ogg")


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, typePlayer: TypePlayer):
		super().__init__()
		self.image = pygame.image.load("assets/laser1.png")
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.centerx = x
		self.speedx = -10

	def update(self):
		self.rect.x += self.speedx
		if self.rect.bottom < 0:
			self.kill()

	def sound_play(self):
		sound.play()
