from django.urls import path
from recognizer import views

app_name = 'recognize'

urlpatterns = [
    path('', views.index, name='index'),
    path('recognize/', views.get_emotion, name='get_emotion'),
]
