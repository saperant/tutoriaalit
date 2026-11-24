"""Cortex-M-vektoritaulun tulkinta.

Käyttö: python3 vektorit.py KUVA KANTA TAULU [MÄÄRÄ]

KUVA on ladattu osoitteeseen KANTA, ja taulu alkaa osoitteesta TAULU.
Sana 0 on pinon alkuarvo, sanat 1..15 järjestelmäpoikkeukset ja siitä
eteenpäin ulkoiset keskeytykset (IRQ0 = sana 16).
"""
import sys

from kuva import Kuva

NIMET = ["pino (MSP)", "Reset", "NMI", "HardFault", "MemManage",
         "BusFault", "UsageFault", "-", "-", "-", "-", "SVCall",
         "DebugMon", "-", "PendSV", "SysTick"]


def main() -> None:
    kanta, taulu = int(sys.argv[2], 0), int(sys.argv[3], 0)
    kuva = Kuva.lue(sys.argv[1], kanta)
    maara = int(sys.argv[4]) if len(sys.argv) > 4 else 16
    kasittelijat: dict[int, list[str]] = {}
    for i in range(maara):
        arvo = kuva.u32(taulu + 4 * i)
        nimi = NIMET[i] if i < 16 else f"IRQ{i - 16}"
        if i == 0:
            print(f"{i:2} {nimi:<11} {arvo:#010x}")
            continue
        if arvo == 0:
            continue
        huomio = "" if arvo & 1 else "  VIRHE: Thumb-bitti puuttuu"
        print(f"{i:2} {nimi:<11} {arvo:#010x}{huomio}")
        kasittelijat.setdefault(arvo & ~1, []).append(nimi)
    print("eri käsittelijöitä:", len(kasittelijat))
    for osoite, nimet in sorted(kasittelijat.items()):
        if len(nimet) > 2:
            print(f"  {osoite:#x}: {len(nimet)} vektoria "
                  "(oletuskäsittelijä)")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
