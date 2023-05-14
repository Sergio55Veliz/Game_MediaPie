import pygame

# Inicializar Pygame
pygame.init()

# Configurar la ventana
width = 800
height = 600
window = pygame.display.set_mode((width, height))

# Configurar los cuadrados
square_size = 50
square_color_left = (255, 0, 0)
square_color_right = (0, 0, 255)
left_square_x = 50
right_square_x = width - square_size - 50
left_square_y = height // 2 - square_size // 2
right_square_y = height // 2 - square_size // 2
left_square_speed = 0
right_square_speed = 0

# Bucle principal del juego
running = True
while running:
    # Manejar eventos
    for event in pygame.event.get():
        print("event")
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Controlar el cuadrado izquierdo
            if event.key == pygame.K_w:
                left_square_speed = -5
            elif event.key == pygame.K_s:
                left_square_speed = 5
            # Controlar el cuadrado derecho
            elif event.key == pygame.K_UP:
                right_square_speed = -5
            elif event.key == pygame.K_DOWN:
                right_square_speed = 5
            print("LEFT: {}  -  RIGHT: {}".format(left_square_y, right_square_y))
        elif event.type == pygame.KEYUP:
            # Detener el movimiento del cuadrado izquierdo
            if event.key == pygame.K_w or event.key == pygame.K_s:
                left_square_speed = 0
            # Detener el movimiento del cuadrado derecho
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                right_square_speed = 0
            print("LEFT: {}  -  RIGHT: {}".format(left_square_y, right_square_y))

    # Actualizar la posición de los cuadrados
    left_square_y += left_square_speed
    right_square_y += right_square_speed

    # Comprobar si los cuadrados chocan con los bordes de la ventana
    if left_square_y < 0:
        left_square_y = 0
    elif left_square_y > height - square_size:
        left_square_y = height - square_size
    if right_square_y < 0:
        right_square_y = 0
    elif right_square_y > height - square_size:
        right_square_y = height - square_size

    # Dibujar los cuadrados en la ventana
    window.fill((255, 255, 255))
    left_square = pygame.draw.rect(window, square_color_left, (left_square_x, left_square_y, square_size, square_size))
    right_square = pygame.draw.rect(window, square_color_right, (right_square_x, right_square_y, square_size, square_size))

    # Actualizar la pantalla
    pygame.display.flip()

# Cerrar Pygame al salir
pygame.quit()
