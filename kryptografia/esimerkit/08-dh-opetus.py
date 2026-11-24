"""Opetusesimerkki: Diffie–Hellman pienillä luvuilla ja välimieshyökkäys."""


def main() -> None:
    # @alku dh
    p, g = 23, 5                  # julkiset parametrit
    a, b = 6, 15                  # Ainon ja Bertan salaiset luvut
    A = pow(g, a, p)              # Aino lähettää A = g^a mod p
    B = pow(g, b, p)              # Bertta lähettää B = g^b mod p
    print(f"verkossa näkyy: A={A}, B={B}")
    print("Aino laskee:", pow(B, a, p), " Bertta laskee:", pow(A, b, p))
    # @loppu dh

    # @alku mitm
    # Mallory vaihtaa välissä molempien julkiset arvot omiinsa.
    m = 13
    M = pow(g, m, p)
    ainon_avain = pow(M, a, p)    # Aino luulee puhuvansa Bertalle
    bertan_avain = pow(M, b, p)
    print("Mallory tuntee molemmat avaimet:",
          (ainon_avain, bertan_avain) == (pow(A, m, p), pow(B, m, p)))
    # @loppu mitm


if __name__ == "__main__":
    main()
