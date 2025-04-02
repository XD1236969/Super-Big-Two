import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random, math

# ======================
#     Cylinder 類別
# ======================
class Cylinder:
    def __init__(self):
        # 隨機方向：用球面座標分布，theta 為 0~2π，phi 為 0~π
        theta = random.uniform(0, 2*math.pi)
        phi   = random.uniform(0, math.pi)
        # 轉換為 (x, y, z) 向量
        self.direction = (
            math.sin(phi) * math.cos(theta),
            math.sin(phi) * math.sin(theta),
            math.cos(phi)
        )
        # 隨機顏色 (R,G,B)
        self.color = (random.random(), random.random(), random.random())
        # 移動相關
        self.speed = 0.2       # 移動速度
        self.distance = 0.0    # 與中心距離
        # 圓柱外觀
        self.radius = 0.15
        self.height = random.uniform(1.0, 3.0)  # 隨機長度
        self.num_sides = 20    # 邊數多一點會更圓滑

    def update(self):
        self.distance += self.speed

    def draw(self):
        """繪製立體圓柱，從 (0,0,0) 沿 z 軸方向延伸，之後再做旋轉/平移。"""
        # 先計算當前位置
        x = self.distance * self.direction[0]
        y = self.distance * self.direction[1]
        z = self.distance * self.direction[2]
        
        # 進行座標變換
        glPushMatrix()
        # 移動到正確位置
        glTranslatef(x, y, z)
        # 設定顏色
        glColor3fv(self.color)

        # 使圓柱 z 軸對齊 self.direction
        # 預設圓柱是沿著 (0,0,1)，現在要算跟 self.direction 的夾角與旋轉軸
        dx, dy, dz = self.direction
        # 夾角：跟 (0,0,1) 做內積
        # dot = dz (因為 (0,0,1)·(dx,dy,dz) = dz)
        # cos(angle) = dot / (|v1|*|v2|) = dz / 1
        angle = math.degrees(math.acos(dz))
        # 旋轉軸： (0,0,1) x (dx, dy, dz) = ( -dy, dx, 0 )
        rx, ry, rz = -dy, dx, 0
        norm = math.sqrt(rx*rx + ry*ry + rz*rz)
        if norm > 1e-6:
            glRotatef(angle, rx, ry, rz)

        # 繪製圓柱
        draw_cylinder(self.radius, self.height, self.num_sides)
        glPopMatrix()

# ======================
#   繪製圓柱 (OpenGL)
# ======================
def draw_cylinder(radius, height, num_sides):
    # 側面
    glBegin(GL_QUAD_STRIP)
    for i in range(num_sides+1):
        angle = 2 * math.pi * i / num_sides
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, 0)
        glVertex3f(x, y, height)
    glEnd()

    # 底部圓盤
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)
    for i in range(num_sides+1):
        angle = 2 * math.pi * i / num_sides
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, 0)
    glEnd()

    # 頂部圓盤
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, height)
    for i in range(num_sides+1):
        angle = 2 * math.pi * i / num_sides
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, height)
    glEnd()

# ======================
#    主程式開始
# ======================
def main():
    pygame.init()
    screen = pygame.display.set_mode((2160, 1080), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Link Start - 多彩立體長條")
    
    # 設定背景顏色：白色 (1,1,1,1)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # 開啟深度測試
    glEnable(GL_DEPTH_TEST)

    # 設定透視視角
    gluPerspective(45, (1000 / 800), 0.1, 50.0)
    # 將攝影機往 Z 軸後退一些
    glTranslatef(0.0, 0.0, -10)

    # 存放所有飛出的圓柱
    cylinders = []

    def emit_cylinders():
        "按下空白鍵時，一次發射多個彩色圓柱"
        num = 40  # 一次多發一些，效果更明顯
        for _ in range(num):
            cylinders.append(Cylinder())

    clock = pygame.time.Clock()
    running = True
    while running:
        # 事件處理
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_SPACE:
                    emit_cylinders()

        # 每次更新畫面
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 更新、繪製所有圓柱
        for cyl in cylinders:
            cyl.update()
            cyl.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
