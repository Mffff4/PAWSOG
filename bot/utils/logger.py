import logging
from datetime import datetime
from rich.console import Console
from rich.theme import Theme
from rich.emoji import Emoji
from bot.config import settings

custom_theme = Theme({
    "info": "green",
    "warning": "yellow",
    "error": "red",
    "success": "bold green",
    "timestamp": "cyan",
    "debug": "dim white"  # Для детальных логов
})

console = Console(theme=custom_theme)

class PawsLogger:
    EMOJIS = {
        "info": "ℹ️ ",
        "warning": "⚠️ ",
        "error": "❌ ",
        "success": "✅ ",
        "debug": "🔍 "
    }

    @staticmethod
    def _get_timestamp():
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def _format_message(emoji: str, message: str, level: str):
        timestamp = f"[timestamp]{PawsLogger._get_timestamp()}[/timestamp]"
        return f"{emoji}{timestamp} | [{level}]{message}[/{level}]"

    @classmethod
    def _should_log_detail(cls, detail_type: str) -> bool:
        if not settings.DETAILED_LOGGING:
            return False
        
        detail_map = {
            'auth': settings.LOG_AUTH_DATA,
            'response': settings.LOG_RESPONSE_DATA,
            'request': settings.LOG_REQUEST_DATA,
            'user_agent': settings.LOG_USER_AGENT,
            'proxy': settings.LOG_PROXY
        }
        return detail_map.get(detail_type, False)

    @classmethod
    def info(cls, message: str, detail_type: str = None):
        if detail_type and not cls._should_log_detail(detail_type):
            return
        formatted = cls._format_message(cls.EMOJIS["info"], message, "info")
        console.print(formatted)

    @classmethod
    def debug(cls, message: str, detail_type: str = None):
        if detail_type and not cls._should_log_detail(detail_type):
            return
        if settings.DETAILED_LOGGING:
            formatted = cls._format_message(cls.EMOJIS["debug"], message, "debug")
            console.print(formatted)

    @classmethod
    def warning(cls, message: str):
        formatted = cls._format_message(cls.EMOJIS["warning"], message, "warning")
        console.print(formatted)

    @classmethod
    def error(cls, message: str):
        formatted = cls._format_message(cls.EMOJIS["error"], message, "error")
        console.print(formatted)

    @classmethod
    def success(cls, message: str):
        formatted = cls._format_message(cls.EMOJIS["success"], message, "success")
        console.print(formatted)

# Отключаем логи Pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session.auth").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session.session").setLevel(logging.WARNING)

# Создаем глобальный экземпляр логгера
logger = PawsLogger()
