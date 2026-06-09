"""
Game Logic - Estado do Jogo

Responsabilidades:
1. Manter o estado global do jogo
2. Separar dados (state) da lógica de renderização
"""

from dataclasses import dataclass


@dataclass
class GameState:
    """Estado imutável do jogo. Não contém lógica, apenas dados."""
    # Lanterna
    flash_yaw: float = 0.0
    flash_pitch: float = 0.0
    light_on: bool = True
    
    # Menu
    menu_view: str = "game"  # "game", "pause", "controls"


class GameManager:
    """Gerenciador de estado e lógica do jogo."""

    def __init__(self):
        """Inicializa o gerenciador do jogo."""
        self.state = GameState()

    def toggle_light(self) -> None:
        """Liga/desliga a lanterna."""
        self.state.light_on = not self.state.light_on

    def toggle_menu(self) -> None:
        """Alterna entre menu e jogo."""
        if self.state.menu_view == "game":
            self.state.menu_view = "pause"
        elif self.state.menu_view == "pause":
            self.state.menu_view = "game"
        else:
            self.state.menu_view = "pause"

    def show_controls(self) -> None:
        """Mostra tela de controles."""
        if self.state.menu_view == "pause":
            self.state.menu_view = "controls"

    def return_to_pause(self) -> None:
        """Volta para a tela de pausa."""
        if self.state.menu_view == "controls":
            self.state.menu_view = "pause"

    def update_flashlight(self, yaw_delta: float, pitch_delta: float, dt: float) -> None:
        """
        Atualiza a orientação da lanterna.
        
        Args:
            yaw_delta: Mudança em yaw por segundo (graus/s)
            pitch_delta: Mudança em pitch por segundo (graus/s)
            dt: Delta time em segundos
        """
        self.state.flash_yaw += yaw_delta * dt
        self.state.flash_pitch += pitch_delta * dt
        
        # Clampar pitch para evitar gimbal lock
        self.state.flash_pitch = max(-89.0, min(89.0, self.state.flash_pitch))

    def is_in_game(self) -> bool:
        """Retorna True se o jogo está rodando (não no menu)."""
        return self.state.menu_view == "game"

    def is_menu_open(self) -> bool:
        """Retorna True se algum menu está aberto."""
        return self.state.menu_view != "game"
