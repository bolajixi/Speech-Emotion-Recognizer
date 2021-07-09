import os
import glob
from os import path
from pathlib import Path

import numpy as np

from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from recognizer.forms import AudioForm

import speech_recognition as sr
from .process_audio import extract_features


# Create your views here.

def index(request):
    return render(request, 'recognizer/index.html', )


def privacy(request):
    return render(request, 'recognizer/privacy.html', )


def get_emotion_recording(request):
    if request.method == "POST":
        HOME_path = Path.cwd() / 'media' / 'recordings'

        audio_data = request.FILES.get('data')
        path = default_storage.save(
            str(HOME_path) + '/recording.wav', ContentFile(audio_data.read()))

        recent_file_path = get_latest_file_path()  # Get latest file recorded

        if recent_file_path:

            print(predict_audio(recent_file_path).shape)
            transcription = get_transcription(recent_file_path)
            print(transcription['success'], transcription['transcription'])

            # Delete file after processing
            # os.remove(recent_file_path)

    return render(request, 'recognizer/get_emotion.html', )


def get_emotion_upload(request):
    if request.method == "POST":

        filename = request.FILES.get('record').name
        file_extension = filename.split('.')[-1]

        if file_extension.lower() != 'wav':
            return HttpResponse('Bad upload')

        form = AudioForm(request.POST, request.FILES or None)

        if form.is_valid():
            form.save()

            recent_file_path = get_latest_file_path()  # Get latest file uploaded

            if recent_file_path:

                predict_audio(recent_file_path)
                transcription = get_transcription(recent_file_path)
                print(transcription['success'], transcription['transcription'])

                # Delete file after processing
                # os.remove(recent_file_path)

            return HttpResponse('Success')
    else:
        form = AudioForm()

    return render(request, 'recognizer/get_emotion.html', {'form': form})


def predict_audio(audio_file):
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
