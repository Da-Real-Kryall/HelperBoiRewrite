import discord
from discord.ext import commands
from utils import general_utils, database_utils

def setup(Bot):

    Bot.command_info.update({"baltop":{
        "aliases":["baltop"],
        "syntax":"[isglobal]",
        "usage":"Shows the leaderboard of the richest players in the server, or optionally in all applicable servers if 'global' is given.",
        "category":"economy"
    }})#make command return only if its in a DM and the guild-wide board is requested
    @commands.guild_only()
    @commands.command(name="baltop")
    async def _baltop(ctx, isglobal=''):
        if isglobal != '':
            await ctx.send("global leaderboard hasnt been implemented yet.. sorey! just leave the 'isglobal' arg blank for now.")
            return
        userlist = []
        for user in ctx.guild.members:
            userlist += [[f"{user.display_name[:24]}{' '*(24-len(user.display_name))}", database_utils.fetch_balance(user.id)]] # *detabase...{user.discriminator}
        
        userlist.sort(key = lambda l: l[1])
        userlist = list(reversed(userlist))

        userlist = userlist[:10]
        
        res_desc = []
        for index, member in enumerate(userlist):
            index += 1
            res_desc += [f"{index}.{' '*(4-len(str(index)))}§{general_utils.si_suffix(member[1]) if member[1] > 1000 else member[1]}{' '*(7-len(str(general_utils.si_suffix(member[1]) if member[1] > 1000 else member[1])))}  {member[0]}"]#{' '*(37-len(member[0]))}

        baltop_embed = general_utils.format_embed(ctx.author, discord.Embed(title="Richest Bois!", description=""+("\n".join(res_desc))+""), "yellow")
        await ctx.send(embed=baltop_embed)

    Bot.add_command(_baltop)