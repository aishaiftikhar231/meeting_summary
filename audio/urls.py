from django.contrib import admin
from django.urls import path, include
from audio import views  # Import views from your 'audio' app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', views.transcription_chat, name='transcription_chat'),
    path('', views.transcription_chat, name='home'),  # Add this line to handle the root URL
]
