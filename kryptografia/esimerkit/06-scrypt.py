"""scrypt vakiokirjastosta: RFC 7914:n testivektori."""

import hashlib

ODOTETTU = bytes.fromhex(
    "fdbabe1c9d3472007856e7190d01e9fe7c6ad7cbc8237830e77376634b373162"
    "2eaf30d92e22a3886ff109279d9830dac727afb94a83ee6d8360cbdfa2cc0640")


def main() -> None:
    # @alku scrypt
    avain = hashlib.scrypt(b"password", salt=b"NaCl", n=1024, r=8, p=16,
                           dklen=64)
    # @loppu scrypt
    print("RFC 7914 täsmää:", avain == ODOTETTU)


if __name__ == "__main__":
    main()
