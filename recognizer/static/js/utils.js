URL = window.URL || window.webkitURL;
var gumStream;
//stream from getUserMedia() 
var rec;
//Recorder.js object 
var input;
//MediaStreamAudioSourceNode we'll be recording 
// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext = new AudioContext;
//new audio context to help us record 
var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var downloadLink = document.getElementById('download');
var upload = document.getElementById('id_record')

//add events to those 3 buttons 
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

stopButton.disabled = true;

var seconds = 0;
var el = document.getElementById('seconds');

function incrementSeconds() {
    seconds += 1;
    el.innerText = seconds;
}

var cancel;



function startRecording() { console.log("recordButton clicked");

    var constraints = {
        audio: true,
        video: false
    } 
    /* Disable the record button until we get a success or fail from getUserMedia() */

    recordButton.disabled = true;
    recordButton.setAttribute('title', 'Click the Stop button to stop recording');

    stopButton.disabled = false;

    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ..."); 
        /* assign to gumStream for later use */
        gumStream = stream;
        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);
        /* Create the Recorder object and configure to record mono sound (1 channel) Recording 2 channels will double the file size */
        rec = new Recorder(input, {
            numChannels: 1
        }) 
        //start the recording process 
        rec.record()
        console.log("Recording started");
        // Start the timer
        cancel = setInterval(incrementSeconds, 1000);
        seconds = 0
    }).catch(function(err) {
        //enable the record button if getUserMedia() fails 
        recordButton.disabled = false;
        stopButton.disabled = true;
    });
}

function stopRecording() {
    console.log("stopButton clicked");
    //disable the stop button, enable the record too allow for new recordings 
    stopButton.disabled = true;
    stopButton.setAttribute('title', 'Click the Record button to start recording');

    recordButton.disabled = false;
    //tell the recorder to stop the recording 
    rec.stop(); //stop microphone access 
    gumStream.getAudioTracks()[0].stop();
    //Stop the timer
    clearInterval(cancel);
    //create the wav blob and pass it on to createDownloadLink 
    rec.exportWAV(createDownloadLink);
}

function createDownloadLink(blob) {
    var url = URL.createObjectURL(blob);
    var au = document.createElement('audio');
    var li = document.createElement('li');
    var link = document.createElement('a');
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    //add controls to the <audio> element 
    au.controls = true;
    au.src = url;

    //link the a element to the blob 
    var filename = new Date().toISOString();
    link.href = url;
    link.download = filename + '.wav';
    link.innerHTML = link.download;

    //add the new audio and a elements to the li element 
    li.appendChild(au);
    li.appendChild(link);
    // upload.value = filename + '.wav';

    //Upload link
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 302) {
            var json = JSON.parse(this.responseText); 
            console.log(json.prediction); 
            console.log(json.url);
            window.location.href = json.url;
        }
    };

    xhttp.open("POST", "/recognize/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrftoken);
    var data = new FormData();
    data.append('data', blob, filename);
    xhttp.send(data);
    //add the li element to the ordered list `
    recordingsList.appendChild(li);
}