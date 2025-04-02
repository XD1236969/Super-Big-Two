import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

def draw_cylinder(radius, height, num_sides):
    """使用 OpenGL 繪製立體圓柱"""
    # 繪製圓柱側面
    glBegin(GL_QUAD_STRIP)
    for i in range(num_sides + 1):
        angle = 2 * math.pi * i / num_sides
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, 0)  # 底部
        glVertex3f(x, y, height)  # 頂部
    glEnd()
    
    # 繪製底部圓盤
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)
    for i in range(num_sides + 1):
        angle = 2 * math.pi * i / num_sides
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, 0)
    glEnd()
    
    # 繪製頂部圓盤
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, height)
    for i in range(num_sides + 1):
        angle = 2 * math.pi * i / num_sides
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, height)
    glEnd()

# 初始化 Pygame & OpenGL
pygame.init()
screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
gluPerspective(45, (800 / 600), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5)

running = True
while running:
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    glRotatef(1, 1, 1, 0)  # 旋轉圓柱
    draw_cylinder(1, 2, 30)  # 繪製 3D 圓柱

    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()
