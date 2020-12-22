"""

The gamesys module is a simple framework for writing little games.  It
contains all the little pieces of code that I got tired of writing
over and over and over again.

The module provides:

- a game loop with framerate limiting (currently hard coded to 30fps)
- automatic exit when K_ESCAPE is pressed or the window is closed
- 'f' key toggles full screen mode
- resource management (loads all images and sounds from data/images
  and data/sounds and inserts them in a couple of dictionaries)
- z sorted drawing of objects, so you can easily arrange them in
  layers
- a method after(seconds, method, *args) which can be used to
  schedule events
- an unnecessary but convenient shortcut to pygame.sprite.Sprite

Author: Ole Martin Bjorndalen
olemb@stud.cs.uit.no
http://www.cs.uit.no/~olemb/
"""

import pygame
import glob
import os
import sched
import time
from pygame.locals import *

# Just a shortcut
Sprite = pygame.sprite.Sprite

class EscapeException(Exception):
    "Raised when the user presses escape"
    pass

# z-sorted rendering
# from Ken 'MrPython' Seehof's game Parrot
# http://www.neuralintegrator.com/parrot/
class RenderZSort(pygame.sprite.RenderUpdates):
    def draw(self, surface):
        "draw all sprites onto a surface in z order (lowest z first)"
        spritedict = self.spritedict
        items = sorted(spritedict.items(), key=lambda a: a[0].z)
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append

        for s, r in items:
            newrect = surface_blit(s.image, s.rect)
            #s.post_draw(surface)
            surface_blit(s.image, s.rect)
            if r is not 0:
                dirty_append(newrect.union(r))
            else:
                dirty_append(newrect)
            spritedict[s] = newrect
        return dirty

class Game:
    def __init__(self):
        pygame.init()  # Perhaps this shouldn't be done here

        self._sched = sched.scheduler(time.time, time.sleep)

        # Public members
        self.screen = pygame.display.get_surface()
        self.background = pygame.Surface(self.screen.get_size())
        self.rect = self.screen.get_rect()
        self.objects = RenderZSort()
        self.images = self._load_images()
        self.sounds = self._load_sounds()

        self.init()
        self.blit_background()

    def blit_background(self):
        self.screen.blit(self.background, (0, 0))
        pygame.display.update()  # In case the background has changed

    def after(self, secs, func, *args):
        self._sched.enter(secs, 1, func, args)

    def _load_images(self):
        images = {}
        for name in glob.glob(os.path.join('data', 'images', '*')):
            img = pygame.image.load(name).convert_alpha()
            name = os.path.splitext(os.path.basename(name))[0]
            images[name] = img
        return images

    def _load_sounds(self):
        sounds = {}
        for name in glob.glob(os.path.join('data', 'sounds', '*')):
            snd = pygame.mixer.Sound(name)
            name = os.path.splitext(os.path.basename(name))[0]
            sounds[name] = snd
        return sounds

    def _redraw(self):
        self._sched.enter(1.0/30.0, 0, self._redraw, ())

        self.objects.clear(self.screen, self.background)

        events = pygame.event.get()
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    raise EscapeException
                elif e.unicode == 'f':
                    pygame.display.toggle_fullscreen()
            elif e.type == QUIT:
                raise SystemExit
        self.update(events)
        self.objects.update()

        dirty = self.objects.draw(self.screen)
        pygame.display.update(dirty)

    def mainloop(self):
        self._redraw()
        try:
            self._sched.run()
        except EscapeException:
            return 0
        else:
            return 1

    #
    # These are just stubs to be overridden
    #
    def init(self):
        "Called at init time. Put initialization code for the game here."

    def update(self, events):
        "Handles events and updates the objects. Called every frame."
        pass

