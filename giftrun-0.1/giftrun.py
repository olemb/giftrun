"""
Gift Run 0.1 
20. December 2002

Author: Ole Martin Bjordalen
olemb@stud.cs.uit.no
http://www.cs.uit.no/~olemb/
"""

import pygame
from pygame.locals import *
import random
import os
import gamesys

config_drop_limit = 1
config_snowflakes = 10
config_music = 1
#config_screen_flags = FULLSCREEN
config_screen_flags = 0
config_screen_size = (640, 480)

sky_color = (180, 180, 255)

HOLE_LAYER = -1
HOUSE_LAYER = 0
REINDEER_LAYER = 1
GIFT_LAYER = 2

SNOW_LAYER = 3

class Reindeer(gamesys.Sprite):
    def __init__(self, game, pos, delay, rudolph=0):
        gamesys.Sprite.__init__(self)

        self.game = game
        self.delay = delay
        if rudolph:
            self.image = self.game.images['rudolph1']
            self.other_image = self.game.images['rudolph2']
        else:
            self.image = self.game.images['reindeer1']
            self.other_image = self.game.images['reindeer2']
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.add([self.game.objects])

        self.z = REINDEER_LAYER

        self.walk()

    def move(self, rel):
        self.rect.move_ip(rel)

    def walk(self):
        self.image, self.other_image = self.other_image, self.image
        self.game.after(0.3, self.walk)

    def update(self):
        # Counteract speed
        self.rect.left -= self.game.speed

class Santa(gamesys.Sprite):
    def __init__(self, game, pos, delay=0):
        gamesys.Sprite.__init__(self)

        self.game = game
        self.delay = delay
        self.image = self.game.images['santa1']
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.add([self.game.objects])

        self.z = REINDEER_LAYER

        self.dropping = 0

    def move(self, rel):
        self.rect.move_ip(rel)

    def drop(self):
        if self.dropping and config_drop_limit:
            return
        
        Gift(self.game, self.rect.center)
        self.dropping += 1
        self.game.after(0.2, self._fetch)
        self._set_image('santa2')

        self.game.gifts_dropped += 1

    def _fetch(self):
        self._set_image('santa3')
        self.game.after(0.2, self._undrop)

    def _undrop(self):
        self._set_image('santa1')
        self.dropping -= 1

    def _set_image(self, image):
        bottomleft = self.rect.bottomleft
        self.image = self.game.images[image]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = bottomleft

    def update(self):
        # Counteract speed
        self.rect.left -= self.game.speed

class Gift(gamesys.Sprite):
    def __init__(self, game, pos, delay=0):
        gamesys.Sprite.__init__(self)

        self.game = game
        self.delay = delay
        self.image = self.game.images['gift']
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.rect.move_ip((-15, 10))

        self.add([self.game.objects, self.game.gifts])

        self.z = GIFT_LAYER

        self.xspeed = self.game.speed
        self.yspeed = 1.0

        self.sound = self.game.sounds['whistle'].play()

    def move(self, rel):
        self.rect.move_ip(rel)

    def update(self):
        self.rect.left -= self.xspeed
        self.rect.top += self.yspeed
        self.yspeed += 0.5

        if self.rect.top >= (self.game.rect.bottom - 28):
            if pygame.sprite.spritecollideany(self, self.game.houses):
                Thing(self.game, self.rect.center, 'splat', 'splat')
                self.kill()
            elif self.rect.top >= self.game.rect.bottom + 100:
                Thing(self.game, self.rect.center, 'splat', 'splat')
                self.kill()

    def kill(self):
        gamesys.Sprite.kill(self)
        if self.sound:
            self.sound.stop()

class Hole(gamesys.Sprite):
    image = pygame.Surface((1, 1))
    image.fill((0, 255, 0))

    def __init__(self, game, pos, smoking):
        gamesys.Sprite.__init__(self)

        self.game = game
        self.image = Hole.image
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.smoking = smoking

        self.add([self.game.objects, self.game.holes])

        self.z = HOLE_LAYER

class Smoke(gamesys.Sprite):
    def __init__(self, game, hole):
        gamesys.Sprite.__init__(self)

        self.game = game

        self.image = self.game.images['smoke1']
        self.other = self.game.images['smoke2']
        self.rect = self.image.get_rect()
        self.rect.midbottom = hole.rect.center
        self.rect.top -= 10
        
        self.add([self.game.objects])

        self.z = HOUSE_LAYER

        self.switch()

    def switch(self):
        self.image, self.other = self.other, self.image
        self.game.after(0.3, self.switch)

class House(gamesys.Sprite):
    def __init__(self, game):
        gamesys.Sprite.__init__(self)

        self.game = game

        self.smoking = random.choice((0, 0, 0, 1))
        self.image = self.game.images['chimney']

        self.rect = self.image.get_rect()
        self.rect.right = self.game.rect.left
        self.rect.bottom = self.game.rect.bottom + 2

        self.add([self.game.objects, self.game.houses])

        self.z = HOUSE_LAYER

        x, y = self.rect.topleft
        x += 53
        y += 8
        self.hole = Hole(self.game, (x, y), self.smoking)
        if self.smoking:
            self.smoke = Smoke(self.game, self.hole)

    def update(self):
        if self.rect.left >= self.game.rect.right:
            self.kill()
            self.hole.kill()
            if self.smoking:
                self.smoke.kill()

class Thing(gamesys.Sprite):
    def __init__(self, game, pos, image, sound, motion=None):
        gamesys.Sprite.__init__(self)

        self.game = game
        self.image = self.game.images[image]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.motion = motion

        self.add([self.game.objects])

        self.z = GIFT_LAYER

        self.game.sounds[sound].play()

    def update(self):
        if self.motion:
            self.rect.move_ip(self.motion)
        # Outside the screen now?
        if not self.rect.colliderect(self.game.rect):
            self.kill()

class Snowflake(gamesys.Sprite):
    def __init__(self, game):
        gamesys.Sprite.__init__(self)

        self.game = game

        self.image = self.game.images['snowflake']
        self.rect = self.image.get_rect()
        self.restart()

        self.z = SNOW_LAYER

        self.add([self.game.objects])

        self.rect.centerx = random.randrange(self.game.rect.width)
        self.rect.centery = random.randrange(self.game.rect.height)
        self.speed = random.randrange(1, 5)

        self.drift = 0

    def restart(self):
        if random.choice((0, 1)):
            self.rect.bottom = 0
            self.rect.centerx = random.randrange(self.game.rect.width)
            self.speed = random.randrange(1, 5)
        else:
            self.rect.right = 0
            self.rect.centery = random.randrange(self.game.rect.height)
            self.speed = random.randrange(1, 5)

    def update(self):
        self.rect.top += self.speed

        if self.rect.top >= self.game.rect.bottom \
               or self.rect.left >= self.game.rect.right:
            self.restart()

class Game(gamesys.Game):
    def init(self):
        self.background.fill(sky_color)

        self.box = pygame.Surface((20, 20))
        self.box.fill((100, 100, 100))
        self.smallbox = pygame.Surface((10, 10))
        self.smallbox.fill((100, 100, 100))

        self.speed = 6

        self.gifts = pygame.sprite.Group()
        self.holes = pygame.sprite.Group()
        self.houses = pygame.sprite.Group()
        self.reindeer = [
            Reindeer(self, (200, 200), 0, rudolph=1),
            Reindeer(self, (292, 200), 0.07),
            Santa(self, (400, 200), 0.07*2),
            ]
        # Make a bounding box covering santa and both reindeer.
        # This is used for collision detection with the screen.
        self.bbox = pygame.Rect(self.reindeer[0].rect)
        self.bbox.union_ip(self.reindeer[1].rect)
        self.bbox.union_ip(self.reindeer[2].rect)
        
        self.house_dist = 0

        if config_snowflakes:
            for i in range(config_snowflakes):
                Snowflake(self)

        # Estimated world population at 20. december 2002,
        # from http://blue.census.gov/cgi-bin/ipc/popclockw
        self.world_population = 6263245616
        self.gifts_dropped = 0
        self.gifts_delivered = 0

    def move_rudolph(self, rel):
        # Only move if everyone will still be
        # inside the screen
        rect = self.bbox.move(rel)
        if self.rect.contains(rect):
            self.bbox = rect
            for r in self.reindeer:
                self.after(r.delay, r.move, rel)

    def update(self, events):
        if self.house_dist <= 0:
            House(self)
            self.house_dist = 200 + random.randrange(200)
        else:
            self.house_dist -= self.speed

        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    self.reindeer[-1].drop()

        pressed = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if pressed[K_LEFT]:
            dx -= 1
        if pressed[K_RIGHT]:
            dx += 1
        if pressed[K_UP]:
            dy -= 1
        if pressed[K_DOWN]:
            dy += 1
        if dx or dy:
            self.move_rudolph((dx*10, dy*10))

        coll = pygame.sprite.groupcollide
        for gift, holes in coll(self.gifts, self.holes, 1, 0).items():
            hole = holes[0]
            if hole.smoking:
                Thing(self, hole.rect.center, 'poof', 'poof', (0, -6))
            else:
                Thing(self, hole.rect.center, 'star', 'plingeling', (0, -6))
                self.gifts_delivered += 1
                if self.gifts_delivered >= self.world_population:
                    Thing(self, self.rect.center,
                          'youdidit', 'plingeling', (-self.speed, 0))

        self.speed = (320 - (self.reindeer[0].rect.centerx))/20
        if self.speed < 0:
            self.speed = 0
        
        # move all objects a bit to the right
        for obj in self.objects.sprites():
            obj.rect.left += self.speed

class TitleScreen(gamesys.Game):
    def init(self):
        self.background.fill(sky_color)
        img = self.images['title']
        rect = img.get_rect()
        rect.center = self.rect.center
        self.background.blit(img, rect)

        if config_snowflakes:
            for i in range(config_snowflakes):
                Snowflake(self)

        # Start music
        music = os.path.join('data', 'music', 'jinglebells.mod')
        pygame.mixer.music.load(os.path.join(music))
        pygame.mixer.music.play(-1)
        
    def play_game(self):
        # Stop music
        pygame.mixer.music.stop()

        Game().mainloop()

        # Stop sounds
        pygame.mixer.stop()

        # Redraw the title screen and restart music
        self.init()
        self.blit_background()

    def update(self, events):
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    self.play_game()

pygame.display.set_mode(config_screen_size,
                        config_screen_flags)
pygame.display.set_caption('Gift Run')
TitleScreen().mainloop()

