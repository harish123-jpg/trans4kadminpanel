from django.db import models

STREAM_TYPE_CHOICES = [
    ('mpeg2', 'MPEG2'),
    ('mpeg4', 'MPEG4'),
    ('h264', 'H264'),
    ('h265', 'H265'),
]

OUTPUT_CODEC_CHOICES = [
    ('h264', 'H264'),
    ('h265', 'H265'),
]

OUTPUT_STREAM_CHOICES = [
    ('HLS', 'HLS'),
    ('MPD', 'MPD'),
]

AUDIO_CODEC_CHOICES = [
    ('AAC', 'AAC'),
    ('AC3', 'AC3'),
    ('MP3', 'MP3'),
    ('MP2', 'MP2'),
]

PRESET_CHOICES = [
    ('slow', 'Slow'),
    ('medium', 'Medium'),
    ('fast', 'Fast'),
    ('hq', 'HQ'),
]


class Stream(models.Model):
    name = models.CharField(max_length=100, unique=True)
    source = models.CharField(max_length=255)
    mapping = models.CharField(max_length=255, blank=True, null=True)
    gpu = models.IntegerField(null=True, blank=True)
    deinterlacing = models.CharField(max_length=255, blank=True, null=True)
    stream_type = models.CharField(max_length=20, choices=STREAM_TYPE_CHOICES)
    resolution = models.CharField(max_length=20)
    output_codec = models.CharField(max_length=20, choices=OUTPUT_CODEC_CHOICES)
    bitrate = models.CharField(max_length=20)
    max_bitrate = models.CharField(max_length=20)
    preset = models.CharField(max_length=20, choices=PRESET_CHOICES)
    output_stream = models.CharField(max_length=10, choices=OUTPUT_STREAM_CHOICES)
    output_ip = models.CharField(max_length=50, blank=True, null=True)
    frame_rate = models.IntegerField()

    # Audio
    audio_bitrate = models.CharField(max_length=20)
    audio_volume = models.IntegerField()
    audio_codec = models.CharField(max_length=10, choices=AUDIO_CODEC_CHOICES)

    is_running = models.BooleanField(default=False)

    def __str__(self):
        return self.name
