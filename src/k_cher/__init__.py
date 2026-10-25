"""Навчальний пакет для практичної з GitHub Actions."""

__version__ = "1.2.0"


def hello(name: str = "world") -> str:
    return f"Hello, {name}!"
