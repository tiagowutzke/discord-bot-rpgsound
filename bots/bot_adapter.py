import os

from discord.utils import get
from discord import FFmpegPCMAudio

from database.adapter import get_database_objects
from utils.listening import get_audio_from_tag


def get_channels_id():
    conn, _, query = get_database_objects()
    voice_channel, text_channel = query.query_config()
    conn.close()
    return voice_channel, text_channel


async def bot_ready(message, client):
    print(message)

    voice_id, text_id = get_channels_id()

    voice_channel = client.get_channel(voice_id)

    voice = get(client.voice_clients, guild=voice_channel.guild)

    if voice and voice.is_connected():
        await voice.move_to(voice_channel)
    else:
        await voice_channel.connect()


async def connect_channel(client):
    voice_id, _ = get_channels_id()

    voice_channel = client.get_channel(voice_id)
    await voice_channel.connect()
    return True


async def play_sound(client, voice_channel, text_channel, audio):

    source = FFmpegPCMAudio(audio)
    voice = get(client.voice_clients, guild=voice_channel.guild)

    if voice and voice.is_connected():
        await voice.move_to(voice_channel)
    else:
        voice = await voice_channel.connect()

    try:
        voice.play(source)
    except:
        pass


async def play_manually(client, query_table, query_col, tag, ctx):
    voice_id, text_id = get_channels_id()

    voice_channel = client.get_channel(voice_id)
    text_channel = client.get_channel(text_id)

    if not tag:
        await text_channel.send("Algo errado ocorreu. Você inseriu a tag?")

    audio_file = await get_audio_from_tag(query_table=query_table, query_col=query_col, tag=tag)
    if audio_file:
        await play_sound(client, voice_channel, text_channel, audio_file)
    else:
        await ctx.send("Tag não encontrada")


async def stop_sound(client):
    voice_id, text_id = get_channels_id()

    voice_channel = client.get_channel(voice_id)
    text_channel = client.get_channel(text_id)

    if not voice_channel:
        await text_channel.send("Você não está conectado ao canal de voz. Conecte e tente novamente.")

    voice = get(client.voice_clients, guild=voice_channel.guild)

    try:
        if voice and voice.is_connected():
            await voice.move_to(voice_channel)
        else:
            voice = await voice_channel.connect()
    except:
        pass

    voice.stop()
