"""Kantoaaltomodulaatio: konstellaatiot ja niiden kohinansieto."""

import math

import numpy as np

rng = np.random.default_rng(4)


# @alku qam
def gray(n: int) -> int:
    return n ^ (n >> 1)


def qam(bitteja: int) -> dict[int, complex]:
    """Neliön muotoinen QAM. Puolet biteistä valitsee tason I-akselilta
    ja puolet Q-akselilta, ja tasot numeroidaan Gray-koodilla. Pisteet
    skaalataan niin, että keskimääräinen teho on 1."""
    puolet = bitteja // 2
    tasoja = 2 ** puolet
    akseli = {gray(i): 2 * i - (tasoja - 1) for i in range(tasoja)}
    pisteet = {(i << puolet) | q: complex(akseli[i], akseli[q])
               for i in akseli for q in akseli}
    teho = sum(abs(p) ** 2 for p in pisteet.values()) / len(pisteet)
    return {bitit: p / math.sqrt(teho) for bitit, p in pisteet.items()}


BPSK = {0: complex(-1, 0), 1: complex(1, 0)}
# @loppu qam


def lyhin_etaisyys(pisteet: dict[int, complex]) -> float:
    arvot = list(pisteet.values())
    return min(abs(a - b) for i, a in enumerate(arvot) for b in arvot[:i])


# @alku kanava
def bittivirhesuhde(pisteet: dict[int, complex], snr_db: float,
                    symboleja: int = 50_000) -> float:
    """Lähetetään satunnaisia symboleja, lisätään kohina ja päätetään
    vastaanottimessa lähin konstellaation piste."""
    bitit = np.array(list(pisteet))
    arvot = np.array(list(pisteet.values()))
    lahetetty = rng.integers(len(arvot), size=symboleja)
    hajonta = math.sqrt(10 ** (-snr_db / 10) / 2)
    kohina = hajonta * (rng.standard_normal(symboleja)
                        + 1j * rng.standard_normal(symboleja))
    vastaanotettu = arvot[lahetetty] + kohina
    paatos = np.argmin(np.abs(vastaanotettu[:, None] - arvot[None, :]),
                       axis=1)
    vaarat = np.bitwise_count(bitit[lahetetty] ^ bitit[paatos]).sum()
    return float(vaarat) / (symboleja * math.log2(len(arvot)))
# @loppu kanava


# @alku vertailu
modulaatiot = [("BPSK", BPSK), ("QPSK", qam(2)), ("16-QAM", qam(4)),
               ("64-QAM", qam(6))]
print("modulaatio  bit/symboli  lyhin väli   BER 10 dB   16 dB   22 dB")
for nimi, pisteet in modulaatiot:
    virheet = [bittivirhesuhde(pisteet, snr) for snr in (10, 16, 22)]
    print(f"{nimi:<11} {math.log2(len(pisteet)):>11.0f}"
          f" {lyhin_etaisyys(pisteet):>11.2f}"
          f"   {virheet[0]:>9.4f} {virheet[1]:>7.4f} {virheet[2]:>7.4f}")
# @loppu vertailu
