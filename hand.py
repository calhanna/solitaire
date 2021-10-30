from pygame.rect import Rect

class Hand(Rect):
    """ Container for the currently held cards. Basically just a glorified array that can draw itself """

    def __init__(self, mouse):
        Rect.__init__(self, 0, 0, 70, 90)
        self.center = mouse
        self.cards = []

    def draw(self, screen):
        # Will eventually do something clever here 

        if len(self.cards) > 0:
            screen.blit(self.cards[-1].image, self)

    def update(self, mouse):
        self.center = mouse