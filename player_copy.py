from __init__ import *
from bullet import*
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
        super(Player, self).__init__()
        self.type = type

        #self.surf = pygame.image.load("assets/player.png").convert_alpha()
        self.image = pygame.image.load("assets/player.png").convert()
        self.image.set_colorkey(BLACK)

        #self.rect = self.surf.get_rect()
        self.rect = self.image.get_rect()
        #self.original_surf = self.surf
        self.rect.centery = HEIGHT // 2
        self.rect.centerx = WIDTH // 2
        '''
        if type.value == TypePlayer.LEFT.value:
            self.rect.left = 20
            self.surf = pygame.transform.rotate(self.image, -90)
        elif type.value == TypePlayer.RIGHT.value:
            #self.rect.right = WIDTH - 10
            self.rect.right = 0
            self.surf = pygame.transform.rotate(self.image, 90)
        '''
        self.speed_y = 0

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

    def shoot(self, all_sprites, bullets):
        bullet = Bullet(self.rect.centery, self.rect.top)
        all_sprites.add(bullet)
        all_sprites.add(bullet)
        bullets.add(bullet)

        # Agregamos sonido
        bullet.sound_play()


all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player(TypePlayer.LEFT)
all_sprites.add(player)

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
    #screen.blit(player.surf, player.rect)
    all_sprites.update()

    # Draw / Render
    screen.fill(BLACK)
    #all_sprites.draw(screen)
    # *after* drawing everything, flip the display.
    pygame.display.flip()

pygame.quit()
