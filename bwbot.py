import os
import requests
import json
import datetime
import dotenv

from discord.ext import commands

dotenv.load_dotenv()

TOKEN = os.environ.get("discord-bot-token")
API_KEY = os.environ.get("hypixel-api-key")

bot = commands.Bot(command_prefix='!')

last_time = datetime.datetime.now()

def stats_string(username):

	username_is_valid = None

	# Get the uuid of username
	uuid_response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{username}')
	uuid_string = None
	username_string = None
	try:
		uuid_json = json.loads(uuid_response.text)
		uuid_string = uuid_json['id']
		username_string = uuid_json['name']
		username_is_valid = True
	except:
		username_is_valid = False
		username_string = username

	# Get the stats
	api_json = None
	try:
		api_response = requests.get(f'https://api.hypixel.net/player?key={API_KEY}&uuid={uuid_string}')
		api_json = json.loads(api_response.text)
	except:
		pass

	# Stars
	stars = ''
	try:
		stars = api_json['player']['achievements']['bedwars_level']
	except:
		stars = '?'
	stars_string = f'[{stars}✫]'

	# Final kill-death ratio
	fkdr_string = ''
	try:
		final_kills = int(api_json['player']['stats']['Bedwars']['final_kills_bedwars'])
		final_deaths = int(api_json['player']['stats']['Bedwars']['final_deaths_bedwars'])
		fkdr = final_kills / final_deaths
		fkdr_string += f'{fkdr:.4f}'
		fkdr_string += f'({final_kills}/{final_deaths})'
	except:
		fkdr_string += '?'
	
	# Winrate
	winrate_string = ''
	try:
		wins = int(api_json['player']['stats']['Bedwars']['wins_bedwars'])
		losses = int(api_json['player']['stats']['Bedwars']['losses_bedwars'])
		winrate = wins / (wins + losses) * 100
		winrate_string += f'{winrate:.2f}%'
	except:
		winrate_string += '?'

	# Winstreak
	winstreak_string = ''
	try:
		winstreak = api_json['player']['stats']['Bedwars']['winstreak']
		winstreak_string += str(winstreak)
	except:
		winstreak_string += '?'

	ret = ''
	ret += stars_string.rjust(7) + ' ‖ '
	ret += username_string.ljust(17) + ' ‖ '
	ret += fkdr_string.ljust(22) + ' ‖ '
	ret += winrate_string.ljust(7) + ' ‖ '
	ret += winstreak_string.ljust(6) + '\n'

	return ret

# Stats command
@bot.command(name='stats')
async def stats(ctx, *username_args):
	# Impose 6 argument limit
	if len(username_args) > 6:
		return await ctx.send('Too many arguments! Maximum number of arguments is 6.')
	# Check if sufficient time has passed since last query
	global last_time
	current_time = datetime.datetime.now()
	delta_seconds = (current_time - last_time).total_seconds();
	# At most 6 calls every 3.5 seconds, at most ~100 queries per minute
	if delta_seconds < 3.5:
		return await ctx.send(f'Please wait {3.5 - delta_seconds:.2f}s before sending another query!')
	last_time = current_time
	# Output stats table
	output = '```c\n'
	output += '        ‖ USERNAME          ‖ FKDR                   ‖ WR      ‖ WS   \n'
	output += '========‖===================‖========================‖=========‖======\n'
	for username in username_args:
		output += stats_string(username)
	output += '```\n'
	return await ctx.send(output)

bot.run(TOKEN)