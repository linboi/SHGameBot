from random import shuffle
from deck import Deck
from collections import namedtuple

class SecretHitlerGame:
	
	################# GAME INITIALISATION #################
	# Here is where the player and deck setup happens.

	def __init__(self, players, publicChannel, client):
		if len(players) < 5 or len(players) > 10:
			print('Game cannot be started with more than 10 or fewer than 5 players')
			#raise Exception("Wrong player count")
		
		self.players = self.setTeams(players) # One player is randomly assigned hitler, the rest are randomly assigned fascist and liberal roles
		shuffle(self.players) # Players are shuffled again so that their order in the table doesn't give away their team
		self.publicChannel = publicChannel
		self.client = client
		self.deck = Deck(6, 11)
		# Special power name/emoji relation
		self.powers = {
			"NONE":"⬜",
			"INSPECT":"🔎",
			"PICKPRESIDENT":"🤵",
			"PEEKCARDS":"👀",
			"KILL":"🔪",
			"FWIN":"☠",
			"LWIN":"🕊"
		}
		# Set tracks
		self.libTrack = ["NONE", "NONE", "NONE", "NONE", "NONE", "LWIN"]
		if (len(players) < 7):	# The fascist track changes depending on the number of players in the game
			self.fascTrack = ["NONE", "NONE", "PEEKCARDS", "KILL", "KILL", "FWIN"]
		elif (len(players) < 9):
			self.fascTrack = ["NONE", "INSPECT", "PICKPRESIDENT", "KILL", "KILL", "FWIN"]
		else:
			self.fascTrack = ["INSPECT", "INSPECT", "PICKPRESIDENT", "KILL", "KILL", "FWIN"]
		# set these to start game values
		self.libTrackProgress = 0
		self.fascTrackProgress = 0
		self.failedElections = 0

	def setTeams(self, players):
		PlayerData = namedtuple('PlayerData', ['discordUser', 'team', 'isHitler', 'termLimited'])
		shuffle(players) # Give the teams to random players
		resultantPlayers = []
		resultantPlayers.append(PlayerData(players[0], 'F', True, False))	# Make one player hitler
		for i in range(((len(players) - 5)//2 + 1)): # Weird formula for fascist count
			resultantPlayers.append(PlayerData(players[i], 'F', False, False))
		for i in range(((len(players) - 5)//2 + 3 + (len(players)-5)%2)): # Weird formula for liberal count
			resultantPlayers.append(PlayerData(players[i], 'L', False, False))
		return resultantPlayers

	################# GAME LOOP #################
	# Here is the standard loop that the game
	# goes through each round.
	
	async def gameLoop(self):
		chanc = await chooseChancellor(pres)

	#async def chooseChancellor(self, pres):


	async def legislativeSession(self, pres, chanc):
		cards = [self.deck.deal(), self.deck.deal(), self.deck.deal()]
		presMessage = await pres.discordUser.send("The cards you have been dealt are: " + str(cards) + "\n Choose a card to *discard*.")
		if cards.__contains__('L'):
			await presMessage.add_reaction('🇱')
		if cards.__contains__('F'):
			await presMessage.add_reaction('🇫')

		def check(reaction, user):
			return user == pres and reaction.message.id == presMessage.id and ((reaction.emoji == '🇱' and cards.__contains__('F')) or (reaction.emoji == '🇫' and cards.__contains__('F')))

		reaction, user = await self.client.wait_for('reaction_add', check=check)
		
		if reaction.emoji == '🇱':
			cards.remove('L')
		elif reaction.emoji == '🇫':
			cards.remove('F')

		chancMessage = await chanc.discordUser.send("The cards you have been given by the president " + pres.display_name + " are: " + str(cards) + "\n Choose a card to *discard*.")
		if cards.__contains__('L'):
			await chancMessage.add_reaction('🇱')
		if cards.__contains__('F'):
			await chancMessage.add_reaction('🇫')

		def check(reaction, user):
			return user == chanc and reaction.message.id == chancMessage.id and ((reaction.emoji == '🇱' and cards.__contains__('F')) or (reaction.emoji == '🇫' and cards.__contains__('F')))

		reaction, user = await self.client.wait_for('reaction_add', check=check)
		
		if reaction.emoji == '🇱':
			cards.remove('L')
		elif reaction.emoji == '🇫':
			cards.remove('F')

		if(self.deck.cardsLeft() < 3):
			this.deck.shuffle()

	# functions for showing the current game state to players
	def showTrack(self):
		msg = ''
		msg += "---------Fascist Track---------\n"
		for i in range(self.fascTrackProgress):
			msg += '🇫'+"\t"
		for i in range(self.fascTrackProgress, len(self.fascTrack)):
			msg += self.powers[self.fascTrack[i]] + "\t"
		msg += "\n===============================\n---------Liberal Track---------\n"
		for i in range(self.libTrackProgress):
			msg += '🇱'+"\t"
		for i in range(self.libTrackProgress, len(self.libTrack)):
			msg += self.powers[self.libTrack[i]] + "\t"
		msg += "\n===============================\nFailed Elections:"
		for i in range(3):
			if self.failedElections > i:
				msg += "❌"
			else:
				msg += "⭕"
		msg += ''
		return msg

	def showTable(self):
		msg = '```'
		for p in self.players:
			msg += p.discordUser.display_name
		msg += '```'
		return msg