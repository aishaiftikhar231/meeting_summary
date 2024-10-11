from django.db import models

class MeetingTranscript(models.Model):
    speaker_name = models.CharField(max_length=100)
    audio_file = models.FileField(upload_to='uploads/')
    transcript_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Transcript by {self.speaker_name} on {self.timestamp}"
