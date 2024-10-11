from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_and_transcribe, name='upload_and_transcribe'),  # Homepage URL for audio upload
    path('chat/', views.transcription_chat, name='transcription_chat'),  # URL for the transcription chat
]
