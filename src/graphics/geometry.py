"""
Geometry - Lógica de Desenho de Geometria

Responsabilidades:
1. Definir a lógica de como desenhar objetos (salas, lanternas, etc)
2. Usar o Renderer abstrato para não conhecer detalhes de OpenGL
3. Não gerenciar texturas (responsabilidade do Asset Manager)
"""

import OpenGL.GL as GL
import OpenGL.GLU as GLU


def draw_room(
    renderer,
    size_x=10,
    size_z=10,
    size_y=10,
    divs_x=20,
    divs_z=20,
    divs_y=20,
    floor_texture_id=None,
    wall_texture_id=None,
    floor_texture_repeat=1.0,
    wall_texture_repeat=1.0,
):
    """
    Desenha a sala inteira composta por chão, teto e quatro paredes.
    
    Args:
        renderer: Instância do Renderer
        size_x, size_z, size_y: Dimensões da sala
        divs_x, divs_z, divs_y: Subdivisões de faces
        floor_texture_id: ID da textura do piso (opcional)
        wall_texture_id: ID da textura das paredes (opcional)
        floor_texture_repeat: Repetições de textura do piso
        wall_texture_repeat: Repetições de textura das paredes
    """
    GL.glColor3f(0.5, 0.5, 0.5)

    # Chão
    renderer.draw_plane_y(
        y=-size_y,
        normal_y=1.0,
        size_x=size_x,
        size_z=size_z,
        divs_x=divs_x,
        divs_z=divs_z,
        texture_id=floor_texture_id,
        repeat_x=floor_texture_repeat,
        repeat_z=floor_texture_repeat,
    )

    # Teto
    renderer.draw_plane_y(
        y=size_y,
        normal_y=-1.0,
        size_x=size_x,
        size_z=size_z,
        divs_x=divs_x,
        divs_z=divs_z,
        texture_id=None,
    )

    # Paredes
    # Parede esquerda (X negativo)
    renderer.draw_plane_x(
        x=-size_x,
        normal_x=1.0,
        size_y=size_y,
        size_z=size_z,
        divs_y=divs_y,
        divs_z=divs_z,
        texture_id=wall_texture_id,
        repeat_y=wall_texture_repeat,
        repeat_z=wall_texture_repeat,
    )

    # Parede direita (X positivo)
    renderer.draw_plane_x(
        x=size_x,
        normal_x=-1.0,
        size_y=size_y,
        size_z=size_z,
        divs_y=divs_y,
        divs_z=divs_z,
        texture_id=wall_texture_id,
        repeat_y=wall_texture_repeat,
        repeat_z=wall_texture_repeat,
    )

    # Parede traseira (Z negativo)
    renderer.draw_plane_z(
        z=-size_z,
        normal_z=1.0,
        size_x=size_x,
        size_y=size_y,
        divs_x=divs_x,
        divs_y=divs_y,
        texture_id=wall_texture_id,
        repeat_x=wall_texture_repeat,
        repeat_y=wall_texture_repeat,
    )

    # Parede frontal (Z positivo)
    renderer.draw_plane_z(
        z=size_z,
        normal_z=-1.0,
        size_x=size_x,
        size_y=size_y,
        divs_x=divs_x,
        divs_y=divs_y,
        texture_id=wall_texture_id,
        repeat_x=wall_texture_repeat,
        repeat_y=wall_texture_repeat,
    )


def draw_flashlight(flash_yaw, flash_pitch, light_on):
    """
    Desenha a lanterna no centro da cena usando a orientação atual.
    
    Args:
        flash_yaw: Rotação horizontal (graus)
        flash_pitch: Rotação vertical (graus)
        light_on: Se a lanterna está ligada
    """
    GL.glPushMatrix()
    GL.glColor3f(0.18, 0.18, 0.18)
    GL.glRotatef(flash_yaw, 0, 1, 0)
    GL.glRotatef(-flash_pitch, 1, 0, 0)
    GL.glTranslatef(0.18, -0.12, -0.42)

    quadric = GLU.gluNewQuadric()
    GLU.gluCylinder(quadric, 0.11, 0.11, 0.65, 16, 16)

    if light_on:
        GL.glColor3f(1.0, 0.98, 0.86)
    else:
        GL.glColor3f(0.08, 0.08, 0.08)

    GLU.gluDisk(quadric, 0.0, 0.11, 16, 1)
    GLU.gluDeleteQuadric(quadric)
    GL.glPopMatrix()
