var all_voices = window.speechSynthesis.getVoices();

function make_bumper(words) {
    $('#player').animate({volume: 0.1}, 500);
    var msg = new SpeechSynthesisUtterance(words);
    var this_hour = (new Date()).getHours();
    msg.voice = all_voices[this_hour];
    msg.onend = function() {
        // after speech is over, bring volume back
        $('#player').animate({volume: 1.0}, 500);
    }
    window.speechSynthesis.speak(msg);
}

function miliseconds_from_now(some_date) {
    // passed in must be an instance of Date.
    return some_date.getTime() - (new Date()).getTime();
}

$("#mute").click(function() {
    $(this).hide();
    $('#player').get(0).volume = 0.01;
    $("#unmute").show();
});

$("#unmute").click(function() {
    $(this).hide();
    $('#player').get(0).volume = 1.0;
    $("#mute").show();
});

var stream_enabled = false;
$("#stop").click(function() {
    $('#player').get(0).pause();
    stream_enabled = false;
    $("#start2").show();
    $(this).hide();
    $("#currently_playing").addClass("grayed");
    $("#currently_playing .status").text("Not Streaming");
});
$("#start").click(function(event, autostart) {
    // get the streaming process going.
    console.log("start button clicked!!!!");
    stream_enabled = true;
    if(!autostart) {
        // don't call this function when doing autostart,
        // because of a race condition.
        start_playing_song();
    }
    $("#stop").show();
    $("#mute").show();
    $(this).hide();
    $("#currently_playing").removeClass("grayed");
});

$("#player").on('timeupdate', function() {
    // update the seek bar as the song plays.
    $('progress').attr("value", this.currentTime / this.duration);
});

$("#player").on('ended', function() {
    // when a song ends, add it to the play history section.
    // there is a one second gap between the last song ending
    // and the next song starting. During that gap, the "current
    // song" is actualy the previous song.

    console.log("Song ended event!!!!!");

    var artist = $("#currently_playing .artist").text();
    var title = $("#currently_playing .title").text();
    var year = $("#currently_playing .year").text();

    var new_row = $(
        "<div class='play_history'>" +
        artist + " - " + year + " - " + title +
        "</div>"
    );

    $("#last_played_header").show()
    $("#last_played_container").prepend(new_row);
});

function start_playing_song() {
    // This function is called at the time of the next song starting
    // either at the begining of the song, or while it is in progress.

    if(stream_enabled) {
        var player = $("#player");
        player.text($("#currently_playing .tips").text());
        $("#currently_playing .status").text("Currently Streaming");
        player.attr("src", $("#currently_playing .cache_audio").attr('src'));
        player.get(0).play();
    } else {
        console.log("not playing sound or loading mp3 because not started");
    }

    var start_time = new Date($("#currently_playing .start_time").text());

    console.log("start time of currently playing song", start_time);
    console.log("time is now", (new Date()));

    var seconds_in_prgress = -1 * miliseconds_from_now(start_time) / 1000;

    console.log($("#currently_playing .title").text(), "is", seconds_in_prgress, " seconds in progress")

    if(seconds_in_prgress > 10 && enable_skip_ahead) {
        // song was supposed to start more than 10 seconds ago. Skip ahead
        // to the correct time
        $('#player').bind('canplay', function() {
            this.currentTime = seconds_in_prgress;
        });
    }
}

function make_currently_playing(song, element) {
    // song = object that comes from next_song or current_song (API call)
    // element = the element we write this info to. can be either the
    // visible one or the hidden one (for cache).

    var preload = stream_enabled ? "auto" : "none";
    var status = stream_enabled ? "Currently Streaming" : "Not Currently Streaming"

    element.html("<span class='status'>" + status + "</span><br><br>"
        + "<audio class='cache_audio' src='" + song.url + "' preload='" + preload + "'></audio>"
        + "<span class='tips'>" + JSON.stringify(song.tips) + "</span>"
        + "<img src='" + song.img + "'><br>"
        + "<span class='artist'>" + song.artist + "</span> - "
        + "[<span class='year'>" + song.year + "</span>] "
        + "<span class='title'>" + song.title + "</span>"
        + "<span class='start_time'>" + song.start_time + "</span>"
        + "<br><progress value='0' max='1' style='width: 80%'></progress>"
    );
}

function fetch_next_track() {
    // hit the backend to get the next song.
    $.ajax({
        url: "/current_and_next_song",
        type: "get",
        complete: function(response) {
            console.log("fetching next song");
            response = response.responseJSON;
            next_song = response.next_song;
            current_song = response.current_song;

            $("#next_song").html(
                "<span class='artist'>" + next_song.artist + "</span>" +
                " - <span class='title'>" + next_song.title + "</span>"
            );

            // load next track into the background so the image and mp3 preload
            // that way when its time to switch to the next track, it is instant.
            make_currently_playing(next_song, $("#currently_playing_cache"));

            if($("#currently_playing").text().trim() == '') {
                // the station has just started up, fill in currently playing too.
                make_currently_playing(current_song, $("#currently_playing"));
                start_playing_song();
            }

            // schedule the next song switch event
            var next_start_date = new Date(next_song.start_time);
            var from_now_miliseconds = next_start_date.getTime() - (new Date()).getTime();
            console.log("setting play switch event of", next_song.title);
            setTimeout(function() {
                console.log("executing play switch event for", next_song.title);
                make_currently_playing(next_song, $("#currently_playing"));
                $("#next_song").html("&nbsp");
                start_playing_song();
            }, from_now_miliseconds);

            // schedule the next track fetch (every 20 seconds)
            setTimeout(fetch_next_track, 20000);
        },
        error: function() {
            $("#next_song").html("<span class='error'>Could not fetch next song. Try restarting the station.</span>")
            $("#stop").click();
        }
    });
}
fetch_next_track();
