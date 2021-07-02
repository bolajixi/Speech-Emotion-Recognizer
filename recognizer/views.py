from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'recognizer/index.html', )


def get_emotion(request):
    return render(request, 'recognizer/get_emotion.html', )
