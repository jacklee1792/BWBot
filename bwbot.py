import os
import random
import datetime
import requests
import json

from discord.ext import commands

TOKEN = 'YOUR-DISCORD-BOT-TOKEN'
API_KEY = 'YOUR-HYPIXEL-API-KEY'

bot = commands.Bot(command_prefix='!')

last_time = datetime.datetime.now()

@bot.command(name='stats')
async def stats(ctx, username):
	global last_time
	current_time = datetime.datetime.now()
	delta_seconds = (current_time - last_time).total_seconds();
	if delta_seconds < 1:
		return await ctx.send(f'Please wait {1 - delta_seconds:.2f}s before sending another command!')
	last_time = current_time

	# get the uuid and name
	uuid_response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{username}')
	uuid_json = None
	try:
		uuid_json = json.loads(uuid_response.text)
	except:
		return await ctx.send('No such user found!')
	uuid_string = uuid_json['id']

	# get the stats
	api_response = requests.get(f'https://api.hypixel.net/player?key={API_KEY}&uuid={uuid_string}')
	api_json = json.loads(api_response.text)

	# parse the stats
	stars = 0
	has_stats = True
	try:
		stars = api_json['player']['achievements']['bedwars_level']
	except:
		has_stats = False
		pass

	name_string = f'[{stars}✫]' + uuid_json['name']
	fkdr_string = 'FKDR:'
	winrate_string = 'WR:'
	winstreak_string = 'WS:'

	if has_stats:
		# fkdr
		final_kills = int(api_json['player']['stats']['Bedwars']['final_kills_bedwars'])
		final_deaths = int(api_json['player']['stats']['Bedwars']['final_deaths_bedwars'])
		if final_deaths > 0:
			fkdr = final_kills / final_deaths
			fkdr_string += f'{fkdr:.4f}'
		else:
			fkdr_string += 'N/A'
		# winrate
		wins = int(api_json['player']['stats']['Bedwars']['wins_bedwars'])
		losses = int(api_json['player']['stats']['Bedwars']['losses_bedwars'])
		if wins + losses > 0:
			winrate = wins / (wins + losses) * 100
			winrate_string += f'{winrate:.2f}%'
		else:
			winrate_string += 'N/A'
		# winstreak
		winstreak = api_json['player']['stats']['Bedwars']['winstreak']
		winstreak_string += str(winstreak)
	else:
		fkdr_string += 'N/A'
		winrate_string += 'N/A'
		winstreak_string += 'N/A'

	# print the thing
	output = '```'
	output += name_string + ' '
	output += fkdr_string + ' '
	output += winrate_string + ' '
	output += winstreak_string
	output += '```'
	return await ctx.send(output)

bot.run(TOKEN)