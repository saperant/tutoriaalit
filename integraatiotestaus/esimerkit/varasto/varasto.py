"""Varaston tallennus: rajapinta, PostgreSQL-toteutus ja muistiväärennös."""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import IntegrityError

from varasto.malli import SaldoEiRiita, SkuVarattu, Tuote, Varaus


# @alku rajapinta
class Varasto(Protocol):
    """Tallennuksen rajapinta, jota palvelu käyttää."""

    def lisaa(self, tuote: Tuote) -> None: ...
    def hae(self, sku: str) -> Tuote | None: ...
    def varaa(self, sku: str, maara: int) -> Varaus: ...
    def varaukset(self, sku: str) -> list[Varaus]: ...
# @loppu rajapinta


# @alku pg
class PgVarasto:
    """PostgreSQL-toteutus. Lähde on joko Engine (jokainen kutsu omassa
    transaktiossaan) tai valmiiksi avattu Connection, jolloin kutsu tehdään
    tallennuspisteen (SAVEPOINT) sisällä. Jälkimmäinen sallii testin
    perua kaiken lopuksi."""

    def __init__(self, lahde: Engine | Connection) -> None:
        self._lahde = lahde

    @contextmanager
    def _transaktio(self) -> Iterator[Connection]:
        if isinstance(self._lahde, Engine):
            with self._lahde.begin() as yhteys:
                yield yhteys
        else:
            with self._lahde.begin_nested():
                yield self._lahde

    def lisaa(self, tuote: Tuote) -> None:
        try:
            with self._transaktio() as y:
                y.execute(text(
                    "INSERT INTO tuotteet (sku, nimi, saldo)"
                    " VALUES (:sku, :nimi, :saldo)"),
                    {"sku": tuote.sku, "nimi": tuote.nimi,
                     "saldo": tuote.saldo})
        except IntegrityError as e:
            raise SkuVarattu(tuote.sku) from e

    def hae(self, sku: str) -> Tuote | None:
        with self._transaktio() as y:
            rivi = y.execute(text(
                "SELECT sku, nimi, saldo FROM tuotteet"
                " WHERE lower(sku) = lower(:sku)"), {"sku": sku}).first()
        return None if rivi is None else Tuote(rivi.sku, rivi.nimi,
                                               rivi.saldo)

    def varaa(self, sku: str, maara: int) -> Varaus:
        if maara <= 0:
            raise ValueError("varattava määrä on positiivinen")
        with self._transaktio() as y:
            # Ehdollinen päivitys on atominen: kaksi samanaikaista
            # varausta eivät voi molemmat nähdä vanhaa saldoa.
            rivi = y.execute(text(
                "UPDATE tuotteet SET saldo = saldo - :m"
                " WHERE lower(sku) = lower(:sku) AND saldo >= :m"
                " RETURNING sku"), {"sku": sku, "m": maara}).first()
            if rivi is None:
                raise SaldoEiRiita(sku)
            uusi = y.execute(text(
                "INSERT INTO varaukset (sku, maara) VALUES (:sku, :m)"
                " RETURNING tunnus, luotu"),
                {"sku": rivi.sku, "m": maara}).one()
        return Varaus(uusi.tunnus, rivi.sku, maara, uusi.luotu)

    def varaukset(self, sku: str) -> list[Varaus]:
        with self._transaktio() as y:
            rivit = y.execute(text(
                "SELECT tunnus, sku, maara, luotu FROM varaukset"
                " WHERE lower(sku) = lower(:sku) ORDER BY tunnus"),
                {"sku": sku}).all()
        return [Varaus(r.tunnus, r.sku, r.maara, r.luotu) for r in rivit]
# @loppu pg


# @alku muisti
class MuistiVarasto:
    """Väärennös (fake): toimiva toteutus muistissa yksikkötesteihin.

    Väärennös on hyödyllinen vain, jos se noudattaa samoja sääntöjä
    kuin oikea tallennus. Siksi sama sopimustestisarja ajetaan sekä
    tälle että PgVarastolle (luku 6)."""

    def __init__(self) -> None:
        self._tuotteet: dict[str, Tuote] = {}
        self._varaukset: list[Varaus] = []
        self._lukko = threading.Lock()

    def lisaa(self, tuote: Tuote) -> None:
        with self._lukko:
            if tuote.sku.lower() in self._tuotteet:
                raise SkuVarattu(tuote.sku)
            if tuote.saldo < 0:
                raise ValueError("saldo ei voi olla negatiivinen")
            self._tuotteet[tuote.sku.lower()] = tuote

    def hae(self, sku: str) -> Tuote | None:
        return self._tuotteet.get(sku.lower())

    def varaa(self, sku: str, maara: int) -> Varaus:
        if maara <= 0:
            raise ValueError("varattava määrä on positiivinen")
        with self._lukko:
            tuote = self._tuotteet.get(sku.lower())
            if tuote is None or tuote.saldo < maara:
                raise SaldoEiRiita(sku)
            self._tuotteet[sku.lower()] = Tuote(
                tuote.sku, tuote.nimi, tuote.saldo - maara)
            varaus = Varaus(len(self._varaukset) + 1, tuote.sku, maara,
                            datetime.now(UTC))
            self._varaukset.append(varaus)
        return varaus

    def varaukset(self, sku: str) -> list[Varaus]:
        return [v for v in self._varaukset if v.sku.lower() == sku.lower()]
# @loppu muisti
