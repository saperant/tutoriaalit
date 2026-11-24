"""SRAM-PUF ja sumea poimija (fuzzy extractor).

SRAM-solun käynnistysarvo riippuu valmistusvaihtelusta: sama laite
antaa lähes saman bittijonon joka käynnistyksellä, eri laitteet eri
jonot. Lukema on kuitenkin kohinainen, joten avainta ei voi tiivistää
siitä suoraan. Sumea poimija tallentaa julkisen apudatan, jonka avulla
kohinainen lukema korjataan samaksi avaimeksi.

Tässä virheenkorjaus on 7-kertainen toistokoodi. Se on helppo
ymmärtää, mutta todelliset poimijat käyttävät tehokkaampia koodeja
(BCH, Reed–Muller), koska toistokoodin apudata vuotaa entropiaa.
"""

import hashlib
import random

BITTEJA = 128     # avaimen bitit
TOISTO = 7        # jokainen bitti seitsemään soluun


# @alku puf
class SramPuf:
    """Solun luonne syntyy valmistuksessa; lukema on kohinainen."""

    def __init__(self, valmistus: random.Random, solut: int) -> None:
        self.viite = [valmistus.getrandbits(1) for _ in range(solut)]
        # Useimmat solut ovat vakaita, osa epävakaita.
        self.virhe = [0.02 if valmistus.random() < 0.9 else 0.25
                      for _ in range(solut)]

    def lue(self, kohina: random.Random) -> list[int]:
        return [b ^ (kohina.random() < p)
                for b, p in zip(self.viite, self.virhe, strict=True)]
# @loppu puf


# @alku poimija
def rekisteroi(lukema: list[int],
               salaisuus: list[int]) -> list[int]:
    """Apudata = lukema XOR koodattu salaisuus. Tallennetaan julkisena."""
    koodi = [b for b in salaisuus for _ in range(TOISTO)]
    return [a ^ b for a, b in zip(lukema, koodi, strict=True)]


def palauta(lukema: list[int], apudata: list[int]) -> list[int]:
    """Enemmistöpäätös jokaisesta seitsemän bitin ryhmästä."""
    kohinainen = [a ^ b for a, b in zip(lukema, apudata, strict=True)]
    return [int(sum(kohinainen[i:i + TOISTO]) > TOISTO // 2)
            for i in range(0, len(kohinainen), TOISTO)]


def avain(bitit: list[int]) -> bytes:
    return hashlib.sha256(bytes(bitit)).digest()
# @loppu poimija


# @alku vakaat
def vakaat_solut(puf: SramPuf, kohina: random.Random, maara: int,
                 kertoja: int = 20) -> list[int]:
    """Rekisteröinnissä luetaan monta kertaa ja valitaan solut, jotka
    eivät vaihtaneet arvoaan. Indeksit tallennetaan apudataan."""
    lukemat = [puf.lue(kohina) for _ in range(kertoja)]
    vakaat = [i for i in range(len(puf.viite))
              if len({luku[i] for luku in lukemat}) == 1]
    return vakaat[:maara]
# @loppu vakaat


def tehdas(puf: SramPuf, kohina: random.Random,
           solut: list[int]) -> tuple[list[int], bytes]:
    """Rekisteröinti tehtaalla: apudata (julkinen) ja oikea avain."""
    salaisuus = [random.Random(4).getrandbits(1) for _ in range(BITTEJA)]
    lukema = puf.lue(kohina)
    apudata = rekisteroi([lukema[i] for i in solut], salaisuus)
    return apudata, avain(salaisuus)


def kenttakoe(puf: SramPuf, kohina: random.Random, solut: list[int],
              apudata: list[int], oikea: bytes, kertoja: int) -> int:
    """Monellako käynnistyksellä avain palautuu oikein."""
    oikein = 0
    for _ in range(kertoja):
        lukema = puf.lue(kohina)
        oikein += avain(palauta([lukema[i] for i in solut],
                                apudata)) == oikea
    return oikein


def main() -> None:
    tarve = BITTEJA * TOISTO
    laite = SramPuf(random.Random(1), 2 * tarve)
    toinen = SramPuf(random.Random(2), 2 * tarve)
    kohina = random.Random(3)

    a, b = laite.lue(kohina), laite.lue(kohina)
    virheet = sum(x != y for x, y in zip(a, b, strict=True))
    osuus = f"{100 * virheet / len(a):.1f}".replace(".", ",")
    print(f"Bittivirheitä kahden lukeman välillä: {osuus} %")
    print("Suora lukema sama kahdesti:", a == b)

    for nimi, solut in [("kaikki solut", list(range(tarve))),
                        ("vakaat solut",
                         vakaat_solut(laite, kohina, tarve))]:
        apudata, oikea = tehdas(laite, kohina, solut)
        oikein = kenttakoe(laite, kohina, solut, apudata, oikea, 1000)
        vieras = kenttakoe(toinen, kohina, solut, apudata, oikea, 1000)
        print(f"Toistokoodi, {nimi}: {oikein}/1000 oikein, "
              f"toinen laite {vieras}/1000")
    ero = sum(x != y for x, y in zip(laite.viite, toinen.viite,
                                      strict=True))
    print(f"Eri laitteiden ero: {100 * ero / len(laite.viite):.0f} % "
          "biteistä")


if __name__ == "__main__":
    main()
