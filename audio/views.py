from django.shortcuts import render, redirect
from .models import MeetingTranscript
from django.core.files.storage import FileSystemStorage
import requests
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from time import sleep
from reportlab.pdfgen import canvas
from io import BytesIO

ASSEMBLYAI_API_KEY = '630e32c3bbec45aea3f0c2790f924b87'

@csrf_exempt
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
        transcription = transcribe_audio(fs.path(filename))  # Pass the correct file path for transcription

        # Save the transcript in the database
        transcript = MeetingTranscript(
            speaker_name=speaker_name,
            audio_file=audio_file,
            transcript_text=transcription
        )
        transcript.save()

        # Generate PDF and return it as a response
        return generate_transcription_pdf(transcript)

    return render(request, 'audio/index.html')


def transcribe_audio(file_path):
    """
    Transcribes the audio file using AssemblyAI API.
    """
    # Upload the audio file to Assembly AI and get the audio URL
    upload_url = upload_audio_to_assembly_ai(file_path)

    if not upload_url:
        return "Error: Failed to upload audio."

    headers = {
        'authorization': ASSEMBLYAI_API_KEY,
        'content-type': 'application/json',
    }

    # Send the transcription request
    transcript_request = {'audio_url': upload_url}
    response = requests.post('https://api.assemblyai.com/v2/transcript', headers=headers, json=transcript_request)

    # Check if the transcription request was successful
    if response.status_code != 200:
        return f"Error: Failed to submit for transcription. Response: {response.json()}"

    transcript_id = response.json().get('id')

    if not transcript_id:
        return "Error: Transcription ID not returned."

    # Poll for transcription result
    transcription_result = poll_transcription_result(transcript_id)

    return transcription_result


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


def upload_audio_to_assembly_ai(file_path):
    """
    Uploads an audio file to AssemblyAI and returns the upload URL.
    """
    upload_url = "https://api.assemblyai.com/v2/upload"
    headers = {'authorization': ASSEMBLYAI_API_KEY}

    try:
        with open(file_path, 'rb') as f:
            response = requests.post(upload_url, headers=headers, files={'file': f})

        if response.status_code == 200:
            return response.json().get('upload_url')
        else:
            print(f"Error: Failed to upload audio. Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred during file upload: {e}")
        return None


# Function to generate and return transcription as a PDF
def generate_transcription_pdf(transcript):
    """
    Generate a PDF with the transcription text.
    """
    buffer = BytesIO()  # Create an in-memory buffer to store the PDF
    pdf = canvas.Canvas(buffer)

    # Set PDF title and header
    pdf.setTitle("Meeting Transcript")
    pdf.drawString(100, 800, f"Transcript of {transcript.speaker_name}")

    # Add the transcription text
    text_object = pdf.beginText(100, 750)
    text_object.setFont("Helvetica", 12)

    # Ensure the transcription is displayed in a readable format
    for line in transcript.transcript_text.splitlines():
        text_object.textLine(line)
    
    pdf.drawText(text_object)
    pdf.showPage()
    pdf.save()

    # Get the value of the BytesIO buffer and prepare a FileResponse
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="transcription.pdf")
