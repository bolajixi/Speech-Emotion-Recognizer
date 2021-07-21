import os
import glob
from os import path
import requests
import json
from pathlib import Path

import numpy as np

from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import reverse
from django.views import View
from django.views.decorators.cache import cache_page

from recognizer.forms import AudioForm

import speech_recognition as sr
from .process_audio import extract_features

app_name = "recognizer"

# Model Server URL (Docker)
url = 'http://localhost:8501/v1/models/Multimodal_SER:predict'
cache_time_in_minutes = 60

# Create your views here.


@cache_page(60 * cache_time_in_minutes)
def index(request):
    return render(request, 'recognizer/index.html', )


def privacy(request):
    return render(request, 'recognizer/privacy.html', )


def result(request):
    return render(request, 'recognizer/result.html', )


def get_emotion_recording(request):
    if request.method == "POST":
        HOME_path = Path.cwd() / 'media' / 'recordings'

        audio_data = request.FILES.get('data')
        path = default_storage.save(
            str(HOME_path) + '/recording.wav', ContentFile(audio_data.read()))

        recent_file_path = get_latest_file_path()  # Get latest file recorded

        if recent_file_path:

            features = process_audio(recent_file_path)
            transcription = get_transcription(recent_file_path)

            print(transcription['success'], transcription['transcription'])

            predictions = make_prediction(
                [{"conv2d_input": features.tolist(
                )[0], "keras_layer_input": transcription['transcription']}]
            )
            result_url = reverse('recognize:result')

            # Check if persistent prediction in session
            if 'prediction' in request.session:
                del request.session['prediction']

            # Add prediction to session
            request.session['prediction'] = predictions

            return JsonResponse(status=302, data={"prediction": predictions, "url": request.build_absolute_uri(result_url)})

    return render(request, 'recognizer/get_emotion.html', )


def get_emotion_upload(request):
    if request.method == "POST":

        filename = request.FILES.get('record').name
        file_extension = filename.split('.')[-1]

        if file_extension.lower() != 'wav':
            return JsonResponse('Bad upload')

        form = AudioForm(request.POST, request.FILES or None)

        if form.is_valid():
            form.save()

            recent_file_path = get_latest_file_path()  # Get latest file uploaded

            if recent_file_path:

                features = process_audio(recent_file_path)
                transcription = get_transcription(recent_file_path)
                print(transcription['success'], transcription['transcription'])

                predictions = make_prediction(
                    [{"conv2d_input": features.tolist(
                    )[0], "keras_layer_input": transcription['transcription']}]
                )

                # Check if persistent prediction in session
                if 'prediction' in request.session:
                    del request.session['prediction']

                # Add prediction to session
                request.session['prediction'] = predictions

                result_url = reverse('recognize:result')

                # return JsonResponse(status=302, data={"prediction": predictions, "url": request.build_absolute_uri(result_url)})
                return redirect("recognize:result")
    else:
        form = AudioForm()

    return render(request, 'recognizer/get_emotion.html', {'form': form})


def make_prediction(instances):

    emotion_class = ['Angry', 'Happy', 'Neutral', 'Sad']

    data = json.dumps({"signature_name": "serving_default",
                       "instances": instances})
    headers = {"content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)

    predictions = json.loads(json_response.text)['predictions']
    return emotion_class[np.argmax(predictions)]


def process_audio(audio_file):
    features = extract_features(audio_file)
    return features


def get_transcription(audio_file):
    '''
    Transcribe audio recording.
    '''
    print(audio_file)

    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    r = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        # r.adjust_for_ambient_noise(source)
        audio = r.record(source)  # read the entire audio file

        try:
            response["transcription"] = r.recognize_google(
                audio, language="en-US")

        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"

        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"

    os.remove(audio_file)

    return response


def get_latest_file_path():
    HOME_path = Path.cwd() / 'media' / 'recordings'

    if os.listdir(HOME_path):
        # Check if recording is in recordings directory
        latest_file = os.path.join(
            HOME_path, str(os.listdir(HOME_path)[-1]))

    return str(latest_file)
