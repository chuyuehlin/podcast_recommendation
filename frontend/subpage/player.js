const playfromo = (deviceID, token) => {
    const playaURL = `https://api.spotify.com/v1/me/player/play?device_id=${deviceID}`;
    const d = { uris: ['spotify:episode:{{ episode_id }}'],position_ms:0};
    fetch(playaURL, {
        method: 'PUT',
        body: JSON.stringify(d),
        headers: new Headers({
            Authorization: `Bearer ${token}`,
        }),
    })
    .then((res) => res.json())
    .catch((error) => console.error('Error:', error))
    .then((response) => console.log('Success:', response));
}
  
  
const play = (deviceID, token) => {
    const playaURL = `https://api.spotify.com/v1/me/player/play?device_id=${deviceID}`;
    const d = { uris: ['spotify:episode:{{ episode_id }}']};
    fetch(playaURL, {
        method: 'PUT',
        body: JSON.stringify(d),
        headers: new Headers({
            Authorization: `Bearer ${token}`,
        }),
    })
    .then((res) => res.json())
    .catch((error) => console.error('Error:', error))
    .then((response) => console.log('Success:', response));
}
  
  
const seek = (deviceID, token) => {
    const playaURL = `https://api.spotify.com/v1/me/player/seek?position_ms=0&device_id=${deviceID}`;
    fetch(playaURL, {
        method: 'PUT',
        headers: new Headers({
            Authorization: `Bearer ${token}`,
        }),
    })
    .then((res) => res.json())
    .catch((error) => console.error('Error:', error))
    .then((response) => console.log('Success:', response));
}
  
  
  
window.onSpotifyWebPlaybackSDKReady = () => {
    token = '{{access_token}}';
    player = new Spotify.Player({
        name: 'Hello',
        getOAuthToken: cb => { cb(token); }
    });
  
    // Error handling
    player.addListener('initialization_error', ({ message }) => { console.error(message); });
    player.addListener('authentication_error', ({ message }) => { console.error(message); });
    player.addListener('account_error', ({ message }) => { console.error(message); });
    player.addListener('playback_error', ({ message }) => { console.error(message); });
  
    // Playback status updates
    player.addListener('player_state_changed', state => { console.log(state); });
  
    // Ready
    player.addListener('ready', ({ device_id }) => {
        playfromo(device_id,token)
        did=device_id
        // player.resume()
        console.log('Ready with Device ID', device_id);
    });
  
    // Not Ready
    player.addListener('not_ready', ({ device_id }) => {
      console.log('Device ID has gone offline', device_id);
    });
    console.log(player)
    // Connect to the player!
    player.connect();
};

// let now_playing = document.querySelector(".now-playing");
let track_art = document.querySelector(".track-art");
let track_name = document.querySelector(".track-name");
let track_artist = document.querySelector(".track-artist");
  
let playpause_btn = document.querySelector(".playpause-track");
let next_btn = document.querySelector(".next-track");
let prev_btn = document.querySelector(".prev-track");
  
let seek_slider = document.querySelector(".seek_slider");
let volume_slider = document.querySelector(".volume_slider");
let curr_time = document.querySelector(".current-time");
let total_duration = document.querySelector(".total-duration");
  
let track_index = 0;
let isPlaying = false;
let updateTimer;
let duration;
let currentTime;
// Create new audio element
// let curr_track = document.createElement('audio');
  
// Define the tracks that have to be played
let track_list = [{
    name: "{{ name }}",
    artist: "{{ artist }}",
    image: "{{ image }}",
    path: "{{ path }}",
}];
  
function loadTrack(track_index) {
    clearInterval(updateTimer);
    resetValues();
  
    // Load a new track
    // curr_track.src = track_list[track_index].path;
    // curr_track.load();
  
    // Update details of the track
    track_art.style.backgroundImage = "url(" + track_list[track_index].image + ")";
    track_name.textContent = track_list[track_index].name;
    track_artist.textContent = track_list[track_index].artist;
    // now_playing.textContent = "PLAYING " + (track_index + 1) + " OF " + track_list.length;
  
    // Set an interval of 1000 milliseconds for updating the seek slider
    updateTimer = setInterval(seekUpdate, 500);
  
    // Move to the next track if the current one finishes playing
    // curr_track.addEventListener("ended", nextTrack);
  
    // Apply a random background color
    //random_bg_color();
}
  
  
// Reset Values
function resetValues() {
    curr_time.textContent = "00:00";
    total_duration.textContent = "00:00";
    seek_slider.value = 0;
}
  
function playpauseTrack() {
    if (!isPlaying) playTrack();
    else pauseTrack();
}
  
function playTrack() {
        
    play(did,token);
    isPlaying = true;
  
    // Replace icon with the pause icon
    playpause_btn.innerHTML = '<i class="fa fa-pause-circle fa-5x"></i>';
}
  
function pauseTrack() {
    player.pause()
    isPlaying = false;
  
    // Replace icon with the play icon
    playpause_btn.innerHTML = '<i class="fa fa-play-circle fa-5x"></i>';;
}
  
function nextTrack() {
    // if (track_index < track_list.length - 1)
    //   track_index += 1;
    // else track_index = 0;
    // loadTrack(track_index);
    // playTrack();
}
  
function prevTrack() {
    // if (track_index > 0)
    //   track_index -= 1;
    // else track_index = track_list.length;
    // loadTrack(track_index);
    // playTrack();
}
  
function seekTo() {
  
    seekto = duration * (seek_slider.value / 100);
    player.seek(seekto * 1000).then(() => {
        console.log('Changed position!');
    });
        
    // seek_slider.value = seekPosition;
}
  
function setVolume() {
    player.setVolume(volume_slider.value / 100);
}
  
function seekUpdate() {
    let seekPosition = 0;
    player.getCurrentState().then(response => {
        currentTime=Math.floor(response.position/1000)
        duration=Math.floor(response.duration/1000)
    });
  
    // Check if the current track duration is a legible number
    if (!isNaN(duration)) {
        seekPosition = currentTime * (100 / duration);
        seek_slider.value = seekPosition;
  
        // Calculate the time left and the total duration
        let currentMinutes = Math.floor(currentTime / 60);
        let currentSeconds = Math.floor(currentTime - currentMinutes * 60);
        let durationMinutes = Math.floor(duration / 60);
        let durationSeconds = Math.floor(duration - durationMinutes * 60);

        // Adding a zero to the single digit time values
        if (currentSeconds < 10) { currentSeconds = "0" + currentSeconds; }
        if (durationSeconds < 10) { durationSeconds = "0" + durationSeconds; }
        if (currentMinutes < 10) { currentMinutes = "0" + currentMinutes; }
        if (durationMinutes < 10) { durationMinutes = "0" + durationMinutes; }
  
        curr_time.textContent = currentMinutes + ":" + currentSeconds;
        total_duration.textContent = durationMinutes + ":" + durationSeconds;
    }
}
  
// Load the first track in the tracklist
loadTrack(track_index);