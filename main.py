from __init__ import *
from player import *


def draw_text(screen, text, size, x, y):
    font = pygame.font.SysFont("serif", size)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)


def showFinishScreen(screen, clock, message_winner):
    #screen.blit(background, [0, 0])
    draw_text(screen, "MediaPie SHOOTER", 62, WIDTH // 2, HEIGHT / 4)
    draw_text(screen, message_winner, 27, WIDTH // 2, HEIGHT // 2)
    draw_text(screen, "Press key to FINISH", 17, WIDTH // 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shooter")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()

    player_r = Player(TypePlayer.RIGHT)
    player_l = Player(TypePlayer.LEFT)
    all_sprites.add(player_r)
    all_sprites.add(player_l)

    # Game Loop
    running = True
    game_over = False
    while running:
        if game_over:
            message_winner = messageWinner(player_r, player_l)
            showFinishScreen(screen, clock, message_winner)
            running = False

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
                    player_l.bullets.add(bullet_l)
                if event.key == pygame.K_LEFT:
                    player_r.shoot()
                    bullet_r = player_r.shoot()
                    all_sprites.add(bullet_r)
                    player_r.bullets.add(bullet_r)
        # Update
        # screen.blit(player.surf, player.rect)
        all_sprites.update()

        # Colisiones players - laser
        hits_pl = pygame.sprite.spritecollide(player_l, player_r.bullets, True)  # Collides player left
        for hit in hits_pl:
            player_l.live.value -= 25
            if player_l.live.value <= 0:
                # running = False
                game_over = True

        hits_pr = pygame.sprite.spritecollide(player_r, player_l.bullets, True)  # Collides player right
        for hit in hits_pr:
            player_r.live.value -= 25
            if player_r.live.value <= 0:
                # running = False
                game_over = True

        # Draw / Render
        screen.fill(BLACK)
        all_sprites.draw(screen)

        # BARRA de vida
        player_r.live.draw_live_bar(screen, player_r.live.value)
        player_l.live.draw_live_bar(screen, player_l.live.value)

        # *after* drawing everything, flip the display.
        pygame.display.flip()

    pygame.quit()


def messageWinner(player_r, player_l):
    if player_r.live.value < player_l.live.value:
        return "Ganador: " + player_l.name
    elif player_r.live.value > player_l.live.value:
        return "Ganador: "+player_r.name
    elif player_r.live.value == player_l.live.value:
        return "EMPATE!!"


if __name__ == '__main__':
    main()
