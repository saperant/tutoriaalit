# Johdanto {.runko-johdanto}

Lähes jokainen palvelinohjelma ajetaan nykyään virtuaalikoneessa,
kontissa tai molemmissa. Pilvipalvelun "palvelin" on virtuaalikone,
jonka hypervisor jakaa fyysisen koneen kymmenille asiakkaille.
Kubernetes-klusterin "sovellus" on kontti, eli tavallinen
Linux-prosessi, jolle ydin näyttää oman näkymän järjestelmästä.
Kehittäjän kehityskontti, CI-ajon eristetty ympäristö ja
selainhiekkalaatikko käyttävät samoja mekanismeja.

Tämä tutoriaali selittää, miten virtualisointi toimii laitteistosta
ytimeen asti, ja näyttää mekanismit testattuina esimerkkeinä: oma
pieni käyttöjärjestelmän ydin ajetaan QEMU:lla, virtualisoinnin
perusongelma toistetaan lelusuorittimella, virtio-jono toteutetaan
määrittelyn rakenteilla ja kontti kootaan ilman konttityökaluja
nimiavaruuksista, overlay-tiedostojärjestelmästä ja itse kirjoitetusta
init-prosessista.

## Virtuaalikone ja kontti

**Virtuaalikone** (virtual machine, VM) on ohjelmallisesti tuotettu
kokonainen tietokone: suoritin, muisti, laitteet ja oma
käyttöjärjestelmän ydin. **Hypervisor** eli virtuaalikonemonitori
(VMM) jakaa fyysisen koneen virtuaalikoneille ja pitää ne erillään.
Vieraan ytimen näkökulmasta kone on aito: se käynnistyy, käsittelee
keskeytyksiä ja ohjaa laitteita.

**Kontti** (container) on joukko prosesseja, jotka jakavat isännän
ytimen mutta näkevät oman tiedostojärjestelmänsä, prosessilistansa,
verkkonsa ja konenimensä. Rajat tulevat ytimen mekanismeista:
nimiavaruuksista (mitä prosessi näkee), cgroupeista (paljonko se saa
käyttää), kyvyistä ja seccompista (mitä se saa tehdä).

| | Virtuaalikone | Kontti |
|---|---|---|
| Eristyksen raja | laitteisto (VT-x, EPT, IOMMU) | ytimen tietorakenteet |
| Ydin | oma | isännän |
| Käynnistys | sekunteja (mikro-VM: ~100 ms) | millisekunteja |
| Muistin yleiskulu | kymmeniä megatavuja | lähes nolla |
| Hyökkäyspinta | hypervisor ja emuloidut laitteet | koko ytimen järjestelmäkutsurajapinta |
| Eri käyttöjärjestelmät | kyllä | ei (sama ydin) |

Kumpikaan ei korvaa toista. Pilvessä kontit ajetaan tyypillisesti
virtuaalikoneissa: virtuaalikone erottaa asiakkaat toisistaan, kontit
saman asiakkaan sovellukset. Mikro-VM:t (luku 8) yhdistävät
virtuaalikoneen eristyksen konttien keveyteen.

## Lyhyt historia

| Vuosi | Tapahtuma |
|-------|-----------|
| 1967 | IBM CP-67: virtuaalikoneet keskustietokoneella |
| 1974 | Popek ja Goldberg: virtualisoitavuuden muodolliset ehdot |
| 1979 | `chroot` Unixissa: ensimmäinen tiedostojärjestelmän eristys |
| 1999 | VMware Workstation: x86:n virtualisointi binäärikäännöksellä |
| 2003 | Xen: paravirtualisointi, vieras tietää olevansa vieras |
| 2005–2006 | Intel VT-x ja AMD-V: laitteistotuki suorittimessa |
| 2007 | KVM Linuxin ytimeen; cgroups ja nimiavaruudet kehittyvät |
| 2008 | Intel EPT ja AMD NPT: sivutaulujen laitteistotuki |
| 2013 | Docker tekee konteista tavallisen kehitystyökalun |
| 2015 | OCI-standardi konttikuville ja ajoympäristöille |
| 2018 | gVisor ja AWS Firecracker: uudet eristyksen tasot |

## Ympäristö ja työkalut

Esimerkit on testattu Ubuntu 24.04:ssä. Tarvitaan:

| Työkalu | Käyttö |
|---------|--------|
| QEMU 8 (`qemu-system-x86_64`, `qemu-img`, `qemu-io`) | virtuaalikoneet ja levykuvat |
| GCC ja binutils | vieraan ytimen ja esimerkkien kääntäminen |
| util-linux (`unshare`, `nsenter`, `setpriv`) | nimiavaruudet ja oikeudet |
| libcap2-bin (`capsh`) | kyvyt |
| Python 3.12 | QEMU:n hallintarajapinta QMP |

Kehityskontissa (`.devcontainer/virtualisointi`) kaikki on valmiina.
Kontti saa oikeudet `SYS_ADMIN` sekä rajoittamattoman seccompin ja
AppArmorin, koska kontin sisällä luodaan uusia nimiavaruuksia ja
liitoksia. Kontteja käsittelevät esimerkit tarvitsevat pääkäyttäjän
oikeudet: ne käynnistävät itsensä tarvittaessa `sudo -n`:llä.

Esimerkit eivät tarvitse laitteistotukea. QEMU käyttää
ohjelmallista **TCG**-käännöstä (Tiny Code Generator), joka toimii
missä tahansa ja tuottaa saman tuloksen joka kerta. Oikeassa käytössä
QEMU:lle annetaan `-accel kvm`, jolloin vieraan koodi suoritetaan
suoraan suorittimella. KVM-rajapintaa käyttävä esimerkki (luku 4)
ajetaan vain, jos laite `/dev/kvm` on käytettävissä.

## Ensimmäinen virtuaalikone

Ensimmäinen esimerkki kääntää pienen käyttöjärjestelmän ytimen ja
käynnistää sen QEMU:lla. Ydin tulostaa viestin sarjaporttiin ja
sammuttaa koneen. Vieraan lähdekoodi on hakemistossa
`esimerkit/vieras/lahteet/`:

```{.c tiedosto="esimerkit/vieras/lahteet/hei.c"}
```

Funktiot `tulosta` ja `lopeta` kirjoittavat I/O-portteihin:

```{.c tiedosto="esimerkit/vieras/lahteet/laitteet.h"}
```

Käynnistyskoodi asettaa pinon ja kutsuu C-funktiota. Sen alussa on
**Multiboot**-otsake, jonka ansiosta QEMU osaa ladata ytimen suoraan
ilman käynnistyslataajaa (valitsin `-kernel`):

```{.gnuassembler tiedosto="esimerkit/vieras/lahteet/alku.S"}
```

Rakennusskripti kääntää 32-bittisen ytimen. Vieras ei käytä C-kirjastoa
(`-ffreestanding`), ja linkkeriskripti sijoittaa sen 1 MiB:n
osoitteeseen:

```{.bash tiedosto="esimerkit/vieras/lahteet/rakenna.sh"}
```

```{.text tiedosto="esimerkit/vieras/lahteet/linkki.ld"}
```

Kone käynnistetään näin:

```{.bash tiedosto="esimerkit/01-ensimmainen.sh" osa="qemu"}
```

```{.tuloste tiedosto="esimerkit/01-ensimmainen.odotettu"}
```

QEMU tarjoaa vieraalle PC:n laitteet: sarjapiiri 16550 portissa
`0x3f8` ja testilaite `isa-debug-exit`, jolla vieras voi sammuttaa
koneen. Jokainen vieraan `outb`-käsky on virtuaalikoneessa
**VM exit**: suoritin pysähtyy, hypervisor tutkii käskyn ja emuloi
laitteen. Tämä vieraan ja hypervisorin välinen vuoropuhelu on koko
tutoriaalin punainen lanka.

## Tutoriaalin rakenne

1. Johdanto
2. Hypervisorit ja virtualisoinnin teoria – tyypit, Popekin ja
   Goldbergin ehdot, trap-and-emulate, binäärikäännös
3. Laitteistotuki – VT-x ja AMD-V, VM exit, EPT ja NPT
4. KVM ja QEMU – KVM-rajapinta, QMP, qcow2-levykuvat
5. I/O-virtualisointi – emuloitu laite, virtio, läpivienti, SR-IOV
6. Kontit: nimiavaruudet ja minikontti
7. Kontit: cgroups, kyvyt ja seccomp
8. Eristyksen tasot – kontti, gVisor, mikro-VM, virtuaalikone
9. Tilannevedokset ja siirto
10. Lopuksi – nyrkkisäännöt ja lähteet

Esitietona on taito *Käyttöjärjestelmät*: prosessit,
järjestelmäkutsut, virtuaalimuisti ja keskeytykset oletetaan
tutuiksi. Taito *Kontit ja pilvi* jatkaa tästä konttien käyttöön
(Docker, Kubernetes) ja taito *Palvelinympäristöt*
virtualisointialustojen ylläpitoon.
