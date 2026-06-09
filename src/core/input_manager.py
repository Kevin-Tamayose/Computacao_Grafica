"""
Input Manager - Gerenciador Centralizado de Inputs

Responsabilidades:
1. Centralizar tratamento de eventos do pygame
2. Fornecer estado de inputs para serem consultados
3. Desacoplar a lógica de jogo do sistema de inputs
"""

from dataclasses import dataclass
from typing import Callable, Dict, Optional
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, K_l, K_LEFT, K_RIGHT, K_UP, K_DOWN


@dataclass
class InputState:
    """Estado atual dos inputs."""
    # Teclado
    w_pressed: bool = False
    a_pressed: bool = False
    s_pressed: bool = False
    d_pressed: bool = False
    left_pressed: bool = False
    right_pressed: bool = False
    up_pressed: bool = False
    down_pressed: bool = False
    
    # Mouse
    mouse_dx: float = 0.0
    mouse_dy: float = 0.0
    
    # Eventos discretos (por frame)
    escape_pressed: bool = False
    l_pressed: bool = False
    c_pressed: bool = False
    q_pressed: bool = False
    quit_requested: bool = False


class InputManager:
    """Gerenciador centralizado de inputs."""

    def __init__(self):
        """Inicializa o gerenciador de inputs."""
        self.state = InputState()
        self.callbacks: Dict[str, Callable] = {}

    def register_callback(self, event_name: str, callback: Callable) -> None:
        """
        Registra uma callback para um evento específico.
        
        Args:
            event_name: Nome do evento (ex: 'escape_pressed', 'l_pressed')
            callback: Função a ser chamada quando o evento ocorrer
        """
        self.callbacks[event_name] = callback

    def update(self) -> None:
        """
        Processa eventos pygame e atualiza o estado de inputs.
        
        Deve ser chamado uma vez por frame no game loop.
        """
        # Resetar eventos discretos
        self.state.escape_pressed = False
        self.state.l_pressed = False
        self.state.c_pressed = False
        self.state.q_pressed = False
        self.state.quit_requested = False
        
        # Processar eventos pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state.quit_requested = True
                self._trigger_callback('quit_requested')
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.state.escape_pressed = True
                    self._trigger_callback('escape_pressed')
                elif event.key == K_l:
                    self.state.l_pressed = True
                    self._trigger_callback('l_pressed')
                elif event.key == pygame.K_c:
                    self.state.c_pressed = True
                    self._trigger_callback('c_pressed')
                elif event.key == pygame.K_q:
                    self.state.q_pressed = True
                    self._trigger_callback('q_pressed')
        
        # Atualizar estado contínuo do teclado
        keys = pygame.key.get_pressed()
        self.state.w_pressed = keys[pygame.K_w]
        self.state.a_pressed = keys[pygame.K_a]
        self.state.s_pressed = keys[pygame.K_s]
        self.state.d_pressed = keys[pygame.K_d]
        self.state.left_pressed = keys[K_LEFT]
        self.state.right_pressed = keys[K_RIGHT]
        self.state.up_pressed = keys[K_UP]
        self.state.down_pressed = keys[K_DOWN]
        
        # Atualizar mouse
        self.state.mouse_dx, self.state.mouse_dy = pygame.mouse.get_rel()

    def get_movement_vector(self) -> tuple:
        """
        Retorna um vetor normalizado de movimento baseado em WASD.
        
        Returns:
            Tupla (x, y, z) representando a direção de movimento
        """
        x = float(self.state.d_pressed) - float(self.state.a_pressed)
        z = float(self.state.w_pressed) - float(self.state.s_pressed)
        return (x, 0.0, z)

    def get_flashlight_rotation(self) -> tuple:
        """
        Retorna a rotação da lanterna baseada nas setas do teclado.
        
        Returns:
            Tupla (yaw_delta, pitch_delta) em graus
        """
        yaw_speed = 90.0  # Graus por segundo
        pitch_speed = 90.0
        
        yaw_delta = (float(self.state.right_pressed) - float(self.state.left_pressed)) * yaw_speed
        pitch_delta = (float(self.state.up_pressed) - float(self.state.down_pressed)) * pitch_speed
        
        return (yaw_delta, pitch_delta)

    def set_mouse_capture(self, enabled: bool) -> None:
        """
        Ativa/desativa captura de mouse e visibilidade do cursor.
        
        Args:
            enabled: Se True, captura o mouse e oculta o cursor
        """
        pygame.mouse.set_visible(not enabled)
        pygame.event.set_grab(enabled)

    def _trigger_callback(self, event_name: str) -> None:
        """Chama a callback registrada para um evento, se existir."""
        if event_name in self.callbacks:
            self.callbacks[event_name]()
