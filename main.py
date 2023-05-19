import time

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
    # Consola
    print("""
*************************************
        Mensaje de Bienvenida
*************************************
    """)
    player_r_name = input("Ingrese el nombre del jugador de la derecha: ")
    player_l_name = input("Ingrese el nombre del jugador de la izquierda: ")

    # Iniciando la ventana de pygame
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shooter")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()

    # Game Loop
    running = True
    # TODO: Hacer pantalla de inicio del juego
    #has_started = False
    has_started = True
    game_over = False

    # Facemesh
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    with mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            refine_landmarks=True
    ) as face_mesh:
        
        
        player_r = Player(player_r_name, TypePlayer.RIGHT, face_mesh)
        player_l = Player(player_l_name, TypePlayer.LEFT,face_mesh)
        all_sprites.add(player_r)
        all_sprites.add(player_l)

        while running:
            '''
            events = [e.type for e in pygame.event.get()]
            if pygame.QUIT in events:
                print("Si funciona, hay que remover los for y dejarlo en una sola variable events")
            '''
            for event in pygame.event.get():
                # check for closing window
                if event.type == pygame.QUIT:
                    running = False

            if not has_started:
                # TODO: Ventana de inicio
                for event in pygame.event.get():
                    #Cuando no hemos empezado, ENTER comienza el juego
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        has_started = True
            else:
                if game_over:
                    #message_winner = messageWinner(player_r, player_l)
                    #showFinishScreen(screen, clock, message_winner)
                    running = False

                # Keep loop running at the right speed
                clock.tick(60)
                # Process input (events)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_d:
                            #player_l.shoot()
                            print("Izquierda dispara")
                        if event.key == pygame.K_LEFT:
                            player_r.shoot()
                            print("Derecha dispara")
                # Update
                # screen.blit(player.surf, player.rect)
                all_sprites.update()
                player_r.bullets.update()
                player_l.bullets.update()

                ########algoinixio
                
                ########algofin
                
                # Cancelar disparos del oponente (colisiones entre los lasers)
                #pygame.sprite.groupcollide(player_r.bullets, player_l.bullets, True, True)  # Collides player right

                # Colisiones players - laser
                #hits_pl = pygame.sprite.spritecollide(player_l, player_r.bullets, True)  # Collides player left
                #for hit in hits_pl:
                #    player_l.live.value -= 25
                #    if player_l.live.value <= 0:
                #        # running = False
                #        game_over = True

                #hits_pr = pygame.sprite.spritecollide(player_r, player_l.bullets, True)  # Collides player right
                #for hit in hits_pr:
                #    player_r.live.value -= 25
                #    if player_r.live.value <= 0:
                #        # running = False
                #        game_over = True

                # Draw / Render
                screen.fill(BLACK)
                all_sprites.draw(screen)
                player_r.bullets.draw(screen)
                #player_l.bullets.draw(screen)

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
