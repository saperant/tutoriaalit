"""Putkitus: monta komentoa yhdellä edestakaisella matkalla."""

from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    r = ymp.redis()
    r.flushall()
    for i in range(100):
        r.set(f"hinta:{i}", i * 10)

    # @alku putki
    putki = r.pipeline(transaction=False)
    for i in range(100):
        putki.get(f"hinta:{i}")          # jonoon, ei vielä lähetetä
    hinnat = putki.execute()             # yksi edestakainen matka
    print("tuloksia:", len(hinnat), "summa:", sum(int(h) for h in hinnat))
    # @loppu putki

    # @alku mget
    print("mget:", r.mget("hinta:1", "hinta:2", "hinta:3"))
    # @loppu mget


if __name__ == "__main__":
    aja(ajo)
