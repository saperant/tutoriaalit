# Hypervisorit ja virtualisoinnin teoria

Hypervisorin tehtävä on näyttää jokaiselle vieraalle oma kone, vaikka
fyysinen suoritin, muisti ja laitteet ovat yhteisiä. Luku käsittelee
hypervisorien tyypit, ehdot, joilla suoritin on virtualisoitavissa, ja
kolme tapaa täyttää ehdot: trap-and-emulate, binäärikäännös ja
paravirtualisointi. Laitteistotuki on luvun 3 aihe.

## Tyyppi 1 ja tyyppi 2

| | Tyyppi 1 (bare metal) | Tyyppi 2 (hosted) |
|---|---|---|
| Missä ajetaan | suoraan raudalla | tavallisen käyttöjärjestelmän päällä |
| Esimerkkejä | VMware ESXi, Xen, Hyper-V, AWS Nitro | VirtualBox, VMware Workstation, QEMU ilman KVM:ää |
| Laiteajurit | hypervisorissa tai hallintakoneessa (Xenin dom0) | isännän käyttöjärjestelmässä |

Jako on nykyään sumea. **KVM** tekee Linuxin ytimestä hypervisorin:
ydin ajaa virtuaalikoneet kuten tyypin 1 hypervisor, mutta sama kone
ajaa myös tavallisia prosesseja. Hyper-V puolestaan ajaa
Windows-isännänkin virtuaalikoneena. Olennaisempi kysymys on, kuinka
suuri osa koodista ajetaan etuoikeutetussa tilassa, sillä se on
hyökkäyspinta: Xenin hypervisor on muutamia satoja tuhansia rivejä,
Linux-ydin kymmeniä miljoonia.

## Popekin ja Goldbergin ehdot

Popek ja Goldberg määrittelivät vuonna 1974, milloin suorittimelle
voidaan rakentaa tehokas hypervisor. He jakoivat käskyt kahteen
luokkaan:

- **Etuoikeutetut käskyt** (privileged) aiheuttavat ansan (trap), jos
  niitä yritetään suorittaa käyttäjätilassa. Esimerkiksi keskeytysten
  kieltäminen (`cli`) ja I/O-käskyt.
- **Sensitiiviset käskyt** (sensitive) lukevat tai muuttavat koneen
  tilaa, joka kuuluu hypervisorille: keskeytyslippua, sivutauluja,
  suoritintilaa.

**Ehto:** suoritin on virtualisoitavissa trap-and-emulate-menetelmällä,
jos jokainen sensitiivinen käsky on etuoikeutettu. Silloin vieraan
ytimen voi ajaa käyttäjätilassa: tavalliset käskyt suoritetaan suoraan
täydellä nopeudella, ja jokainen sensitiivinen käsky aiheuttaa ansan,
jonka käsittelijä (hypervisor) emuloi vieraan virtuaalista tilaa
vasten.

Hypervisorilta vaaditaan kolme ominaisuutta:

1. **Vastaavuus** (equivalence): ohjelma käyttäytyy virtuaalikoneessa
   samoin kuin raudalla (ajoitusta lukuun ottamatta).
2. **Resurssien hallinta** (resource control): vieras ei voi ottaa
   hallintaansa resursseja, joita sille ei ole annettu.
3. **Tehokkuus** (efficiency): valtaosa käskyistä suoritetaan suoraan
   ilman hypervisorin väliintuloa.

Alkuperäinen x86 ei täyttänyt ehtoa. Siinä on 17 sensitiivistä käskyä,
jotka eivät ole etuoikeutettuja. Tunnetuin on `popf`: käyttäjätilassa
se jättää keskeytyslipun muutoksen **hiljaa huomiotta** eikä aiheuta
ansaa. Samoin `pushf`, `sgdt` ja `smsw` paljastavat oikean koneen tilan
ilman ansaa.

## Lelusuoritin

Seuraava ohjelma toistaa ongelman pienessä mittakaavassa. Lelusuorittimen
käskyistä `CLI`, `STI`, `OUT` ja `HLT` ovat etuoikeutettuja. `LUEIF`
ja `ASETAIF` vastaavat x86:n `pushf`- ja `popf`-käskyjä: ne ovat
sensitiivisiä mutta eivät etuoikeutettuja.

```{.c tiedosto="esimerkit/02-lelukone.c" osa="kaskyt"}
```

Suoritin tekee käskyn kuten rauta. Etuoikeutettu käsky käyttäjätilassa
aiheuttaa ansan. `ASETAIF` ohittaa käyttäjätilassa muutoksen hiljaa,
kuten `popf`:

```{.c tiedosto="esimerkit/02-lelukone.c" osa="askel"}
```

Hypervisor ajaa vieraan ytimen käyttäjätilassa ja pitää yllä vieraan
**virtuaalista** keskeytyslippua. Ansan tullen se emuloi käskyn:

```{.c tiedosto="esimerkit/02-lelukone.c" osa="vmm"}
```

Vieraana on ytimen pätkä, joka kieltää keskeytykset, lukee lipun ja
palauttaa keskeytykset. Tulokset neljällä tavalla:

```{.tuloste tiedosto="esimerkit/02-lelukone.odotettu" rivit="1-4"}
```

Ohjelman toinen taulukko näyttää, kuka kunkin käskyn suorittaa:
hypervisor ansan kautta vai vieras itse.

```{.tuloste tiedosto="esimerkit/02-lelukone.odotettu" rivit="6-11"}
```

Pelkkä trap-and-emulate epäonnistuu kahdesti. `LUEIF` lukee isännän
oikean lipun (1), vaikka vieras juuri kielsi keskeytykset. `ASETAIF`
ei aiheuta ansaa, joten hypervisor ei saa tietää, että vieras salli
keskeytykset. Hypervisor uskoo niiden olevan yhä kiellettyjä eikä
välitä vieraalle yhtään keskeytystä: vieras jumittuu.

## Binäärikäännös

VMware ratkaisi ongelman vuonna 1999 **binäärikäännöksellä** (binary
translation). Hypervisor lukee vieraan ytimen koodin ennen suoritusta
ja korvaa ongelmalliset käskyt kutsuilla, jotka tekevät oikean asian.
Käyttäjätilan koodi ajetaan suoraan, koska sen sensitiiviset käskyt
eivät koske hypervisorin tilaa.

```{.c tiedosto="esimerkit/02-lelukone.c" osa="kaannos"}
```

Tulos on oikea, mutta ansoja tulee enemmän (5): taulukon
keskimmäisessä sarakkeessa hypervisor käsittelee jokaisen käskyn. Oikeissa toteutuksissa
käännetty koodi tallennetaan välimuistiin, ja suurin osa
korvatuista käskyistä emuloidaan suoraan käännetyssä koodissa ilman
ansaa. Menetelmä on monimutkainen mutta toimi x86:lla ennen
laitteistotukea hämmästyttävän hyvin. QEMU:n TCG on samaa
sukua: se kääntää **kaikki** vieraan käskyt isännän käskyiksi, jolloin
vieras voi olla eri arkkitehtuuria kuin isäntä.

## Paravirtualisointi

Xen otti toisen tien vuonna 2003: muutetaan vierasta. **Paravirtualisoitu**
vieras tietää olevansa vieras ja kutsuu hypervisoria suoraan
**hyperkutsulla** (hypercall) sen sijaan, että yrittäisi ohjata
laitteistoa. Etuna on nopeus ja yksinkertaisuus, haittana se, että
vieraan ydintä on muutettava. Laitteistotuen myötä paravirtualisointi
on säilynyt siellä, missä siitä on eniten hyötyä: I/O-laitteissa
(virtio, luku 5), kelloissa ja keskeytysten välityksessä.

## Laitteistotuki lyhyesti

Viimeinen rivi tulosteessa on laitteistotuki, jonka Intel ja AMD
lisäsivät suorittimiin vuosina 2005–2006. Suorittimella on erillinen
**vierastila**, jossa vieraalla on oma kopio rekistereistä, myös
keskeytyslipusta. `CLI` ja `LUEIF` toimivat vieraan omaa tilaa vasten
ilman ansaa, ja vain hypervisorin valitsemat tapahtumat (tässä I/O ja
`HLT`) aiheuttavat **VM exitin**. Tulos on oikea, ja ansoja on vähiten:
taulukon oikeassa sarakkeessa vieras suorittaa itse kaiken paitsi
I/O:n ja pysäytyksen.
Luku 3 käsittelee mekanismin tarkemmin.

## Käytännössä

- **Ansat maksavat.** Jokainen ansa tai VM exit vie satoja tai tuhansia
  kellojaksoja, koska suorittimen tila tallennetaan ja palautetaan.
  Virtualisoinnin suorituskyky on pitkälti sitä, kuinka harvoin
  vieras joutuu pysähtymään. Sama ajatus toistuu kaikkialla: virtio
  kokoaa I/O:n eriksi, EPT poistaa sivutaulumuutosten ansat.
- **Tyyppi ei kerro turvallisuutta.** Oleellista on etuoikeutetussa
  tilassa ajettavan koodin määrä ja vieraalle näkyvä rajapinta. Siksi
  pilvipalvelut siirtävät laitteiden emuloinnin pois hypervisorista
  omalle laitteistolleen (AWS Nitro) tai erilliseen prosessiin.
- **Emulointi ja virtualisointi ovat eri asioita.** TCG suorittaa minkä
  tahansa arkkitehtuurin koodia, mutta noin 5–20 kertaa hitaammin.
  Laitteistotuettu virtualisointi ajaa saman arkkitehtuurin koodia
  lähes täydellä nopeudella. QEMU:n `-accel kvm` valitsee jälkimmäisen.
- **Vastaavuus ei koske aikaa.** Vieras voi huomata olevansa
  virtuaalikoneessa ajoituksista (esim. `cpuid` vie poikkeuksellisen
  kauan) ja suorittimen tunnisteista. Tätä käyttävät sekä
  haittaohjelmat (virtuaaliympäristön tunnistus) että lisenssien
  valvonta.

## Itsearviointi

- Osaat selittää tyypin 1 ja tyypin 2 hypervisorin eron ja sen, miksi
  KVM ei sovi siististi kumpaankaan.
- Osaat määritellä etuoikeutetut ja sensitiiviset käskyt ja kertoa
  Popekin ja Goldbergin ehdon.
- Osaat selittää, miksi x86:n `popf` esti trap-and-emulate-menetelmän,
  ja näyttää ongelman esimerkillä.
- Osaat verrata binäärikäännöstä, paravirtualisointia ja laitteistotukea
  niiden hinnan ja vaatimusten kannalta.
