"""Samanaikaiset varaukset oikeaa PostgreSQLia vasten."""

from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import Engine

from varasto.malli import SaldoEiRiita, Tuote
from varasto.varasto import PgVarasto


# @alku samanaikaisuus
def test_samanaikaiset_varaukset_eivat_ylivaraa(kone: Engine) -> None:
    # Testi tarvitsee oikeat, toisistaan riippumattomat transaktiot,
    # joten se kirjoittaa pysyvästi. Satunnainen SKU pitää sen erillään
    # muista testeistä ja aiemmista ajoista.
    sku = f"TESTI-{uuid.uuid4().hex[:8]}"
    varasto = PgVarasto(kone)
    varasto.lisaa(Tuote(sku, "Kilpailtu", 10))

    def yrita(_: int) -> bool:
        try:
            varasto.varaa(sku, 3)
            return True
        except SaldoEiRiita:
            return False

    with ThreadPoolExecutor(max_workers=8) as poolit:
        onnistuneet = sum(poolit.map(yrita, range(8)))

    assert onnistuneet == 3          # 3 * 3 = 9 <= 10 < 12
    tuote = varasto.hae(sku)
    assert tuote is not None and tuote.saldo == 1
# @loppu samanaikaisuus
