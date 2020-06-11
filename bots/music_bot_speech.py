import os
import sys

from discord.ext import commands
from bots.bot_adapter import get_channels_id, play_sound, stop_sound

TOKEN = os.environ['MUSIC_BOT_TOKEN']
client = commands.Bot(command_prefix='music_')

import asyncio

loop = asyncio.new_event_loop()

@client.event
async def on_ready():
    print('Music Bot speech pronto!')

    audio = list(sys.argv)[1]
    await play(audio)


@client.command(pass_context=True)
async def stop(ctx):
    await stop_sound(client)


async def play(audio):
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


if __name__ == "__main__":
    client.run(TOKEN)
