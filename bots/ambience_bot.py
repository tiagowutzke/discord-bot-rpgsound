import os
import sys

from discord.ext import commands
from bots.bot_adapter import bot_ready, stop_sound, play_manually, get_channels_id, play_sound

TOKEN = os.environ['AMBIENCE_BOT_TOKEN']
client = commands.Bot(command_prefix='ambience_')


@client.event
async def on_ready():
    await bot_ready('Ambience bot pronto!', client)


@client.command(pass_context=True)
async def stop(ctx):
    await stop_sound(client=client)


@client.command(pass_context=True)
async def play(ctx, tag):
    await  play_manually(
        client=client,
        query_table='som_ambiente',
        query_col='filename',
        tag=tag,
        ctx=ctx
    )




client.run(TOKEN)
