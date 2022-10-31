import warnings
import discord
import logging
import yaml
from discord.ext import commands
from apiRequest import riot_api_request

with open('config.yml') as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)

discord_token = keys['Keys']['discordAPIToken']
Riot_Token = keys['Keys']['riotAPIToken']
api_call = riot_api_request(Riot_Token)

tier_list = {
    'default': 0,
    'IRON': 1,
    'BRONZE': 2,
    'SILVER': 3,
    'GOLD': 4,
    'PLATINUM': 5,
    'DIAMOND': 6,
    'MASTER': 7,
    'GRANDMASTER': 8,
    'CHALLENGER': 9
}


def compare_tier(solo_rank, flex_rank):
    if tier_list[solo_rank] > tier_list[flex_rank]:
        return 0
    elif tier_list[flex_rank] > tier_list[solo_rank]:
        return 1
    else:
        return 2


# -----------------------------------------------------------
intents = discord.Intents.default()
client = discord.Client(intents=intents)
warnings.filterwarnings(action='ignore')
bot = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Browsing the Rift"))
    print("New log in as {0.user}".format(client))


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!help"):
        embed = discord.Embed(title="Help", description="Use these commands to get started", color=0x5CE5D1)
        embed.add_field(name="Search Match History",value="!history {summoner name}",inline=False)
        embed.add_field(name="Search Most Played Champioons",value="!mostplayed {summoner name", inline=False)
        embed.set_footer(text='DiscodLOL by yoonj#0492',
                         icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')

        await message.channel.send(embed=embed)

    if message.content.startswith("!history"):
        try:
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="Please include your Summoner name!", description="", color=0x5CE5D1)
                embed.add_field(name="Summoner name not entered",
                                value="To use command !history: !history (summoner name)"
                                , inline=False)
                embed.set_footer(text='DiscodLOL by yoonj#0492',
                                 icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')
                await message.channel.send("Please include your Summoner name!", embed=embed)
            else:
                sum_name = ' '.join(message.content.split(' ')[1:])
                get_record_box = api_call.get_personal_game_record(sum_name)
                if not get_record_box:
                    embed = discord.Embed(title="Summoner does not exist", description="", color=0x5CE5D1)
                    embed.add_field(name="Summoner does not exits",
                                    value="Please check your summoner name."
                                    , inline=False)
                    embed.set_footer(text='DiscodLOL by yoonj#0492',
                                     icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')
                    await message.channel.send("Summoner does not exist", embed=embed)
                else:
                    record = get_record_box["Record"]
                    keys = record.keys()
                    mastery = get_record_box["ChampionMastery"]
                    if len(record) == 2:
                        solo_wr = int((record['Personal/Duo Rank']['win']
                                       / (record['Personal/Duo Rank']['win'] + record['Personal/Duo Rank'][
                                    'loss'])) * 100)
                        flex_wr = int((record['Flex 5:5 Rank']['win']
                                       / (record['Flex 5:5 Rank']['win'] + record['Flex 5:5 Rank']['loss'])) * 100)
                        solo_tier = record['Personal/Duo Rank']['tier']
                        flex_tier = record['Flex 5:5 Rank']['tier']
                        tc = compare_tier(solo_tier, flex_tier)
                        thumbnail = "lorem ipsum"
                        if tc == 0 or tc == 2:
                            thumbnail = solo_tier
                        else:
                            thumbnail = flex_tier
                        embed = discord.Embed(title="Summoner Match History", description="", color=0x5CE5D1)
                        embed.add_field(name="Account", value=f"{sum_name}", inline=False)
                        embed.add_field(
                            name=f"Ranked Solo : {record['Personal/Duo Rank']['tier']} {record['Personal/Duo Rank']['Rank']}",
                            value=f"{record['Personal/Duo Rank']['leaguepoint']} LP / {record['Personal/Duo Rank']['win']}W {record['Personal/Duo Rank']['loss']}L"
                                  f" / Win Ratio {solo_wr}%", inline=False)
                        embed.add_field(
                            name=f"Ranked Flex 5:5 : {record['Flex 5:5 Rank']['tier']} {record['Flex 5:5 Rank']['Rank']}",
                            value=f"{record['Flex 5:5 Rank']['leaguepoint']} LP / {record['Flex 5:5 Rank']['win']}W {record['Flex 5:5 Rank']['loss']}L"
                                  f" / Win Ratio {flex_wr}%", inline=False)
                        embed.add_field(name=f"Most Used Champion : {mastery['championname']}",
                                        value=f"Mastery Level : {mastery['championlevel']}. / Mastery Point : {mastery['championpoint']}pts")
                        embed.set_thumbnail(url=f"https://github.com/yoonjaejasonlee/DiscordLOL/blob/main/ranked-emblems/Emblem_{thumbnail}.png?raw=true")
                        embed.set_footer(text='DiscodLOL by yoonj#0492',
                                         icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')
                        await message.channel.send(embed=embed)
                    elif len(record) == 0:
                        embed = discord.Embed(title="Summoner Match History", description="", color=0x5CE5D1)
                        embed.add_field(name="Account", value=f"{sum_name}", inline=False)
                        embed.add_field(name="Ranked Solo", value="Unranked", inline=False)
                        embed.add_field(name="Ranked Flex 5:5", value="Unranked", inline=False)
                        embed.set_footer(text='DiscodLOL by yoonj#0492',
                                         icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')
                        await message.channel.send(embed=embed)

                    elif len(record) == 1 and "Personal/Duo Rank" not in keys:
                        flex_wr = int((record['Flex 5:5 Rank']['win'] / (
                                    record['Flex 5:5 Rank']['win'] + record['Flex 5:5 Rank']['loss'])) * 100)
                        embed = discord.Embed(title="Summoner Match History", description="", color=0x5CE5D1)
                        embed.add_field(name="Account", value=f"{sum_name}", inline=False)
                        embed.add_field(name="Ranked Solo :", value="Unranked", inline=False)
                        embed.add_field(
                            name=f"Ranked Flex 5:5 : {record['Flex 5:5 Rank']['tier']} {record['Flex 5:5 Rank']['Rank']}",
                            value=f"{record['Flex 5:5 Rank']['leaguepoint']} LP / {record['Flex 5:5 Rank']['win']}W {record['Flex 5:5 Rank']['loss']}L"
                                  f" / Win Ratio {flex_wr}%", inline=False)
                        embed.add_field(name=f"Most Used Champion : {mastery['championname']}",
                                        value=f"Mastery Level : {mastery['championlevel']}. / Mastery Point : {mastery['championpoint']}pts")
                        embed.set_thumbnail(url=f"https://github.com/yoonjaejasonlee/DiscordLOL/blob/main/ranked-emblems/Emblem_{record['Flex 5:5 Rank']['tier']}.png?raw=true")
                        embed.set_footer(text='DiscodLOL by yoonj#0492',
                                         icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')
                        await message.channel.send(embed=embed)

                    elif len(record) == 1 and "Flex 5:5 Rank" not in keys:
                        solo_wr = int((record['Personal/Duo Rank']['win']
                                       / (record['Personal/Duo Rank']['win'] + record['Personal/Duo Rank'][
                                    'loss'])) * 100)
                        embed = discord.Embed(title="Summoner Match History", description="", color=0x5CE5D1)
                        embed.add_field(name="Account", value=f"{sum_name}", inline=False)
                        embed.add_field(
                            name=f"Ranked Solo : {record['Personal/Duo Rank']['tier']} {record['Personal/Duo Rank']['rank']}",
                            value=f"{record['Personal/Duo Rank']['leaguepoint']} LP / {record['Personal/Duo Rank']['win']}W {record['Personal/Duo Rank']['loss']}L"
                                  f" / Win Ratio {solo_wr}%", inline=False)
                        embed.add_field(name="Ranked Flex 5:5", value="Unranked", inline=False)
                        embed.add_field(name=f"Most Used Champion : {mastery['championname']}",
                                        value=f"Mastery Level : {mastery['championlevel']} / Mastery Point : {mastery['championpoint']}pts")
                        embed.set_thumbnail(url=f"https://github.com/yoonjaejasonlee/DiscordLOL/blob/main/ranked-emblems/Emblem_{record['Personal/Duo Rank']['tier']}.png?raw=true")
                        embed.set_footer(text='DiscodLOL by yoonj#0492',
                                         icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')
                        await message.channel.send(embed=embed)
        except BaseException as e:
            print(e)
            logging.error(logging.traceback.format_exc())
            embed = discord.Embed(title="Bot Error", description="", color=0x5CE5D1)
            embed.add_field(name="Error Found.", value="please report to yoonj#0492", inline=False)
            embed.set_footer(text='DiscodLOL by yoonj#0492',
                             icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')
            await message.channel.send(embed=embed)

    if message.content.startswith("!mostplayed"):
        try:
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="Please include your Summoner Name!", description="", color=0x5CE5D1)
                embed.add_field(name="Summoner name not entered",
                                value="To use command !mostplayed: !mostplayed (summoner name)"
                                , inline=False)
                embed.set_footer(text='DiscodLOL by yoonj#0492',
                                 icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')
                await message.channel.send(embed=embed)
            else:
                sum_name = ' '.join(message.content.split(' ')[1:])
                get_mastery_box = api_call.get_personal_champ_masteries(sum_name)
                keys = list(get_mastery_box.keys())

                if not get_mastery_box:
                    embed = discord.Embed(title="Summoner does not exist", description="", color=0x5CE5D1)
                    embed.add_field(name="Summoner does not exists",
                                    value="Please check your summoner name."
                                    , inline=False)
                    embed.set_footer(text='DiscodLOL by yoonj#0492',
                                     icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')
                    await message.channel.send("Summoner does not exist", embed=embed)
                else:
                    embed = discord.Embed(title=f"Top 3 Champions Played", description="",
                                          color=0x5CE5D1)
                    embed.add_field(name="Account", value=f"{sum_name}", inline=False)
                    counter = 1
                    thumbnail = 'lorem ipsum'
                    for i in get_mastery_box:
                        key = keys[counter - 1]
                        p = get_mastery_box[key]
                        embed.add_field(name=f"Most{counter} : {key}",
                                        value=f"Mastery Level : {p['championlevel']} / Mastery Point : {p['championpoint']}pts",
                                        inline=False)
                        if counter == 1:
                            thumbnail = p['championImage']
                        else:
                            pass
                        counter += 1
                    embed.set_thumbnail(url=f"https://ddragon.leagueoflegends.com/cdn/12.20.1/img/champion/{thumbnail}")
                    embed.set_footer(text='DiscodLOL by yoonj#0492',
                                     icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')
                    await message.channel.send(embed=embed)
        except BaseException as e:
            print(e)
            logging.error(logging.traceback.format_exc())
            embed = discord.Embed(title="Bot Error", description="", color=0x5CE5D1)
            embed.add_field(name="Error Found.", value="please report to yoonj#0492", inline=False)
            embed.set_footer(text='DiscodLOL by yoonj#0492',
                             icon_url='https://cdn.countryflags.com/thumbs/south-korea/flag-800.png')
            await message.channel.send("Bot Error", embed=embed)


client.run(discord_token)
