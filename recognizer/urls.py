from django.urls import path
from recognizer import views

app_name = 'recognize'

urlpatterns = [
    path('', views.index, name='index'),
    path('recognize/', views.get_emotion_upload, name='get_emotion'),
    path('recognize/recording/', views.get_emotion_recording, name='get_emotion_rec'),
]
