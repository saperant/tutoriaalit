"""ML-KEM (FIPS 203) ja hybridi avaintenvaihto X25519:n kanssa."""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import mlkem
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def main() -> None:
    # @alku kem
    # Vastaanottaja luo avainparin ja julkaisee julkisen avaimen.
    salainen = mlkem.MLKEM768PrivateKey.generate()
    julkinen = salainen.public_key()
    # Lähettäjä kapseloi: saa jaetun salaisuuden ja kapselin lähetettäväksi.
    jaettu_l, kapseli = julkinen.encapsulate()
    # Vastaanottaja avaa kapselin samaksi salaisuudeksi.
    jaettu_v = salainen.decapsulate(kapseli)
    # @loppu kem
    print("sama salaisuus:", jaettu_l == jaettu_v)
    print(f"julkinen avain {len(julkinen.public_bytes_raw())} tavua, "
          f"kapseli {len(kapseli)} tavua, salaisuus {len(jaettu_l)} tavua")

    # @alku hybridi
    # Hybridi: avain on turvassa, jos edes toinen menetelmä kestää.
    x_a, x_b = X25519PrivateKey.generate(), X25519PrivateKey.generate()
    klassinen = x_a.exchange(x_b.public_key())
    avain = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                 info=b"hybridi X25519MLKEM768").derive(jaettu_l + klassinen)
    # @loppu hybridi
    print("hybridiavain:", len(avain), "tavua")


if __name__ == "__main__":
    main()
