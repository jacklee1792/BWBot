import os
import datetime
import dotenv
import discord
import sqlite3

from discord.ext import commands
from bwbot.util.user import User
from bwbot.util import utils

dotenv.load_dotenv()
TOKEN = os.environ.get('discord-bot-token')
bot = commands.Bot(command_prefix='pls ')


@bot.command(name='bw')
async def bw(ctx, *args):
	rows = []
	header = 'STARS IGN FKDR WR WS'.split()
	rows.append(header)
	for arg in args:
		user = User(arg)
		row = [
			f'[{"?" if user.bw_stars is None else user.bw_stars}✫]',
			user.ign,
			utils.ratio_str(user.bw_fkills, user.bw_fdeaths),
			utils.prop_str(user.bw_wins, user.bw_losses),
			user.bw_winstreak
		]
		rows.append(row)
	await ctx.send(utils.tabulate(rows))


@bot.command(name='bg')
async def bg(ctx, *args):
	rows = []
	header = 'TITLE,IGN,SOLO WR,2s WR,4s WR,WS'.split(',')
	rows.append(header)
	for arg in args:
		user = User(arg)
		row = [
			f'[{"?" if user.bg_title is None else user.bg_title}]',
			user.ign,
			utils.ratio_str(user.bg_wins1, user.bg_losses1),
			utils.ratio_str(user.bg_wins2, user.bg_losses2),
			utils.ratio_str(user.bg_wins4, user.bg_losses4),
			user.bg_winstreak
		]
		rows.append(row)
	await ctx.send(utils.tabulate(rows))


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
	delta_seconds = (current_time - last_time).total_seconds()
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
	await ctx.send(ctx.message.author.mention)
	return await ctx.send(embed=embed)


@bot.command(name='kill')
@commands.has_permissions(administrator=True)
async def kill(ctx):
	await ctx.send("Goodbye!")
	return await ctx.bot.logout()


if __name__ == '__main__':
	bot.run(TOKEN)
