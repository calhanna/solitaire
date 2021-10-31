import pygame
from pygame.rect import Rect

class Button(Rect):
    """ UI Button class. Rectangle with icon and function """
    
    def __init__(self, pos:tuple, func:str, icon:str):
        Rect.__init__(self, pos[0], pos[1], 30, 30)
        self.function = func

        self.icon = pygame.image.load('images/icons/' + icon + '.png')
        self.alt_icon = pygame.image.load('images/icons/' + icon + '_alt.png')

        try:
            self.disabled_icon = pygame.image.load('images/icons/' + icon + '_disabled.png')
        except FileNotFoundError:
            pass

        self.hover = False
        self.clicked = False

        self.disabled = False

    def draw(self, screen):
        if self.hover: screen.blit(self.alt_icon, self)
        elif self.disabled: screen.blit(self.disabled_icon, self)
        else: screen.blit(self.icon, self)
