import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def get_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value == "True"


@dataclass(frozen=True)
class Config:
    debug: bool
    secret_key: str
    allowed_hosts: list[str]
    openai_api_key: str
    openai_model: str


config = Config(
    debug=get_bool("DEBUG", True),
    secret_key=os.getenv("SECRET_KEY", "django-insecure-local-dev-key"),
    allowed_hosts=[host.strip() for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")],
    openai_api_key=os.getenv("OPENAI_API_KEY", ""),
    openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
)
