#!/usr/bin/python3

# TO DO
# - Fan held cards
# - Add ability to win
# - Maybe if I have time try and make every game solvable with some Weird Maths (tm)

import pygame, random

from card import Card
from stack import Stack
from hand import Hand
from button import Button

# Initialise window
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption('Solitaire')

# Variable Definition
card_back = pygame.image.load('images/cards/cardBack.png')	# Card back sprite. Used for hidden cards and the stock
card_back = pygame.transform.scale(card_back, (70, 95))
click_timer = 0
dt = 0
double_click = False

congrats = pygame.image.load('images/congrats.png')
title_rect = pygame.rect.Rect(0,0,300,60)
title_rect.center = (400, 250)

victory = False

# UI buttons
buttons = [
	Button((15,15), 'reset()', 'new_game'), # Reset button
	Button((55,15), 'undo()', 'undo'), # Undo button
	]

hand = Hand(pygame.mouse.get_pos())

history = [] 		# An array of tuples that contain the current tableau, foundations and stock. Used for undo/redo functionality

def handle_events(events):
	""" Handle pygame events. Returns True if the window has been closed"""

	global click_timer, double_click

	mouse = pygame.mouse.get_pos()

	for event in events:
		if event.type == pygame.QUIT:
			pygame.quit()
			return True

		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				if click_timer == 0:
					click_timer = 0.001
				elif click_timer < 0.5:
					double_click = True
					click_timer = 0

				for button in buttons:
					# Button functionality.
					if button.collidepoint(pygame.mouse.get_pos()):
						button.clicked = True

				if not victory:
					if mouse[1] < 175:							# If the mouse is at the top of the screen, check for stock
						if stock.collidepoint(mouse):
							history.insert(0, update_history())
							cycle_stock()
						elif stock.move(100,0).collidepoint(mouse) and len(stock.revealed_cards) > 0:
							if double_click:
								card = stock.revealed_cards[-1]
								for foundation in foundations:
									if check_cards(card, foundation):
										foundation.revealed_cards.append(card)
										card.rect = foundation
										stock.revealed_cards.remove(card)

										return False
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

									if card == stack.revealed_cards[-1] and double_click:
										for foundation in foundations:
											if check_cards(card, foundation):
												foundation.revealed_cards.append(card)
												card.rect = foundation
												stack.revealed_cards.remove(card)

												return False

									hand.cards = stack.revealed_cards[stack.revealed_cards.index(card):]

				double_click = False

		elif event.type == pygame.MOUSEBUTTONUP:
			if len(hand.cards) > 0:
				hand.cards = place_cards()
			
			for button in buttons:
				if button.clicked and button.collidepoint(mouse):
					try:
						exec(button.function)
					except IndexError:
						return True
				button.clicked = False

def place_cards():
	""" Handles the movement of cards after all checks have completed """

	global history

	mouse = pygame.mouse.get_pos()

	history.insert(0, update_history())
	
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
		stack = Stack(x, 250, 400)

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
		foundations.append(Stack(x, 80, 90))
		x += 100

	# Remaining cards get added to stock.
	stock = Stack(65, 80, 90)
	for card in deck:
		stock.hidden_cards.append(Card(card[0], card[1], stock.center))

	return tableau, foundations, stock

deck = create_deck()
tableau, foundations, stock = create_board(deck)

def reset():
	""" Resets the game """

	global deck, tableau, foundations, stock, history, victory, buttons

	deck = create_deck()
	tableau, foundations, stock = create_board(deck)
	history = []
	victory = False

	buttons = [
		Button((15,15), 'reset()', 'new_game'), # Reset button
		Button((55,15), 'undo()', 'undo'), # Undo button
	]

def undo():	
	""" Reverts the gamestate back to the frontmost entry in the history, and then removes the frontmost entry """
	global tableau, foundations, stock

	try:
		# Set the contents of every stack in the tableau to the contents of the previous equavalent 
		old_tableau = history[0][0]
		for stack in tableau:
			stack_num = tableau.index(stack)
			stack.hidden_cards = old_tableau[stack_num].hidden_cards
			stack.revealed_cards = old_tableau[stack_num].revealed_cards
		
		old_foundations = history[0][1]
		for stack in foundations:
			stack_num = foundations.index(stack)
			stack.revealed_cards = old_foundations[stack_num].revealed_cards
		
		stock.hidden_cards = history[0][2][0]
		stock.revealed_cards = history[0][2][1]

		history.pop(0)
	except IndexError:
		# This error occurs if the history is empty and there is nothing to undo. As such, we simply ignore it.
		pass

def update_history():
	""" Adds a new entry to the history containing the current gamestate """

	current_tableau = []		# List of all the stacks currently in the tableau
	current_foundations = []	# list of the all the current foundations

	# We have to create new stacks like this because if we just add the current stacks, they're the same object in two lists and so the stacks in the history are the same as the current
	# As such, we create completely new objects to add to the history. We do this for the tableau, the foundation and the stock.
	for stack in tableau:
		new_stack = Stack(stack.x, stack.y, stack.height)
		
		for card in stack.revealed_cards:
			new_card = Card(card.suit, card.value, card.rect.center)
			new_stack.revealed_cards.append(new_card)

		for card in stack.hidden_cards:
			new_card = Card(card.suit, card.value, card.rect.center)
			new_stack.hidden_cards.append(new_card)

		current_tableau.append(new_stack)

	for foundation in foundations:
		new_foundation = Stack(foundation.x, foundation.y, foundation.height)

		for card in foundation.revealed_cards:
			new_card = Card(card.suit, card.value, card.rect.center)
			new_foundation.revealed_cards.append(new_card)
		
		current_foundations.append(new_foundation)

	current_stock = [[], []]				# First list is the hidden cards, second is the revealed cards
	for card in stock.hidden_cards:
		new_card = Card(card.suit, card.value, card.rect.center)
		current_stock[0].append(new_card)
	for card in stock.revealed_cards:
		new_card = Card(card.suit, card.value, card.rect.center)
		current_stock[1].append(new_card)

	return (current_tableau, current_foundations, current_stock)

def draw():
	""" Draws every object to the screen """

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

	for button in buttons:
		button.draw(screen)

	if victory:
		screen.blit(congrats, title_rect)

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

	# Change the colour of the currently moused-over button so it looks clickable
	hovering = False
	for button in buttons:
		if button.collidepoint(pygame.mouse.get_pos()) and not button.clicked:
			button.hover = True
			hovering = True
		else:
			button.hover = False

	# Change cursor if over a clickable button, and change it back if not.
	if hovering:
		pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
	else:
		pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

	draw()

	# Delay for double clicking
	if click_timer > 0:
		click_timer += dt
		if click_timer >= 0.5:
			click_timer = 0

	# Victory checking
	if not victory:
		victory = True
		for stack in tableau:
			if len(stack.hidden_cards) != 0 or len(stack.revealed_cards) != 0:
				victory = False
		if len(stack.revealed_cards) != 0 or len(stack.hidden_cards) != 0:
			victory = False
		
		if victory:
			buttons = [
				Button((300, 280), 'reset()', 'new_game_l'),
				Button((400, 280), 'raise IndexError', 'quit')
			]
	

	dt = clock.tick(60) / 1000
