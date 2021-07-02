from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'recognizer/index.html', )


def recognize(request):
    return render(request, 'recognizer/get_emotion.html', )
