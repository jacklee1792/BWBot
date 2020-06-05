import os
import requests
import json
import datetime
import dotenv
import discord

from discord.ext import commands

dotenv.load_dotenv()

# retrieve api keys and discord token
API_KEY = os.environ.get("hypixel-api-key")
TOKEN = os.environ.get("discord-bot-token")
# modify this to change bot prefix
bot = commands.Bot(command_prefix='!')


item_cnt = 5
last_time = datetime.datetime.now()
pull_cnt = 0
menu_items = ['STARS', 'IGN', 'FKDR', 'WR', 'WS']
longest = []


# function used to get the json files according to info_type
def get_json(API_KEY, uuid_string, info_type):
	api_json = None
	try:
		api_response = requests.get(f'https://api.hypixel.net/{info_type}?key={API_KEY}&uuid={uuid_string}')
		api_json = json.loads(api_response.text)
	except:
		pass
	return api_json


# Get the uuid of username
def get_uuid(username):

	uuid_response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{username}')
	uuid_string = None
	username_string = None
	try:
		uuid_json = json.loads(uuid_response.text)
		uuid_string = uuid_json['id']
		username_string = uuid_json['name']
	except:
		username_string = username
	return (uuid_string, username_string)


# get statistics function
def get_stats(username):
	global longest_star, longest_username, longest_fkdr, longest_winrate, longest_winstreak
	username_is_valid = None

	# Get the uuid of username
	uuid_string, username_string = get_uuid(username)
	# Get the stats
	api_json = get_json(API_KEY, uuid_string, "player")

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
	global longest, last_time, pull_cnt
	# Impose 6 argument limit
	longest = [7, 6, 6, 4, 4]
	if len(username_args) > 6:
		await ctx.send(ctx.message.author.mention)
		return await ctx.send('Too many arguments! Please input between 1 and 6 usernames')

	elif len(username_args) == 0:
		await ctx.send(ctx.message.author.mention)
		return await ctx.send('Too few arguments! Please input between 1 and 6 usernames')

	current_time = datetime.datetime.now()
	# print log
	with open("log.txt", "a") as log:
		log.write(f"[{current_time}] New stats query about {len(username_args)} players from {ctx.author}\n")

	# Check if sufficient time has passed since last query
	delta_seconds = (current_time - last_time).total_seconds();
	# At most 6 calls every 3.5 seconds, at most ~100 queries per minute
	# print(current_time, last_time)
	if delta_seconds < 3.5 and len(username_args) + pull_cnt >= 6:
		await ctx.send(ctx.message.author.mention)
		return await ctx.send(f'Please wait {3.5 - delta_seconds:.2f}s before sending another query!')

	# if the cooldown has passed, reset the cnt and time
	elif delta_seconds >= 3.5:
		last_time = current_time
		pull_cnt = 0
	pull_cnt += len(username_args)
	# Output stats table
	output = '```py\n#  '
	# Fetch results
	results = []

	for username in username_args:
		results.append(get_stats(username))

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


# get status of the player
@bot.command(name="status")
async def status(ctx, *username_arg):
	global last_time, pull_cnt
	if(len(username_arg) > 1):
		await ctx.send(ctx.message.author.mention)
		return await ctx.send("Please input 1 username only for each query!")
	elif len(username_arg) == 0:
		await ctx.send(ctx.message.author.mention)
		return await ctx.send("Please input 1 username for each query!")
	# print(current_time, last_time)
	current_time = datetime.datetime.now()
	delta_seconds = (current_time - last_time).total_seconds();
	# print log
	with open("log.txt", "a") as log:
		log.write(f"[{current_time}] New status query about \"{username_arg[0]}\" from {ctx.author}\n")
	# print(f"{last_time} - {current_time} : {delta_seconds}")
	# print(f"pull cnt: {pull_cnt + 1}")
	# At most 6 calls every 3.5 seconds, at most ~100 queries per minute
	if delta_seconds < 3.5 and len(username_arg) + pull_cnt >= 6:
		await ctx.send(ctx.message.author.mention)
		return await ctx.send(f'Please wait {3.5 - delta_seconds:.2f}s before sending another query!')
	# if the cooldown has passed, reset the cnt and time
	elif delta_seconds >= 3.5:
		last_time = current_time
		pull_cnt = 0

	pull_cnt += len(username_arg)
	# get uuid and username
	uuid_string, username_string = get_uuid(username_arg[0])

	api_json = get_json(API_KEY, uuid_string, "status")
	if not bool(api_json["success"]):
		await ctx.send(ctx.message.author.mention)
		return await ctx.send(embed=discord.Embed(description = f'The player "{username_string}" doesn\'t exist or has not logged on to Hypixel before!'))
	# first retrieve the player model
	image = f"https://mc-heads.net/head/{uuid_string}/128"
	#default embed
	embed = discord.Embed(
			title = "Status",
			description = "Online",
			colour = discord.Colour.blue()
	)
	embed.set_author(
		name = username_string,
		icon_url = image
	)
	embed.set_thumbnail(url = image)
	# if player is online
	if bool(api_json["session"]["online"]):
		# displays gamemode, status and mode
		embed.add_field(name="gameType",value=api_json["session"]["gameType"])
		embed.add_field(name="mode", value=api_json["session"]["mode"])

	else:
		# displays status as offline
		embed.description = "Offline"
	# return the embed
	return await ctx.send(embed=embed)


# only admin accessible kill command
@bot.command(name='kill')
@commands.has_permissions(administrator=True)
async def kill(ctx):
	with open("log.txt", "a") as log:
		log.write(f"[{datetime.datetime.now()}] Shutting Down command from {ctx.author}\n")
	await ctx.send("shutting down...")
	return await ctx.bot.logout()


# main function
def main():
	with open("log.txt", "w") as log:
		log.write(f"[{datetime.datetime.now()}] Bot Started! Waiting for Query...\n")
	bot.run(TOKEN)

if __name__ == '__main__':
	main()