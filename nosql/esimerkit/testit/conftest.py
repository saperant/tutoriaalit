"""Yhteinen tietokantaympäristö kaikille testeille (yksi istunto)."""

from collections.abc import Iterator

import pytest

from nosql.kontit import Ymparisto


@pytest.fixture(scope="session")
def ymp() -> Iterator[Ymparisto]:
    with Ymparisto() as ymparisto:
        yield ymparisto
