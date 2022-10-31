import discord
import yaml
from discord.ext import commands
from apiRequest import riot_api_request
import warnings

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
client = discord.Client()
warnings.filterwarnings(action='ignore')
bot = commands.Bot(command_prefix='!')

@client.event
async def ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Browsing the Rift"))
    print("New log in as {0.user}".format(client))

@bot.command()
async def test(ctx,arg):
    await ctx.send(arg)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!help"):
        embed = discord.Embed(title="Help", description="!history {summoner_name}", color=0x5CE5D1)
        embed.set_footer(text='DiscodLOL by yoonj#0492',icon_url='https://upload.wikimedia.org/wikipedia/commons/2/2a/LoL_icon.svg')

        await message.channel.send("help!",embed=embed)


    if message.content.startswith("!history"):
        try:
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="Please include your Summoner name!", description="",color=0x5CE5D1)
                embed.add_field(name="Summoner name not entered", value="To use command !history: !history (summoner name)"
                                , inline=False)
                embed.set_footer(text='DiscodLOL by yoonj#0492',icon_url='https://upload.wikimedia.org/wikipedia/commons/2/2a/LoL_icon.svg')
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
                                     icon_url='https://upload.wikimedia.org/wikipedia/commons/2/2a/LoL_icon.svg')
                    await message.channel.send("Summoner does not exist", embed=embed)
                else:
                    record = get_record_box["Record"]
                    keys = record.keys()
                    mastery = get_record_box["ChampionMastery"]
                    if len(record) == 2:
                        solo_wr = int((record['Personal/Duo Rank']['win']
                                       / (record['Personal/Duo Rank']['win'] + record['Personal/Duo Rank']['loss'])) * 100)
                        flex_wr = int((record['Flex 5:5 Rank']['win']
                                       / (record['Flex 5:5 Rank']['win'] + record['Flex 5:5 Rank']['loss'])) * 100)
                        solo_tier = record['Personal/Duo Rank']['tier']
                        flex_tier = record['Flex 5:5 Rank']['tier']
                        tc = compare_tier(solo_tier,flex_tier)
                        thumbnail = "lorem ipsum"
                        if tc == 0 or tc == 2:
                            thumbnail = solo_tier
                        else:
                            thumbnail = flex_tier
                embed = discord.Embed(title="Summoner Match History", description="", color=0x5CE5D1)
                embed.add_field(name=f"Ranked Solo : {record['Personal/Duo Rank']['tier']} {record['Personal/Duo Rank']['Rank']}",
                                value=f"{record['Personal/Duo Rank']['leaguepoint']} LP / {record['Personal/Duo Rank']['win']}W {record['Personal/Duo Rank']['loss']}L"
                                      f" / Win Ratio {solo_wr}%", inline=False)
                embed.add_field(name=f"Ranked Flex 5:5 : {record['Flex 5:5 Rank']['tier']} {record['Flex 5:5 Rank']['Rank']}",
                                value=f"{record['Flex 5:5 Rank']['leaguepoint']} LP / {record['Flex 5:5 Rank']['win']}W {record['Flex 5:5 Rank']['loss']}L"
                                        f" / Win Ratio {flex_wr}%", inline=False)
                embed.add_field(name=f"Most Used Champion : {mastery['championname']}",value=f"Mastery Level : {mastery['championlevel']}.LV / Champion Point : {mastery['championpoint']}pts")
                embed.set_thumbnail(url=)









