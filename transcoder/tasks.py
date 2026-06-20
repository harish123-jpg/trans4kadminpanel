# transcoder/tasks.py
from celery import shared_task

@shared_task
def generate_script_task(stream_id):
    from transcoder.models import Stream
    from transcoder.views import generate_script  # adjust if different
    stream = Stream.objects.get(id=stream_id)
    generate_script(stream)

