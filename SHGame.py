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
		shuffle(self.players) # Players are shuffled again so that their order in the table doesn't reveal their team
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
		self.presidentTracker = 0
		self.vetoEnabled = False

	def setTeams(self, players):
		PlayerData = namedtuple('PlayerData', ['discordUser', 'team', 'isHitler', 'termLimited'])
		shuffle(players) # Give the teams to random players
		resultantPlayers = []
		resultantPlayers.append(PlayerData(players[0], 'F', True, False))	# Make one player hitler
		for i in range(((len(players) - 5)//2 + 1)): # Weird formula for fascist count
			resultantPlayers.append(PlayerData(players[i], 'F', False, False))
		for i in range(((len(players) - 5)//2 + 3 + (len(players)-5)%2)): # Weird formula for liberal count
			resultantPlayers.append(PlayerData(players[((len(players) - 5)//2 + 1)+i], 'L', False, False))
		return resultantPlayers

	################# GAME LOOP #################
	# Here is the standard loop that the game
	# goes through each round.
	
	async def gameLoop(self, pres=None):
		if pres is None: # president will be given for a special election
			pres = self.players[self.presidentTracker]
			self.presidentTracker = (self.presidentTracker + 1) % len(self.players) #President moves forward one by one and loops
		chanc = await chooseChancellor(pres)
		# voting logic goes here

		# Hitler is enacted chancellor and at least 3 fascist policies are enacted, fascists win
		if(chanc.isHitler and (self.fascTrackProgress > 2)):
			self.gameOver('F')

		chosenCard = await self.legislativeSession(pres, chanc)
		for p in self.players:
			p.termLimited = False
		pres.termLimited = True
		chanc.termLimited = True
		if chosenCard == 'F':
			self.fascTrackProgress += 1
			if(self.fascTrackProgress == 4):
				self.vetoEnabled = True
			elif(self.fascTrackProgress == 5):
				await self.gameOver('F')
			else:
				await self.usePower(pres, self.fascTrack[self.fascTrackProgress])
		elif chosenCard == 'L':
			self.libTrackProgress += 1
			if(self.libTrackProgress == 4):
				await self.gameOver('L')
			else:
				await self.usePower(pres, self.libTrack[self.libTrackProgress])
		else:
			await self.gameLoop()		# This will run if a veto is called, we do the regular game loop again moving the president forward

	async def usePower(self, pres, power):
		nextPres = None		# in all cases except special election, this will regularly move the president forward one spot
		if power == "INSPECT":	# Peek a player's party membership card
			player = await self.choosePlayer(pres, True)
			await pres.send(str(player.discordUser.display_name) + "'s party membership is " + player.team)
		elif power == "PICKPRESIDENT":
			player = await self.choosePlayer(pres, True)
			nextPres = player	# Start a special election with the chosen player
		elif power == "PEEKCARDS":	# Peek the top 3 cards of the deck
			await pres.send(str(self.deck.peek()) + " are the top 3 cards of the deck.")
		elif power == "KILL": 	# The president chooses a player to kill
			player = await self.choosePlayer(pres, True)
			self.players.remove(player)
		# Maybe put 'FWIN' and 'LWIN' here instead of being part of gameLoop()
		await gameLoop(nextPres)

	async def chooseChancellor(self, pres):
		chancChoiceMsg = await self.publicChannel.send(pres.discordUser.display_name + " choose a chancellor by mentioning a player(with @username):\n" + self.showTable(pres))
		def check(message):
			if len(message.mentions) != 1 or message.author != pres.discordUser or message.channel != self.publicChannel:
				return False
			return True
		# Make sure the president has made a valid choice
		valid = False
		while not valid:
			message = await self.client.wait_for('message', check=check)
			isPlayerInGame = False
			for p in self.players:
				print(p)
				if p.discordUser == message.mentions[0]:
					chosenPlayer = p
					isPlayerInGame = True
			if not isPlayerInGame:
				await self.publicChannel.send("Couldn't find player " + message.mentions[0] + " in this game")
			elif chosenPlayer.termLimited:
				await self.publicChannel.send("Cannot choose a term limited player as chancellor")
			elif chosenPlayer == pres:
				await self.publicChannel.send("Cannot choose yourself")
			else:
				valid = True
		return chosenPlayer
					
		# Could use reactions instead of mentions for chancellor choice
		#REACTIONS = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
		#i = 1
		#for p in self.players:
			#await chancChoiceMsg.add_reaction(REACTIONS[i])
			#i += 1

	async def choosePlayer(self, chooser, public):
		# All current powers are public but whatever this could come in useful
		if public:
			channel = self.publicChannel
		else:
			channel = chooser
		choiceMsg = await channel.send(chooser.discordUser.display_name + " choose a player by mentioning them (with @username)")
		def check(message):	#find a message that the chooser mentions one player, and that player is not themselves
			if message.author!=chooser or len(message.mentions)!=1 or message.mentions[0]==chooser:
				return False
			isInGame = False
			for p in self.players:
				if p == message.mentions[0]:
					isInGame = True
			return isInGame
		message = await client.wait_for('message', check=check)
		return message.mentions[0]

	async def legislativeSession(self, pres, chanc):
		cards = [self.deck.deal(), self.deck.deal(), self.deck.deal()]
		presMessage = await pres.discordUser.send("The cards you have been dealt are: " + str(cards) + "\n Choose a card to *discard*.")
		if cards.__contains__('L'):
			await presMessage.add_reaction('🇱')
		if cards.__contains__('F'):
			await presMessage.add_reaction('🇫')

		def check(reaction, user):
			return user == pres.discordUser and reaction.message.id == presMessage.id and ((reaction.emoji == '🇱' and cards.__contains__('F')) or (reaction.emoji == '🇫' and cards.__contains__('F')))

		reaction, user = await self.client.wait_for('reaction_add', check=check)
		
		if reaction.emoji == '🇱':
			cards.remove('L')
		elif reaction.emoji == '🇫':
			cards.remove('F')

		chancMessage = await chanc.discordUser.send("The cards you have been given by the president " + pres.discordUser.display_name + " are: " + str(cards) + "\n Choose a card to *discard*.")
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

		return cards[0]

	# When the game ends, add logic in here to delete the game from outer dictionaries keeping track of running games.
	async def gameOver(self, team):
		self.publicChannel.send("Game over, " + ("fascists" if team=='F' else "liberals") + " win.")

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

	def showTable(self, pres):
		msg = '```'
		i = 1
		for p in self.players:
			msg += str(i) + ". " + p.discordUser.display_name + (" ❌" if p.termLimited else "")
			if(p == pres):
				msg += "\t< President"
			msg += "\n"
			i += 1
		msg += '```'
		return msg