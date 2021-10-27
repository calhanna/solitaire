
import pygame, random

from card import Card

# Initialise window
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption('Solitaire')

# Variable Definition
revealed_cards = pygame.sprite.Group()
hidden_cards = pygame.sprite.Group()

def handle_events(events):
	""" Handle pygame events. Returns True if the window has been closed"""

	for event in events:
		if event.type == pygame.QUIT:
			pygame.quit()
			return True

def create_deck():
	deck = []
	suits = ['Spades', 'Clubs', 'Diamonds', 'Hearts']

	# Create deck as tuples of (Suit, Value)
	for suit in suits:
		for i in range(13):
			new_card = (suit, i+1)
			deck.append(new_card)

	# Shuffle deck
	shuffled_deck = []
	for i in range(52):
		new_card = deck[random.randint(0,len(deck)-1)]
		deck.remove(new_card)
		shuffled_deck.append(new_card)
	deck = shuffled_deck
	
	return deck

deck = create_deck()
revealed_cards.add(Card(deck[0][0], deck[0][1], (400,300)))

def draw():
	screen.fill((0,150,0))

	revealed_cards.draw(screen)

	pygame.display.flip()

done = False
while not done:
	done = handle_events(pygame.event.get())
	if done: break

	draw()

	clock.tick(60)