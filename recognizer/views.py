import os
import glob
from pathlib import Path

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import opensmile

from recognizer.forms import AudioForm


# Create your views here.

def index(request):
    return render(request, 'recognizer/index.html', )


def get_emotion(request):
    if request.method == "POST":

        filename = request.FILES.get('record').name
        file_extension = filename.split('.')[-1]

        if file_extension.lower() != 'wav':
            return HttpResponse('Bad upload')

        form = AudioForm(request.POST, request.FILES or None)

        if form.is_valid():
            form.save()

            HOME_path = Path.cwd() / 'media' / 'recordings'

            if os.listdir(HOME_path):
                # Check if recording is in recordings directory
                latest_file_recording = os.path.join(
                    HOME_path, str(os.listdir(HOME_path)[-1]))

                foo = process_audio(latest_file_recording)

                # Delete file after processing
                os.remove(latest_file_recording)

            return HttpResponse('Success')
    else:
        form = AudioForm()

    return render(request, 'recognizer/get_emotion.html', {'form': form})


def process_audio(audio_file):

    smile = opensmile.Smile(
        feature_set=opensmile.FeatureSet.eGeMAPSv02,
        feature_level=opensmile.FeatureLevel.LowLevelDescriptors,
    )
    processed = smile.process_file(audio_file)

    print(processed.shape)
