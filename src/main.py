"""
Projeto CG - Síntese de Imagem (Lanterna)

Ponto de entrada da aplicação.

Arquitetura:
1. Engine (motor gráfico abstrato)
2. Game (lógica do jogo)
3. Graphics (rendering de geometria e iluminação)
4. Core (câmera e input)
"""

import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
import OpenGL.GL as GL
import OpenGL.GLU as GLU

# Engine
from engine.asset_manager import AssetManager
from engine.renderer import Renderer
from core.input_manager import InputManager

# Game
from game.state import GameManager

# Graphics
from graphics.geometry import draw_room, draw_flashlight
from graphics.lighting import setup_lighting, update_flashlight_light

# Core
from core.camera import Camera


# =====================================================================
# Configurações Iniciais
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

# Cores HUD
HUD_BG_COLOR = (10, 14, 22, 210)
HUD_PANEL_COLOR = (255, 255, 255, 28)
HUD_TITLE_COLOR = (255, 238, 200)
HUD_TEXT_COLOR = (235, 235, 235)
HUD_ACCENT_COLOR = (255, 214, 120)


# =====================================================================
# Funções de HUD (mantidas do original)
# =====================================================================

class HUDButton:
    """Representa um botão clicável na HUD."""
    def __init__(self, x, y, width, height, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
    
    def is_clicked(self, mouse_x, mouse_y):
        """Verifica se o botão foi clicado."""
        return self.rect.collidepoint(int(mouse_x), int(mouse_y))


def set_mouse_capture(enabled: bool) -> None:
    """Captura ou libera o mouse."""
    pygame.mouse.set_visible(not enabled)
    pygame.event.set_grab(enabled)


def draw_hud(display, game_manager, title_font, body_font):
    """Desenha o HUD da aplicação e retorna os botões clicáveis."""
    hud_surface = pygame.Surface(display, pygame.SRCALPHA)
    hud_surface.fill((0, 0, 0, 0))
    buttons = []

    state = game_manager.state
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
                ("Voltar ao jogo", "resume"),
                ("Mostrar controles", "show_controls"),
                ("Sair do jogo", "quit"),
                (f"Lanterna: {'ligada' if state.light_on else 'desligada'}", "toggle_light"),
            ]
        else:
            lines = [
                ("Voltar para pausa", "back"),
                ("WASD: mover", None),
                ("Mouse: olhar", None),
                ("Setas: orientar a lanterna", None),
                ("L: liga/desliga a lanterna", None),
            ]
        
        y = panel_y + 88
        button_width = 480
        button_height = 32
        
        for index, (line_data) in enumerate(lines):
            if isinstance(line_data, tuple):
                line, action = line_data
            else:
                line = line_data
                action = None
            
            color = HUD_ACCENT_COLOR if index == 0 else HUD_TEXT_COLOR
            text = body_font.render(line, True, color)
            text_x = panel_x + 32
            hud_surface.blit(text, (text_x, y))
            
            # Criar botão se tem action
            if action:
                button = HUDButton(text_x - 10, y - 2, button_width, button_height, action)
                buttons.append(button)
            
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
    
    return buttons


# =====================================================================
# Game Loop
# =====================================================================
def main():
    """Função principal do programa."""
    # Inicializar pygame
    pygame.init()
    pygame.font.init()

    # Criar janela OpenGL
    display = (WINDOW_WIDTH, WINDOW_HEIGHT)
    pygame.display.set_mode(display, int(DOUBLEBUF) | int(OPENGL))
    pygame.display.set_caption("Projeto CG - Síntese de Imagem (Lanterna)")

    # ===================================================================
    # INICIALIZAR SISTEMAS
    # ===================================================================

    # Motor gráfico
    renderer = Renderer()
    renderer.initialize(display)

    # Gerenciador de recursos
    asset_manager = AssetManager()

    # Gerenciador de input
    input_manager = InputManager()

    # Gerenciador de estado do jogo
    game_manager = GameManager()

    # Câmera
    camera = Camera(room_width=ROOM_WIDTH, room_depth=ROOM_DEPTH)

    # Iluminação
    setup_lighting()

    # Texturas
    floor_texture_id = asset_manager.load_texture('chats.jpg')
    wall_texture_id = asset_manager.load_texture('wall.jpg')
    floor_texture_repeat = 4.0
    wall_texture_repeat = 1.25

    # Fontes para HUD
    title_font = pygame.font.SysFont("Arial", 42, bold=True)
    body_font = pygame.font.SysFont("Arial", 26)

    # Controle de mouse
    set_mouse_capture(game_manager.is_menu_open())

    # ===================================================================
    # GAME LOOP
    # ===================================================================
    clock = pygame.time.Clock()
    running = True
    hud_buttons = []  # Será atualizado a cada frame

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time em segundos

        # -----------------------------------------------------------------
        # FASE 1: INPUT & UPDATE
        # -----------------------------------------------------------------
        input_manager.update()

        if input_manager.state.quit_requested:
            running = False

        if input_manager.state.escape_pressed:
            game_manager.toggle_menu()
            set_mouse_capture(game_manager.is_menu_open())

        if input_manager.state.c_pressed and game_manager.state.menu_view == "pause":
            game_manager.show_controls()

        if input_manager.state.q_pressed:
            running = False

        if input_manager.state.l_pressed:
            game_manager.toggle_light()
        
        # Processar cliques do mouse no HUD
        if input_manager.state.mouse_clicked and not game_manager.is_in_game():
            for button in hud_buttons:
                if button.is_clicked(input_manager.state.mouse_x, input_manager.state.mouse_y):
                    if button.action == "resume":
                        game_manager.toggle_menu()
                        set_mouse_capture(game_manager.is_menu_open())
                    elif button.action == "show_controls":
                        game_manager.show_controls()
                    elif button.action == "back":
                        game_manager.return_to_pause()
                    elif button.action == "quit":
                        running = False
                    elif button.action == "toggle_light":
                        game_manager.toggle_light()
                    break  # Processar apenas um botão por frame

        # Atualizar câmera e lanterna apenas se no jogo
        if game_manager.is_in_game():
            # Câmera (mouse + teclado)
            camera.update_mouse(input_manager.state.mouse_dx, input_manager.state.mouse_dy)
            camera.update_keyboard([
                input_manager.state.w_pressed,
                input_manager.state.a_pressed,
                input_manager.state.s_pressed,
                input_manager.state.d_pressed,
            ], dt)

            # Lanterna
            yaw_delta, pitch_delta = input_manager.get_flashlight_rotation()
            game_manager.update_flashlight(yaw_delta, pitch_delta, dt)
        else:
            # Se no menu, consumir input do mouse
            input_manager.state.mouse_dx = 0.0
            input_manager.state.mouse_dy = 0.0

        # -----------------------------------------------------------------
        # FASE 2: RENDERIZAÇÃO
        # -----------------------------------------------------------------
        renderer.clear_screen(0.0, 0.0, 0.0)
        renderer.setup_modelview()

        # Aplicar transformação da câmera
        camera.apply_transform()

        # Atualizar luz da lanterna (segue a câmera)
        update_flashlight_light(
            game_manager.state.flash_yaw,
            game_manager.state.flash_pitch,
            game_manager.state.light_on
        )

        # Desenhar sala
        draw_room(
            renderer,
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

        # Desenhar lanterna
        draw_flashlight(
            game_manager.state.flash_yaw,
            game_manager.state.flash_pitch,
            game_manager.state.light_on
        )

        # Desenhar HUD
        hud_buttons = draw_hud(display, game_manager, title_font, body_font)

        # Atualizar display
        pygame.display.flip()

    # ===================================================================
    # CLEANUP
    # ===================================================================
    asset_manager.unload_all_textures()
    pygame.quit()


if __name__ == "__main__":
    main()
