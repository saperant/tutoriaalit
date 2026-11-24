# KVM ja QEMU käytännössä

Linuxin virtualisointipino on kaksiosainen. **KVM** (Kernel-based
Virtual Machine) on ytimen moduuli, joka hoitaa VT-x:n tai AMD-V:n:
se ajaa vieraan koodia ja palauttaa VM exitit. **QEMU** on
käyttäjätilan ohjelma, joka tekee kaiken muun: luo virtuaalikoneen,
emuloi laitteet, hallitsee levykuvia ja tarjoaa hallintarajapinnan.
Samaa KVM:ää käyttävät myös Firecracker, Cloud Hypervisor ja
crosvm, joissa QEMU:n laaja laitemalli on korvattu suppealla.

## Arkkitehtuuri

| Osa | Missä | Tehtävä |
|-----|-------|---------|
| KVM | isännän ydin | VM entry ja exit, EPT, keskeytysten injektointi |
| vCPU | QEMU:n säie | `ioctl(KVM_RUN)` silmukassa |
| Laitemalli | QEMU | sarjaportti, levyohjaimet, verkkokortit, virtio |
| vhost | isännän ydin | nopea virtio-taustaosa ilman QEMU:ta |
| Hallinta | QEMU:n QMP | käynnistys, pysäytys, vedokset, siirto |
| libvirt | hallintapalvelu | koneiden määrittely ja elinkaari (`virsh`) |

Isännän näkökulmasta virtuaalikone on tavallinen prosessi, ja sen
vCPU:t ovat säikeitä. Ne näkyvät `top`-komennossa, isännän vuorontaja
ajaa niitä, ja cgroupit (luku 7) rajoittavat niitä kuten mitä tahansa
prosessia.

## KVM-rajapinta

KVM:ää käytetään `ioctl`-kutsuilla kolmen tiedostokuvaajan kautta:
`/dev/kvm` (koko järjestelmä), virtuaalikone ja vCPU. Seuraava
ohjelma on pienin mahdollinen hypervisor. Vieraana on 12 tavun
reaalitilan ohjelma, joka laskee $2 + 2$ ja tulostaa tuloksen:

```{.c tiedosto="esimerkit/valinnaiset/kvm/kvm.c" osa="vieras"}
```

Ensin luodaan virtuaalikone ja annetaan sille muistia. Vieraan
"fyysinen muisti" on tavallista prosessin muistia, jonka KVM kuvaa
vieraan osoitteeseen `0x1000`:

```{.c tiedosto="esimerkit/valinnaiset/kvm/kvm.c" osa="vm"}
```

Sitten luodaan vCPU ja asetetaan sen rekisterit. Rakenne `kvm_run`
on vCPU:n kanssa jaettua muistia, josta VM exitin syy luetaan:

```{.c tiedosto="esimerkit/valinnaiset/kvm/kvm.c" osa="vcpu"}
```

Hypervisorin ydin on silmukka, joka ajaa vierasta ja käsittelee
exitit. Tämä on QEMU:n vCPU-säikeen pelkistetty muoto:

```{.c tiedosto="esimerkit/valinnaiset/kvm/kvm.c" osa="silmukka"}
```

Kun `/dev/kvm` on käytettävissä, ohjelma tulostaa:

```{.tuloste tiedosto="esimerkit/valinnaiset/kvm/kvm.odotettu"}
```

Esimerkkien Makefile kääntää ohjelman aina mutta ajaa sen vain, jos
laite on käytettävissä. Pilvessä ajettavissa CI-ympäristöissä ja
konteissa se puuttuu usein: KVM vaatii laitteistotuen, eikä sitä
yleensä anneta virtuaalikoneen sisälle.

## QEMU:n käynnistys

Luvun 1 esimerkki käynnisti QEMU:n valitsimin, jotka kannattaa tuntea:

| Valitsin | Merkitys |
|----------|----------|
| `-machine pc` / `q35` | emuloitava emolevy: vanha i440FX tai PCIe-pohjainen Q35 |
| `-accel kvm` / `tcg` | laitteistotuki tai ohjelmallinen käännös |
| `-cpu host` / nimetty malli | vieraalle näytettävät suoritinominaisuudet |
| `-m 4G`, `-smp 4` | muisti ja vCPU:iden määrä |
| `-drive file=…,if=virtio` | levy virtio-ohjaimella |
| `-netdev user,id=n -device virtio-net,netdev=n` | verkko |
| `-display none`, `-serial stdio` | ilman näyttöä, sarjakonsoli päätteeseen |
| `-qmp unix:…` | hallintarajapinta |

Tuotannossa QEMU:a ei juuri käynnistetä käsin. **libvirt** kuvaa
koneet XML-tiedostoina ja huolehtii elinkaaresta, Proxmox ja OpenStack
käyttävät joko libvirtiä tai omaa kerrostaan. Kaikki päätyvät samaan
QMP-rajapintaan.

## Hallintarajapinta QMP

**QMP** (QEMU Machine Protocol) on JSON-pohjainen rajapinta, jolla
käynnissä olevaa konetta ohjataan: pysäytys, jatkaminen, vedokset,
levyjen ja laitteiden lisäys sekä siirto. Pieni asiakas riittää:

```{.python tiedosto="esimerkit/04-qmp.py" osa="qmp"}
```

QEMU käynnistetään pysäytettynä (`-S`), ja QMP-pistoke kuuntelee
Unix-pistokkeessa:

```{.python tiedosto="esimerkit/04-qmp.py" osa="kaynnistys"}
```

```{.python tiedosto="esimerkit/04-qmp.py" osa="hallinta"}
```

```{.tuloste tiedosto="esimerkit/04-qmp.odotettu"}
```

Tila `prelaunch` tarkoittaa, että kone on luotu mutta suoritin ei ole
vielä käynnistynyt. Vieras sammuttaa koneen testilaitteella, ja QEMU
palauttaa arvon $(3 \ll 1) \mid 1 = 7$.

## Levykuvat: qcow2

Raakakuva (`raw`) on levyn tavut sellaisinaan. **qcow2** (QEMU Copy
On Write) lisää kolme ominaisuutta: kuva kasvaa vasta, kun siihen
kirjoitetaan; kuvan voi rakentaa toisen kuvan päälle **kerrokseksi**
(backing file); ja kuvaan voi tallentaa **sisäisiä tilannevedoksia**.

```{.bash tiedosto="esimerkit/04-qcow2.sh" osa="kerrokset"}
```

```{.bash tiedosto="esimerkit/04-qcow2.sh" osa="vedokset"}
```

```{.bash tiedosto="esimerkit/04-qcow2.sh" osa="yhdista"}
```

```{.tuloste tiedosto="esimerkit/04-qcow2.odotettu"}
```

`qemu-img map` näyttää, kummasta tiedostosta kukin alue luetaan.
Kerroksessa on vain kone1:n muuttama megatavu. Sama peruskuva voi
palvella satoja koneita, kunhan sitä ei kirjoiteta: pilvipalveluiden
käyttöjärjestelmäkuvat ja CI-ajojen pohjat toimivat näin.
`qemu-img commit` yhdistää kerroksen muutokset peruskuvaan.

## Käytännössä

- **Älä kirjoita jaettuun peruskuvaan.** Jos peruskuva muuttuu, kaikki
  sen päälle rakennetut kerrokset näkevät rikkinäisen levyn. Tee
  peruskuvista vain luettavia ja päivitä ne uutena kuvana.
- **Kerrosketjut pidetään lyhyinä.** Jokainen kerros lisää hakuja
  lukuihin. Pitkä vedos- tai kerrosketju yhdistetään säännöllisesti
  (`commit`, `rebase` tai `block-stream` käynnissä olevalle koneelle).
- **raw vai qcow2?** Raakakuva on nopein ja helpoin varmuuskopioida
  tiedostotasolla. qcow2 kannattaa, kun tarvitaan harvaa varausta,
  kerroksia tai sisäisiä vedoksia. LVM- tai ZFS-taltio on kolmas
  vaihtoehto, kun vedokset hoidetaan tallennuskerroksessa.
- **Ohjaa koneita QMP:llä tai libvirtillä, ei näppäilemällä.**
  Ihmisen monitori (`-monitor stdio`) on vianetsintään. Automaatio
  käyttää QMP:tä, jonka vastaukset ovat rakenteisia ja
  versioituja.
- **Rajaa laitemalli.** Jokainen emuloitu laite on hyökkäyspintaa. Ota
  käyttöön vain tarvittavat laitteet ja suosi virtio-laitteita
  emuloitujen sijaan (luku 5).

## Itsearviointi

- Osaat kuvata KVM:n ja QEMU:n työnjaon ja sen, miksi
  virtuaalikone näkyy isännälle prosessina.
- Osaat kertoa KVM-rajapinnan vaiheet: virtuaalikone, muistialue, vCPU
  ja `KVM_RUN`-silmukka exitin käsittelyineen.
- Osaat käynnistää QEMU:n tärkeimmillä valitsimilla ja ohjata sitä
  QMP-rajapinnan kautta.
- Osaat rakentaa qcow2-kerroksen peruskuvan päälle, ottaa ja palauttaa
  sisäisen vedoksen sekä yhdistää kerroksen peruskuvaan.
