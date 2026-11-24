"""Kuluttajan sopimus: hintapalvelun vastaus täyttää skeeman."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from testcontainers.core.container import DockerContainer

from testiapu import kontit
from testiapu.kontit import osoite

SKEEMA = json.loads(
    (Path(__file__).parent.parent / "sopimukset" / "hinta-v1.schema.json")
    .read_text("utf-8"))


def hae(palvelu: DockerContainer, sku: str) -> Any:
    with urllib.request.urlopen(
            f"{osoite(palvelu, 8080)}/hinnat/{sku}", timeout=5) as v:
        return json.loads(v.read())


# @alku sopimustesti
@pytest.mark.parametrize("sku", ["ABC-1", "XYZ-9", "LMN-5"])
def test_tuottaja_tayttaa_sopimuksen(hintapalvelu: DockerContainer,
                                    sku: str) -> None:
    jsonschema.validate(hae(hintapalvelu, sku), SKEEMA)


def test_rikkova_muutos_havaitaan(apukuva: str) -> None:
    """Rajapinnan versio 2 nimeää kentän uudelleen: sopimus rikkoutuu."""
    with kontit.hintapalvelu(rajapinta="2") as uusi:
        with pytest.raises(jsonschema.ValidationError,
                           match="'hinta_snt' is a required property"):
            jsonschema.validate(hae(uusi, "ABC-1"), SKEEMA)
# @loppu sopimustesti
