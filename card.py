import pygame
class Card(pygame.sprite.Sprite):
	""" 
		Basic Card Class.
		Arguments:
			- suit: String containing the suit of the card
			- num: int card number
			- center: position tuple 
	"""
	def __init__(self, suit, num, center):
		pygame.sprite.Sprite.__init__(self)

		self.revealed = False
		self.value = num
		self.suit = suit
		
		# Convert num into string for filepath. Values above 10 need to be converted to face cards
		if num == 1: num = 'A'
		elif num == 11: num = 'J'
		elif num == 12: num = 'Q'
		elif num == 13: num = 'K'
		else: num = str(num)

		# Find card image (stored as cardSuitNum.png)
		image_direc = 'images/cards/card' + suit + num + '.png'
		self.image = pygame.image.load(image_direc)
		self.image = pygame.transform.scale(self.image, (70, 95))

		self.rect = self.image.get_rect()
		self.rect.center = center

