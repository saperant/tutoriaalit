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

```{.dot otsikko="Neljä eristyksen tasoa kerrospinoina. Punainen rivi on raja, jonka läpi eristetty koodi puhuu etuoikeutetulle koodille; harmaat kerrokset ovat isännän. gVisor ja mikro-VM esitellään luvussa 8"}
digraph {
  rankdir=TB; nodesep=0.25; ranksep=0.15;
  node [shape=plaintext, fontsize=9];
  k [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0"><b>kontti</b></td></tr>
    <tr><td>sovellus</td></tr>
    <tr><td bgcolor="#f3c8c8">raja: ~350 järjestelmäkutsua</td></tr>
    <tr><td bgcolor="#d9d9d9">isännän ydin</td></tr>
    <tr><td bgcolor="#d9d9d9">rauta</td></tr></table>>];
  g [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0"><b>gVisor</b></td></tr>
    <tr><td>sovellus</td></tr>
    <tr><td bgcolor="#f3c8c8">raja: Sentryn toteuttamat kutsut</td></tr>
    <tr><td>Sentry: ydin käyttäjätilassa</td></tr>
    <tr><td bgcolor="#f3c8c8">raja: kymmeniä isännän kutsuja</td></tr>
    <tr><td bgcolor="#d9d9d9">isännän ydin</td></tr>
    <tr><td bgcolor="#d9d9d9">rauta</td></tr></table>>];
  m [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0"><b>mikro-VM</b></td></tr>
    <tr><td>sovellus</td></tr>
    <tr><td>vieraan ydin</td></tr>
    <tr><td bgcolor="#f3c8c8">raja: VM exitit, muutama virtio-laite</td></tr>
    <tr><td>suppea VMM (Firecracker)</td></tr>
    <tr><td bgcolor="#d9d9d9">isännän ydin ja KVM</td></tr>
    <tr><td bgcolor="#d9d9d9">rauta (VT-x, EPT)</td></tr></table>>];
  v [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0"><b>virtuaalikone</b></td></tr>
    <tr><td>sovellus</td></tr>
    <tr><td>vieraan ydin</td></tr>
    <tr><td bgcolor="#f3c8c8">raja: VM exitit, koko emuloitu PC</td></tr>
    <tr><td>QEMU: laitemalli</td></tr>
    <tr><td bgcolor="#d9d9d9">isännän ydin ja KVM</td></tr>
    <tr><td bgcolor="#d9d9d9">rauta (VT-x, EPT)</td></tr></table>>];
  {rank=same; k; g}
  {rank=same; m; v}
  k -> m [style=invis];
  g -> v [style=invis];
}
```

Kuvan kaksi ääripäätä rinnakkain:

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
suoraan suorittimella.

Kaksi esimerkkiä tarvitsee ympäristöltä enemmän, ja ne ovat siksi
hakemistossa `esimerkit/valinnaiset/`. `make testaa` ajaa ne, jos
ympäristö sallii, ja muuten tulostaa rivin "ajo ohitetaan":

| Esimerkki | Tarvitsee | Miten sen saa ajettua |
|-----------|-----------|-----------------------|
| `kvm/kvm.c` (luku 4) | laitteen `/dev/kvm` | Linux-isäntäkoneella, jonka suoritin tukee virtualisointia; kehityskontille `--device /dev/kvm` |
| `cgroups/pids.sh` (luku 7) | kirjoitettavan cgroup-puun | isäntäkoneella pääkäyttäjänä; tavallisessa kontissa cgroup-puu on vain luettava |

Kehityskontissa ja CI:ssä nämä kaksi yleensä ohitetaan. Niiden
tulosteet tekstissä ovat isäntäkoneella ajetuista ajoista, eikä testi
suojaa niitä vanhenemiselta samalla tavalla kuin muita. Komento
`make -C esimerkit` ajaa ne erikseen.

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

## Esitiedot ja rajaus

Esitietona on taito *Käyttöjärjestelmät*: prosessit,
järjestelmäkutsut, virtuaalimuisti, keskeytykset sekä käyttäjät,
oikeudet ja kyvyt oletetaan tutuiksi. Esimerkit ovat C:tä, Bashia ja
Pythonia; C++:aa ei tarvita. Sivutaulujen ja suojaustasojen
laitteistopuoli on taidossa *Tietokonearkkitehtuuri*, joka on
*Käyttöjärjestelmien* esitieto.

Tutoriaali käsittelee mekanismit, ei tuotteiden käyttöä. Taito
*Kontit ja pilvi-infrastruktuuri* jatkaa tästä konttien käyttöön
(Docker, konttikuvien rakentaminen, Kubernetes) ja taito
*Palvelinympäristöt* virtualisointialustojen ylläpitoon.
