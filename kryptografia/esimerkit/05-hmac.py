"""HMAC: viestin aitous jaetulla avaimella, esimerkkinä webhook-kutsu."""

import hashlib
import hmac


# @alku webhook
def allekirjoita(avain: bytes, runko: bytes) -> str:
    return hmac.new(avain, runko, hashlib.sha256).hexdigest()


def tarkista(avain: bytes, runko: bytes, otsake: str) -> bool:
    odotettu = allekirjoita(avain, runko)
    return hmac.compare_digest(odotettu, otsake)   # vakioaikainen
# @loppu webhook


def main() -> None:
    # RFC 4231, testitapaus 2.
    tunniste = hmac.new(b"Jefe", b"what do ya want for nothing?",
                        hashlib.sha256).hexdigest()
    print("RFC 4231 täsmää:", tunniste.startswith("5bdcc146bf60754e6a04"))

    avain = b"jaettu-webhook-salaisuus"
    runko = b'{"tapahtuma": "maksu", "summa": 100}'
    otsake = allekirjoita(avain, runko)
    print("aito kutsu:", tarkista(avain, runko, otsake))
    print("muutettu runko:",
          tarkista(avain, runko.replace(b"100", b"900"), otsake))


if __name__ == "__main__":
    main()
