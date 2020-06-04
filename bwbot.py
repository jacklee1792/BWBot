import os
import requests
import json
import datetime
import dotenv

from discord.ext import commands

dotenv.load_dotenv()

API_KEY = os.environ.get("hypixel-api-key")
TOKEN = os.environ.get("discord-bot-token")
bot = commands.Bot(command_prefix='!')

item_cnt = 5
last_time = datetime.datetime.now()
menu_items = ['STARS', 'IGN', 'FKDR', 'WR', 'WS']
longest = []
def stats_string(username):
	global longest_star, longest_username, longest_fkdr, longest_winrate, longest_winstreak
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
		fkdr_string += f'{fkdr:.2f}'
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
	ret = []
	ret.append(stars_string)
	ret.append(username_string)
	ret.append(fkdr_string)
	ret.append(winrate_string)
	ret.append(winstreak_string)
	for i in range(item_cnt):
		longest[i] = max(longest[i], len(ret[i]) + 2)
	return ret

# Stats command
@bot.command(name='stats')
async def stats(ctx, *username_args):
	# Impose 6 argument limit
	global longest
	longest = [7, 6, 6, 4, 4]
	print(f"New Stats Query from {ctx.author}")
	if len(username_args) > 6:
		await ctx.send(ctx.message.author.mention)
		return await ctx.send('Too many arguments! Please input between 1 and 6 usernames')
	elif len(username_args) == 0:
		await ctx.send(ctx.message.author.mention)
		return await ctx.send('Too few arguments! Please input a number between 1 and 6 usernames')
	# Check if sufficient time has passed since last query
	global last_time
	current_time = datetime.datetime.now()
	delta_seconds = (current_time - last_time).total_seconds();
	# At most 6 calls every 3.5 seconds, at most ~100 queries per minute
	if delta_seconds < 3.5:
		return await ctx.send(f'Please wait {3.5 - delta_seconds:.2f}s before sending another query!')
	last_time = current_time
	# Output stats table
	output = '```py\n#  '
	# Fetch results
	results = []
	for username in username_args:
		results.append(stats_string(username))
	# add menu items to output
	for item_idx in range(item_cnt):
		output += menu_items[item_idx].ljust(longest[item_idx])
	output += '\n'
	# add each query's result to output
	splitter = ''
	for idx in range(len(results)):
		current_string = f'{idx + 1}. '
		for item_idx in range(item_cnt):
			current_string += results[idx][item_idx].ljust(longest[item_idx])
		current_string += '\n'
		splitter = '—' * len(current_string) + '\n'
		output += splitter
		output += current_string
	output += splitter +  '```\n'
	await ctx.send(ctx.message.author.mention)
	return await ctx.send(output)

# only admin accessible kill command
@bot.command(name='kill')
@commands.has_permissions(administrator=True)
async def kill(ctx):
	print(f"Shutting Down command from {ctx.author}")
	await ctx.send("shutting down...")
	await ctx.bot.logout()


def main():
	print("Bot Started! Waiting for Query...")
	bot.run(TOKEN)

if __name__ == '__main__':
	main()