import json
import logging
from django.views import View
from django.http import JsonResponse

from dtb.settings import DEBUG
from tgbot.dispatcher import process_telegram_event

logger = logging.getLogger(__name__)


def index(request):
    return JsonResponse({'error': 'You got the wrong address'})


class TelegramBotWebhookView(View):
    # WARNING: if fail - Telegram webhook will be delivered again. 
    # Can be fixed with async celery task execution
    def post(self, request, *args, **kwargs):
        if DEBUG:
            process_telegram_event(json.loads(request.body))
        else:  
            # Process Telegram event in Celery worker (async)
            # Don't forget to run it and & Redis (message broker for Celery)! 
            # Read Procfile for details
            # You can run all of these services via docker-compose.yml
            # process_telegram_event.delay(json.loads(request.body))

            # When use .delay, messages are received by different workers
            # And another worker doesn't know about current conversation
            # e.g, when we receiving many images from user (contract photos)
            process_telegram_event(json.loads(request.body))

        # e.g. remove buttons, typing event
        return JsonResponse({'ok': 'POST request processed'})
    
    def get(self, request, *args, **kwargs):  # for debug
        return JsonResponse({'ok': 'Get request received! But nothing done'})
