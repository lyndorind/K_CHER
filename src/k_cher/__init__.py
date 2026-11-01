"""Навчальний пакет для практичної з GitHub Actions."""

__version__ = "1.4.1"


def hello(name: str = "world") -> str:
    return f"Hello, {name}!"
