# Johdanto {.runko-johdanto}

Sulautettu Linux on Linux-järjestelmä, joka on rakennettu yhtä laitetta
varten: reititin, teollisuuden ohjausyksikkö, auton viihdejärjestelmä,
kamera tai lääkintälaite. Ydin on sama kuin palvelimissa ja
työasemissa, mutta kaikki sen ympärillä valitaan laitteen mukaan:
prosessoriarkkitehtuuri, käynnistin, ytimen asetukset, laitepuu,
C-kirjasto, juuritiedostojärjestelmä ja palvelut. Laitteessa ei ole
paketinhallintaa, jolla ylläpitäjä asentaisi puuttuvan työkalun, vaan
koko ohjelmisto rakennetaan kehityskoneella ja kirjoitetaan laitteeseen
yhtenä kuvana.

Linux valitaan sulautettuun laitteeseen, kun laitteessa on muistinhallintayksikkö
(MMU) ja muistia vähintään kymmeniä megatavuja ja kun tarvitaan
verkkopinoa, tiedostojärjestelmiä, USB:tä, näyttöä tai valmiita
ohjelmistoja. Pienempiin laitteisiin ja kovan reaaliaikaisuuden tehtäviin
sopivat paremmin bare-metal-ohjelma tai reaaliaikakäyttöjärjestelmä
(taidot *Mikrokontrollerit ja bare-metal-ohjelmointi* ja
*Reaaliaikakäyttöjärjestelmät*). Usein laitteessa on molemmat: Linux
sovellusprosessorilla ja RTOS erillisellä mikrokontrollerilla, joka
hoitaa ajoituskriittiset tehtävät.

Tutoriaali käsittelee

- **ristiinkääntämistä**: työkaluketjun nimeäminen, sysroot, C-kirjaston
  valinta, staattinen ja dynaaminen linkitys sekä ohjelmien testaus
  QEMU:n käyttäjätilan emulaattorilla
- **ytimen konfigurointia ja kääntämistä**: Kconfig, fragmentit,
  riippuvuudet, toistettava käännös ja moduulit
- **ensimmäistä käynnistystä**: initramfs, init-prosessi ja ytimen
  virtuaaliset tiedostojärjestelmät
- **käynnistysketjua**: ROM-käynnistin, SPL, U-Boot, ytimen
  Image-otsake, extlinux ja U-Bootin skriptit
- **laitepuuta**: miten ydin saa tietää laitteistosta ja miten
  laitepuun solmu sidotaan ajuriin
- **palveluja**: oma pieni init-järjestelmä valmiusilmoituksineen,
  uudelleenkäynnistyksineen ja sammutuksineen sekä vertailu BusyBoxiin
  ja systemd:hen
- **juuritiedostojärjestelmää**: hakemistorakenne, vain luku -juuri,
  overlayfs ja päivitysten periaatteet
- **Buildrootia ja Yoctoa**: miten edellä käsin tehdyt vaiheet
  automatisoidaan tuotannossa
- **käynnistystestejä**: järjestelmän automaattinen käynnistys,
  tulosteen seuraaminen ja vikojen tunnistaminen CI:ssä
- **vianetsintää kohteessa**: käynnistymättömän ohjelman virhekoodit,
  järjestelmäkutsujen jäljitys, ydinvedos ja etädebuggaus.

## Esitiedot ja rajaus

Esitietoina oletetaan taidot *Käyttöjärjestelmät* (prosessit,
järjestelmäkutsut, signaalit, tiedostojärjestelmät ja laitteet) ja
*Käännösjärjestelmät, testaus ja CI* (Make, gdb ja CI-putket). Taidosta
*Objektitiedostot, linkitys ja ABI* on hyötyä ristiinkääntämisen ja
vianetsinnän luvuissa ja taidosta *Virtualisointi* QEMU:n käytössä.

Tutoriaali rakentaa järjestelmän käsin ytimestä ja omista C-ohjelmista,
jotta jokainen osa näkyy. Kohteessa ei siksi ole kuorta eikä BusyBoxia,
vaan jokainen koe on oma init-ohjelmansa. Buildroot ja Yocto, joilla
tuotantojärjestelmät rakennetaan, esitellään asetustiedostoina, mutta
niitä ei ajeta (luku 9). Ytimen ajurit ja ytimen oma vianetsintä
kuuluvat taitoon *Linux-laiteajurit*, joka käyttää tämän tutoriaalin
ympäristöä, ja laitteen suojaaminen taitoon *Sulautettujen
järjestelmien tietoturva*.

Reaaliaikaisuudesta käsitellään vain rajanveto. Tavallinen Linux ei
takaa vasteaikoja. Ytimen `PREEMPT_RT`-asetus, joka on ollut
pääkehityshaarassa versiosta 6.12, tekee lähes koko ytimestä
keskeytettävän ja riittää moneen pehmeän ja kiinteän reaaliajan
tehtävään. Lyhimmät ja todistettavat vasteajat vaativat edelleen
erillisen mikrokontrollerin ja RTOS:n (taito
*Reaaliaikakäyttöjärjestelmät*).

## Laboratorio: QEMU:n virt-kone

Kaikki esimerkit ajetaan QEMU:n `virt`-koneessa, joka on suunniteltu
virtuaalikoneita varten eikä jäljittele mitään oikeaa piirilevyä.
Prosessoriksi valitaan Cortex-A53, joka on yleinen 64-bittinen ARM-ydin
esimerkiksi Raspberry Pi 3:ssa ja monissa teollisuuden
järjestelmäpiireissä. Koneessa on 256 Mt muistia, PL011-sarjaportti,
GIC-keskeytysohjain, ARM:n yleinen ajastin ja virtio-laitteita.

```{.bash tiedosto="esimerkit/ymparisto/aja-qemu.sh" osa="kone"}
```

Kaikki käynnistykset tehdään yhdellä skriptillä, joka lisää koneen
valitsimet, ohjaa sarjakonsolin vakiotulosteeseen ja katkaisee jumiin
jääneen ajon aikarajalla:

```{.bash tiedosto="esimerkit/ymparisto/aja-qemu.sh" osa="ajo"}
```

Valitsin `-no-reboot` tekee uudelleenkäynnistyksestä QEMU:n
lopetuksen, ja ytimen parametri `panic=-1` käynnistää ytimen
paniikin jälkeen heti uudelleen. Yhdessä ne lopettavat QEMU:n myös
silloin, kun järjestelmä kaatuu, joten testi ei jää odottamaan. Siisti
sammutus (PSCI:n `SYSTEM_OFF`-kutsu) lopettaa QEMU:n paluuarvolla 0.
Valitsin `-nic none` jättää pois oletusverkkokortin, jota esimerkit
eivät tarvitse ja jonka käynnistys-ROM puuttuu kevyistä QEMU-asennuksista.

Kaikki tarvittava tulee Ubuntun paketeista: ytimen lähdekoodi
(`linux-source-6.8.0`), ristikääntäjä (`gcc-aarch64-linux-gnu`), QEMU,
U-Boot (`u-boot-qemu`, `u-boot-tools`) ja laitepuutyökalut
(`device-tree-compiler`). Jakelun paketeista rakentaminen pitää
esimerkit toistettavina ilman verkkoa. Omassa projektissa ytimen
lähteet haetaan tavallisesti osoitteesta kernel.org tai piirin
valmistajalta ja koko järjestelmä rakennetaan Buildrootilla tai
Yoctolla (luku 9). Kun järjestelmän on kerran koonnut käsin, tietää,
mitä rakennustyökalut tekevät.

## Ympäristö: ytimen rakennus kerran

Ytimen kääntäminen kestää 4-ytimisellä koneella useita minuutteja ja
vie levyltä lähteineen noin kaksi gigatavua. Siksi ydin käännetään
kerran ja jaetaan kaikkien esimerkkien kesken. Rakennuksen hoitaa
tiedosto `esimerkit/ymparisto/ydin.mk`, jonka voi ottaa mukaan mihin
tahansa Makefileen. Sen keskeiset muuttujat ovat:

```{.make tiedosto="esimerkit/ymparisto/ydin.mk" osa="muuttujat"}
```

Käännöksen hakemiston nimi sisältää konfiguraatiofragmenttien
tiivisteen. Kun fragmentti muuttuu, syntyy uusi käännöshakemisto, eikä
vanhaa tarvitse siivota käsin ennen kuin se halutaan poistaa. Taito
*Linux-laiteajurit* käyttää samaa tiedostoa omien moduuliensa
kääntämiseen.

## Esimerkkien rakenne

Esimerkit ovat hakemistossa `esimerkit/`, ja niiden Makefile kääntää
ytimen, ohjelmat, initramfs-arkistot ja levykuvat, käynnistää jokaisen
järjestelmän QEMU:ssa ja vertaa tulosteen tiedostoon
`testit/<testi>.odotettu`. Ytimen omasta lokista otetaan vertailuun
vain valittuja rivejä, koska siinä on aikaleimoja ja osoitteita.

| Hakemisto | Sisältö | Luku |
|-----------|---------|-----:|
| `ymparisto/` | ytimen rakennus, QEMU-skripti, konfiguraation tarkistus | 1, 3 |
| `testit/` | testien odotetut tulosteet | kaikki |
| `02-ristiin/` | sama ohjelma isännälle ja ARM64:lle | 2 |
| `03-ydin/` | väärä fragmentti, moduuli ja sen lataaja | 3 |
| `04-init/` | pienin init ja initramfs | 4 |
| `05-uboot/` | Image-otsake, levykuva, extlinux, käynnistysskripti, käsikäynnistys | 5 |
| `06-laitepuu/` | laitepuun purku, muokkaus ja tutkiminen | 6 |
| `07-palvelut/` | init-järjestelmä palveluineen | 7 |
| `08-juuri/` | vain luku -juuri ja overlayfs | 8 |
| `09-buildroot/` | Buildroot- ja Yocto-asetukset (ei ajeta) | 9 |
| `10-kaynnistystesti/` | käynnistystestien ajuri | 10 |
| `11-vianetsinta/` | käynnistyskokeet, jäljitys, ydinvedos, gdb-istunto | 11 |

Kaikki ajetaan komennolla `make testaa` paketin juuressa. Ensimmäinen
ajo purkaa ytimen lähteet ja kääntää ytimen; seuraavat ajot käyttävät
välimuistia ja kestävät noin puoli minuuttia.

## Lukuohje

Luvut 2–4 rakentavat toimivan järjestelmän alusta: työkaluketju, ydin
ja init. Luvut 5 ja 6 käsittelevät sitä, miten laite käynnistää ytimen
ja miten ydin saa tietää laitteistosta. Luvut 7 ja 8 tekevät
järjestelmästä tuotantokelpoisen: palvelut, sammutus ja juuren
suojaaminen. Luku 9 näyttää, miten sama tehdään rakennustyökaluilla,
luku 10, miten se testataan automaattisesti, ja luku 11, miten vian syy
löydetään, kun ohjelma ei kohteessa toimi. Kokenut lukija voi lukea
lukujen itsearvioinnit ja pikaoppaan ja palata lukuihin, joiden
väitteistä ei ole varma.
