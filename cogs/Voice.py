from discord.ext import commands
import discord
import importlib
import utils

importlib.reload(utils)


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="setup",
                    description="Create the setup channel",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="name",
                    description="Rename the voice channel you're in",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                ),
                discord.ApplicationCommandOption(
                    name="limit",
                    description="Set the max users for a channel",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                )
            ],
        )
    )
    async def voice(self, ctx, *arg):
        """Allow Synthy to create/delete channels as needed to keep things tidy"""

    @commands.has_permissions(administrator=True)
    @voice.command(aliases=[], application_command_meta=commands.ApplicationCommandMeta(options=[]))
    @commands.defer(ephemeral=True)
    async def setup(self, ctx):
        """Create the initial voice channel"""
        channel: discord.VoiceChannel = await ctx.guild.create_voice_channel(name="VC Foyer")
        await utils.sql('INSERT INTO "database1".synthy.voice (guild_id, channel_id) VALUES (%s, %s) ON CONFLICT (guild_id) DO UPDATE SET channel_id = %s;', (ctx.guild.id, channel.id, channel.id,))
        await ctx.send(content=f"I have created {channel.mention} for you.")

    @voice.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="name",
                    description="Rename the voice channel you're in",
                    type=discord.ApplicationCommandOptionType.string,
                    required=True,
                )
            ],
        )
    )
    async def name(self, ctx, name):
        if not ctx.author.voice:
            emb = await utils.embed(ctx, f"Voice", "You're not connected to a voice channel")
            await ctx.send(embed=emb)
            return

        elif not str(ctx.author.voice.channel.name).startswith("🔊"):
            emb = await utils.embed(ctx, f"Voice", "The voice channel you're in isn't one I should touch.")
            await ctx.send(embed=emb)
            return

        try:
            await ctx.author.voice.channel.edit(name=f"🔊 {name}")
            emb = await utils.embed(ctx, f"Voice", f"The name of your voice channel is now is now 🔊 {name}.")
        except discord.Forbidden as e:
            emb = await utils.embed(ctx, f"Voice", "I don't have permission to edit that channel.")
        except discord.HTTPException as e:
            emb = await utils.embed(ctx, f"Voice", "I wasn't able to edit that channel, try this again. If you keep seeing this please let my [code slave](https://discord.gg/bDAa7cu) know.")
        except discord.InvalidArgument as e:
            emb = await utils.embed(ctx, f"Voice", "What you entered wasn't able to be used for this setting.")
        await ctx.send(embed=emb)

    @voice.command(
        aliases=[],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="user_count",
                    description="Set the max users for the voice channel you're in",
                    type=discord.ApplicationCommandOptionType.integer,
                    required=True,
                )
            ],
        )
    )
    async def limit(self, ctx, user_count: int):
        if not ctx.author.voice:
            emb = await utils.embed(ctx, f"Voice", "You're not connected to a voice channel")
            await ctx.send(embed=emb)
            return

        elif not str(ctx.author.voice.channel.name).startswith("🔊"):
            emb = await utils.embed(ctx, f"Voice", "The voice channel you're in isn't one I should touch.")
            await ctx.send(embed=emb)
            return

        try:
            arg = int(user_count)
            if arg < 0 or arg > 99:
                raise ValueError
            await ctx.author.voice.channel.edit(user_limit=arg)
            emb = await utils.embed(ctx, f"Voice", f"The maximum users for {ctx.author.voice.channel.name} is now {arg}.")
        except ValueError as e:
            emb = await utils.embed(ctx, f"Voice", "I can only work with 0 to 99 for this command.")
        except discord.Forbidden as e:
            emb = await utils.embed(ctx, f"Voice", "I don't have permission to edit that channel.")
        except discord.HTTPException as e:
            emb = await utils.embed(ctx, f"Voice", "I wasn't able to edit that channel, try this again. If you keep seeing this please let my [code slave](https://discord.gg/bDAa7cu) know.")
        except discord.InvalidArgument as e:
            emb = await utils.embed(ctx, f"Voice", "What you entered wasn't able to be used for this setting.")
        await ctx.send(embed=emb)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before, after):
        # Ah shit i'm not ready!
        if not self.bot.is_ready(): return

        # Figure out if I should care about this event
        if before.channel == after.channel:
            return

        # Figure out if this guy will cause a scene in the club
        if after.channel is not None and after.channel.name.lower() == "vc foyer":
            # Let the guy in, but make sure he ain't got a gun
            if member.display_name.capitalize().endswith("s"):
                user_name = f"{member.display_name.capitalize()}'"
            else:
                user_name = f"{member.display_name.capitalize()}'s"

            chnl = await after.channel.clone(name=f"🔊 {user_name} Chat")
            await member.edit(voice_channel=chnl)

        # Check is the club is empty.
        elif before.channel is not None and "🔊" in before.channel.name:
            # Last One Out, Get the Lights. #FinishTheFight
            if len(before.channel.members) == 0:
                await before.channel.delete()


def setup(bot):
    print("INFO: Loading [Voice]... ", end="")
    bot.add_cog(Voice(bot))
    print("Done!")


def teardown(bot):
    print("INFO: Unloading [Voice]")
