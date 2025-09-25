from __future__ import annotations

import os

from dotenv import load_dotenv


def add(a: int, b: float):
    return a + b


def main():
    load_dotenv()
    print(f"{os.getenv('HELLO')}, world!")
