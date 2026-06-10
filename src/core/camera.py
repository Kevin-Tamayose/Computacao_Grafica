import math
from math import radians, sin, cos
from OpenGL.GL import glRotatef, glTranslatef


class Camera:
    """Representa a câmera do jogador."""

    def __init__(self, position=(0.0, 0.0, 8.0), yaw=0.0, pitch=0.0,
                 speed=15.0, sensitivity=0.1, room_size=10.0, room_width=None, room_depth=None):
        self.position = list(position)
        self.yaw = yaw
        self.pitch = pitch
        self.speed = speed
        self.sensitivity = sensitivity
        self.room_width = room_width if room_width is not None else room_size
        self.room_depth = room_depth if room_depth is not None else room_size
        self.room_size = max(self.room_width, self.room_depth)

    def update_mouse(self, dx, dy):
        """Atualiza a orientação da câmera com base no movimento do mouse."""
        self.yaw += dx * self.sensitivity
        self.pitch += dy * self.sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch))

    def get_speed_multiplier(self, running: bool) -> float:
        return 1.5 if running else 1.0
    
    def update_keyboard(self, keys_pressed, dt):
        """
        Move a câmera com as teclas WASD, preservando a direção atual.
        
        Args:
            keys_pressed: Lista/tupla [w, a, s, d] com os estados das teclas
            dt: Delta time em segundos
        """
        w_pressed, a_pressed, s_pressed, d_pressed, running = keys_pressed

        velocity = self.speed * self.get_speed_multiplier(running) * dt
        yaw_rad = radians(self.yaw)   

        if w_pressed:
            self.position[0] += sin(yaw_rad) * velocity
            self.position[2] -= cos(yaw_rad) * velocity
        if s_pressed:
            self.position[0] -= sin(yaw_rad) * velocity
            self.position[2] += cos(yaw_rad) * velocity
        if a_pressed:
            self.position[0] -= cos(yaw_rad) * velocity
            self.position[2] -= sin(yaw_rad) * velocity
        if d_pressed:
            self.position[0] += cos(yaw_rad) * velocity
            self.position[2] += sin(yaw_rad) * velocity
        
        # =================================================================
        # SISTEMA DE COLISÃO (Evitar entidades sobrepostas)
        # =================================================================
        
        # 1. Colisão com as Paredes (Clamping)
        # A sala tem tamanho dinâmico. Deixamos margem de 0.5 para simular o "corpo" do usuário
        margin_x = self.room_width - 0.5
        margin_z = self.room_depth - 0.5
        self.position[0] = max(-margin_x, min(margin_x, self.position[0]))
        self.position[2] = max(-margin_z, min(margin_z, self.position[2]))
        
        # 2. Colisão com o Objeto Central (Lanterna no ponto 0,0,0)
        # Usamos o Teorema de Pitágoras para saber a distância da câmera até o centro
        dist_to_center = math.sqrt(self.position[0]**2 + self.position[2]**2)
        min_dist = 1.5 # Raio de proteção/colisão em volta da lanterna
        
        # Se a câmera invadir o raio mínimo, empurramos ela de volta para a borda do raio
        if dist_to_center < min_dist and dist_to_center > 0:
            self.position[0] = (self.position[0] / dist_to_center) * min_dist
            self.position[2] = (self.position[2] / dist_to_center) * min_dist

    def apply_transform(self):
        """Aplica a rotação e translação da câmera na matriz ModelView."""
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glTranslatef(-self.position[0], -self.position[1], -self.position[2])
