from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def validate_video_url(value):
    """Accept HTTP(S) links and same-origin video paths, including demo assets."""
    if value.startswith('/') and not value.startswith('//'):
        if '\\' not in value and not any(char.isspace() for char in value):
            return
        raise ValidationError('本地视频路径不能包含空白或反斜杠。')
    URLValidator(schemes=['http', 'https'])(value)
