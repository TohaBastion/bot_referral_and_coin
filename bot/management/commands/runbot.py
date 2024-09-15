import asyncio
import logging
import sys
from django.core.management.base import BaseCommand
from bot.bot import main


class Command(BaseCommand):
    help = 'Запускає Telegram-бота'

    def handle(self, *args, **kwargs):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
