from django import forms
from transcoder.models import Stream

class StreamForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = '__all__'
        widgets = {
            'stream_type': forms.Select(choices=[
                ('mpeg2', 'mpeg2'),
                ('mpeg4', 'mpeg4'),
                ('h264', 'h264'),
                ('h265', 'h265'),
            ]),
            'output_codec': forms.Select(choices=[
                ('h264', 'h264'),
                ('h265', 'h265'),
            ]),
            'preset': forms.Select(choices=[
                ('slow', 'slow'),
                ('medium', 'medium'),
                ('fast', 'fast'),
                ('hq', 'hq'),
            ]),
            'output_stream': forms.Select(choices=[
                ('HLS', 'HLS'),
                ('UDP', 'UDP'),
                ('MPD', 'MPD'),
                ('RTP', 'RTP'),
                ('TS', 'TS'),
                ('MP4', 'MP4'),
            ]),
            'audio_codec': forms.Select(choices=[
                ('AAC', 'AAC'),
                ('AC3', 'AC3'),
                ('MP3', 'MP3'),
                ('MP2', 'MP2'),
            ]),
            'name': forms.TextInput(attrs={'class': 'p-2 border border-gray-300 rounded-lg w-1/2'}),
            'source': forms.TextInput(attrs={'class': 'p-2 border border-gray-300 rounded-lg w-1/2'}),
            'gpu': forms.NumberInput(attrs={'class': 'p-2 border border-gray-300 rounded-lg w-1/2'}),
        }

    def __init__(self, *args, **kwargs):
        super(StreamForm, self).__init__(*args, **kwargs)

        # Optional: Improve all field styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'})

        # ✅ Dynamically make GPU optional based on request POST data
        data = kwargs.get('data')
        if data:
            if data.get('force_cpu') == 'true':  # this key should be in your POST payload
                self.fields['gpu'].required = False

    def clean_stream_name(self):
        stream_name = self.cleaned_data['stream_name']
        if not stream_name.isalnum():
            raise forms.ValidationError("Stream name should not have spaces or special characters.")
        return stream_name

    def clean_stream_source(self):
        stream_source = self.cleaned_data['stream_source']
        if not stream_source.startswith(('udp://', 'rtp://', 'http://', 'https://')):
            raise forms.ValidationError("Stream source must start with udp://, rtp://, http://, or https://")
        return stream_source

