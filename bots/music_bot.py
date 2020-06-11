import os
import sys

from discord.ext import commands
from bots.bot_adapter import bot_ready, stop_sound, get_channels_id, play_sound, play_manually

TOKEN = os.environ['MUSIC_BOT_TOKEN']
client = commands.Bot(command_prefix='music_')


@client.event
async def on_ready():
    await bot_ready('Music bot pronto!', client)


@client.command(pass_context=True)
async def stop(ctx):
    await stop_sound(client=client)


@client.command(pass_context=True)
async def play(ctx, tag):
    await  play_manually(
        client=client,
        query_table='musica_ambiente',
        query_col='filename',
        tag=tag,
        ctx=ctx
    )


async def play_by_speech(audio):
    voice_id, text_id = get_channels_id()

    global client
    voice_channel = client.get_channel(voice_id)
    text_channel = client.get_channel(text_id)

    await play_sound(
        client,
        voice_channel,
        text_channel,
        audio
    )
    sys.exit()


client.run(TOKEN)

