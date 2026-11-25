"""Klassinen tyyli: oikeat yhteistyöoliot, tarkistetaan lopputila."""

import pytest
from kassa import Kassa, MaksuEpaonnistui
from muisti import MuistiMaksut, MuistiVarasto

HINNAT = {"kahvi": 549, "tee": 189}


# @alku tila
def test_osto_vahentaa_saldoa_ja_veloittaa_summan() -> None:
    varasto = MuistiVarasto({"kahvi": 5, "tee": 1})
    maksut = MuistiMaksut()
    kassa = Kassa(varasto, maksut, HINNAT)

    kuitti = kassa.osta({"kahvi": 2, "tee": 1}, kortti="1234")

    assert kuitti.summa == 1287
    assert maksut.veloitettu == 1287
    assert varasto.saldo("kahvi") == 3
    assert varasto.saldo("tee") == 0


def test_epaonnistunut_maksu_palauttaa_tuotteet_varastoon() -> None:
    varasto = MuistiVarasto({"kahvi": 5, "tee": 1})
    kassa = Kassa(varasto, MuistiMaksut(suljetut={"9999"}), HINNAT)

    with pytest.raises(MaksuEpaonnistui):
        kassa.osta({"kahvi": 2}, kortti="9999")

    assert varasto.saldo("kahvi") == 5
# @loppu tila
