from __future__ import annotations

import pytest
from foo import add


def test_main():
    assert add(3.3, 4) == 7.3
