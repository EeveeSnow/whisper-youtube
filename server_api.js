var socket = new WebSocket('ws://localhost:8765');


socket.onopen = function (event) {
    console.log('WebSocket is open now.');
};


socket.onerror = function (error) {
    console.log(`WebSocket error: ${error}`);
};


socket.onclose = function (event) {
    if (event.wasClean) {
        console.log(`WebSocket closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
        console.log('WebSocket connection lost');
    }
    socket = new WebSocket('ws://localhost:8765');
};

var videoPlayer = document.getElementById("video-player");
var videoAudio = document.getElementById("video-audio");
var videoForm = document.getElementById("video-form");
var videoUrl = document.getElementById("video-url");
var videoSubmit = document.getElementById("video-submit");
var videoSubs = document.getElementById("video-st");


videoForm.addEventListener("submit", function (event) {

    event.preventDefault();
    if (videoUrl.value) {
        socket.send(videoUrl.value)
    }
    ;
});
videoPlayer.addEventListener("play", function () {
    videoAudio.play();
});
videoPlayer.addEventListener("pause", function () {
    videoAudio.pause();
});
videoPlayer.onseeked = function() {
    videoAudio.currentTime = videoPlayer.currentTime;
};
socket.onmessage = function (event) {
    console.log(`Server response: ${event.data}`);
    videoPlayer.src = event.data + ".mp4"
    videoSubs.src = event.data + ".vtt"
    videoAudio.src = event.data + ".webm"

};