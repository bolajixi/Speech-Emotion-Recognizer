import os
import glob
from os import path
from pathlib import Path
import speech_recognition as sr

from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import opensmile

from recognizer.forms import AudioForm


# Create your views here.

def index(request):
    return render(request, 'recognizer/index.html', )


def get_latest_file_path():
    HOME_path = Path.cwd() / 'media' / 'recordings'

    if os.listdir(HOME_path):
        # Check if recording is in recordings directory
        latest_file = os.path.join(
            HOME_path, str(os.listdir(HOME_path)[-1]))

    return str(latest_file)


def get_emotion_upload(request):
    if request.method == "POST":

        filename = request.FILES.get('record').name
        file_extension = filename.split('.')[-1]

        if file_extension.lower() != 'wav':
            return HttpResponse('Bad upload')

        form = AudioForm(request.POST, request.FILES or None)

        if form.is_valid():
            form.save()

            latest_path = get_latest_file_path()  # Get latest file uploaded

            if latest_path:

                process_audio(latest_path)
                transcription = get_transcription(latest_path)
                print(transcription)

                # Delete file after processing
                os.remove(latest_path)

            return HttpResponse('Success')
    else:
        form = AudioForm()

    return render(request, 'recognizer/get_emotion.html', {'form': form})


def get_emotion_recording(request):
    if request.method == "POST":
        HOME_path = Path.cwd() / 'media' / 'recordings'

        audio_data = request.FILES.get('data')
        path = default_storage.save(
            str(HOME_path) + '/recording.wav', ContentFile(audio_data.read()))

        latest_path = get_latest_file_path()  # Get latest file recorded

        if latest_path:

            process_audio(latest_path)
            transcription = get_transcription(latest_path)
            print(transcription)

            # Delete file after processing
            os.remove(latest_path)

    return render(request, 'recognizer/get_emotion.html', )


def process_audio(audio_file):

    smile = opensmile.Smile(
        feature_set=opensmile.FeatureSet.eGeMAPSv02,
        feature_level=opensmile.FeatureLevel.LowLevelDescriptors,
    )
    processed = smile.process_file(audio_file)

    print(processed.shape)


def get_transcription(audio_file):
    '''
    Transcribe audio recording.
    '''
    print(audio_file)

    transcription = []
    r = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)  # read the entire audio file

        trans = r.recognize_google(audio, language="en-US")
        transcription.append(trans)

    return ''.join(transcription)
