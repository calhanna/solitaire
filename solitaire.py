# TO DO
# - Fan held cards
# - Add ability to reset game
# - Add ability to win
# - Undo/Redo
# - Maybe if I have time try and make every game solvable with some Weird Maths (tm)

import pygame, random

from card import Card
from stack import Stack
from hand import Hand

# Initialise window
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption('Solitaire')

# Variable Definition
card_back = pygame.image.load('images/cards/cardBack.png')	# Card back sprite. Used for hidden cards and the stock
card_back = pygame.transform.scale(card_back, (70, 95))

hand = Hand(pygame.mouse.get_pos())

def handle_events(events):
	""" Handle pygame events. Returns True if the window has been closed"""
	mouse = pygame.mouse.get_pos()

	for event in events:
		if event.type == pygame.QUIT:
			pygame.quit()
			return True

		elif event.type == pygame.MOUSEBUTTONDOWN:
			if mouse[1] < 120:							# If the mouse is at the top of the screen, check for stock
				if stock.collidepoint(mouse):
					cycle_stock()
				elif stock.move(100,0).collidepoint(mouse) and len(stock.revealed_cards) > 0:
					hand.cards = [stock.revealed_cards[-1]]
				else:
					for foundation in foundations:
						if foundation.collidepoint(mouse):
							hand.cards = [foundation.revealed_cards[-1]]
			else:
				for stack in tableau:
					if stack.move(-35,-45).collidepoint(mouse):		# Check if the mouse is over the stack. We move it because the stack's actual position is a little offset from where it's drawn
						# Find all cards that are below the mouse
						eligible_cards = []
						for card in stack.revealed_cards:
							if card.rect.collidepoint(mouse):
								eligible_cards.append(card)
						
						# We only want to grab the card we are actually hovering over, so get the furthest forward eligible card
						if len(eligible_cards) > 0:
							card = eligible_cards[-1]
							hand.cards = stack.revealed_cards[stack.revealed_cards.index(card):]

		elif event.type == pygame.MOUSEBUTTONUP:
			if len(hand.cards) > 0:
				hand.cards = place_cards()

def place_cards():
	mouse = pygame.mouse.get_pos()
	
	for stack in tableau:
		# Check if the card has been dragged over a stack
		if stack.move(-35, -45).collidepoint(mouse):
			# Check if the bottom card of the hand can be placed on the top card of the stack
			if check_cards(hand.cards[0], stack):
				# Remove cards in hand from their original stacks
				for card in hand.cards:
					for origin in tableau:
						if card in origin.revealed_cards:
							origin.revealed_cards.remove(card)
					
					if card in stock.revealed_cards:
						stock.revealed_cards.remove(card)

					for origin in foundations:
						if card in origin.revealed_cards:
							origin.revealed_cards.remove(card)

					# Add cards to new stack
					stack.revealed_cards.append(card)
					try:
						card.rect = stack.revealed_cards[-2].rect.move(0, 20)	# Returns index error if the card is being placed on an empty space
					except IndexError:
						card.rect.center = (stack.x, stack.y)					# Place first card of new stack
					
				return []

	for foundation in foundations:
		if foundation.collidepoint(mouse):
			if len(hand.cards) == 1 and check_cards(hand.cards[0], foundation):
				for origin in tableau:
					if hand.cards[0] in origin.revealed_cards:
						origin.revealed_cards.remove(hand.cards[0])

				if hand.cards[0] in stock.revealed_cards:
					stock.revealed_cards.remove(hand.cards[0])

				# Usually this won't do anything (bc you can't move cards between foundations) but it does do something when you move an ace to an empty foundation
				for origin in foundations:
					if hand.cards[0] in origin.revealed_cards:
						origin.revealed_cards.remove(hand.cards[0])

				foundation.revealed_cards.append(hand.cards[0])
				hand.cards[0].rect = foundation

				return []			

	return []
				
def cycle_stock():
	""" Reveals the next card in the stock or flips the revealed stock back over"""

	if len(stock.hidden_cards) > 0:
		# Move card from the hidden stock to the revealed stock

		stock.revealed_cards.append(stock.hidden_cards[-1])
		stock.hidden_cards.remove(stock.hidden_cards[-1])
	else:
		# Reset stock
		stock.hidden_cards = stock.revealed_cards
		stock.hidden_cards.reverse()
		stock.revealed_cards = []

def check_cards(card, dest):
	""" Returns True if card can be placed on the front card of dest """

	red = ['Hearts', 'Diamonds']		# Red Suits
	black = ['Spades', 'Clubs']			# Black Suits
	if dest in tableau:
		try:
			dest_card = dest.revealed_cards[-1]
		except IndexError:
			if card.value == 13:
				return True
			else:
				return False
		if dest_card.suit in red:
			if card.suit in black: 
				if card.value == dest_card.value - 1:
					return True
		elif dest_card.suit in black:
			if card.suit in red: 
				if card.value == dest_card.value - 1:
					return True
		return False

	if dest in foundations:
		if len(dest.revealed_cards) == 0:
			if card.value == 1:
				return True
		else:
			if card.suit == dest.revealed_cards[0].suit and card.value == dest.revealed_cards[-1].value + 1:
				return True
		return False

def create_deck():
	""" Returns a shuffled deck of 52 cards """

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

def create_board(deck):
	""" Returns the 'tableau', 'foundations' and 'stock' with which one plays Solitaire """

	tableau = []
	foundations = []

	# Create tableau
	x = 100
	length = 1
	for i in range(7):
		stack = Stack(x, 200, 400)

		for i in range(length):
			stack.hidden_cards.append(Card(deck[0][0], deck[0][1], (x, stack.y+20*i)))		# Add cards to stack
			deck.remove(deck[0])
		
		# Reveal the first card in the stack
		last_card = stack.hidden_cards[-1]
		stack.revealed_cards.append(last_card)
		stack.hidden_cards.remove(last_card)

		tableau.append(stack)
		x += 100
		length += 1

	# Create foundations
	x = 365
	for i in range(4):
		foundations.append(Stack(x, 30, 90))
		x += 100

	# Remaining cards get added to stock.
	stock = Stack(65, 30, 90)
	for card in deck:
		stock.hidden_cards.append(Card(card[0], card[1], stock.center))

	return tableau, foundations, stock

deck = create_deck()
tableau, foundations, stock = create_board(deck)

def draw():
	screen.fill((0,150,0))

	# Draw cards in tableau
	for stack in tableau:
		for card in stack.hidden_cards:
			screen.blit(card_back, card.rect)
		
		for card in stack.revealed_cards:
			if card not in hand.cards:
				screen.blit(card.image, card.rect)

	# Draw the front card of each foundation, an empty space if the foundation is empty, or the next card if the front card is in the hand
	for foundation in foundations:
		pygame.draw.rect(screen, (50,175,50), foundation)
		if len(foundation.revealed_cards) > 0:
			if foundation.revealed_cards[-1] not in hand.cards:
				screen.blit(foundation.revealed_cards[-1].image, foundation)
			else:
				if len(foundation.revealed_cards) > 1:
					screen.blit(foundation.revealed_cards[-2].image, foundation)

	# Draw stock

	if len(stock.hidden_cards) > 0:
		screen.blit(card_back, stock)		# Draw card back for stock pile
	else:
		pygame.draw.rect(screen, (50,175,50), stock)

	if len(stock.revealed_cards) > 0:	# Draw the front revealed stock card
		if stock.revealed_cards[-1] not in hand.cards:	# Checks whether the first stock card has been picked up
			revealed_stock = stock.revealed_cards[-1]
			screen.blit(revealed_stock.image, stock.move(100, 0))
		else:
			if len(stock.revealed_cards) >= 2:			# If the first stock card has been picked up, draw the second one instead. If there is no second one, draw nothing.
				revealed_stock = stock.revealed_cards[-2]
				screen.blit(revealed_stock.image, stock.move(100, 0))

	hand.draw(screen)

	pygame.display.flip()

done = False
while not done:
	done = handle_events(pygame.event.get())
	if done: break

	hand.update(pygame.mouse.get_pos())

	for stack in tableau:
		if len(stack.revealed_cards) == 0 and len(stack.hidden_cards) > 0:
			stack.revealed_cards.append(stack.hidden_cards[-1])
			stack.hidden_cards.pop(-1)

	draw()

	clock.tick(60)