import os

from discord.ext import commands
from bots.bot_adapter import play_manually, stop_sound, connect_channel

TOKEN = os.environ['SOUND_BOT_TOKEN']
client = commands.Bot(command_prefix='sound_')


@client.event
async def on_ready():
    print('SoundBot manual pronto!')
    await connect_channel(client)


@client.command(pass_context=True)
async def off(ctx):
    await ctx.send("Até logo!")
    await ctx.bot.logout()


@client.command(pass_context=True)
async def play(ctx, tag):
    await  play_manually(
        client=client,
        query_table='efeito_sonoro',
        query_col='filename',
        tag=tag,
        ctx=ctx
    )


@client.command(pass_context=True)
async def stop(ctx):
    await stop_sound(client=client)


client.run(TOKEN)
