from saa.palvelu import Palvelu

LUKEMA = {"asema": "kumpula", "aika": "2026-11-25T12:00:00+02:00",
          "lampotila_c": -3.5, "kosteus": 81.0}


def test_lisays_ja_haku() -> None:
    palvelu = Palvelu()
    assert palvelu.kasittele("POST", "/lukemat", LUKEMA).tila == 201
    vastaus = palvelu.kasittele("GET", "/lukemat",
                                kysely={"asema": "kumpula"})
    assert vastaus.runko == [LUKEMA]


def test_virheellinen_lukema_hylataan() -> None:
    vastaus = Palvelu().kasittele("POST", "/lukemat",
                                  LUKEMA | {"lampotila_c": 99})
    assert vastaus.tila == 422
    assert "mittausalueen" in vastaus.runko["virhe"]


def test_tuntematon_asema() -> None:
    vastaus = Palvelu().kasittele("GET", "/asemat/ei-ole/yhteenveto")
    assert vastaus.tila == 404
