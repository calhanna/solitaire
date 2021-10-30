from pygame.rect import Rect

class Stack(Rect):
    """ A Rect class for the piles of cards that make up the 'tableau' and 'foundations' of Solitaire """

    def __init__(self, x:int, y:int, h:int):
        Rect.__init__(self, x, y, 70, h)

        self.revealed_cards = []
        self.hidden_cards = []