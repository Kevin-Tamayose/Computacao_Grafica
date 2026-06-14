"""
Renderer - Abstração da API Gráfica OpenGL

Responsabilidades:
1. Encapsular toda a lógica de OpenGL
2. Fornecer interfaces de alto nível para desenho (draw_mesh, draw_textured_plane, etc)
3. Gerenciar estado OpenGL (iluminação, texturas, projeção)
4. Isolar mudanças da API do resto do código

O código de movimentação de NPCs, por exemplo, NÃO deve conhecer VAOs/VBOs.
"""

from typing import Tuple, Optional
import OpenGL.GL as GL
import OpenGL.GLU as GLU

from engine.object_model.objmodel import OBJModel


class Renderer:
    """Abstração de renderização OpenGL."""

    def __init__(self):
        """Inicializa o renderizador."""
        self.initialized = False

    def initialize(self, display_size: Tuple[int, int], fov: float = 60.0) -> None:
        """
        Inicializa o contexto de renderização.
        
        Args:
            display_size: Tupla (width, height)
            fov: Field of view em graus
        """
        # Habilitar teste de profundidade (Z-Buffer)
        GL.glEnable(GL.GL_DEPTH_TEST)

        # Configurar matriz de projeção
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        
        aspect_ratio = display_size[0] / display_size[1]
        far_plane = 500.0
        GLU.gluPerspective(fov, aspect_ratio, 0.1, far_plane)
        
        # Voltar para modo modelview
        GL.glMatrixMode(GL.GL_MODELVIEW)

        self.initialized = True
        print("✓ Renderizador inicializado")

    def clear_screen(self, r: float = 0.0, g: float = 0.0, b: float = 0.0) -> None:
        """Limpa a tela com a cor especificada."""
        GL.glClearColor(r, g, b, 1.0)
        GL.glClear(int(GL.GL_COLOR_BUFFER_BIT) | int(GL.GL_DEPTH_BUFFER_BIT))

    def setup_modelview(self) -> None:
        """Prepara a matriz modelview para desenho."""
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

    def draw_plane_y(
        self,
        y: float,
        normal_y: float,
        size_x: float,
        size_z: float,
        divs_x: int,
        divs_z: int,
        texture_id: Optional[int] = None,
        repeat_x: float = 1.0,
        repeat_z: float = 1.0,
    ) -> None:
        """
        Desenha um plano paralelo ao eixo XZ (piso/teto).
        
        Args:
            y: Altura do plano
            normal_y: Direção da normal (1.0 ou -1.0)
            size_x, size_z: Dimensões do plano
            divs_x, divs_z: Subdivisões para faces
            texture_id: ID da textura (None para sem textura)
            repeat_x, repeat_z: Repetições de textura
        """
        if texture_id is not None:
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
            GL.glColor3f(1.0, 1.0, 1.0)
        
        GL.glNormal3f(0.0, normal_y, 0.0)
        step_x = (size_x * 2) / divs_x
        step_z = (size_z * 2) / divs_z
        
        GL.glBegin(GL.GL_QUADS)
        for i in range(divs_x):
            for j in range(divs_z):
                x = -size_x + i * step_x
                z = -size_z + j * step_z

                if texture_id is not None:
                    u0 = (i / divs_x) * repeat_x
                    u1 = ((i + 1) / divs_x) * repeat_x
                    v0 = (j / divs_z) * repeat_z
                    v1 = ((j + 1) / divs_z) * repeat_z

                    GL.glTexCoord2f(u0, v0)
                
                GL.glVertex3f(x, y, z)
                
                if texture_id is not None:
                    GL.glTexCoord2f(u1, v0)
                
                GL.glVertex3f(x + step_x, y, z)
                
                if texture_id is not None:
                    GL.glTexCoord2f(u1, v1)
                
                GL.glVertex3f(x + step_x, y, z + step_z)
                
                if texture_id is not None:
                    GL.glTexCoord2f(u0, v1)
                
                GL.glVertex3f(x, y, z + step_z)
        
        GL.glEnd()
        
        if texture_id is not None:
            GL.glDisable(GL.GL_TEXTURE_2D)

    def draw_plane_x(
        self,
        x: float,
        normal_x: float,
        size_y: float,
        size_z: float,
        divs_y: int,
        divs_z: int,
        texture_id: Optional[int] = None,
        repeat_y: float = 1.0,
        repeat_z: float = 1.0,
    ) -> None:
        """
        Desenha um plano paralelo ao eixo YZ (parede lateral).
        """
        if texture_id is not None:
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
            GL.glColor3f(1.0, 1.0, 1.0)
        
        GL.glNormal3f(normal_x, 0.0, 0.0)
        step_y = (size_y * 2) / divs_y
        step_z = (size_z * 2) / divs_z
        
        GL.glBegin(GL.GL_QUADS)
        for i in range(divs_y):
            for j in range(divs_z):
                y = -size_y + i * step_y
                z = -size_z + j * step_z

                if texture_id is not None:
                    u0 = (j / divs_z) * repeat_z
                    u1 = ((j + 1) / divs_z) * repeat_z
                    v0 = (i / divs_y) * repeat_y
                    v1 = ((i + 1) / divs_y) * repeat_y

                    GL.glTexCoord2f(u0, v0)
                
                GL.glVertex3f(x, y, z)
                
                if texture_id is not None:
                    GL.glTexCoord2f(u1, v0)
                
                GL.glVertex3f(x, y, z + step_z)
                
                if texture_id is not None:
                    GL.glTexCoord2f(u1, v1)
                
                GL.glVertex3f(x, y + step_y, z + step_z)
                
                if texture_id is not None:
                    GL.glTexCoord2f(u0, v1)
                
                GL.glVertex3f(x, y + step_y, z)
        
        GL.glEnd()
        
        if texture_id is not None:
            GL.glDisable(GL.GL_TEXTURE_2D)

    def draw_plane_z(
        self,
        z: float,
        normal_z: float,
        size_x: float,
        size_y: float,
        divs_x: int,
        divs_y: int,
        texture_id: Optional[int] = None,
        repeat_x: float = 1.0,
        repeat_y: float = 1.0,
    ) -> None:
        """
        Desenha um plano paralelo ao eixo XY (parede frontal/traseira).
        """
        if texture_id is not None:
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
            GL.glColor3f(1.0, 1.0, 1.0)
        
        GL.glNormal3f(0.0, 0.0, normal_z)
        step_x = (size_x * 2) / divs_x
        step_y = (size_y * 2) / divs_y
        
        GL.glBegin(GL.GL_QUADS)
        for i in range(divs_x):
            for j in range(divs_y):
                x = -size_x + i * step_x
                y = -size_y + j * step_y

                if texture_id is not None:
                    u0 = (i / divs_x) * repeat_x
                    u1 = ((i + 1) / divs_x) * repeat_x
                    v0 = (j / divs_y) * repeat_y
                    v1 = ((j + 1) / divs_y) * repeat_y

                    GL.glTexCoord2f(u0, v0)
                
                GL.glVertex3f(x, y, z)
                
                if texture_id is not None:
                    GL.glTexCoord2f(u1, v0)
                
                GL.glVertex3f(x + step_x, y, z)
                
                if texture_id is not None:
                    GL.glTexCoord2f(u1, v1)
                
                GL.glVertex3f(x + step_x, y + step_y, z)
                
                if texture_id is not None:
                    GL.glTexCoord2f(u0, v1)
                
                GL.glVertex3f(x, y + step_y, z)
        
        GL.glEnd()
        
        if texture_id is not None:
            GL.glDisable(GL.GL_TEXTURE_2D)

    def draw_model(self, model: OBJModel, texture_id: Optional[int] = None) -> None:
        """
        Renderiza um objeto do tipo OBJModel.
        """
        if model is None or model.display_list_id is None:
            return

        if texture_id is not None:
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
            GL.glColor3f(1.0, 1.0, 1.0)

        # Executa instantaneamente toda a geometria pré-compilada na placa de vídeo
        GL.glCallList(model.display_list_id)
        
        if texture_id is not None:
            GL.glDisable(GL.GL_TEXTURE_2D)

    def push_matrix(self) -> None:
        """Salva a matriz atual na pilha."""
        GL.glPushMatrix()

    def pop_matrix(self) -> None:
        """Restaura a matriz da pilha."""
        GL.glPopMatrix()
