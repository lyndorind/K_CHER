"""Навчальний пакет для практичної з GitHub Actions."""

__version__ = "1.3.2"


def hello(name: str = "world") -> str:
    return f"Hello, {name}!"
