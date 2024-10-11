import requests
from django.shortcuts import render
from django.http import HttpResponse
from .models import MeetingTranscript
from reportlab.pdfgen import canvas
from io import BytesIO

ASSEMBLYAI_API_KEY = 'your_assembly_ai_api_key'

# Function to handle file upload and transcription
def upload_and_transcribe(request):
    if request.method == 'POST':
        # Get the uploaded audio file
        audio_file = request.FILES['audio_file']
        
        # Upload the file to Assembly AI for transcription
        transcription = transcribe_audio(audio_file)

        # Save transcript to the database
        transcript = MeetingTranscript(
            speaker_name="Speaker",
            audio_file=audio_file,
            transcript_text=transcription
        )
        transcript.save()

        # Generate and return PDF file of the transcript
        return generate_pdf(transcription)

    return render(request, 'upload.html')

# Function to send audio to Assembly AI and get the transcription
def transcribe_audio(audio_file):
    # Upload audio to Assembly AI
    upload_url = upload_audio_to_assembly_ai(audio_file)
    
    # Send the file for transcription
    headers = {
        'authorization': ASSEMBLYAI_API_KEY,
        'content-type': 'application/json'
    }
    transcript_request = {
        'audio_url': upload_url
    }
    
    response = requests.post('https://api.assemblyai.com/v2/transcript', headers=headers, json=transcript_request)
    transcript_id = response.json()['id']

    # Wait for transcription to complete
    transcription_result = poll_transcription_result(transcript_id)

    return transcription_result

# Function to upload audio to Assembly AI
def upload_audio_to_assembly_ai(audio_file):
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=audio_file)
    return response.json()['upload_url']

# Function to poll the transcription result
def poll_transcription_result(transcript_id):
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    transcript_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    
    while True:
        response = requests.get(transcript_url, headers=headers)
        status = response.json()['status']
        
        if status == 'completed':
            return response.json()['text']
        elif status == 'failed':
            return "Transcription failed."
        else:
            import time
            time.sleep(5)

# Function to generate a PDF file with the transcript text
def generate_pdf(transcription_text):
    # Create a PDF response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transcript.pdf"'

    # Create a PDF buffer to write to
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Write the transcription text to the PDF
    p.drawString(100, 750, "Meeting Transcript")
    text_object = p.beginText(100, 730)
    text_object.setTextOrigin(100, 730)
    text_object.setFont("Helvetica", 12)

    # Split text into lines and add to PDF
    for line in transcription_text.splitlines():
        text_object.textLine(line)

    p.drawText(text_object)
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

# Corrected transcription_chat view function
def transcription_chat(request):
    return render(request, 'chat.html')

