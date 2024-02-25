function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob);

    fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}


document.addEventListener('DOMContentLoaded', function () {
    const startRecord = document.getElementById('startRecord');
    const stopRecord = document.getElementById('stopRecord');
    const audioPlayer = document.getElementById('audioPlayer');
    const audioUpload = document.getElementById('audioUpload');
    let mediaRecorder;
    let audioChunks = [];

    startRecord.onclick = () => {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = e => {
                    audioChunks.push(e.data);
                };
                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks);
                    const audioUrl = URL.createObjectURL(audioBlob);
                    audioPlayer.src = audioUrl;
                    audioPlayer.hidden = false;
                    sendAudioToServer(audioBlob);
                };
                audioChunks = [];
                mediaRecorder.start();
                startRecord.disabled = true;
                stopRecord.disabled = false;
            })
            .catch(e => console.error(e));
    };

    stopRecord.onclick = () => {
        mediaRecorder.stop();
        startRecord.disabled = false;
        stopRecord.disabled = true;
    };

    audioUpload.onchange = () => {
        const files = audioUpload.files;
        if (files.length > 0) {
            const audioUrl = URL.createObjectURL(files[0]);
            audioPlayer.src = audioUrl;
            audioPlayer.hidden = false;
            sendAudioToServer(files[0]);
        }
    };
});