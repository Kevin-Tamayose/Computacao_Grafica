import pygame
from pygame.locals import DOUBLEBUF, OPENGL, KEYDOWN, K_ESCAPE, K_l, K_LEFT, K_RIGHT, K_UP, K_DOWN
import OpenGL.GL as GL
import OpenGL.GLU as GLU
import math

from core.camera import Camera
from graphics.geometry import draw_room, draw_flashlight, load_floor_texture, load_wall_texture
from graphics.lighting import setup_lighting, update_flashlight_light

# =====================================================================
# Configurações Iniciais e Variáveis Globais
# =====================================================================
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Sala retangular: metade da largura no eixo X e metade da profundidade no eixo Z
ROOM_WIDTH = 36
ROOM_DEPTH = 24
ROOM_HEIGHT = 24
ROOM_DIVS_X = 20
ROOM_DIVS_Z = 16
ROOM_DIVS_Y = 24

# Câmera e controle de jogador serão gerenciados em Camera

# A rotação e o estado da lanterna são controlados localmente no loop principal.

# =====================================================================
# Funções de Geometria
# =====================================================================
# As funções de desenho da sala e da lanterna foram movidas para geometry.py.
# Isso mantém o main.py focado no controle do fluxo do programa.

# =====================================================================
# Loop Principal
# =====================================================================
def main():
    pygame.init()
    display = (WINDOW_WIDTH, WINDOW_HEIGHT)
    camera = Camera(room_width=ROOM_WIDTH, room_depth=ROOM_DEPTH)
    flash_yaw = 0.0
    flash_pitch = 0.0
    light_on = True
    # DOUBLEBUF (2 buffers para evitar flickering) e OPENGL (contexto 3D)
    pygame.display.set_mode(display, int(DOUBLEBUF) | int(OPENGL))
    pygame.display.set_caption("Projeto CG - Síntese de Imagem (Lanterna)")
    
    # Esconde o cursor do mouse e o prende na janela (estilo FPS)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    GL.glEnable(GL.GL_DEPTH_TEST) # Habilita o teste de profundidade (Z-Buffer)
    setup_lighting()
    
    # Carrega textura do chão
    floor_texture_id = load_floor_texture()
    wall_texture_id = load_wall_texture()
    # Repetição separada para piso e paredes
    floor_texture_repeat = 4.0
    wall_texture_repeat = 1.25

    # Matriz de Projeção (Define a lente da Câmera)
    # O far plane é ajustado dinamicamente com base no tamanho da sala
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glLoadIdentity()
    far_plane = max(50.0, max(ROOM_WIDTH, ROOM_DEPTH, ROOM_HEIGHT) * 5)  # Escala o far plane com a sala
    GLU.gluPerspective(60, (display[0]/display[1]), 0.1, far_plane) # FOV, Aspect Ratio, Near, Far

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0 # Delta time (segundos por frame)
        
        # 1. TRATAMENTO DE EVENTOS ====================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_l: # Tecla L liga/desliga a lanterna
                    light_on = not light_on

        # Movimento da Câmera (Mouse)
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        camera.update_mouse(mouse_dx, mouse_dy)

        # Movimento da Câmera (Teclado - WASD)
        keys = pygame.key.get_pressed()
        camera.update_keyboard(keys, dt)
        
        # Movimento da Lanterna (Setas do Teclado)
        flash_speed = 90.0 * dt
        if keys[K_LEFT]:  flash_yaw += flash_speed
        if keys[K_RIGHT]: flash_yaw -= flash_speed
        if keys[K_UP]:    flash_pitch += flash_speed
        if keys[K_DOWN]:  flash_pitch -= flash_speed

        # 2. RENDERIZAÇÃO =============================================
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glClear(int(GL.GL_COLOR_BUFFER_BIT) | int(GL.GL_DEPTH_BUFFER_BIT))

        # Matriz ModelView (Aplica as transformações no mundo/objetos)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        # Primeiro: Aplica a visão da câmera na cena (transforma o mundo)
        camera.apply_transform()

        # Segundo: Posiciona a luz NO CENTRO DA CÂMERA após a transformação
        # Assim a lanterna segue o jogador
        update_flashlight_light(flash_yaw, flash_pitch, light_on)

        # Terceiro: Desenhar os objetos
        draw_room(
            size_x=ROOM_WIDTH,
            size_z=ROOM_DEPTH,
            size_y=ROOM_HEIGHT,
            divs_x=ROOM_DIVS_X,
            divs_z=ROOM_DIVS_Z,
            divs_y=ROOM_DIVS_Y,
            floor_texture_id=floor_texture_id,
            wall_texture_id=wall_texture_id,
            floor_texture_repeat=floor_texture_repeat,
            wall_texture_repeat=wall_texture_repeat,
        )
        draw_flashlight(flash_yaw, flash_pitch, light_on)

        # Atualiza a tela
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()