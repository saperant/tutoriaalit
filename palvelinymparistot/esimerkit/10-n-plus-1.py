"""Virtualisointiklusterin N+1-mitoitus.

Klusterin on kestettävä yhden isäntäkoneen vika tai huoltokatko: sen
virtuaalikoneiden on mahduttava muille isännille. Tarkistus kokeilee
jokaisen isännän poistamista ja sijoittaa sen koneet muille
"suurin ensin" -periaatteella (first fit decreasing), kuten
korkean saatavuuden (HA) uudelleenkäynnistys tekisi.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Vm:
    nimi: str
    vcpu: int
    muisti_gt: int


@dataclass
class Isanta:
    nimi: str
    ytimet: int
    muisti_gt: int
    vmt: list[Vm]

    def vapaa(self, ylivaraus: float) -> tuple[float, int]:
        return (self.ytimet * ylivaraus - sum(v.vcpu for v in self.vmt),
                self.muisti_gt - sum(v.muisti_gt for v in self.vmt))


# @alku tarkistus
def kestaako_vian(isannat: list[Isanta], kaatuva: str,
                  ylivaraus: float = 4.0) -> list[str]:
    """Palauttaa virtuaalikoneet, jotka eivät mahdu muualle."""
    eloon = [Isanta(i.nimi, i.ytimet, i.muisti_gt, list(i.vmt))
             for i in isannat if i.nimi != kaatuva]
    siirrettavat = next(i.vmt for i in isannat if i.nimi == kaatuva)
    ei_mahdu = []
    for vm in sorted(siirrettavat, key=lambda v: -v.muisti_gt):
        for isanta in eloon:
            cpu, muisti = isanta.vapaa(ylivaraus)
            if vm.vcpu <= cpu and vm.muisti_gt <= muisti:
                isanta.vmt.append(vm)
                break
        else:
            ei_mahdu.append(vm.nimi)
    return ei_mahdu
# @loppu tarkistus


def klusteri() -> list[Isanta]:
    def vmt(etuliite: str, kpl: int, vcpu: int, gt: int) -> list[Vm]:
        return [Vm(f"{etuliite}{n}", vcpu, gt) for n in range(1, kpl + 1)]
    return [
        Isanta("esx1", 32, 768, vmt("web", 6, 4, 16) + vmt("db", 2, 16, 128)),
        Isanta("esx2", 32, 768, vmt("app", 8, 8, 32) + vmt("db", 1, 16, 128)),
        Isanta("esx3", 32, 768, vmt("ci", 4, 16, 64)
               + [Vm("analytiikka", 32, 448)]),
    ]


def main() -> None:
    isannat = klusteri()
    for i in isannat:
        cpu, muisti = i.vapaa(4.0)
        print(f"{i.nimi}: {len(i.vmt)} vm, vapaana {cpu:.0f} vCPU, "
              f"{muisti} Gt")
    for i in isannat:
        puuttuvat = kestaako_vian(isannat, i.nimi)
        tila = "kestää" if not puuttuvat else \
            f"EI KESTÄ, ilman paikkaa: {', '.join(puuttuvat)}"
        print(f"{i.nimi} kaatuu: {tila}")


if __name__ == "__main__":
    main()
