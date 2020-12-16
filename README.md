# RPG Sound: A discord bot

RPG Sound is a discord bot to play sounds and musics for RPG games. The bot can be activated in two ways:
- Automatically: by speech recogniton
- Manually: by command inside discord channel

Besides that, there is an audio capture to play sounds in web browser with no discord needed.

## User documentation

The following section describes the app features and his usages.

### Main page

Address: https://rpg-sound.herokuapp.com/
 
It's the main page of the app, and contains shortcuts to main features of the app.

### Áudios online

(*Online audios in english*)

Address: https://rpg-sound.herokuapp.com/jogar

This page contains the audio capture to classify and reproduce sounds. Each shound must be registered with a label and 
sentences to be validated by the bot classifier. The proccess to register a sound is described in [Uploads](#uploads) section.

For sound classify, first click on speaker icon in the middle of the page. In this moment, your microphone device will start
capture your voice (allow microphone permission in google chrome needed). Then, just star talking for label classification.

The classification is made by three types of label:
- Ambience sounds
- Effect sounds
- Music

If your speech match the three types of labels, and there are these three sounds and validations registered in app, these three
sounds can be reproduced at same time.

To stop the reproduction of on type of sound, just talk one of these in microphone:

- `parar música` (*stop music in english*): to stop music reproduction.   
- `parar som` (*stop sound in english*): to stop ambience sounds reproduction.
- `parar efeitos` (*stop effects in english*): to stop sound effects reproduction.

### Discord bots

Address: https://rpg-sound.herokuapp.com/discord-bots

This page contains the audio capture to classify and reproduce sounds in discord voice channel. Each sound must be registered with a label and 
sentences to be validated by the bot classifier. The proccess to register a sound is described in [Uploads](#uploads) section.

**Important:** to sound be reproduced in discord voice channel, there is a (simple) configuration needed. See more in 
[configuration](#configurações) section. 

For sound classify, first click on discord bot icon in the middle of the page. In this moment, your microphone device will start
capture your voice (allow microphone permission in google chrome needed) and the discord bots will be online and connected in
discord voice channel. Then, just start talking for label classification.

The classification and sounds reproduction is the same like the [Áudios online](#áudios-online) section: there are three 
types of sounds and its possible to stop them, but in this case, the commands are used in discord text channel:

- type `music_play <tag>` in text channel to reproduce a specific music by the `<tag>` name.
- type `ambience_play <tag>` in text channel to reproduce a specific ambience sound by the `<tag>` name.
- type `sound_play <tag>` in text channel to reproduce a specific sound effect by the `<tag>` name.

For stop sounds, the commands are the following:

- type `music_stop` in text channel to stop music reproduction.
- type `ambience_stop` in text channel to stop ambience sound reproduction.
- type `sound_stop` in text channel to stop sound effect reproduction.

## Technical documentation