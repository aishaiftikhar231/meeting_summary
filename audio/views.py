from django.shortcuts import render, redirect
from .models import MeetingTranscript
from django.core.files.storage import FileSystemStorage

def upload_and_transcribe(request):
    if request.method == 'POST' and request.FILES['audio_file']:
        speaker_name = request.POST['speaker_name']
        audio_file = request.FILES['audio_file']

        fs = FileSystemStorage()
        filename = fs.save(audio_file.name, audio_file)
        file_url = fs.url(filename)

        # Here you would integrate AssemblyAI transcription logic
        transcript_text = f"Dummy transcription for {audio_file}"

        MeetingTranscript.objects.create(
            speaker_name=speaker_name,
            audio_file=audio_file,
            transcript_text=transcript_text
        )

        return redirect('transcription_chat')

    return render(request, 'audio/index.html')


def transcription_chat(request):
    transcripts = MeetingTranscript.objects.all().order_by('-timestamp')
    return render(request, 'audio/chat.html', {'transcripts': transcripts})
