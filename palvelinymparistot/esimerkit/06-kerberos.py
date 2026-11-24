"""Kerberoksen periaate: liput, aikaleimat ja kellojen tahdistus.

Käyttäjä todistaa henkilöllisyytensä kerran avainjakelukeskukselle
(KDC) ja saa lipun (TGT). Sillä hän hakee palvelukohtaisia lippuja,
eikä salasana kulje verkossa. Palvelu tarkistaa lipun aitouden omalla
avaimellaan ja todentimen aikaleiman: jos kellot eroavat yli viisi
minuuttia, todennus epäonnistuu. Siksi toimialueen koneiden kellot
tahdistetaan (NTP). Esimerkissä salaus on korvattu HMAC-allekirjoituksella;
oikea Kerberos myös salaa liput.
"""

import hashlib
import hmac
import json
from dataclasses import dataclass, field

SALLITTU_POIKKEAMA = 300   # sekuntia (oletus Kerberoksessa ja AD:ssa)


def sinetoi(avain: bytes, sisalto: dict[str, object]) -> str:
    data = json.dumps(sisalto, sort_keys=True)
    tunniste = hmac.new(avain, data.encode(), hashlib.sha256).hexdigest()
    return data + "|" + tunniste


def avaa(avain: bytes, sinetoity: str) -> dict[str, object]:
    data, tunniste = sinetoity.rsplit("|", 1)
    odotettu = hmac.new(avain, data.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(tunniste, odotettu):
        raise PermissionError("lippu on väärennetty")
    tulos: dict[str, object] = json.loads(data)
    return tulos


# @alku palvelu
@dataclass
class Palvelu:
    nimi: str
    avain: bytes                      # jaettu vain KDC:n kanssa (keytab)
    nahdyt: set[str] = field(default_factory=set)  # toistovälimuisti

    def todenna(self, lippu: str, todentimen_aika: int,
                kello: int) -> str:
        sisalto = avaa(self.avain, lippu)
        aika = todentimen_aika
        if kello > int(str(sisalto["voimassa_asti"])):
            raise PermissionError("lippu on vanhentunut")
        if abs(kello - aika) > SALLITTU_POIKKEAMA:
            raise PermissionError("kellot eroavat liikaa (clock skew)")
        avainpari = f"{sisalto['kayttaja']}@{aika}"
        if avainpari in self.nahdyt:
            raise PermissionError("todennin toistettu (replay)")
        self.nahdyt.add(avainpari)
        return f"{sisalto['kayttaja']} sisään palveluun {self.nimi}"
# @loppu palvelu


def kdc_palvelulippu(palvelu: Palvelu, kayttaja: str, kello: int,
                     kesto: int = 10 * 3600) -> str:
    return sinetoi(palvelu.avain, {"kayttaja": kayttaja,
                                   "palvelu": palvelu.nimi,
                                   "voimassa_asti": kello + kesto})


def main() -> None:
    # @alku kokeet
    tiedostot = Palvelu("cifs/tiedostot.esimerkki.fi", b"keytab-avain")
    nyt = 1_764_000_000
    lippu = kdc_palvelulippu(tiedostot, "aino@ESIMERKKI.FI", nyt)
    kokeet = [
        ("normaali", lippu, nyt + 5, nyt + 6),
        ("sama todennin uudelleen", lippu, nyt + 5, nyt + 7),
        ("asiakkaan kello 7 min jäljessä", lippu, nyt - 420, nyt + 10),
        ("11 tunnin päästä", lippu, nyt + 39_600, nyt + 39_600),
        ("väärennetty lippu", lippu.replace("aino", "olli"), nyt + 20,
         nyt + 20),
    ]
    for nimi, lp, aika, kello in kokeet:
        try:
            print(f"{nimi}: {tiedostot.todenna(lp, aika, kello)}")
        except PermissionError as virhe:
            print(f"{nimi}: HYLÄTTY, {virhe}")
    # @loppu kokeet


if __name__ == "__main__":
    main()
