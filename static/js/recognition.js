    // Global variable to control mic image icon on/off
    var mic_status = 'off';
    // Global recognition to control pause in recognition and audio capture
    var recognition = new webkitSpeechRecognition();

    function check_mic_icon(image_on, image_off){
        var image = document.getElementById('sound_icon')

        if(mic_status == 'off'){
            mic_status = 'on'
            image.src = image_on;
            return true;
        }
        else {
            mic_status = 'off'
            image.src = image_off
            image.style.opacity = "0.6"
            recognition.stop();
            if(music_is_playing) music_is_playing.pause();
            if(effects_is_playing) effects_is_playing.pause();
            if(sound_is_playing) sound_is_playing.pause();
            return false;
        }
    }

    function check_mic_discord_icon(){
        var image = document.getElementById('sound_icon');

        if(mic_status == 'off'){
            mic_status = 'on'
            image.style.opacity = '1'
            start_bots();
        }
        else {
            mic_status = 'off'
            image.style.opacity = '0.3'
            recognition.stop();
            stop_bots();
        }
    }

   /* Transcription function */
    function start_transcription(image_on, image_off, is_discord_bots) {

        if(is_discord_bots)
            check_mic_discord_icon();
        else{
            mic_on = check_mic_icon(image_on, image_off);
            if(!mic_on) return false;
        }

        // Allow mic in browser
        if(navigator.mediaDevices) {
             navigator.mediaDevices.getUserMedia({ audio: true })

             .then(function(stream) {
                console.log('Mic allowed!')
              })

             .catch(function(err) {
                console.log('Mic not allowed!')
              });
         }

        // Output to print recognition
        const output = document.querySelector('#output');
        // Recognition params
        recognition.interimResults = true;
        recognition.lang = "pt-BR";
        recognition.continuous = true;
        recognition.start();

        // Classifiers
        audio_types = ['efeito_sonoro', 'som_ambiente', 'musica_ambiente']

        // This event happens when you talk in the microphone
        recognition.onresult = function(event) {
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    // Here you can get the string of what you told
                    const content = event.results[i][0].transcript.trim();
                    output.textContent = 'Áudio captado: ' + content;

                    if (should_stop_audio(content)) break;

                    for (var type in audio_types) {
                        classify_sentence(content, audio_types[type], is_discord_bots).then(response => { });
                    }
                }
            }
        };

        // Keep transcription alive
        recognition.onend = function() {
            recognition.start();
        }
    };

    function save_suggestions(suggestions, audio_type) {
        url = '/save_suggestions?suggestions=' + suggestions + '&audio_type=' + audio_type

        $.ajax({
              url: url,
              type: "get",
              success: function(response) {
                console.log(response)
              },
              error: function(response) {
                console.log('error on save suggestions: ' + response)
              }
        });
    }

    function should_stop_audio(content){

        sentence = content.toLowerCase().trim()

        switch (sentence){
            case 'parar música':
                music_is_playing.pause();
                return true;
                break;
            case 'parar som':
                sound_is_playing.pause();
                return true;
                break;
            case 'parar efeitos':
                effects_is_playing.pause();
                return true;
                break;
        }

        return false;
    }

   // Send sentence to aws lambda function to be classified
   async function classify_sentence(audio_transcription, audio_type, is_discord_bots){
        url = '/classify?sentence=' + audio_transcription + '&type=' + audio_type
        const output = document.querySelector('#output');

        $.ajax({
              url: url,
              type: "get",
              success: function(response) {
                result = String(response)
                result = JSON.parse(result);

                if(result.label){
                    get_audio_classified(result.label, audio_type, is_discord_bots);
                    output.textContent = 'Label identificada: ' + result.label + ' Score: ' + result.score;
                }
                if(result.suggestions) save_suggestions(result.suggestions, audio_type);
              },
              error: function(response) {
                return false
              }
        });
   }

   var music_is_playing = false;
   var effects_is_playing = false;
   var sound_is_playing = false;


   function get_audio_classified(label, type, is_discord_bots){
        url = "/audio_by_label?type=" + type + '&label=' + label

        $.ajax({
            url: url,
            type: "get",
            success: function(response) {
                switch (type) {
                    case 'efeito_sonoro':
                        if (is_discord_bots) play_audio_discord(response, type)
                        else effects_is_playing = playSound(response, type)
                        break;
                    case 'som_ambiente':
                        if (is_discord_bots) play_audio_discord(response, type)
                        else sound_is_playing = playSound(response, type)
                        break;
                    case 'musica_ambiente':
                        if (is_discord_bots) play_audio_discord(response, type)
                        else music_is_playing = playSound(response, type)
                        break;
                }
            },
            error: function(response) {
                return false
            }
        });
   }


   function playSound(url, type) {

        switch (type) {
            case 'efeito_sonoro':
                if(effects_is_playing)
                    effects_is_playing.pause()
                break;
            case 'som_ambiente':
                if(sound_is_playing)
                    sound_is_playing.pause()
            case 'musica_ambiente':
                if(music_is_playing)
                    music_is_playing.pause()
        }

        var audio = new Audio(url);
        audio.play();

        return audio;
    }


    /**
     ** DISCORD BOT TRANSCRIPTION
     **/

   /* Transcription function */
    function start_bots(){
        url = "/start_bots"

        $.ajax({
            url: url,
            type: "get",
            success: function(response) {
                console.log('Bots on!')
            },
            error: function(response) {
                return false;
            }
        });
    }

    function stop_bots(){
        url = "/stop_bots"

        $.ajax({
            url: url,
            type: "get",
            success: function(response) {
                console.log(response);
            },
            error: function(response) {
                return false;
            }
        });
    }

    function play_audio_discord(audio_url, audio_type){
       url = '/get_discord_audio?audio_url=' + audio_url + '&audio_type=' + audio_type

        $.ajax({
            url: url,
            type: "get",
            success: function(response) {
                console.log(response);
            },
            error: function(response) {
                console.log('Error on playing in discord');
            }
        });
    }