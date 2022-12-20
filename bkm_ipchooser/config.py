import os

from django.conf import settings

IP_CHOOSER_CC_ROOT_URL = os.environ.get("IP_CHOOSER_CC_ROOT_URL", settings.BK_CC_HOST)
