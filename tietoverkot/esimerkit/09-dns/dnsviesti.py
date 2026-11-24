"""DNS-viestien koodaus ja purku (RFC 1035), myös nimien pakkaus."""

import ipaddress
import struct
from dataclasses import dataclass

TYYPIT = {"A": 1, "NS": 2, "CNAME": 5, "PTR": 12, "MX": 15, "TXT": 16,
          "AAAA": 28, "SRV": 33}
TYYPIN_NIMI = {v: k for k, v in TYYPIT.items()}
VASTAUSKOODIT = {0: "NOERROR", 2: "SERVFAIL", 3: "NXDOMAIN", 5: "REFUSED"}


@dataclass(frozen=True)
class Tietue:
    nimi: str
    tyyppi: str
    ttl: int
    arvo: str


@dataclass(frozen=True)
class Vastaus:
    tunniste: int
    koodi: str
    vastaukset: list[Tietue]


# @alku koodaus
def koodaa_nimi(nimi: str) -> bytes:
    """www.esim.fi -> 3www4esim2fi0: osat pituustavun kanssa."""
    tulos = b""
    for osa in nimi.rstrip(".").split("."):
        tavut = osa.encode("ascii")
        if not 0 < len(tavut) < 64:
            raise ValueError(f"virheellinen nimen osa: {osa!r}")
        tulos += bytes([len(tavut)]) + tavut
    return tulos + b"\x00"


def kysely(nimi: str, tyyppi: str, tunniste: int,
           rekursio: bool = True) -> bytes:
    liput = 0x0100 if rekursio else 0       # RD: rekursio toivottu
    otsake = struct.pack("!HHHHHH", tunniste, liput, 1, 0, 0, 0)
    return otsake + koodaa_nimi(nimi) + struct.pack(
        "!HH", TYYPIT[tyyppi], 1)            # luokka IN
# @loppu koodaus


# @alku purku
def pura_nimi(data: bytes, kohta: int) -> tuple[str, int]:
    """Palauttaa nimen ja kohdan sen jälkeen. Pakattu nimi on osoitin
    (kaksi ylintä bittiä 11) aiemmin viestissä olevaan nimeen."""
    osat: list[str] = []
    paluu = -1
    hyppyja = 0
    while True:
        pituus = data[kohta]
        if pituus & 0xC0 == 0xC0:
            if paluu < 0:
                paluu = kohta + 2
            kohta = struct.unpack("!H", data[kohta:kohta + 2])[0] & 0x3FFF
            hyppyja += 1
            if hyppyja > 20:
                raise ValueError("osoitinsilmukka")
            continue
        if pituus == 0:
            kohta += 1
            break
        osat.append(data[kohta + 1:kohta + 1 + pituus].decode("ascii"))
        kohta += 1 + pituus
    return ".".join(osat), (paluu if paluu >= 0 else kohta)


def pura_arvo(data: bytes, alku: int, pituus: int, tyyppi: int) -> str:
    rdata = data[alku:alku + pituus]
    if tyyppi == TYYPIT["A"]:
        return str(ipaddress.IPv4Address(rdata))
    if tyyppi == TYYPIT["AAAA"]:
        return str(ipaddress.IPv6Address(rdata))
    if tyyppi in (TYYPIT["CNAME"], TYYPIT["NS"], TYYPIT["PTR"]):
        return pura_nimi(data, alku)[0]
    if tyyppi == TYYPIT["MX"]:
        (prioriteetti,) = struct.unpack("!H", rdata[:2])
        return f"{prioriteetti} {pura_nimi(data, alku + 2)[0]}"
    if tyyppi == TYYPIT["SRV"]:
        prio, paino, portti = struct.unpack("!HHH", rdata[:6])
        return f"{prio} {paino} {portti} {pura_nimi(data, alku + 6)[0]}"
    if tyyppi == TYYPIT["TXT"]:
        return rdata[1:1 + rdata[0]].decode()
    return rdata.hex()


def pura(data: bytes) -> Vastaus:
    tunniste, liput, kysymyksia, vastauksia = struct.unpack(
        "!HHHH", data[:8])
    kohta = 12
    for _ in range(kysymyksia):
        _, kohta = pura_nimi(data, kohta)
        kohta += 4
    tietueet = []
    for _ in range(vastauksia):
        nimi, kohta = pura_nimi(data, kohta)
        tyyppi, _, ttl, pituus = struct.unpack(
            "!HHIH", data[kohta:kohta + 10])
        kohta += 10
        tietueet.append(Tietue(nimi, TYYPIN_NIMI.get(tyyppi, str(tyyppi)),
                               ttl, pura_arvo(data, kohta, pituus, tyyppi)))
        kohta += pituus
    koodi = VASTAUSKOODIT.get(liput & 0x0F, str(liput & 0x0F))
    return Vastaus(tunniste, koodi, tietueet)
# @loppu purku


# @alku vastaus
def vastaus(kysely_data: bytes, tietueet: list[tuple[str, int, bytes]],
            ttl: int) -> bytes:
    """Rakentaa vastauksen kyselyyn. Tietueen nimi viittaa pakattuna
    kysymyksen nimeen (kohta 12): osoitin 0xC00C."""
    tunniste, liput = struct.unpack("!HH", kysely_data[:4])
    _, loppu = pura_nimi(kysely_data, 12)
    kysymys = kysely_data[12:loppu + 4]
    otsake = struct.pack("!HHHHHH", tunniste, 0x8180 | (liput & 0x0100),
                         1, len(tietueet), 0, 0)
    osat = b""
    for _, tyyppi, rdata in tietueet:
        osat += struct.pack("!HHHIH", 0xC00C, tyyppi, 1, ttl, len(rdata))
        osat += rdata
    return otsake + kysymys + osat
# @loppu vastaus
