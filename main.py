from __init__ import *
from player import *

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shooter")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    player_r = Player(TypePlayer.RIGHT)
    player_l = Player(TypePlayer.LEFT)
    all_sprites.add(player_r)
    all_sprites.add(player_l)

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    player_l.shoot()
                    bullet_l = player_l.shoot()
                    all_sprites.add(bullet_l)
                    bullets.add(bullet_l)
                if event.key == pygame.K_LEFT:
                    player_r.shoot()
                    bullet_r = player_r.shoot()
                    all_sprites.add(bullet_r)
                    bullets.add(bullet_r)
        # Update
        # screen.blit(player.surf, player.rect)
        all_sprites.update()

        # Draw / Render
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # BARRA de vida
        player_r.live.draw_live_bar(screen, player_r.live.value)
        player_l.live.draw_live_bar(screen, player_l.live.value)

        # *after* drawing everything, flip the display.
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
