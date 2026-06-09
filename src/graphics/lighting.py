from OpenGL.GL import *
import math


def setup_lighting():
    """Configura a iluminação global e o spotlight inicial do OpenGL."""
    glEnable(GL_LIGHTING)
    
    # LUZ AMBIENTE (Global) - Resolvendo a iluminação mínima padrão
    # Valores RGB aumentados para [0.35, 0.35, 0.35]. Isso garante que a 
    # sala fique visível em um tom de cinza base sem depender do holofote.
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.35, 0.35, 0.35, 1.0])
    
    # Configuração do SpotLight (Lanterna)
    glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [1.0, 1.0, 0.9, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 35.0)
    glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 10.0)
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.02)
    glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.001)

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)


def update_flashlight_light(flash_yaw, flash_pitch, light_on):
    """Atualiza posição e direção do spotlight de acordo com a orientação da lanterna."""
    if light_on:
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [0.0, 0.0, 0.0, 1.0])

        f_yaw_rad = math.radians(flash_yaw)
        f_pitch_rad = math.radians(flash_pitch)
        dir_x = math.sin(f_yaw_rad) * math.cos(f_pitch_rad)
        dir_y = math.sin(f_pitch_rad)
        dir_z = -math.cos(f_yaw_rad) * math.cos(f_pitch_rad)

        glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, [dir_x, dir_y, dir_z])
    else:
        glDisable(GL_LIGHT1)
