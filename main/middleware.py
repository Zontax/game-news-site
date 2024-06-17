from django.utils.translation import get_language
from django.utils import timezone
from django.http import HttpRequest

from user_agents import parse
import logging

logging.basicConfig(filename='detail.log', level=logging.INFO)
logger = logging.getLogger()


class PrintRequestInfoMiddleware:

    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request: HttpRequest):
        ip_address = request.META.get('REMOTE_ADDR')
        user_locale = get_language()
        user_timezone = timezone.get_current_timezone_name()
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_string)
        device_type = 'PC' if user_agent.is_pc else 'Mobile' if user_agent.is_mobile else 'Tablet' if user_agent.is_tablet else 'Other'
        browser_info = f'{user_agent.browser.family} {user_agent.browser.version_string}'

        logger.info(f'User: {request.user}')
        logger.info(f'IP Address: {ip_address}')
        logger.info(f'Locale: {user_locale}')
        logger.info(f'Timezone: {user_timezone}')
        logger.info(f'Device: {device_type}')
        logger.info(f'Browser: {browser_info}')

        response = self._get_response(request)

        return response
