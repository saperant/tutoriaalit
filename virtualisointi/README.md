# Virtualisointi

Tiivis suomenkielinen tutoriaali virtuaalikoneista ja konteista
laitteistosta ytimeen: hypervisorit ja virtualisoinnin teoria,
VT-x ja EPT, KVM ja QEMU, I/O-virtualisointi, nimiavaruudet, cgroups,
kyvyt ja seccomp, eristyksen tasot sekä vedokset ja siirto. Valmiit
dokumentit:
[virtualisointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/virtualisointi.pdf)
ja pikaopas
[virtualisointi-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/virtualisointi-pikaopas.pdf).

## Sisältö

1. Johdanto – virtuaalikone ja kontti, historia, ensimmäinen
   virtuaalikone omalla ytimellä
2. Hypervisorit ja virtualisoinnin teoria – tyypit, Popekin ja
   Goldbergin ehdot, lelusuoritin, binäärikäännös, paravirtualisointi
3. Laitteistotuki – VMX, VMCS, VM exitin syyt, varjotaulut ja EPT,
   kaksiulotteinen sivutaulukävely, muistin ylivaraus
4. KVM ja QEMU – pienin hypervisor KVM-rajapinnalla, vCPU säikeenä,
   QMP, qcow2
5. I/O-virtualisointi – emuloitu laite, virtqueue, vhost, IOMMU ja
   VFIO, SR-IOV
6. Kontit: nimiavaruudet ja minikontti – unshare, nsenter, overlay,
   oma init
7. Kontit: cgroups, kyvyt ja seccomp
8. Eristyksen tasot – gVisor, mikro-VM:t, luottamuksellinen laskenta
9. Tilannevedokset ja siirto – esikopiointi, jälkikopiointi, siirto
   QMP:llä
10. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

`make testaa` tarkistaa rakenteen ja ajaa kaikki esimerkit (C: GCC ja
Clang sanitoijineen; Bash: ShellCheck; Python: ruff ja mypy --strict).
Virtuaalikoneet ajetaan QEMU:lla ohjelmallisella TCG-käännöksellä,
joten laitteistotukea ei tarvita. Nimiavaruuksia ja kyvyjä käyttävät
esimerkit vaativat pääkäyttäjän oikeudet ja käynnistävät itsensä
tarvittaessa `sudo -n`:llä.

`esimerkit/Makefile` ajaa valinnaiset esimerkit: KVM-rajapinnan
esimerkki ajetaan, jos `/dev/kvm` on käytettävissä, ja cgroup-esimerkki,
jos cgroup-tiedostojärjestelmään voi kirjoittaa. Muuten ne ohitetaan
ilmoituksella. Kehityskontissa KVM-esimerkin saa ajoon antamalla
kontille laitteen (`--device /dev/kvm`); cgroup-esimerkki ajetaan
isäntäkoneella pääkäyttäjänä.

Kehityskontissa (`.devcontainer/virtualisointi`) on QEMU ja muut
työkalut sekä oikeudet `SYS_ADMIN`, rajoittamaton seccomp ja
AppArmor, koska kontin sisällä luodaan nimiavaruuksia ja liitoksia.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.
