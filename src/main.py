import numpy as np

import pygame
from pygame.locals import DOUBLEBUF, OPENGL, KEYDOWN, K_ESCAPE, K_l, K_LEFT, K_RIGHT, K_UP, K_DOWN
import OpenGL.GL as GL
import OpenGL.GLU as GLU
from dataclasses import dataclass

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

HUD_BG_COLOR = (10, 14, 22, 210)
HUD_PANEL_COLOR = (255, 255, 255, 28)
HUD_TITLE_COLOR = (255, 238, 200)
HUD_TEXT_COLOR = (235, 235, 235)
HUD_ACCENT_COLOR = (255, 214, 120)


@dataclass
class GameState:
    flash_yaw: float = 0.0
    flash_pitch: float = 0.0
    light_on: bool = True
    menu_view: str = "game"

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
def set_mouse_capture(menu_open):
    pygame.mouse.set_visible(menu_open)
    pygame.event.set_grab(not menu_open)


def draw_hud(display, state, title_font, body_font):
    hud_surface = pygame.Surface(display, pygame.SRCALPHA)
    hud_surface.fill((0, 0, 0, 0))

    if state.menu_view != "game":
        hud_surface.fill(HUD_BG_COLOR)

        panel_width = 560
        panel_height = 280 if state.menu_view == "pause" else 300
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill(HUD_PANEL_COLOR)
        pygame.draw.rect(panel, (255, 255, 255, 64), panel.get_rect(), 2, border_radius=18)

        panel_x = (display[0] - panel_width) // 2
        panel_y = (display[1] - panel_height) // 2
        hud_surface.blit(panel, (panel_x, panel_y))

        title_text = "PAUSA" if state.menu_view == "pause" else "CONTROLES"
        title = title_font.render(title_text, True, HUD_TITLE_COLOR)
        hud_surface.blit(title, (panel_x + 28, panel_y + 24))

        if state.menu_view == "pause":
            lines = [
                "ESC: voltar ao jogo",
                "C: mostrar controles",
                "Q: sair do jogo",
                f"Lanterna: {'ligada' if state.light_on else 'desligada'}",
            ]
        else:
            lines = [
                "ESC: voltar para pausa",
                "WASD: mover",
                "Mouse: olhar",
                "Setas: orientar a lanterna",
                "L: liga/desliga a lanterna",
            ]
        y = panel_y + 88
        for index, line in enumerate(lines):
            color = HUD_ACCENT_COLOR if index == 0 else HUD_TEXT_COLOR
            text = body_font.render(line, True, color)
            hud_surface.blit(text, (panel_x + 32, y))
            y += 34
    else:
        status = body_font.render(
            f"ESC: menu   L: lanterna ({'on' if state.light_on else 'off'})   WASD: mover   Mouse: olhar",
            True,
            HUD_TEXT_COLOR,
        )
        hud_surface.blit(status, (18, 14))

    hud_data = pygame.image.tostring(hud_surface, "RGBA", True)

    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPushMatrix()
    GL.glLoadIdentity()
    GL.glOrtho(0, display[0], 0, display[1], -1, 1)

    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glPushMatrix()
    GL.glLoadIdentity()

    GL.glDisable(GL.GL_LIGHTING)
    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
    GL.glRasterPos2i(0, 0)
    GL.glDrawPixels(display[0], display[1], GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, hud_data)

    GL.glDisable(GL.GL_BLEND)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_LIGHTING)

    GL.glMatrixMode(GL.GL_MODELVIEW)
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_MODELVIEW)


def main():
    pygame.init()
    pygame.font.init()
    display = (WINDOW_WIDTH, WINDOW_HEIGHT)
    camera = Camera(room_width=ROOM_WIDTH, room_depth=ROOM_DEPTH)
    state = GameState()
    title_font = pygame.font.SysFont("Arial", 42, bold=True)
    body_font = pygame.font.SysFont("Arial", 26)
    # DOUBLEBUF (2 buffers para evitar flickering) e OPENGL (contexto 3D)
    pygame.display.set_mode(display, int(DOUBLEBUF) | int(OPENGL))
    pygame.display.set_caption("Projeto CG - Síntese de Imagem (Lanterna)")

    set_mouse_capture(state.menu_view != "game")

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
                    if state.menu_view == "game":
                        state.menu_view = "pause"
                    elif state.menu_view == "pause":
                        state.menu_view = "game"
                    else:
                        state.menu_view = "pause"
                    set_mouse_capture(state.menu_view != "game")
                if state.menu_view == "pause" and event.key == pygame.K_c:
                    state.menu_view = "controls"
                if state.menu_view == "pause" and event.key == pygame.K_q:
                    running = False
                if event.key == K_l and state.menu_view == "game": # Tecla L liga/desliga a lanterna
                    state.light_on = not state.light_on

        if state.menu_view == "game":
            # Movimento da Câmera (Mouse)
            mouse_dx, mouse_dy = pygame.mouse.get_rel()
            camera.update_mouse(mouse_dx, mouse_dy)

            # Movimento da Câmera (Teclado - WASD)
            keys = pygame.key.get_pressed()
            camera.update_keyboard(keys, dt)
            
            # Movimento da Lanterna (Setas do Teclado)
            flash_speed = 90.0 * dt
            if keys[K_LEFT]:  state.flash_yaw += flash_speed
            if keys[K_RIGHT]: state.flash_yaw -= flash_speed
            if keys[K_UP]:    state.flash_pitch += flash_speed
            if keys[K_DOWN]:  state.flash_pitch -= flash_speed
        else:
            pygame.mouse.get_rel()

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
        update_flashlight_light(state.flash_yaw, state.flash_pitch, state.light_on)

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
        draw_flashlight(state.flash_yaw, state.flash_pitch, state.light_on)

        draw_hud(display, state, title_font, body_font)

        # Atualiza a tela
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()