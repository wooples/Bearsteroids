#!/usr/bin/python3

import pygame
import random
import math
sin = lambda x: math.sin(x*math.pi/180)
cos = lambda x: math.cos(x*math.pi/180)
import os
import time

WIDTH, HEIGHT = 1000, 800
FPS = 60
BEAR_SPEED = 2.5
ROT = 3
BULLET_SPEED = 20
FIRE_GOVERNER = 10
FIRE_LIMIT = 10
EDGE_MARGIN = 20
EDGE_MARGIN = 0
ROT_RATE = 5
MAX_SPEED = 8 

WHITE, BLACK = (255,255,255), (0,0,0)

bear_images = os.listdir('images/bears')
baby_images = os.listdir('images/babies')

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

bear_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
antibear_group = pygame.sprite.Group()

clock = pygame.time.Clock()

class Wrap_Sprite(pygame.sprite.Sprite):
    '''abstract class for all sprites.  simply does "screen-wrap"so that
       going off edge brings sprite to opposite side upon update'''
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.image = pygame.image.load(self.picture)

    def update(self):
        self.rect.x = self.rect.x + self.d_x
        self.rect.y = self.rect.y + self.d_y
        self.rect.x = self.rect.x % WIDTH
        self.rect.y = self.rect.y % HEIGHT
        self.image = pygame.image.load(self.picture)
        self.angle = self.angle + self.d_angle
        self.image = pygame.transform.rotate(self.image, self.angle)

    def be_hit(self):
        self.kill()


class Bear(Wrap_Sprite):

    def __init__(self):

        self.picture = 'images/bears/' + random.choice(bear_images)
        super().__init__()
        self.rect = self.image.get_rect()
        self.rect.center = (0,0)

        angle = random.randrange(360)
        self.d_x = BEAR_SPEED * cos(angle)
        self.d_y = BEAR_SPEED * sin(angle)

        self.d_angle = random.random() * ROT_RATE

    def be_hit(self):
        for i in range(3):
            bear_group.add(Baby(self.rect.x, self.rect.y,\
                                self.d_x, self.d_y))
        self.kill()


class Baby(Wrap_Sprite):

    def __init__(self, x, y, d_x, d_y):

        self.picture = 'images/babies/' + random.choice(baby_images)
        super().__init__()
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.d_x = d_x + (1-2*random.random())
        self.d_y = d_y + (1-2*random.random())
        self.d_angle = random.random() * ROT_RATE


class AntiBear(Wrap_Sprite):

    def __init__(self):
        self.picture = 'images/antibear.png'
        super().__init__()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = int(WIDTH/2), int(HEIGHT/2)
        self.d_x, self.d_y = 0, 0
        self.d_angle = 0
        self.speed = 0

    def rot_left(self):
        self.angle = int(self.angle + ROT)%360
        self.image = pygame.image.load("images/antibear.png").convert()
        #dont re-rotate original
        self.image = pygame.transform.rotate(self.image, self.angle)

    def rot_right(self):
        self.angle = int(self.angle - ROT)%360
        self.image = pygame.image.load("images/antibear.png").convert()
        #dont re-rotate original
        self.image = pygame.transform.rotate(self.image, self.angle)

    def thrust(self):
        self.d_x = .1*cos(self.angle) + self.d_x
        self.d_y = -.1*sin(self.angle) + self.d_y
        self.speed = (self.d_x**2+self.d_y**2)**.5
        if self.speed >= MAX_SPEED:
             self.d_x = (MAX_SPEED / self.speed) * self.d_x
             self.d_y = (MAX_SPEED / self.speed) * self.d_y
            
    def fire(self):
        if len(bullet_group)<5:
            bullet_group.add(Bullet(self.rect.x, self.rect.y,\
                             int(BULLET_SPEED*(cos(self.angle))),\
                            -int(BULLET_SPEED*(sin(self.angle)))))

    def be_hit(self):
        for i in range(3):
            screen.fill((255,0,0))
            pygame.display.flip()
            time.sleep(.25)
            screen.fill((255,255,0))
            pygame.display.flip()
            time.sleep(.25)
 
        for b in bear_group:
            b.kill()
        self.__init__()
       
 
class Bullet(Wrap_Sprite):

    def __init__(self, x, y, d_x, d_y):
        self.picture = 'images/bullet.png'

        super().__init__()
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.d_angle = 0
        self.d_x, self.d_y = d_x, d_y
        self.dist = 0

    def update(self):
        super().update()
        self.dist = self.dist + 1
        if self.dist > HEIGHT/BULLET_SPEED:
            self.kill()


def pix_collide(a, b):

    am = pygame.mask.from_surface(a.image)
    bm = pygame.mask.from_surface(b.image)

    offset_x = a.rect[0] - b.rect[0]
    offset_y = a.rect[1] - b.rect[1]

    return bm.overlap(am, (offset_x, offset_y))


def make_bears(n=5):
   # pass
   # '''
    for i in range(5):
        b=Bear()
        bear_group.add(b)
    #'''

antibear_group.add(AntiBear())

#make_bears()

fire_governer = 0

running = True
while running:
    clock.tick(FPS)

    fire_governer = fire_governer + 1
    fire_governer = min(fire_governer, FIRE_GOVERNER)

    pressed = pygame.key.get_pressed()

    if pressed[pygame.K_LEFT]:
        for ab in antibear_group:
            ab.rot_left()
    if pressed[pygame.K_RIGHT]:
        for ab in antibear_group:
            ab.rot_right()
    if pressed[pygame.K_UP]:
            ab.thrust()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            for ab in antibear_group:
                if event.key == pygame.K_SPACE and\
                                fire_governer == FIRE_GOVERNER:
                    fire_governer = 0
                    ab.fire()

    for bear in bear_group:
        
        list(map(lambda x: bear.be_hit() and  x.be_hit() if x.rect.colliderect(bear) else None,  bullet_group))

        for ab in antibear_group:
            if ab.rect.colliderect(bear) and pix_collide(ab, bear):
               ab.be_hit()


    if not bear_group:
        make_bears()

    screen.fill(BLACK)
    bear_group.update()
    bear_group.draw(screen)
    antibear_group.update()
    antibear_group.draw(screen)
    bullet_group.update()
    bullet_group.draw(screen)
    pygame.display.flip()

pygame.quit()
