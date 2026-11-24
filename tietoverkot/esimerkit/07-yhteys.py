"""TCP ja UDP sovelluksen näkökulmasta.

Ilman argumentteja ajaa esittelyn silmukkaosoitteessa. Komentoina
`palvelin OSOITE PORTTI` ja `asiakas OSOITE PORTTI VIESTI [LÄHDEPORTTI]`
sitä käytetään verkkonimiavaruuksien laboratoriossa (07-kattely.sh).
"""

import socket
import sys
import threading
import time


# @alku palvelin
def palvelin(sokeetti: socket.socket) -> None:
    """Hyväksyy yhden yhteyden ja palauttaa viestin isoin kirjaimin."""
    yhteys, _ = sokeetti.accept()
    with yhteys:
        while data := yhteys.recv(1024):
            yhteys.sendall(data.upper())


def kuuntele(osoite: str, portti: int) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((osoite, portti))
    s.listen()
    return s
# @loppu palvelin


def asiakas(osoite: str, portti: int, viesti: str,
            lahdeportti: int = 0) -> str:
    with socket.create_connection((osoite, portti), timeout=2,
                                  source_address=("", lahdeportti)) as s:
        s.sendall(viesti.encode())
        return s.recv(1024).decode()
    # with-lohkon lopussa sokeetti suljetaan, jolloin lähtee FIN.


def esittely() -> None:
    # @alku virta
    with kuuntele("127.0.0.1", 0) as kuuntelija:
        portti = kuuntelija.getsockname()[1]
        saie = threading.Thread(target=palvelin, args=(kuuntelija,))
        saie.start()
        with socket.create_connection(("127.0.0.1", portti)) as s:
            for osa in ["mittaus 1;", "mittaus 2;", "mittaus 3;"]:
                s.sendall(osa.encode())
            time.sleep(0.2)
            # TCP on tavuvirta: kolme lähetystä voi saapua yhtenä.
            print("TCP luki:", s.recv(1024).decode())
        saie.join()
    # @loppu virta

    # @alku datagrammi
    vastaanotin = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    vastaanotin.bind(("127.0.0.1", 0))
    lahettaja = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for osa in ["mittaus 1;", "mittaus 2;", "mittaus 3;"]:
        lahettaja.sendto(osa.encode(), vastaanotin.getsockname())
    for _ in range(3):
        # UDP säilyttää viestirajat: yksi recvfrom, yksi datagrammi.
        data, _ = vastaanotin.recvfrom(1024)
        print("UDP luki:", data.decode())
    # @loppu datagrammi

    # @alku suljettu
    vapaa = vastaanotin.getsockname()[1]
    vastaanotin.close()
    try:
        socket.create_connection(("127.0.0.1", vapaa), timeout=1)
    except ConnectionRefusedError:
        print("TCP suljettuun porttiin: yhteys torjuttu (RST)")
    lahettaja.connect(("127.0.0.1", vapaa))
    lahettaja.send(b"onko ketaan?")
    try:
        lahettaja.recv(1024)
    except ConnectionRefusedError:
        print("UDP suljettuun porttiin: ICMP port unreachable")
    lahettaja.close()
    # @loppu suljettu


def main(argumentit: list[str]) -> None:
    if not argumentit:
        esittely()
    elif argumentit[0] == "palvelin":
        with kuuntele(argumentit[1], int(argumentit[2])) as s:
            palvelin(s)
    elif argumentit[0] == "asiakas":
        lahde = int(argumentit[4]) if len(argumentit) > 4 else 0
        print(asiakas(argumentit[1], int(argumentit[2]), argumentit[3],
                      lahde))
    else:
        sys.exit(f"tuntematon komento: {argumentit[0]}")


if __name__ == "__main__":
    main(sys.argv[1:])
