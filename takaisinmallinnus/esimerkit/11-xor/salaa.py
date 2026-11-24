"""Tuottaa C-otsakkeen, jossa merkkijonot ovat XOR-salattuina.

Käyttö: python3 salaa.py > salaisuudet.h

Avain vaihtuu merkeittäin: k[i] = (ALKU + i * ASKEL) mod 256. Salattuun
jonoon kuuluu myös loppunolla, joten purkaja tietää, missä jono loppuu.
"""

ALKU = 0x5C
ASKEL = 0x1D

JONOT = {
    "PALVELIN": "paivitys.example.invalid",
    "POLKU": "/api/v2/laitteet/rekisteroi",
    "OTSAKE": "X-Laite-Avain: 3f9a-77c1",
}


def salaa(teksti: str) -> bytes:
    data = teksti.encode("ascii") + b"\0"
    return bytes(b ^ ((ALKU + i * ASKEL) & 0xFF) for i, b in enumerate(data))


def main() -> None:
    print("// Tuotettu: python3 salaa.py > salaisuudet.h. Älä muokkaa.")
    for nimi, teksti in JONOT.items():
        tavut = salaa(teksti)
        rivit = [", ".join(f"0x{b:02x}" for b in tavut[i:i + 10])
                 for i in range(0, len(tavut), 10)]
        print(f"static const unsigned char {nimi}[{len(tavut)}] = {{")
        for rivi in rivit:
            print(f"    {rivi},")
        print("};")


if __name__ == "__main__":
    main()
