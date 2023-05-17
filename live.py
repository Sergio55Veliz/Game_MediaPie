import pygame
from constants import *
from enum import Enum


class BarPosition(Enum):  # enum class
	RIGHT = 1
	LEFT = 0


class Live(pygame.sprite.Sprite):
	def __init__(self, barPosition, y=5):
		super().__init__()
		self.value = 100
		self.BAR_LENGHT = 100
		self.BAR_HEIGHT = 10
		self.barPosition = barPosition
		self.y = y
		self.x = 5
		if self.barPosition == BarPosition.RIGHT:
			self.x = WIDTH - self.BAR_LENGHT - 5

	def draw_live_bar(self, screen, percentage):
		fill = (percentage / 100) * self.BAR_LENGHT
		border = pygame.Rect(self.x, self.y, self.BAR_LENGHT, self.BAR_HEIGHT)
		posx = self.x + ((1 - percentage / 100) * self.BAR_LENGHT) * self.barPosition.value
		fill = pygame.Rect(posx, self.y, fill, self.BAR_HEIGHT)
		pygame.draw.rect(screen, GREEN, fill)
		pygame.draw.rect(screen, WHITE, border, 2)
