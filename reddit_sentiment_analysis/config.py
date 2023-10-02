from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = Field('dev')
    feddit_url: str = Field('http://localhost:8080')
    host: str = Field('0.0.0.0')
    port: int = Field(8000)
    reload: bool = Field(True)
    debug: bool = Field(True)
    log_level: str = Field('info')
    access_log: bool = Field(True)
    workers: int = Field(1)

    LOGGING_CONFIG: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        'formatters': {
            'jsonFormatter': {
                '()': 'reddit_sentiment_analysis.logs.CustomJsonFormatter',
                'format': '%(levelname)%(asctime)%(location)%(message)',
            },
        },
        'handlers': {
            'consoleHandler': {
                'class': 'logging.StreamHandler',
                'level': "INFO",
                'formatter': 'jsonFormatter',
            }
        },
        'loggers': {
            'webapp': {
                'handlers': ['consoleHandler'],
                'level': "INFO",
            },
            'uvicorn': {
                'handlers': ['consoleHandler']
            },
            'uvicorn.access': {
                'handlers': ['consoleHandler']
            }
        }
    }



settings = Settings()
