import discord
import json
from deck import Deck
from SHGame import SecretHitlerGame
import random

def main():
	with open('./config.json') as f:
	
		config = json.load(f)

	client.run(config['BOT_TOKEN'])

class MyClient(discord.Client):
	async def on_ready(self):
		print('Logged on as {0}!'.format(self.user))

	async def on_message(self, message):
		if message.author.bot:
			return
		if(message.content.startswith("!start")):
			startPlayer = await message.guild.fetch_member(message.author.id)
			#players = startPlayer.voice.channel.members
			players = [startPlayer, startPlayer, startPlayer, startPlayer, startPlayer, startPlayer, startPlayer, startPlayer, startPlayer]
			#try:
			game = SecretHitlerGame(players, message.channel, client)
			await game.chooseChancellor(game.players[1])
			#except Exception:
			#	await message.channel.send("Player count must be greater than 4 and less than 11")
			#else:
			#	await message.channel.send("Starting game with " + str(list(x.display_name for x in players)))
				#await game.legislativeSession(game.players[0], game.players[0])
			

intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
if __name__ == "__main__":
	main()