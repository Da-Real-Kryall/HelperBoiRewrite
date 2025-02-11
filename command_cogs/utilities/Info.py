import discord, os, json, requests, math
from random import randint
from discord.ext import commands
from discord import app_commands
from utils import general_utils, database_utils

class Controller(discord.ui.View):
    def __init__(self, scroll_index, max_index):
        super().__init__()

        self.add_item(discord.ui.Button(
            label="<",
            style=discord.ButtonStyle.blurple,
            custom_id="df.previous",
            disabled=True if scroll_index == 0 else False
        ))

        self.add_item(discord.ui.Button(
            label=">",
            style=discord.ButtonStyle.blurple,
            custom_id="df.next",
            disabled=True if scroll_index == max_index else False
        )
    )
    
    async def on_error(self, error, item, interaction):
        await interaction.followup.send_message(embed=general_utils.error_embed(message=f"The following error occurred while your interaction:\n```py\n{error}\n```"), ephemeral=True)

async def _next(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = interaction.message.embeds[0]
    word = embed.title.split(' ')[2][:-1]
    data = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}").json()
    index = int(interaction.message.embeds[0].footer.text.split(' ')[1])-1
    length = int(interaction.message.embeds[0].footer.text.split(' ')[3])
    if index < length-1:
        index += 1
    if 'phonetic' not in data[0]:
        data[0]['phonetic'] = None
    embed.description = f"[{data[0]['meanings'][index]['partOfSpeech']}]     {data[0]['phonetic'] if data[0]['phonetic'] != None else ''}\n {data[0]['meanings'][index]['definitions'][0]['definition']}"
    embed.set_footer(text=f"Meaning {index+1} of {length}")
    await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=Controller(index, length-1))

async def _previous(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = interaction.message.embeds[0]
    word = embed.title.split(' ')[2][:-1]
    data = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}").json()
    index = int(interaction.message.embeds[0].footer.text.split(' ')[1])-1
    length = int(interaction.message.embeds[0].footer.text.split(' ')[3])
    if index > 0:
        index -= 1
    if 'phonetic' not in data[0]:
        data[0]['phonetic'] = None
    embed.description = f"[{data[0]['meanings'][index]['partOfSpeech']}]     {data[0]['phonetic'] if data[0]['phonetic'] != None else ''}\n {data[0]['meanings'][index]['definitions'][0]['definition']}"
    embed.set_footer(text=f"Meaning {index+1} of {length}")
    await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=Controller(index, length-1))

async def setup(Bot):

    badge_dict = {
        "hypesquad_bravery": "<:Bravery:767970207942574080>",
        "hypesquad_brilliance": "<:Brilliance:767970221801472020>",
        "hypesquad_balance":"<:Balance:767970262825435146>",
        "early_verified_bot_developer":"<:Early_Verified_Bot_Developer:767970253288112148>",
        "verified_bot_developer": "<:Early_Verified_Bot_Developer:767970253288112148>",
        "bug_hunter": "<:Bughunter_Level1:767970274095136818>",
        "bug_hunter_level_2": "<:Bughunter_Level2:767970285755957259>",
        "staff": "<:Employee:767970387706773504>",
        "early_supporter": "<:Early_Supporter:767970488851890200>",
        "active_developer": "<:activedeveloper:1042047627199512617>"
    }
    statuses_dict = {
        "dnd":':red_circle:',
        'online':':green_circle:',
        'offline':':new_moon:',
        'idle':':yellow_circle:',
        'streaming':'<:streaming:916986928220475393>'
    }
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

    class Info(commands.GroupCog, name="info"):
        def __init__(self, Bot: commands.Bot):
            self.Bot = Bot
            super().__init__()
        
        
        @commands.Cog.listener()
        async def on_interaction(self, interaction: discord.Interaction):
            if interaction.type == discord.InteractionType.component:
                info = interaction.data["custom_id"].split(".")
                if info[0] in ["df"]: 
                    if info[1] == "previous":
                        await _previous(interaction)
                    elif info[1] == "next":
                        await _next(interaction)

        @commands.Cog.listener()
        async def on_ready(self):
            print("Info cog loaded.")
    
        @app_commands.command(name="whois", description="Will return a bunch of info about the given user.")
        async def _whois(self, interaction: discord.Interaction, user: discord.Member):
            user = interaction.guild.get_member(user.id)
            #base embed
            user_info_embed = general_utils.Embed(author=interaction.user, title=f"About {user.name}: {f'{statuses_dict[user.status[1]]} '}")
            
            if user.bot:
                user_info_embed.title += f"{'<:CHECK:768779393509097484>' if user.public_flags.verified_bot else ''}<:B_:768779404888899605><:O_:768779415852417034><:T_:768779427487416341>"
            if type(user) == discord.Member:
                if user.colour.value != 0:
                    user_info_embed.colour = user.colour.value
                #user_info_embed.title += f" {statuses_dict[user.status[0]]}"

            #embed icon
            user_info_embed.set_thumbnail(url=user.avatar.url)

            user_info = {}
            descroption = ""
            #account creation date
            user_info.update({"Account created at:": f"<t:{int(user.created_at.timestamp())}:f> (<t:{int(user.created_at.timestamp())}:R>)"})

            #member only info (only works for users in the guild the message was sent in)
            if type(user) == discord.Member:
                #status
                if user.status[0] != 'offline' and user.activity != None:
                    #print("test2")
                    if user.activity.type == discord.ActivityType.custom:
                        user_info.update({"Activity:": f"\"{user.activity.emoji.__str__()+' ' if user.activity.emoji != None else ''}{user.activity.name if user.activity.name != None else ''}\""})

                    elif user.activity.type == discord.ActivityType.listening:   
                        #excuse the switch-like hardcoding, its the least messy way i can think of.
                        if hasattr(user.activity, 'title') and hasattr(user.activity, 'artist') and hasattr(user.activity, 'name'):
                            user_info.update({"Activity:": f"Listening to {user.activity.title} By {user.activity.artist} on {user.activity.name}."})

                        elif hasattr(user.activity, 'title') and hasattr(user.activity, 'name'):
                            user_info.update({"Activity:": f"Listening to {user.activity.title} on {user.activity.name}."})

                        elif hasattr(user.activity, 'title') and hasattr(user.activity, 'artist'):
                            user_info.update({"Activity:": f"Listening to {user.activity.title} By {user.activity.artist}."})

                        elif hasattr(user.activity, 'name') and hasattr(user.activity, 'artist'):
                            user_info.update({"Activity:": f"Listening to a song by {user.activity.artist} on {user.activity.name}."})

                        elif hasattr(user.activity, 'name'):
                            user_info.update({"Activity:": f"Listening to {user.activity.name}."})

                        elif hasattr(user.activity, 'title'):
                            user_info.update({"Activity:": f"Listening to {user.activity.title}."})

                        elif hasattr(user.activity, 'artist'):
                            user_info.update({"Activity:": f"Listening to a song by {user.activity.artist}."})

                    elif user.activity.type == discord.ActivityType.playing:
                        user_info.update({"Activity:": f"Playing {user.activity.name}."})

                    elif user.activity.type == discord.ActivityType.watching:
                        user_info.update({"Activity:": f"Watching {user.activity.name}."})

                    elif user.activity.type == discord.ActivityType.streaming:
                        user_info.update({"Activity:": f"Streaming {user.activity.name}."})

                #time joined the server  
                user_info.update({"Server join date:": f"<t:{int(user.joined_at.timestamp())}:f> (<t:{int(user.joined_at.timestamp())}:R>)"})

                #roles
                roles = []
                for role in user.roles:
                    roles += [f"<@&{role.id}>"]
                roles = ', '.join(roles[1:])
                if len(roles) == 0:
                    roles = "None :("
                user_info.update({"Roles:": roles})


            #user info (works in dms etc):

            #awards
            awards = "".join([badge_dict[badge[0]] for badge in user.public_flags.all() if badge[0] in list(badge_dict.keys())])
            user_info.update({"Badges:": awards if awards != "" else "None :("})

            #mention
            user_info.update({"Mention:": str(user.mention)})

            #id
            user_info.update({"Id:": str(user.id)})

            #economy stuff

            #slaps
            if user.bot == False:
                slaps = database_utils.fetch_user_data(user.id, "slaps")
                user_info.update({"Slaps:": general_utils.si_format(slaps)})
                if database_utils.fetch_user_data(user.id, "settings")["economy_invisibility"] == False:
                    with open(os.getcwd()+"/Resources/json/items.json") as file:
                        item_json = json.loads(file.read())

                    #coolness
                    level = math.floor(general_utils.exp_to_level(database_utils.fetch_user_data(user.id, "coolness")))
                    user_info.update({"Level:": f"Coolness level {level} {':sunglasses:' if level >= 0 else ':nerd:'}"})

                    #balance
                    user_info.update({"Balance:": f"§{general_utils.si_format(database_utils.fetch_user_data(user.id, 'balance'))}"})

                    #inventory
                    inv_data = database_utils.fetch_user_data(user.id, "inventory")
                    inventory_string = []
                    for item, quantity in inv_data.items():
                        if quantity != 0:
                            inventory_string += [f"{item_json[item]['emoji']} x{quantity}"]
                    if len(inventory_string) == 0:
                        user_info.update({"Inventory:": "Nothing :("})
                    else:
                        user_info.update({"Inventory:": ", ".join(inventory_string)})
                else: #add fields except <hidden> is their value
                    user_info.update({"Level:": "<hidden>"})
                    user_info.update({"Balance:": f"<hidden>"})
                    user_info.update({"Inventory:": "<hidden>"})


            for key, value in user_info.items():
                user_info_embed.add_field(name=key, value=value)

            await interaction.response.send_message(embed=user_info_embed, ephemeral=general_utils.is_ghost(interaction.user.id))

        @app_commands.command(name="server", description="Get info about the server.")
        async def serverinfo_command(self, interaction: discord.Interaction):
            #base embed
            guild_info_embed = general_utils.Embed(author=interaction.user, title=f"Info about the guild \"{interaction.guild.name}\"")

            #embed icon
            guild_info_embed.set_thumbnail(url=interaction.guild.icon.url)

            #server owner
            guild_info_embed.add_field(name="Owner:", value=interaction.guild.owner.mention, inline=True)

            #features
            guild_info_embed.add_field(name='Features:', value=(', '.join(interaction.guild.features) if ', '.join(interaction.guild.features) != '' else 'None :('), inline=True)

            #statuses
            guild_info_embed.add_field(name="Member Statuses:", value=':green_circle: '+str([str(m.status) == "online" for m in interaction.guild.members].count(True))+"\n:yellow_circle: "+str([str(m.status) == "idle" for m in interaction.guild.members].count(True))+"\n:red_circle: "+str([str(m.status) == "dnd" for m in interaction.guild.members].count(True))+"\n:new_moon: "+str([str(m.status) == "offline" for m in interaction.guild.members].count(True)), inline=True)

            #user counts
            guild_info_embed.add_field(name="Member Counts:", value=str(interaction.guild.member_count)+" Total Members\n"+str(len([m for m in interaction.guild.members if not m.bot]))+" People\n"+str(len([m for m in interaction.guild.members if m.bot]))+" Bots", inline=True)

            #channels
            guild_info_embed.add_field(name="Channels:", value=str(len(interaction.guild.voice_channels)+len(interaction.guild.text_channels))+" Total Channels\n"+str(len(interaction.guild.text_channels))+" Text Channels\n"+str(len(interaction.guild.voice_channels))+" Voice Channels", inline=True)

            #static emojis

            #get static emojis string
            if len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in interaction.guild.emojis if emoji.animated==False])) == 0:
                static_emojis = 'None :('
            elif len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in interaction.guild.emojis if emoji.animated==False])) >= 1000:
                static_emojis = 'Too many to show.'
            elif len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in interaction.guild.emojis if emoji.animated==False])) >= 0 and len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in interaction.guild.emojis if emoji.animated==False])) <= 1000:
                static_emojis = ''.join([str(Bot.get_emoji(emoji.id)) for emoji in interaction.guild.emojis if emoji.animated==False])

            #add field
            guild_info_embed.add_field(name='Static Emojis: *('+str(len([emoji for emoji in interaction.guild.emojis if emoji.animated==False]))+')*', value='\u200b'+static_emojis, inline=True)


            #animated emojis (similar deal to static ones)
            if len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in interaction.guild.emojis if emoji.animated==True])) == 0:
                animated_emojis = 'None :('
            elif len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in interaction.guild.emojis if emoji.animated==True])) >= 1000:
                animated_emojis = 'Too many to show.'
            elif len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in interaction.guild.emojis if emoji.animated==True])) >= 0 and len(''.join([str(Bot.get_emoji(emoji.id)) for emoji in interaction.guild.emojis if emoji.animated==True])) <= 1000:
                animated_emojis = ''.join([str(Bot.get_emoji(emoji.id)) for emoji in interaction.guild.emojis if emoji.animated==True])

            guild_info_embed.add_field(name='Anim-Emojis: *('+str(len([emoji for emoji in interaction.guild.emojis if emoji.animated==True]))+')*', value='\u200b'+animated_emojis, inline=True)

            #server creation date
            creation_date = interaction.guild.created_at
            guild_info_embed.add_field(name='Server Creation Date:', value=f"<t:{int(creation_date.timestamp())}:f> (<t:{int(creation_date.timestamp())}:R>)", inline=True)

            #role num
            guild_info_embed.add_field(name='Number of roles:', value=str(len(interaction.guild.roles)), inline=True)

            #server id
            guild_info_embed.add_field(name='Server ID:', value=str(interaction.guild.id), inline=True)

            #total slaps
            total_slaps = 0
            for user in interaction.guild.members:
                if user.bot == False:
                    total_slaps += database_utils.fetch_user_data(user.id, "slaps")
            guild_info_embed.add_field(name="Total slaps:", value=general_utils.si_format(total_slaps))

            #net worth
            net_worth = 0
            for user in interaction.guild.members:
                if user.bot == False:
                    net_worth += database_utils.fetch_user_data(user.id, "balance")
            guild_info_embed.add_field(name="Server Net Worth:", value=f"§{general_utils.si_format(net_worth)}")

            await interaction.response.send_message(embed=guild_info_embed, ephemeral=general_utils.is_ghost(interaction.user.id))

        @app_commands.command(name="define", description="Looks up a dictionary definition for a word.")
        async def _define(self, interaction: discord.Interaction, word: str):
            await interaction.response.defer()
            data = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}").json()
            if 'title' in data:
                error_embed = general_utils.error_embed(author=interaction.user, message=f"I couldn't find \"{word}\" in the dictionary...")
                if randint(0,5) == 3:
                    error_embed.description += "\nWords are more likely to be recognised the less niche their definition is. (For example, scientific terms like 'Diastereoisomerism' probably won't be picked up.)"
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return
            index = 0
            if 'phonetic' not in data[0]:
                data[0]['phonetic'] = None
            embed = general_utils.Embed(
                author=interaction.user,
                title=f"Definition of {word}.",
                description=f"[{data[0]['meanings'][index]['partOfSpeech']}]     {data[0]['phonetic'] if data[0]['phonetic'] != None else ''}\n {data[0]['meanings'][index]['definitions'][0]['definition']}"
            )
            
            if len(data[0]['meanings']) > 1:
                embed.set_footer(text=f"Meaning {index+1} of {len(data[0]['meanings'])}")

                #class Controller(discord.ui.View):
                #    @discord.ui.button(label='<', style=discord.ButtonStyle.blurple, disabled=True)
                #    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
#
                #        index = int(interaction.message.embeds[0].footer.text.split(' ')[1])-1
                #        length = int(interaction.message.embeds[0].footer.text.split(' ')[3])
                #        if index > 0:
                #            index -= 1
                #        if index == 0:
                #            button.disabled = True
                #        if index != length-1:
                #            self.children[1].disabled = False
#
                #        embed.description = f"[{data[0]['meanings'][index]['partOfSpeech']}]     {data[0]['phonetic']}\n {data[0]['meanings'][index]['definitions'][0]['definition']}"
                #        embed.set_footer(text=f"Meaning {index+1} of {length}")
                #        await interaction.response.edit_message(embed=embed, view=self)
#
                #    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
                #    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
#
                #        index = int(interaction.message.embeds[0].footer.text.split(' ')[1])-1
                #        length = int(interaction.message.embeds[0].footer.text.split(' ')[3])
                #        if index < length-1:
                #            index += 1
                #        if index == length-1:
                #            button.disabled = True
                #        if index != 0:
                #            self.children[0].disabled = False
#
                #        embed.description = f"[{data[0]['meanings'][index]['partOfSpeech']}]     {data[0]['phonetic']}\n {data[0]['meanings'][index]['definitions'][0]['definition']}"
                #        embed.set_footer(text=f"Meaning {index+1} of {length}")
                #        await interaction.response.edit_message(embed=embed, view=self)
                await interaction.followup.send(embed=embed, view=Controller(0, len(data[0]['meanings'])), ephemeral=general_utils.is_ghost(interaction.user.id))
            else:
                await interaction.followup.send(embed=embed, ephemeral=general_utils.is_ghost(interaction.user.id))


    await Bot.add_cog(Info(Bot))