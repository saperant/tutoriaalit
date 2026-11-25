"""Mockistinen tyyli: yhteistyöoliot korvataan, tarkistetaan kutsut."""

from unittest.mock import Mock, call

import pytest
from kassa import Kassa, Maksut, MaksuEpaonnistui, Varasto

HINNAT = {"kahvi": 549, "tee": 189}


# @alku vuorovaikutus
def test_osto_varaa_tuotteet_ja_veloittaa_summan() -> None:
    varasto = Mock(spec=Varasto)
    maksut = Mock(spec=Maksut)
    maksut.veloita.return_value = True
    kassa = Kassa(varasto, maksut, HINNAT)

    kassa.osta({"kahvi": 2, "tee": 1}, kortti="1234")

    varasto.varaa.assert_has_calls([call("kahvi", 2), call("tee", 1)])
    maksut.veloita.assert_called_once_with("1234", 1287)


def test_epaonnistunut_maksu_vapauttaa_varaukset() -> None:
    varasto = Mock(spec=Varasto)
    maksut = Mock(spec=Maksut)
    maksut.veloita.return_value = False
    kassa = Kassa(varasto, maksut, HINNAT)

    with pytest.raises(MaksuEpaonnistui):
        kassa.osta({"kahvi": 2}, kortti="9999")

    varasto.vapauta.assert_called_once_with("kahvi", 2)
# @loppu vuorovaikutus
