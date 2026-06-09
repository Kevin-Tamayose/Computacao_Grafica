import math
from math import radians, sin, cos
from OpenGL.GL import glRotatef, glTranslatef
from pygame.locals import K_w, K_s, K_a, K_d


class Camera:
    """Representa a câmera do jogador."""

    def __init__(self, position=(0.0, 0.0, 8.0), yaw=0.0, pitch=0.0,
                 speed=5.0, sensitivity=0.2, room_size=10.0, room_width=None, room_depth=None):
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

    def update_keyboard(self, keys, dt):
        """Move a câmera com as teclas WASD, preservando a direção atual."""
        velocity = self.speed * dt
        yaw_rad = radians(self.yaw)

        if keys[K_w]:
            self.position[0] += sin(yaw_rad) * velocity
            self.position[2] -= cos(yaw_rad) * velocity
        if keys[K_s]:
            self.position[0] -= sin(yaw_rad) * velocity
            self.position[2] += cos(yaw_rad) * velocity
        if keys[K_a]:
            self.position[0] -= cos(yaw_rad) * velocity
            self.position[2] -= sin(yaw_rad) * velocity
        if keys[K_d]:
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
