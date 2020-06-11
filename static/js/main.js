// Input value in <option> element
function setInputValue(input_id, option_selected) {
    document.getElementById(input_id).setAttribute('value', option_selected.value);
}

$(document).ready(function() {
    /* Upload form submit */
     $('#btn-submit').click(function(e){
         $('#btn-text').hide();
         $('#divMsg').show();
     });

     $("#file_input").on("change", function (e) {

        var file = e.currentTarget.files; // puts all files into an array
        var filesize = ((file[0].size/1024)/1024).toFixed(4); // MB

        // call them as such; files[0].size will get you the file size of the 0th file
        if (filesize >= 35) {
            $("#warning").show();
            $("#btn-submit").prop("disabled",true);
        }
        else{
            $("#warning").hide();
            $("#btn-submit").prop("disabled",false);
        }
     });

    // Blocks space character in upload audio page
    $("input#tag").on({
	  keydown: function(e) {
		if (e.which === 32)
		  return false;
	  },
	  change: function() {
		this.value = this.value.replace(/\s/g, "");
	  }
	});

});

function cancel_loading(){
    $('#divMsg').hide();
    $('#btn-text').show();
}

var mouseovertimer;
/*
Global variable for a timer. When the mouse is hovered over the speaker
it will start playing after hovering for 1 second, if less than 1 second
it won't play (incase you accidentally hover over the speaker)
*/
var audiostatus = 'off';

 /* Audio icon - audios page  */
function play_audio(audio_id, speaker_id) {
    var getaudio = $(audio_id)[0];
    /* Get the audio from the player (using the player's ID), the [0] is necessary */

    /* Global variable for the audio's status (off or on). It's a bit crude but it works for determining the status. */
     /* Touchend is necessary for mobile devices, click alone won't work */
     if (!$(speaker_id).hasClass("speakerplay")) {
       if (audiostatus == 'off') {
         $(speaker_id).addClass('speakerplay');
         getaudio.load();
         getaudio.play();
         window.clearTimeout(mouseovertimer);
         audiostatus = 'on';
       } else if (audiostatus == 'on') {
         $(speaker_id).addClass('speakerplay');
         getaudio.play()
       }
     } else if ($(speaker_id).hasClass("speakerplay")) {
       getaudio.pause();
       $(speaker_id).removeClass('speakerplay');
       window.clearTimeout(mouseovertimer);
       audiostatus = 'on';
     }
      $(audio_id).on('ended', function() {
        $(speaker_id).removeClass('speakerplay');
        audiostatus = 'off';
      });

   };

   /* Audio page - edit tag and validation */
   function show_edit_options(btn_edit, id_btn_show){
        var edit_id = '#'.concat(btn_edit.id);
        var cancel_id = '#cancel_'.concat(id_btn_show);
        var save_id = '#save_'.concat(id_btn_show);
        var text_id = '#text_'.concat(id_btn_show);
        var input_id = '#input_'.concat(id_btn_show);
        var check_id = '#check_'.concat(id_btn_show);

        $(edit_id).hide();
        $(text_id).hide();
        $(cancel_id).show();
        $(save_id).show();
        $(check_id).show();

        $(input_id).show();
        $(input_id).css("padding", "0.3em")
        $(input_id).css("width", "90%");

        $(check_id).css("position", "absolute");
        $(check_id).css("display", "inline-flex");
        $(check_id).css("font-size", "0.8em");
        $(check_id).css("margin", "0.9em 5em");

   }

   function cancel_edit_options(btn_cancel, id_btn_show){
        var cancel_id = '#'.concat(btn_cancel.id);
        var edit_id = '#edit_'.concat(id_btn_show);
        var save_id = '#save_'.concat(id_btn_show);
        var text_id = '#text_'.concat(id_btn_show);
        var input_id = '#input_'.concat(id_btn_show);
        var check_id = '#check_'.concat(id_btn_show);

        $(edit_id).show();
        $(text_id).show();
        $(cancel_id).hide();
        $(save_id).hide();
        $(input_id).hide();
        $(check_id).hide();

        $(text_id).css("top", "0.1em")
   }

   function save_edit_audio(form_id){
    var should_update_audio = confirm("Confirma a alteração do audio?");

    if (should_update_audio) {
        document.getElementById(form_id).submit();
    } else {
      return false;
    }
   }

  function delete_audio(form_id){
    var should_update_audio = confirm("Confirma a exclusão do audio?");

    if (should_update_audio) {
        document.getElementById(form_id).submit();
    } else {
      return false;
    }
   }

   /* Dinamic audio search */
   function search_audio(input_text, input_name, form_id){
        setTimeout(function(){
            var text = $(input_text).val();

            $.ajax({
              url: "/search_audios",
              type: "get",
              data: {
                search_text: text,
                column: input_name,
                table: form_id
                },
              success: function(response) {
                $("#tbody_".concat(form_id)).html(response);
              },
              error: function(response) {
                window.alert('Erro na busca dos audios:' + response)
              }
            });
        }, 700);
   }

   // Tooltip
   $(document).ready(function() {
       $(function () {
            $('[data-toggle="tooltip"]').tooltip()
       })
    });


    /* Dinamic load nlp suggestions in train page */
   function load_suggestions(transaction, id, score){

        if(!score.value && transaction == 'search')
            transaction = '';

        setTimeout(function(){
            $.ajax({
              url: "/load_suggestions",
              type: "get",
              data: {
                transaction: transaction,
                id: id,
                score: score.value
                },
              success: function(response) {
                $("#table_suggestions").html(response);
              },
              error: function(response) {
                console.log('Erro na busca de sugestões: ' + response)
              }
            });
        }, 400);
   }

  /*  Delete all suggestions */
  function delete_suggestions(){

       var should_delete = confirm("Deseja apagar TODAS as sugestões?");

       if(should_delete){
            show_loading_buttons('#delete-all-txt', '#delete-all-gif', '#btn-delete-all');
            setTimeout(function(){
                $.ajax({
                  url: "/delete_suggestions",
                  type: "get",
                  data: {
                    },
                  success: function(response) {
                    console.log('All suggestions deleted!')
                    hide_loading_buttons('#delete-all-txt', '#delete-all-gif', '#btn-delete-all');
                  },
                  error: function(response) {
                    console.log('Error on all delete suggestions' + response)
                  }
                });
            }, 100);
            load_suggestions('no_transactions', 'no_id', 'no_score');
       }
  }

  /* Hide text button and show loading gif */
  function show_loading_buttons(to_hide, to_show, to_disable){
        $(to_disable).prop('disabled', true);
        $(to_disable).css('opacity', '0.5');
        $(to_hide).hide();
        $(to_show).show();
  }

  function hide_loading_buttons(to_show, to_hide, to_enable){
        $(to_enable).prop('disabled', false);
        $(to_enable).css('opacity', '1');
        $(to_hide).hide();
        $(to_show).show();
  }



    /* Dinamic load status in train page */
  function start_train(url){
        // Update "WAITING" status on train status table
        setTimeout(function(){
            $.ajax({
              url: url,
              type: "get",
              success: function(response) {
                $("body").html(response);
              },
              error: function(response) {
                window.alert('Erro ao atualizar ' + response)
              }
            });
        }, 100);

        // Call lambda function to start model training
        $.ajax({
            url: '/train_model_lambda',
            type: "get",
            success: function(response) {
            console.log('Success on training model!');
            },
            error: function(response) {
            console.log('Error on train model')
            }
        });
   }

    // Global variable to control mic image icon on/off
    var mic_status = 'off';
    // Global recognition to control pause in recognition and audio capture
    var recognition = new webkitSpeechRecognition();



    /**
     ** ONLINE TRANSCRIPTION
     **/
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