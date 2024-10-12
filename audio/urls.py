import requests
from django.urls import path
from . import views

# AssemblyAI API key (replace with your actual key)
ASSEMBLYAI_API_KEY = 'your_assembly_ai_api_key'

# URL Configuration for your Django app
urlpatterns = [
    path('', views.upload_and_transcribe, name='upload_and_transcribe'),
    path('chat/', views.transcription_chat, name='transcription_chat'),
]

# Function to upload audio to Assembly AI
def upload_audio_to_assembly_ai(audio_file):
    headers = {'authorization': ASSEMBLYAI_API_KEY}

    # Preparing the file to be uploaded
    files = {
        'file': (audio_file.name, audio_file, 'audio/mpeg')  # Modify MIME type as per your file format, e.g., 'audio/wav'
    }

    # Sending the POST request to AssemblyAI API for file upload
    response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files=files)

    # Check for a successful upload
    if response.status_code == 200:
        # Returning the uploaded audio URL from AssemblyAI
        return response.json()['upload_url']
    else:
        # Raise an error if the upload fails
        raise Exception(f"Failed to upload audio to Assembly AI. Status Code: {response.status_code}, Response: {response.text}")
