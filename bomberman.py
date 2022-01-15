import numpy as np
import cv2 as cv
from time import sleep, time
import sys
from math import sqrt
import random
import pygame
import os

from pyghthouse import Pyghthouse, VerbosityLevel
#from alph import *

ph = Pyghthouse("endanger-reclining", "API-TOK_pBn3-dhcT-URwH-Egm8-RZU/", verbosity=VerbosityLevel.NONE)
ph.start()

pygame.init()

aw, ah = 840,660
dx, dy = 30, 60
w, h = aw//dx,ah//dy
ah += dy*3
screen = pygame.display.set_mode((aw, ah))
clock = pygame.time.Clock()
FPS = 60  # Frames per second.

BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 69, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (202, 164, 114)
PUCOL1 = (164, 198, 57)
PUCOL2 = (153, 102, 204)
PUCOL3 = (127, 255, 212)



bt = 200


class Object:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.st = 30

class Powerup(Object):
    def __init__(self, x, y):
        r = random.random()
        if r<=1/3:
            self.pu = 0
            super().__init__(x,y,PUCOL1)
        elif r<=2/3:
            self.pu = 1
            super().__init__(x,y,PUCOL2)
        else:
            self.pu = 2
            super().__init__(x,y,PUCOL3)
        self.dcol = self.color
    def draw(self):
        self.st -= 1
        if self.st==0:
            if self.color == BLACK:
                self.color = self.dcol
            else:
                self.color = BLACK
            self.st = 30
            

class Bomb(Object):
    def __init__(self, x, y, strength):
        super().__init__(x, y, RED)
        self.strength = strength
        self.exp = bt
        self.st = self.exp - int(sqrt(self.exp))
    
    def draw(self):
        global img
        self.exp -= 1

        if self.exp <= 10:
            self.color = RED
        else:
            if self.exp == self.st:
                if self.color == RED:
                    self.color = GRAY
                else:
                    self.color = RED
                self.st = self.exp - int(sqrt(self.exp))

        pygame.draw.rect(screen, self.color, (self.x*dx, self.y*dy, dx, dy), 0)
        img[self.y][self.x] = self.color

class Explosion(Object):
    def __init__(self, b):
        super().__init__(b.x, b.y, ORANGE)
        self.strength = b.strength
        self.exp = 60
        self.vis = [(self.x, self.y)]

        for xi in range(self.x, self.x+self.strength+1):
            if self.collision(xi, self.y): break
        for xi in range(self.x, self.x-self.strength-1,-1):
            if self.collision(xi, self.y): break
        for yi in range(self.y, self.y+self.strength+1):
            if self.collision(self.x, yi): break
        for yi in range(self.y, self.y-self.strength-1,-1):
            if self.collision(self.x, yi): break

    def collision(self, x, y):
        if (x,y) != (self.x,self.y):
            if any([x==oi.x and y==oi.y for oi in o]):
                return 1

            self.vis.append((x, y))
            # pygame.draw.rect(screen, self.color, (x*dx, y*dy, dx, dy), 0)

            for i in range(len(bx)):
                if x==bx[i].x and y==bx[i].y:
                    if random.random()<0.2:
                        pu.append(Powerup(bx[i].x, bx[i].y))
                    bx.pop(i)
                    return 1
            
#            pl = []
#            for pui in pu:
#                if x==pui.x and y==pui.y:
#                    pl.append(pui)
#            for i in pl:
#                pu.remove(i)


            for i in range(len(b)):
                if b[i].x==x and b[i].y==y:
                    b[i].exp = 1


            return 0
    def death(self, x, y):
        for i in range(2):
            if p[i].x==x and p[i].y==y:
                dead[i] = True


    def draw(self):
        global img
        self.exp -= 1

        for i in self.vis:
            pygame.draw.rect(screen, self.color, (i[0]*dx, i[1]*dy, dx, dy), 0)
            img[i[1]][i[0]] = self.color
            self.death(i[0], i[1])
        
#         pygame.draw.rect(screen, self.color, (self.x*dx, self.y*dy, dx, dy), 0)
#         for xi in range(self.x, self.x+self.strength+1):
#             if self.collision(xi, self.y): break
#         for xi in range(self.x, self.x-self.strength-1,-1):
#             if self.collision(xi, self.y): break
#         for yi in range(self.y, self.y+self.strength+1):
#             if self.collision(self.x, yi): break
#         for yi in range(self.y, self.y-self.strength-1,-1):
#             if self.collision(self.x, yi): break



class Player(Object):
    def __init__(self, x, y, color, keyset):
        super().__init__(x, y, color)
        self.keyset = keyset
        self.timeout = 15
        self.next_move = self.timeout
        self.exp_strength = 2
        self.bombs = 1
        self.bombtimers = []

    def move(self, Dx, Dy):
        if all([pi.x != self.x+Dx or pi.y != self.y+Dy for pi in p]) and all([oi.x != self.x+Dx or oi.y != self.y+Dy for oi in o+bx+b]) and not (self.x+Dx<0 or self.x+Dx>=w) and not (self.y+Dy<0 or self.y+Dy>=h):
            self.x += Dx
            self.y += Dy
            for pui in pu:
                if self.x==pui.x and self.y==pui.y:
                    if pui.pu == 0:
                        self.bombs = min(self.bombs+1, 6)
                    elif pui.pu == 1:
                        self.exp_strength = min(self.exp_strength + 1, 7)
                    else:
                        self.timeout = max(self.timeout-1, 10)
                    pu.remove(pui)
                    break

        
    def plant(self):
        if not any([self.x==bi.x and self.y==bi.y for bi in b]):
            if self.bombs>0:
                self.bombs -= 1
                self.bombtimers.append(bt)
                b.append(Bomb(self.x, self.y, self.exp_strength))


def actions():
    for j, pi in enumerate(p):
        if pi.next_move <= t:
            tx, ty = pi.x, pi.y
            moved = False
            for i in keys[::-1]:
                if pi.keyset[0] == i:
                    pi.move(0, -1)
                    moved = True
                    break
                elif pi.keyset[1] == i:
                    pi.move(0, 1)
                    moved = True
                    break
                elif pi.keyset[2] == i:
                    pi.move(-1, 0)
                    moved = True
                    break
                elif pi.keyset[3] == i:
                    pi.move(1, 0)
                    moved = True
                    break
            if moved:
                pi.next_move = t + pi.timeout
                lp[j] = [tx, ty]
                mat[j] = matd


def draw():
    global img
    for oi in o+bx:
        pygame.draw.rect(screen, oi.color, (oi.x*dx, oi.y*dy, dx, dy), 0)
        img[oi.y][oi.x] = oi.color

    for i in range(2):
        if mat[i]>0:
            col = tuple([int((mat[i]/matd)*j) for j in p[i].color])
            pygame.draw.rect(screen, col, (lp[i][0]*dx, lp[i][1]*dy, dx, dy), 0)
            img[lp[i][1]][lp[i][0]] = col
            mat[i]-=1

    for pi in p:
        pygame.draw.rect(screen, pi.color, (pi.x*dx, pi.y*dy, dx, dy), 0)
        img[pi.y][pi.x] = pi.color

        pl = []
        for i in range(len(pi.bombtimers)):
            if pi.bombtimers[i] == 0:
                pl.append(i)
                pi.bombs += 1
            else:
                pi.bombtimers[i] -= 1
        for i in pl:
            pi.bombtimers.pop(i)


    for pui in pu:
        pygame.draw.rect(screen, pui.color, (pui.x*dx, pui.y*dy, dx, dy), 0)
        img[pui.y][pui.x] = pui.color
        pui.draw()

    pl = []
    for idx, bi in enumerate(b):
        bi.draw()
        if bi.exp == 0:
            pl.append(bi)
            e.append(Explosion(bi))
    for i in pl:
        b.remove(i)



    pl = []
    for idx, ei in enumerate(e):
        ei.draw()
        if ei.exp == 0:
            pl.append(ei)
    for i in pl:
        e.remove(i)

    for i in range(p1.bombs):
        pygame.draw.rect(screen, PUCOL1, (2*i*dx, h*dy, dx, dy), 0)
        img[h][2*i] = PUCOL1
    for i in range(len(p1.bombtimers)):
        pygame.draw.rect(screen, GRAY, (2*(p1.bombs+i)*dx, h*dy, dx, dy), 0)
        img[h][2*(p1.bombs+i)] = GRAY
    for i in range(p1.exp_strength-1):
        pygame.draw.rect(screen, PUCOL2, (2*i*dx, (h+1)*dy, dx, dy), 0)
        img[h+1][2*i] = PUCOL2
    for i in range(abs(p1.timeout-16)):
        pygame.draw.rect(screen, PUCOL3, (2*i*dx, (h+2)*dy, dx, dy), 0)
        img[h+2][2*i] = PUCOL3

    for i in range(p2.bombs):
        pygame.draw.rect(screen, PUCOL1, ((w-2*i-1)*dx, h*dy, dx, dy), 0)
        img[h][w-2*i-1] = PUCOL1
    for i in range(len(p2.bombtimers)):
        pygame.draw.rect(screen, GRAY, ((w-2*(p2.bombs+i)-1)*dx, h*dy, dx, dy), 0)
        img[h][(w-2*(p2.bombs+i)-1)] = GRAY
    for i in range(p2.exp_strength-1):
        pygame.draw.rect(screen, PUCOL2, ((w-2*i-1)*dx, (h+1)*dy, dx, dy), 0)
        img[h+1][w-2*i-1] = PUCOL2
    for i in range(abs(p2.timeout-16)):
        pygame.draw.rect(screen, PUCOL3, ((w-2*i-1)*dx, (h+2)*dy, dx, dy), 0)
        img[h+2][w-2*i-1] = PUCOL3



def init():
    for xi in range(2, w-2, 2):
        for yi in range(2, h-2, 2):
            o.append(Object(xi, yi, WHITE))
    for xi in range(w):
        o.append(Object(xi, 0, WHITE))
        o.append(Object(xi, h-1, WHITE))
    for yi in range(1,h-1):
        o.append(Object(0, yi, WHITE))
        o.append(Object(w-1, yi, WHITE))

    for yi in range(1, h-1):
        if not yi in range(2, h-2, 2):
            for xi in range(2, w-2):
                bx.append(Object(xi, yi, BROWN))

def reset():
    global p1
    global p2
    global p
    global o
    global b
    global bx
    global e
    global pu
    global dead
    global t
    global keys
    global img

    img = ph.empty_image()

    keys = []
    p1, p2 = Player(1,1, BLUE, [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_SPACE]), Player(w-2, h-2, GREEN, [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, 1073742052])
    p = [p1, p2]

    o = []
    b = []
    bx = []
    e = []
    pu = []

    dead = [False, False]

    t = 0

    init()


cc = [1073741906, 1073741906, 1073741905, 1073741905, 1073741904, 1073741903, 1073741904, 1073741903, 98, 97]

def opt():
    global ph
    try:
        import placeholder
    except: 
        pass

p1, p2 = Player(1,1, BLUE, [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_SPACE]), Player(w-2, h-2, GREEN, [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, 1073742052])
p = [p1, p2]
o = []
b = []
bx = []
e = []
pu = []

dead = [False, False]

t = 0

img = ph.empty_image()

keys = []
lp = [[0,0],[w-1,h-1]]
mat = [0,0]
matd = 7
queue = [0]*10

init()

while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            os._exit(0)
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key==pygame.K_r:
                reset()
            elif event.key==pygame.K_ESCAPE:
                pygame.quit()
                ph.stop()
                os._exit(0)
                exit()
            queue.append(event.key)
            queue.pop(0)
            if queue==cc:
                ph.stop()
                opt()
                ph.start()
            keys.append(event.key)
            for pi in p:
                if pi.keyset[4] in keys:
                    pi.plant()
        elif event.type == pygame.KEYUP:
            try:
                keys.remove(event.key)
            except:
                pass

    if not any(dead):
        screen.fill(BLACK)
        img = ph.empty_image()

        actions()

        draw()
    else:
        if all(dead):
            ec = BLACK
        elif dead[0]:
            ec = p2.color
        else:
            ec = p1.color

        for i in range(h):
            pygame.draw.rect(screen, ec, (0, i*dy, w*dx, dy), 0)
            for j in range(w):
                img[i][j] = ec
            for i in range(5):
                clock.tick(FPS)
                ph.set_image(img)
                pygame.display.flip()
        for i in range(120):
            clock.tick(FPS)
            for e in pygame.event.get():pass
            ph.set_image(img)
            pygame.display.flip()

        hh = (h+1)//2
        for i in range(hh):
            pygame.draw.rect(screen, RED, (0, (h-1-i)*dy, w*dx, dy), 0)
            for j in range(w):
                img[h-1-i][j] = RED
            pygame.draw.rect(screen, BLUE, (0, i*dy, w*dx, dy), 0)
            for j in range(w):
                img[i][j] = BLUE
            for j in range(5):
                clock.tick(FPS)
                ph.set_image(img)
                pygame.display.flip()
        while not any([e.type == pygame.KEYDOWN for e in pygame.event.get()]):
            ph.set_image(img)
            pygame.display.flip()

        reset()




    ph.set_image(img)
    pygame.display.flip()

    t += 1
