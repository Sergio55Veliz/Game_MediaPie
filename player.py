from __init__ import *
from bullet import *
from constants import*


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter")
clock = pygame.time.Clock()


from enum import Enum


class TypePlayer(Enum):  # enum class
    RIGHT = 0
    LEFT = 1


class Player(pygame.sprite.Sprite):

    def __init__(self, type):
        super().__init__()
        self.type = type

        #self.image = pygame.image.load("assets/player.png").convert()
        #self.image.set_colorkey(BLACK)

        # Cual es la diferencia entre convert y convert_alpha ??

        self.surf = pygame.image.load("assets/player.png").convert_alpha()
        self.update_mask()
        self.original_surf = self.surf

        #self.rect = self.image.get_rect()
        self.rect = self.surf.get_rect()
        self.rect.centerx = WIDTH // 2
        #self.rect.bottom = HEIGHT - 10

        if self.type == TypePlayer.LEFT:
            self.rect.left = 0
            self.surf = pygame.transform.rotate(self.original_surf, 0.5)
        elif self.type == TypePlayer.RIGHT:
            self.rect.right = WIDTH
            self.surf = pygame.transform.rotate(self.original_surf, 1)

        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if self.type == TypePlayer.LEFT:
            if keystate[pygame.K_w]:
                self.speed_x = -5
            if keystate[pygame.K_s]:
                self.speed_x = 5
        elif self.type == TypePlayer.RIGHT:
            if keystate[pygame.K_UP]:
                self.speed_x = -5
            if keystate[pygame.K_DOWN]:
                self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        self.update_mask()

    def update_mask(self):
        # Mascara tiene un 80% del tamano para 'perdonar' al jugador en ciertas colisiones
        maskSurface = self.surf
        maskSurface = pygame.transform.scale(maskSurface, (WIDTH * .8, HEIGHT * .8))
        self.mask = pygame.mask.from_surface(maskSurface)


all_sprites = pygame.sprite.Group()

player = Player(TypePlayer.RIGHT)
#all_sprites.add(player)

# Game Loop
running = True
while running:
    # Keep loop running at the right speed
    clock.tick(60)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

    # Update
    screen.blit(player.surf, player.rect)
    all_sprites.update()

    # Draw / Render
    screen.fill(BLACK)
    #all_sprites.draw(screen)
    # *after* drawing everything, flip the display.
    pygame.display.flip()

pygame.quit()
