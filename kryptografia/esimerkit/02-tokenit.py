"""Tunnisteiden ja avainten luonti secrets-moduulilla."""

import math
import secrets
import uuid


def main() -> None:
    # @alku tokenit
    istunto = secrets.token_urlsafe(32)       # 32 tavua = 256 bittiä
    palautus = secrets.token_hex(16)          # 128 bittiä heksana
    avain = secrets.token_bytes(32)           # raakatavut avaimeksi
    tunnus = uuid.uuid4()                     # 122 satunnaista bittiä
    pin = f"{secrets.randbelow(10**6):06d}"   # tasajakauma 0..999999
    # @loppu tokenit
    print("istuntotunniste:", len(istunto), "merkkiä")
    print("palautuslinkin tunniste:", len(palautus), "merkkiä")
    print("avain:", len(avain), "tavua")
    print("UUID-versio:", tunnus.version)
    print("PIN:", len(pin), "numeroa, entropia",
          f"{math.log2(10**6):.1f} bittiä")


if __name__ == "__main__":
    main()
