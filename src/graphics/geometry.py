import os

import OpenGL.GL as GL
import OpenGL.GLU as GLU
from PIL import Image


floor_texture = None
wall_texture = None


def load_texture(image_name):
    """Carrega uma textura da pasta images/ e retorna o ID OpenGL."""
    texture_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images', image_name))

    if not os.path.exists(texture_path):
        print(f'Textura nao encontrada: {texture_path}')
        return None

    img = Image.open(texture_path).convert('RGB')

    texture_id = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexImage2D(
        GL.GL_TEXTURE_2D,
        0,
        GL.GL_RGB,
        img.width,
        img.height,
        0,
        GL.GL_RGB,
        GL.GL_UNSIGNED_BYTE,
        img.tobytes(),
    )
    return texture_id


def load_floor_texture():
    """Carrega a textura do piso."""
    global floor_texture
    floor_texture = load_texture('chats.jpg')
    if floor_texture is not None:
        print('Textura do piso carregada: chats.jpg')
    return floor_texture


def load_wall_texture():
    """Carrega a textura das paredes."""
    global wall_texture
    wall_texture = load_texture('wall.jpg')
    if wall_texture is not None:
        print('Textura da parede carregada: wall.jpg')
    return wall_texture


def draw_plane_y(y, normal_y, size_x, size_z, divs_x, divs_z):
    """Desenha um plano paralelo ao eixo XZ no nivel Y especificado."""
    GL.glNormal3f(0.0, normal_y, 0.0)
    step_x = (size_x * 2) / divs_x
    step_z = (size_z * 2) / divs_z
    GL.glBegin(GL.GL_QUADS)
    for i in range(divs_x):
        for j in range(divs_z):
            x = -size_x + i * step_x
            z = -size_z + j * step_z
            GL.glVertex3f(x, y, z)
            GL.glVertex3f(x + step_x, y, z)
            GL.glVertex3f(x + step_x, y, z + step_z)
            GL.glVertex3f(x, y, z + step_z)
    GL.glEnd()


def draw_plane_y_textured(y, normal_y, size_x, size_z, divs_x, divs_z, texture_id, repeat_x=1.0, repeat_z=1.0):
    """Desenha um plano XZ com textura repetida."""
    if texture_id is None:
        draw_plane_y(y, normal_y, size_x, size_z, divs_x, divs_z)
        return

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

            u0 = (i / divs_x) * repeat_x
            u1 = ((i + 1) / divs_x) * repeat_x
            v0 = (j / divs_z) * repeat_z
            v1 = ((j + 1) / divs_z) * repeat_z

            GL.glTexCoord2f(u0, v0)
            GL.glVertex3f(x, y, z)
            GL.glTexCoord2f(u1, v0)
            GL.glVertex3f(x + step_x, y, z)
            GL.glTexCoord2f(u1, v1)
            GL.glVertex3f(x + step_x, y, z + step_z)
            GL.glTexCoord2f(u0, v1)
            GL.glVertex3f(x, y, z + step_z)
    GL.glEnd()

    GL.glDisable(GL.GL_TEXTURE_2D)


def draw_plane_x(x, normal_x, size_y, size_z, divs_y, divs_z):
    """Desenha um plano paralelo ao eixo YZ no valor X especificado."""
    GL.glNormal3f(normal_x, 0.0, 0.0)
    step_y = (size_y * 2) / divs_y
    step_z = (size_z * 2) / divs_z
    GL.glBegin(GL.GL_QUADS)
    for i in range(divs_y):
        for j in range(divs_z):
            y = -size_y + i * step_y
            z = -size_z + j * step_z
            GL.glVertex3f(x, y, z)
            GL.glVertex3f(x, y + step_y, z)
            GL.glVertex3f(x, y + step_y, z + step_z)
            GL.glVertex3f(x, y, z + step_z)
    GL.glEnd()


def draw_plane_x_textured(x, normal_x, size_y, size_z, divs_y, divs_z, texture_id, repeat_y=1.0, repeat_z=1.0):
    """Desenha um plano YZ com textura repetida."""
    if texture_id is None:
        draw_plane_x(x, normal_x, size_y, size_z, divs_y, divs_z)
        return

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

            u0 = (j / divs_z) * repeat_z
            u1 = ((j + 1) / divs_z) * repeat_z
            v0 = (i / divs_y) * repeat_y
            v1 = ((i + 1) / divs_y) * repeat_y

            GL.glTexCoord2f(u0, v0)
            GL.glVertex3f(x, y, z)
            GL.glTexCoord2f(u1, v0)
            GL.glVertex3f(x, y, z + step_z)
            GL.glTexCoord2f(u1, v1)
            GL.glVertex3f(x, y + step_y, z + step_z)
            GL.glTexCoord2f(u0, v1)
            GL.glVertex3f(x, y + step_y, z)
    GL.glEnd()

    GL.glDisable(GL.GL_TEXTURE_2D)


def draw_plane_z(z, normal_z, size_x, size_y, divs_x, divs_y):
    """Desenha um plano paralelo ao eixo XY no valor Z especificado."""
    GL.glNormal3f(0.0, 0.0, normal_z)
    step_x = (size_x * 2) / divs_x
    step_y = (size_y * 2) / divs_y
    GL.glBegin(GL.GL_QUADS)
    for i in range(divs_x):
        for j in range(divs_y):
            x = -size_x + i * step_x
            y = -size_y + j * step_y
            GL.glVertex3f(x, y, z)
            GL.glVertex3f(x + step_x, y, z)
            GL.glVertex3f(x + step_x, y + step_y, z)
            GL.glVertex3f(x, y + step_y, z)
    GL.glEnd()


def draw_plane_z_textured(z, normal_z, size_x, size_y, divs_x, divs_y, texture_id, repeat_x=1.0, repeat_y=1.0):
    """Desenha um plano XY com textura repetida."""
    if texture_id is None:
        draw_plane_z(z, normal_z, size_x, size_y, divs_x, divs_y)
        return

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

            u0 = (i / divs_x) * repeat_x
            u1 = ((i + 1) / divs_x) * repeat_x
            v0 = (j / divs_y) * repeat_y
            v1 = ((j + 1) / divs_y) * repeat_y

            GL.glTexCoord2f(u0, v0)
            GL.glVertex3f(x, y, z)
            GL.glTexCoord2f(u1, v0)
            GL.glVertex3f(x + step_x, y, z)
            GL.glTexCoord2f(u1, v1)
            GL.glVertex3f(x + step_x, y + step_y, z)
            GL.glTexCoord2f(u0, v1)
            GL.glVertex3f(x, y + step_y, z)
    GL.glEnd()

    GL.glDisable(GL.GL_TEXTURE_2D)


def draw_room_walls_textured(size_x, size_z, size_y, divs_x, divs_z, divs_y, texture_id, texture_repeat=1.0):
    """Desenha as quatro paredes usando UVs contínuos ao redor do perímetro."""
    if texture_id is None:
        draw_plane_x(-size_x, 1.0, size_y, size_z, divs_y, divs_z)
        draw_plane_x(size_x, -1.0, size_y, size_z, divs_y, divs_z)
        draw_plane_z(-size_z, 1.0, size_x, size_y, divs_x, divs_y)
        draw_plane_z(size_z, -1.0, size_x, size_y, divs_x, divs_y)
        return

    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    GL.glColor3f(1.0, 1.0, 1.0)

    u_scale = texture_repeat
    v_scale = texture_repeat
    back_span = 2.0 * size_x
    right_span = 2.0 * size_z
    front_span = 2.0 * size_x
    top_span = 2.0 * size_z

    # Back wall: z = -size_z, left to right
    GL.glNormal3f(0.0, 0.0, 1.0)
    step_x = back_span / divs_x
    step_y = (2.0 * size_y) / divs_y
    GL.glBegin(GL.GL_QUADS)
    for i in range(divs_x):
        for j in range(divs_y):
            x0 = -size_x + i * step_x
            x1 = x0 + step_x
            y0 = -size_y + j * step_y
            y1 = y0 + step_y
            u0 = (x0 + size_x) * u_scale
            u1 = (x1 + size_x) * u_scale
            v0 = (y0 + size_y) * v_scale
            v1 = (y1 + size_y) * v_scale
            GL.glTexCoord2f(u0, v0)
            GL.glVertex3f(x0, y0, -size_z)
            GL.glTexCoord2f(u1, v0)
            GL.glVertex3f(x1, y0, -size_z)
            GL.glTexCoord2f(u1, v1)
            GL.glVertex3f(x1, y1, -size_z)
            GL.glTexCoord2f(u0, v1)
            GL.glVertex3f(x0, y1, -size_z)
    GL.glEnd()

    # Right wall: x = size_x, back to front
    GL.glNormal3f(-1.0, 0.0, 0.0)
    step_z = right_span / divs_z
    step_y = (2.0 * size_y) / divs_y
    GL.glBegin(GL.GL_QUADS)
    for i in range(divs_z):
        for j in range(divs_y):
            z0 = -size_z + i * step_z
            z1 = z0 + step_z
            y0 = -size_y + j * step_y
            y1 = y0 + step_y
            u0 = (back_span + (z0 + size_z)) * u_scale
            u1 = (back_span + (z1 + size_z)) * u_scale
            v0 = (y0 + size_y) * v_scale
            v1 = (y1 + size_y) * v_scale
            GL.glTexCoord2f(u0, v0)
            GL.glVertex3f(size_x, y0, z0)
            GL.glTexCoord2f(u1, v0)
            GL.glVertex3f(size_x, y0, z1)
            GL.glTexCoord2f(u1, v1)
            GL.glVertex3f(size_x, y1, z1)
            GL.glTexCoord2f(u0, v1)
            GL.glVertex3f(size_x, y1, z0)
    GL.glEnd()

    # Front wall: z = size_z, right to left
    GL.glNormal3f(0.0, 0.0, -1.0)
    step_x = front_span / divs_x
    step_y = (2.0 * size_y) / divs_y
    GL.glBegin(GL.GL_QUADS)
    for i in range(divs_x):
        for j in range(divs_y):
            x0 = size_x - i * step_x
            x1 = x0 - step_x
            y0 = -size_y + j * step_y
            y1 = y0 + step_y
            u0 = (back_span + right_span + (size_x - x0)) * u_scale
            u1 = (back_span + right_span + (size_x - x1)) * u_scale
            v0 = (y0 + size_y) * v_scale
            v1 = (y1 + size_y) * v_scale
            GL.glTexCoord2f(u0, v0)
            GL.glVertex3f(x0, y0, size_z)
            GL.glTexCoord2f(u1, v0)
            GL.glVertex3f(x1, y0, size_z)
            GL.glTexCoord2f(u1, v1)
            GL.glVertex3f(x1, y1, size_z)
            GL.glTexCoord2f(u0, v1)
            GL.glVertex3f(x0, y1, size_z)
    GL.glEnd()

    # Left wall: x = -size_x, front to back
    GL.glNormal3f(1.0, 0.0, 0.0)
    step_z = top_span / divs_z
    step_y = (2.0 * size_y) / divs_y
    GL.glBegin(GL.GL_QUADS)
    for i in range(divs_z):
        for j in range(divs_y):
            z0 = size_z - i * step_z
            z1 = z0 - step_z
            y0 = -size_y + j * step_y
            y1 = y0 + step_y
            u0 = (back_span + right_span + front_span + (size_z - z0)) * u_scale
            u1 = (back_span + right_span + front_span + (size_z - z1)) * u_scale
            v0 = (y0 + size_y) * v_scale
            v1 = (y1 + size_y) * v_scale
            GL.glTexCoord2f(u0, v0)
            GL.glVertex3f(-size_x, y0, z0)
            GL.glTexCoord2f(u1, v0)
            GL.glVertex3f(-size_x, y0, z1)
            GL.glTexCoord2f(u1, v1)
            GL.glVertex3f(-size_x, y1, z1)
            GL.glTexCoord2f(u0, v1)
            GL.glVertex3f(-size_x, y1, z0)
    GL.glEnd()

    GL.glDisable(GL.GL_TEXTURE_2D)


def draw_room(
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
    """Desenha a sala inteira composta por chao, teto e quatro paredes."""
    GL.glColor3f(0.5, 0.5, 0.5)

    if floor_texture_id is not None:
        draw_plane_y_textured(-size_y, 1.0, size_x, size_z, divs_x, divs_z, floor_texture_id, repeat_x=floor_texture_repeat, repeat_z=floor_texture_repeat)
    else:
        draw_plane_y(-size_y, 1.0, size_x, size_z, divs_x, divs_z)

    draw_plane_y(size_y, -1.0, size_x, size_z, divs_x, divs_z)

    if wall_texture_id is not None:
        draw_room_walls_textured(size_x, size_z, size_y, divs_x, divs_z, divs_y, wall_texture_id, texture_repeat=wall_texture_repeat)
    else:
        draw_plane_x(-size_x, 1.0, size_y, size_z, divs_y, divs_z)
        draw_plane_x(size_x, -1.0, size_y, size_z, divs_y, divs_z)
        draw_plane_z(-size_z, 1.0, size_x, size_y, divs_x, divs_y)
        draw_plane_z(size_z, -1.0, size_x, size_y, divs_x, divs_y)


def draw_flashlight(flash_yaw, flash_pitch, light_on):
    """Desenha a lanterna no centro da cena usando a orientacao atual."""
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
