import discord
from discord.ext import commands
from utils import general_utils, database_utils

def setup(Bot):

    regionsdict = { #depreciated
        'us_east':'us',
        'us_west':'us',
        'us_south':'us',
        'us_central':'us',
        'sydney':'au',
        'singapore':'sg',
        'russia':'ru',
        'south_africa':'za',
        'japan':'jp',
        'india':'in',
        'hong_kong':'hk',
        'europe':'eu',
        'brazil':'br'
    }

    Bot.command_info.update({"serverinfo":{
        "aliases":["serverinfo", "guildinfo", "ginfo"],
        "syntax":"",
        "usage":"This will show a bunch of info about the server it has been executed in.",
        "category":"utility"
    }})
    @commands.guild_only()
    @commands.command(name="serverinfo", aliases=["guildinfo", "ginfo"])
    async def _serverinfo(ctx):
        
        #base embed
        guild_info_embed = discord.Embed(title=f"Info about the guild \"{ctx.guild.name}\"")
        
        #embed icon
        guild_info_embed.set_thumbnail(url=ctx.guild.icon.url)

        #server owner
        guild_info_embed.add_field(name="Owner:", value=ctx.guild.owner.mention, inline=True)

        #features
        guild_info_embed.add_field(name='Features:', value=(', '.join(ctx.guild.features) if ', '.join(ctx.guild.features) != '' else 'None :('), inline=True)

        #region (depreciated)
        #region = f":flag_{regionsdict[ctx.guild.region]}: {ctx.guild.region.capitalize()}"
        #guild_info_embed.add_field(name='Region:', value=region, inline=True)
        #print("test")

        #statuses
        guild_info_embed.add_field(name="Member Statuses:", value=':green_circle: '+str([str(m.status) == "online" for m in ctx.guild.members].count(True))+"\n:yellow_circle: "+str([str(m.status) == "idle" for m in ctx.guild.members].count(True))+"\n:red_circle: "+str([str(m.status) == "dnd" for m in ctx.guild.members].count(True))+"\n:new_moon: "+str([str(m.status) == "offline" for m in ctx.guild.members].count(True)), inline=True)

        #user counts
        guild_info_embed.add_field(name="Member Counts:", value=str(ctx.guild.member_count)+" Total Members\n"+str(len([m for m in ctx.guild.members if not m.bot]))+" People\n"+str(len([m for m in ctx.guild.members if m.bot]))+" Bots", inline=True)

        #channels
        guild_info_embed.add_field(name="Channels:", value=str(len(ctx.guild.voice_channels)+len(ctx.guild.text_channels))+" Total Channels\n"+str(len(ctx.guild.text_channels))+" Text Channels\n"+str(len(ctx.guild.voice_channels))+" Voice Channels", inline=True)

        #static emojis
        
        #get static emojis string
        if len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in ctx.guild.emojis if emoji.animated==False])) == 0:
            static_emojis = 'None :('
        elif len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in ctx.guild.emojis if emoji.animated==False])) >= 1000:
            static_emojis = 'Too many to show.'
        elif len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in ctx.guild.emojis if emoji.animated==False])) >= 0 and len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in ctx.guild.emojis if emoji.animated==False])) <= 1000:
            static_emojis = ''.join([str(Bot.get_emoji(emoji.id)) for emoji in ctx.guild.emojis if emoji.animated==False])

        #add field
        guild_info_embed.add_field(name='Static Emojis: *('+str(len([emoji for emoji in ctx.guild.emojis if emoji.animated==False]))+')*', value='\u200b'+static_emojis, inline=True)


        #animated emojis (similar deal to static ones)
        if len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in ctx.guild.emojis if emoji.animated==True])) == 0:
            animated_emojis = 'None :('
        elif len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in ctx.guild.emojis if emoji.animated==True])) >= 1000:
            animated_emojis = 'Too many to show.'
        elif len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in ctx.guild.emojis if emoji.animated==True])) >= 0 and len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in ctx.guild.emojis if emoji.animated==True])) <= 1000:
            animated_emojis = ''.join([str(Bot.get_emoji(emoji.id)) for emoji in ctx.guild.emojis if emoji.animated==True])

        guild_info_embed.add_field(name='Anim-Emojis: *('+str(len([emoji for emoji in ctx.guild.emojis if emoji.animated==True]))+')*', value='\u200b'+animated_emojis, inline=True)
        
        #server creation date
        creation_date = ctx.guild.created_at
        guild_info_embed.add_field(name='Server Creation Date:', value=f"<t:{int(creation_date.timestamp())}:f> (<t:{int(creation_date.timestamp())}:R>)", inline=True)
        
        #role num
        guild_info_embed.add_field(name='Number of roles:', value=str(len(ctx.guild.roles)), inline=True)

        #server id
        guild_info_embed.add_field(name='Server ID:', value=str(ctx.guild.id), inline=True)

        #total boops
        total_boops = 0
        for user in ctx.guild.members:
            if user.bot == False:
                total_boops += database_utils.fetch_boops(user.id)
        guild_info_embed.add_field(name="Total boops:", value=f"{general_utils.num_to_words(total_boops).capitalize() } boop{'s' if total_boops != 1 else ''}")
        
        #net worth
        net_worth = 0
        for user in ctx.guild.members:
            if user.bot == False:
                net_worth += database_utils.fetch_balance(user.id)
        guild_info_embed.add_field(name="Server Net Worth:", value=f"§{net_worth}")
        guild_info_embed = general_utils.format_embed(ctx.author, guild_info_embed)

        await ctx.send(embed=guild_info_embed)

    Bot.add_command(_serverinfo)
