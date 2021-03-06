from random import shuffle
class Deck:
	def __init__(self, liberalCards: int, fascistCards: int):
		self.deck = []
		for i in range(liberalCards + fascistCards):
			if( i < liberalCards):
				self.deck.append('L')
			else:
				self.deck.append('F')
		shuffle(self.deck)
		self.place = 0

	def deal(self):
		card = self.deck[self.place]
		self.place += 1
		return card

	def peek(self, count):
		return self.deck[self.place:self.place+count]
	
	def shuffle(self):
		shuffle(self.deck)
		self.place = 0

	def cardsLeft(self):
		return len(self.deck) - self.place

	# For use only on cards that were dealt and then chosen
	def remove(self, cardType):
		self.deck.remove(cardType)	# The card will always exist and be found before deck[place]
		self.place -= 1 	# This function will only run after cards have been dealt, place cannot be 0
		return cardType

	def pop(self):
		if self.place == len(self.deck):
			self.shuffle()
		return self.deck.pop(self.place)
