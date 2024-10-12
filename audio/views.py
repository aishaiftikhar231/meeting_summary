from django.shortcuts import render, redirect
from .models import MeetingTranscript
from django.core.files.storage import FileSystemStorage
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from time import sleep

ASSEMBLYAI_API_KEY = 'your_assembly_ai_api_key'

@csrf_exempt  # For demo purposes, remove or adjust this for production security
def upload_and_transcribe(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        # Get the speaker name and audio file
        speaker_name = request.POST.get('speaker_name', 'Unknown Speaker')
        audio_file = request.FILES['audio_file']

        # Save the audio file locally
        fs = FileSystemStorage()
        filename = fs.save(audio_file.name, audio_file)
        file_url = fs.url(filename)

        # Transcribe the audio using Assembly AI
        transcription = transcribe_audio(audio_file)

        # Save the transcript in the database
        transcript = MeetingTranscript(
            speaker_name=speaker_name,
            audio_file=audio_file,
            transcript_text=transcription
        )
        transcript.save()

        # Redirect to the chat page where all transcriptions are displayed
        return redirect('transcription_chat')

    return render(request, 'audio/index.html')


def transcription_chat(request):
    # Fetch all transcripts, ordered by the latest timestamp
    transcripts = MeetingTranscript.objects.all().order_by('-timestamp')
    return render(request, 'audio/chat.html', {'transcripts': transcripts})


def transcribe_audio(audio_file):
    # Upload audio to Assembly AI
    upload_url = upload_audio_to_assembly_ai(audio_file)

    headers = {
        'authorization': ASSEMBLYAI_API_KEY,
        'content-type': 'application/json',
    }
    transcript_request = {
        'audio_url': upload_url
    }
    
    # Send the audio file for transcription
    response = requests.post('https://api.assemblyai.com/v2/transcript', headers=headers, json=transcript_request)
    transcript_id = response.json().get('id')

    if not transcript_id:
        return "Error: Failed to upload or transcribe."

    # Poll for transcription result
    transcription_result = poll_transcription_result(transcript_id)

    return transcription_result


# Polling function to check transcription status
def poll_transcription_result(transcript_id):
    headers = {
        'authorization': ASSEMBLYAI_API_KEY,
    }
    transcript_url = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'

    while True:
        response = requests.get(transcript_url, headers=headers)
        status = response.json().get('status')

        if status == 'completed':
            return response.json().get('text')
        elif status == 'failed':
            return "Transcription failed."
        else:
            sleep(5)  # Poll every 5 seconds


# Upload audio to Assembly AI function
def upload_audio_to_assembly_ai(audio_file):
    upload_url = "https://api.assemblyai.com/v2/upload"
    
    headers = {
        'authorization': ASSEMBLYAI_API_KEY,
    }

    # Open the audio file and send it to Assembly AI's upload endpoint
    with open(audio_file.path, 'rb') as f:
        response = requests.post(upload_url, headers=headers, files={'file': f})

    # Return the URL of the uploaded audio
    return response.json().get('upload_url')
