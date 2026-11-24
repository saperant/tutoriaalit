"""Tiivistefunktiot: kiinteän mittainen sormenjälki mistä tahansa datasta."""

import hashlib


def eroavat_bitit(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b, strict=True))


def main() -> None:
    # @alku tiivisteet
    for nimi in ("sha256", "sha3_256", "blake2s"):
        tiiviste = hashlib.new(nimi, b"abc").hexdigest()
        print(f"{nimi:9} {tiiviste[:32]}...")
    # @loppu tiivisteet

    # @alku lumivyory
    a = hashlib.sha256(b"tilisiirto 100 EUR").digest()
    b = hashlib.sha256(b"tilisiirto 101 EUR").digest()
    print(f"yhden merkin muutos: {eroavat_bitit(a, b)}/256 bittiä eroaa")
    # @loppu lumivyory

    # @alku tiedosto
    with open(__file__, "rb") as f:
        sormenjalki = hashlib.file_digest(f, "sha256").hexdigest()
    print("tiedoston tiiviste:", len(sormenjalki), "heksamerkkiä")
    # @loppu tiedosto


if __name__ == "__main__":
    main()
