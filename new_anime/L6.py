import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random, math

# 圓柱物件，改為發射方向帶有偏向螢幕的 z 分量
class Cylinder:
    def __init__(self, angle, color):
        self.angle = angle
        # bias 為發射方向與 XY 平面的夾角，設定為 30°（可調整）
        self.bias = math.radians(30)
        # 計算 3D 方向：先沿 XY 平面轉動，再偏向螢幕 (Z 軸方向)
        self.direction = (
            math.cos(angle) * math.cos(self.bias),
            math.sin(angle) * math.cos(self.bias),
            -math.sin(self.bias)  # 負號表示向螢幕內 (負 Z) 發射
        )
        self.color = color
        self.speed = 0.1
        self.distance = 0.0
        self.radius = 0.2
        self.height = 2.0
        self.num_sides = 20

    def update(self):
        self.distance += self.speed

    def draw(self):
        # 根據方向計算目前位置
        x = self.distance * self.direction[0]
        y = self.distance * self.direction[1]
        z = self.distance * self.direction[2]
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3fv(self.color)
        
        # 旋轉圓柱，使其 z 軸對齊到 self.direction
        # 預設圓柱是在 z 軸上（從 0 到 height）
        dx, dy, dz = self.direction
        # 求預設方向 (0,0,1) 與 self.direction 的夾角
        rot_angle = math.degrees(math.acos(dz))
        # 旋轉軸為 (0,0,1) x self.direction = (-dy, dx, 0)
        rot_axis = (-dy, dx, 0)
        if math.sqrt(rot_axis[0]**2 + rot_axis[1]**2) > 1e-6:
            glRotatef(rot_angle, rot_axis[0], rot_axis[1], 0)
        draw_cylinder(self.radius, self.height, self.num_sides)
        glPopMatrix()

def draw_cylinder(radius, height, num_sides):
    """使用 OpenGL 繪製立體圓柱"""
    # 繪製側面
    glBegin(GL_QUAD_STRIP)
    for i in range(num_sides + 1):
        angle = 2 * math.pi * i / num_sides
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, 0)      # 底部
        glVertex3f(x, y, height) # 頂部
    glEnd()
    
    # 繪製底部
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)
    for i in range(num_sides + 1):
        angle = 2 * math.pi * i / num_sides
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, 0)
    glEnd()
    
    # 繪製頂部
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, height)
    for i in range(num_sides + 1):
        angle = 2 * math.pi * i / num_sides
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, height)
    glEnd()

# 初始化 Pygame 與 OpenGL
pygame.init()
screen = pygame.display.set_mode((2160, 1024), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Link Start - OpenGL 版")
# 設定透視與攝影機位置
gluPerspective(45, (800/600), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5)

# 儲存所有圓柱物件
cylinders = []

def emit_cylinders():
    """從畫面中心發射多個 3D 圓柱，每根圓柱發射角度均勻分布"""
    num = 20
    for i in range(num):
        angle = 2 * math.pi * i / num
        color = (random.random(), random.random(), random.random())
        cylinders.append(Cylinder(angle, color))

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and event.key == K_SPACE:
            emit_cylinders()
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # 更新並繪製所有圓柱
    for cyl in cylinders:
        cyl.update()
        cyl.draw()
    
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()
