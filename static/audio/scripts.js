let chunks = [];
let mediaRecorder;

const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const uploadBtn = document.getElementById("upload-btn");
const audioPlayback = document.getElementById("audio-playback");
const uploadForm = document.getElementById("upload-form");

// Request microphone and speaker access
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = function (e) {
            chunks.push(e.data);
        };

        mediaRecorder.onstop = function () {
            const blob = new Blob(chunks, { 'type': 'audio/wav; codecs=opus' });
            chunks = [];
            const audioURL = window.URL.createObjectURL(blob);
            audioPlayback.src = audioURL;

            // Append audio file to form for upload
            const fileInput = document.getElementById("audio-file");
            const audioFile = new File([blob], "recording.wav", { type: "audio/wav" });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(audioFile);
            fileInput.files = dataTransfer.files;

            uploadBtn.disabled = false;
        };
    });

startBtn.addEventListener("click", () => {
    mediaRecorder.start();
    startBtn.disabled = true;
    stopBtn.disabled = false;
});

stopBtn.addEventListener("click", () => {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
});

// Handle upload and transcription
uploadForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const formData = new FormData(uploadForm);

    fetch('/audio/transcribe/', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("transcription-output").innerText = "Transcription: " + data.transcription;
    })
    .catch(error => console.error('Error:', error));
});
