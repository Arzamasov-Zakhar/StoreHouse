DEFAULT_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"

LOGGINT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "formatter_gunicorn": {
            "format": """{"message": "%(message)s"}""",  # noqa  WPS322
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": DEFAULT_FORMAT,
        },
    },
    "handlers": {
        "handler_gunicorn": {
            "class": "logging.StreamHandler",
            "formatter": "formatter_gunicorn",
            "stream": "ext://sys.stdout",
        },
        "console_json": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "gunicorn": {
            "level": "DEBUG",
            "handlers": ["handler_gunicorn"],
            "propagate": False,
        },
        "src": {
            "level": "DEBUG",
            "handlers": ["console_json"],
            "propagate": False,
        },
    },
}
