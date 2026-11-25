"""Tarkistimen yksikkötestit."""

import pytest

from devkontti import huomiot, lue_jsonc, tarkista


def test_kommentit_ja_ylimaarainen_pilkku() -> None:
    teksti = """
    // rivikommentti
    {
      "name": "a", /* lohko */
      "image": "kuva:1 // ei kommentti",
      "forwardPorts": [8000, 8001,],
    }
    """
    assert lue_jsonc(teksti) == {
        "name": "a",
        "image": "kuva:1 // ei kommentti",
        "forwardPorts": [8000, 8001],
    }


def test_lainausmerkki_merkkijonossa() -> None:
    assert lue_jsonc(r'{"name": "a \" // b"}') == {"name": 'a " // b'}


def test_ylin_taso_on_olio() -> None:
    with pytest.raises(ValueError, match="olio"):
        lue_jsonc("[1, 2]")


@pytest.mark.parametrize(("asetukset", "virhe"), [
    ({}, "kontin lähde puuttuu"),
    ({"image": "a:1", "build": {"dockerfile": "D"}}, "vain yksi lähde"),
    ({"build": {}}, "build.dockerfile: puuttuu"),
    ({"image": "a:1", "init": "true"}, "init: pitää olla totuusarvo"),
    ({"image": "a:1", "appPort": True}, "appPort: pitää olla"),
    ({"dockerComposeFile": "c.yml"}, "service: pakollinen"),
    ({"image": "a:1", "mounts": ["${home}"]}, "tuntematon muuttuja"),
])
def test_virheet(asetukset: dict[str, object], virhe: str) -> None:
    assert any(virhe in rivi for rivi in tarkista(asetukset))


def test_ymparistomuuttujat_kelpaavat() -> None:
    asetukset = {"image": "a:1",
                 "remoteEnv": {"A": "${localEnv:A}",
                               "POLKU": "${containerEnv:PATH}:/x"}}
    assert tarkista(asetukset) == []


def test_huomiot() -> None:
    assert huomiot({"image": "a:1.2"}) == []
    assert huomiot({"image": "a", "runArgs": ["--privileged"]}) == [
        "ajetaan etuoikeutettuna", "kuvan versio on lukitsematta"]
