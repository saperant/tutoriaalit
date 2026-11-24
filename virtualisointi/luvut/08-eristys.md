# Eristyksen tasot

Virtuaalikone ja kontti eivät ole ainoat vaihtoehdot. Viimeisten
kymmenen vuoden aikana niiden väliin on tullut tekniikoita, jotka
yhdistävät konttien keveyden ja virtuaalikoneiden eristyksen. Valinta
on aina vaihtokauppa: mitä vahvempi raja, sitä suurempi hinta
käynnistysajassa, muistissa ja I/O:ssa.

## Raja ja hyökkäyspinta

Eristyksen vahvuus riippuu siitä, kuinka suuren rajapinnan läpi
eristetty koodi pääsee käsiksi etuoikeutettuun koodiin:

| Taso | Raja | Rajapinta isäntään | Esimerkkejä |
|------|------|--------------------|-------------|
| Kontti | isännän ydin | ~350 järjestelmäkutsua (seccompilla vähemmän) | Docker, Podman, containerd |
| Hiekkalaatikkoydin | käyttäjätilan ydin | kymmeniä isännän kutsuja | gVisor |
| Mikro-VM | hypervisor | VM exitit ja muutama virtio-laite | Firecracker, Cloud Hypervisor, Kata Containers |
| Virtuaalikone | hypervisor | VM exitit ja koko emuloitu PC | QEMU/KVM, VMware, Hyper-V |
| Erillinen rauta | fyysinen kone | verkko | omistettu palvelin |

Kontin raja on koko Linux-ydin. Ytimessä löytyy vuosittain
haavoittuvuuksia, joilla prosessi voi nostaa oikeutensa, ja konttien
sisältä niitä hyödynnetään samoin kuin isännästä. Siksi
monivuokralaisissa ympäristöissä (pilvifunktiot, julkiset CI-ajot)
vieraan koodin ympärille laitetaan virtuaalikone.

## gVisor

**gVisor** (Google) on käyttäjätilassa ajettava ydin, joka toteuttaa
Linuxin järjestelmäkutsurajapinnan uudelleen Go-kielellä. Kontin
prosessien kutsut ohjataan gVisorin ytimeen (Sentry), joka käyttää
isännän ydintä vain suppean ja tarkasti suodatetun kutsujoukon kautta.
Hyökkääjän on murrettava ensin gVisor ja sitten isännän ydin.
Hinta on järjestelmäkutsujen ja I/O:n hitaus sekä
yhteensopivuus: kaikkia ytimen ominaisuuksia ei ole toteutettu.

## Mikro-VM

**Mikro-VM** on virtuaalikone, josta on poistettu kaikki, mitä
palvelinkuorma ei tarvitse: BIOS, PCI-väylä, USB, näyttö ja
emuloidut levyohjaimet. **Firecracker** (AWS, Rust) tarjoaa vieraalle
vain virtio-levyn, virtio-verkon, sarjaportin ja näppäimistöohjaimen
uudelleenkäynnistystä varten. Laitemalli on muutamia kymmeniä
tuhansia rivejä QEMU:n miljoonien sijaan, ja kone käynnistyy noin
125 millisekunnissa. AWS Lambda ja Fargate ajavat jokaisen funktion ja
kontin omassa mikro-VM:ssään.

**Kata Containers** käyttää mikro-VM:ää konttiajoympäristönä:
Kubernetes näkee tavallisen kontin, mutta sen ympärillä on oma ydin ja
hypervisor. Valinta tehdään podikohtaisesti (`runtimeClassName`).

## Luottamuksellinen laskenta

Kaikissa edellisissä isäntä näkee vieraan muistin. **Luottamuksellinen
laskenta** (confidential computing) kääntää asetelman: AMD SEV-SNP ja
Intel TDX salaavat vieraan muistin avaimella, jota hypervisor ei
tiedä, ja suoritin estää hypervisoria lukemasta tai muuttamasta
vieraan tilaa. Vieras voi todentaa (attestation) suorittimen
allekirjoittamalla raportilla, että se ajetaan aidossa,
suojatussa ympäristössä. Tällä suojataan dataa pilvipalvelun
ylläpitäjältä.

## Valinta

| Tarve | Valinta |
|-------|---------|
| Omat, luotetut sovellukset samassa klusterissa | kontit, oletusturva-asetukset |
| Vieras koodi (asiakkaiden funktiot, CI-ajot) | mikro-VM tai gVisor |
| Eri käyttöjärjestelmä tai ydinversio | virtuaalikone |
| Sääntely edellyttää fyysistä erottelua | erillinen rauta tai omistettu isäntä |
| Data ei saa näkyä palveluntarjoajalle | luottamuksellinen virtuaalikone |

## Hinnat

| | Kontti | gVisor | Mikro-VM | Virtuaalikone |
|---|---|---|---|---|
| Käynnistys | ~10 ms | ~100 ms | ~125 ms | sekunteja |
| Muistin yleiskulu | ~0 | kymmeniä MiB | ~5 MiB + vieraan ydin | satoja MiB |
| Järjestelmäkutsun hinta | natiivi | moninkertainen | natiivi (vieraan ytimessä) | natiivi |
| I/O | natiivi | hitain | virtio | virtio tai emuloitu |
| Tiheys yhdessä isännässä | tuhansia | satoja | tuhansia | kymmeniä |

Luvut ovat suuruusluokkia ja riippuvat kuormasta. Ne kertovat, mihin
kunkin tekniikan raja osuu: kontti on halpa, koska se ei virtualisoi
mitään, ja mikro-VM on halpa, koska se virtualisoi vain välttämättömän.

## Käytännössä

- **Uhkamalli ensin.** Kysy, kenen koodia ajetaan ja mitä sen
  murtautuminen maksaisi. Luotetulle koodille kontti riittää ja on
  halvin; vieraalle koodille tarvitaan raja, joka ei ole koko ydin.
- **Kerrokset yhdessä.** Tuotannossa yhdistetään: kontit
  virtuaalikoneessa, käyttäjänimiavaruus, seccomp ja LSM konttien
  sisällä. Yksittäinen kerros pettää ennemmin tai myöhemmin.
- **Laitemalli on hyökkäyspintaa.** Suurin osa hypervisorien
  haavoittuvuuksista on emuloiduissa laitteissa (esim. VENOM QEMU:n
  levykeohjaimessa, 2015). Mitä vähemmän laitteita, sitä parempi.
- **Mittaa käynnistysaika.** Pilvifunktioissa käynnistysaika on
  käyttäjän viive. Mikro-VM:n ja kontin ero on pieni, perinteisen
  virtuaalikoneen ero ratkaiseva.

## Itsearviointi

- Osaat järjestää eristyksen tasot rajan ja hyökkäyspinnan mukaan ja
  perustella järjestyksen.
- Osaat selittää, miten gVisor ja mikro-VM:t (Firecracker, Kata)
  pienentävät isäntään näkyvää rajapintaa.
- Osaat valita eristyksen tason uhkamallin perusteella ja arvioida sen
  hinnan käynnistysajassa, muistissa ja I/O:ssa.
- Osaat kertoa, mitä luottamuksellinen laskenta suojaa ja mitä
  todentaminen tarkoittaa.
