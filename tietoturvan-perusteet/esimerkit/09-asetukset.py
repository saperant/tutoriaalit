"""Väärät oletusasetukset: asetusten tarkastus ennen käynnistystä."""

from dataclasses import dataclass, field


# @alku asetukset
@dataclass(frozen=True)
class Asetukset:
    """Oletusarvot ovat turvallisia; vaarallinen valinta on tehtävä
    erikseen ja näkyvästi."""
    debug: bool = False
    tls_tarkistus: bool = True
    sallitut_alkuperat: tuple[str, ...] = ()
    yllapito_osoite: str = "127.0.0.1"
    tunnukset: dict[str, str] = field(default_factory=dict)
# @loppu asetukset


OLETUSSALASANAT = {"admin", "password", "changeme", "1234", "root"}


# @alku tarkastus
def tarkasta(a: Asetukset, tuotanto: bool) -> list[str]:
    loydot = []
    if tuotanto and a.debug:
        loydot.append("debug päällä tuotannossa (pinojäljet näkyvät)")
    if not a.tls_tarkistus:
        loydot.append("TLS-varmenteiden tarkistus pois päältä")
    if "*" in a.sallitut_alkuperat:
        loydot.append("CORS sallii kaikki alkuperät")
    if a.yllapito_osoite == "0.0.0.0":  # noqa: S104 – juuri tätä etsitään
        loydot.append("ylläpitoliittymä kuuntelee kaikkia verkkoja")
    loydot += [f"oletussalasana tunnuksella {k}"
               for k, s in a.tunnukset.items() if s in OLETUSSALASANAT]
    return loydot
# @loppu tarkastus


kehitys = Asetukset(
    debug=True, sallitut_alkuperat=("*",), tls_tarkistus=False,
    yllapito_osoite="0.0.0.0",  # noqa: S104
    tunnukset={"admin": "admin"})
for rivi in tarkasta(kehitys, tuotanto=True):
    print("VIRHE:", rivi)
print("oletusasetukset:", tarkasta(Asetukset(), tuotanto=True))
