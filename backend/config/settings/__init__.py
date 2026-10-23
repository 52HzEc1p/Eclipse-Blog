import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / '.env')

DJANGO_ENV = os.environ.get('DJANGO_ENV', 'dev')
if DJANGO_ENV == 'prod':
    from .prod import *  # noqa: F401, F403
else:
    from .dev import *  # noqa: F401, F403
