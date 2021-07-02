  let shouldStop = false;
  let stopped = false;
  const downloadLink = document.getElementById('download');
  const stopButton = document.getElementById('stop');
  const startButton = document.getElementById('start');

  stopButton.addEventListener('click', function() {
    shouldStop = true;
  });

  if (navigator.mediaDevices.getUserMedia) {
    console.log('getUserMedia supported.');

    let handleSuccess = function(stream) {
      const options = {mimeType: 'audio/webm'};
      const recordedChunks = [];
      const mediaRecorder = new MediaRecorder(stream, options);

      startButton.onclick = function() {
      mediaRecorder.start();
      console.log(mediaRecorder.state);
      console.log("recorder started");
      startButton.style.background = "red";

      stopButton.disabled = false;
      startButton.disabled = true;
    }

    stopButton.onclick = function() {
      mediaRecorder.stop();
      console.log(mediaRecorder.state);
      console.log("recorder stopped");
      startButton.style.background = "";
      startButton.style.color = "";
      // mediaRecorder.requestData();

      startButton.disabled = true;
      startButton.disabled = false;
      shouldStop = true;
    }

    mediaRecorder.addEventListener('dataavailable', function(e) {
      if (e.data.size > 0) {
        recordedChunks.push(e.data);
      }

      if(shouldStop === true && stopped === false) {
        stopped = true;
      }
    });

    mediaRecorder.addEventListener('stop', function() {
      downloadLink.href = URL.createObjectURL(new Blob(recordedChunks));
      downloadLink.download = 'acetest.wav';
    });

  };

    navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        .then(handleSuccess);
  } else {
   console.log('getUserMedia not supported on your browser!');
}
