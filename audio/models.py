from django.db import models

class MeetingTranscript(models.Model):
    speaker_name = models.CharField(max_length=100)  # Speaker's name
    audio_file = models.FileField(upload_to='audio_files/')  # Uploaded audio file
    transcript_text = models.TextField()  # The transcription text
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp for when it was created

    def __str__(self):
        return f"Transcript by {self.speaker_name} at {self.timestamp}"

