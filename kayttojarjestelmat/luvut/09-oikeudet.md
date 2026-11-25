# Käyttäjät, oikeudet ja suojaus

Johdannossa sanottiin, että ydin estää ohjelmia sotkemasta toisiaan.
Muistin osalta sen tekevät erilliset osoiteavaruudet (luku 5).
Tiedostot, laitteet ja toiset prosessit ovat kuitenkin yhteisiä, joten
niiden kohdalla ytimen on päätettävä jokaisessa järjestelmäkutsussa,
saako juuri tämä prosessi tehdä juuri tämän. Edellinen luku näytti,
että inodessa on omistaja ja oikeudet. Tämä luku kertoo, mihin ydin
niitä vertaa: prosessin tunnisteisiin. Sen jälkeen katsotaan, miten
ohjelma luopuu oikeuksistaan ja miten prosessin näkymää ja
järjestelmäkutsuja voi rajata.

Näkökulma on ytimen mekanismi. Käyttäjien ja ryhmien ylläpito
komentoriviltä (`chmod`, `chown`, `sudo`) kuuluu taitoon *Komentorivi
ja Linux*.

## Tunnisteet prosessissa

Ytimelle käyttäjä on pelkkä numero, *käyttäjätunniste* (UID), ja ryhmä
*ryhmätunniste* (GID). Nimet ovat käyttäjätilan asia: `ls -l` hakee
numerolle nimen tiedostosta `/etc/passwd`, eikä ydin lue tiedostoa
koskaan. Tunniste 0 on *pääkäyttäjä* (root), jolle ydin sallii lähes
kaiken. Jokaisella prosessilla on kolme käyttäjätunnistetta:

| Tunniste | Merkitys | Lukeminen |
|----------------|-----------------------------------------------|------------|
| todellinen (RUID) | kuka prosessin käynnisti | `getuid` |
| tehollinen (EUID) | kenen oikeuksilla ydin tarkistaa kutsut | `geteuid` |
| tallennettu (SUID) | tunniste, johon tehollisen saa vaihtaa takaisin | `getresuid` |

Ryhmille on samat kolme sekä luettelo *lisäryhmiä* (`getgroups`).
Tavallisessa prosessissa kaikki kolme ovat samat. Tunnisteet periytyvät
`fork`-kutsussa ja säilyvät `exec`-kutsussa, joten kirjautumisen
jälkeen jokainen käyttäjän käynnistämä ohjelma kantaa samoja numeroita.
Kolmea tunnistetta tarvitaan vasta, kun ohjelman on tehtävä jotain,
mihin sen käynnistäjällä ei ole oikeutta; siihen palataan kohta.

## Oikeuksien tarkistus

Inodessa on omistajan UID, ryhmän GID ja yhdeksän oikeusbittiä: luku
(`r`), kirjoitus (`w`) ja suoritus (`x`) erikseen omistajalle,
ryhmälle ja muille. Kun prosessi avaa tiedoston, ydin valitsee näistä
kolmesta luokasta *yhden* ja katsoo vain sen bittejä:

```{.dot otsikko="Oikeuksien tarkistus avattaessa. Ensimmäinen sopiva luokka ratkaisee, eikä seuraavia katsota."}
digraph {
  node [shape=box];
  k [label="onko prosessilla\nCAP_DAC_OVERRIDE?", shape=diamond];
  o [label="EUID = tiedoston\nomistaja?", shape=diamond];
  r [label="jokin prosessin ryhmistä\n= tiedoston ryhmä?", shape=diamond];
  s [label="sallitaan"]; ob [label="omistajan bitit\nratkaisevat"];
  rb [label="ryhmän bitit\nratkaisevat"]; mb [label="muiden bitit\nratkaisevat"];
  k -> o [label="ei"]; o -> r [label="ei"]; r -> mb [label="ei"];
  k -> s [label="on"]; o -> ob [label="kyllä"]; r -> rb [label="kyllä"];
  { rank=same; k; s; } { rank=same; o; ob; } { rank=same; r; rb; }
}
```

Järjestyksellä on seuraus, joka yllättää: jos omistajan bitit
kieltävät luvun, omistaja ei saa lukea, vaikka muiden bitit
sallisivat sen. Esimerkki kokeilee tätä funktiolla, joka yrittää
avata tiedoston ja palauttaa virhekoodin nimen:

```{.c tiedosto="esimerkit/09-oikeudet.c" osa="kokeile"}
```

```{.c tiedosto="esimerkit/09-oikeudet.c" osa="luokka"}
```

```{.tuloste tiedosto="esimerkit/09-oikeudet.odotettu" rivit="1-4"}
```

Tilalla 0004 kuka tahansa muu saisi lukea tiedoston, mutta omistaja
ei. Omistaja voi tosin aina muuttaa bitit `chmod`-kutsulla, koska
siihen riittää omistajuus.

Tarkistus tehdään vain avattaessa. Sen jälkeen kuvaaja on *valtakirja*:
`read` ja `write` eivät katso oikeuksia uudelleen, vaikka tiedoston
bitit muuttuisivat tai kuvaaja siirtyisi toiselle prosessille
`fork`-kutsussa tai UNIX-soketin kautta (luku 12). Tähän perustuu
tavallinen rakenne, jossa etuoikeutettu prosessi avaa resurssin ja
antaa rajoitetulle prosessille pelkän kuvaajan.

### umask

Tiedostoa luotaessa `open` saa pyydetyt oikeusbitit, mutta ydin
poistaa niistä prosessin *umask*-arvon bitit. Maski periytyy lapsille,
ja sen tarkoitus on, ettei jokaisen ohjelman tarvitse päättää,
kuinka avoimia käyttäjän tiedostot ovat:

```{.c tiedosto="esimerkit/09-oikeudet.c" osa="umask"}
```

```{.tuloste tiedosto="esimerkit/09-oikeudet.odotettu" rivit="5-6"}
```

### Hakemiston bitit

Hakemisto on luettelo nimistä (luku 8), ja sen bitit koskevat
luetteloa, eivät tiedostoja:

| Bitti | Hakemistossa |
|-------|------------------------------------------------------------|
| `r` | nimien luettelointi (`readdir`) |
| `w` | nimien lisääminen ja poistaminen (`open(O_CREAT)`, `unlink`, `rename`) |
| `x` | *haku*: nimen selvittäminen polun osana |

Polkua selvittäessään ydin vaatii hakuoikeuden jokaiseen polun
hakemistoon. Tiedoston poistaminen on hakemiston muutos, joten siihen
tarvitaan hakemiston kirjoitusoikeus, ei tiedoston:

```{.c tiedosto="esimerkit/09-oikeudet.c" osa="hakemisto"}
```

```{.tuloste tiedosto="esimerkit/09-oikeudet.odotettu" rivit="7-11"}
```

Ilman hakuoikeutta tiedostoon ei pääse, vaikka sen omat bitit
sallisivat luvun. Pelkällä hakuoikeudella tiedoston saa auki, jos
tietää nimen, mutta nimiä ei voi luetella. Koska kirjoitusoikeus
hakemistoon riittää minkä tahansa nimen poistamiseen, yhteisissä
hakemistoissa kuten `/tmp` on lisäksi *tahmabitti* (engl. sticky bit,
tila 1777): nimen saa poistaa vain tiedoston tai hakemiston omistaja.

### EACCES ja EPERM

Ydin ilmoittaa kiellosta kahdella virhekoodilla. `EACCES` tarkoittaa,
että oikeusbitit eivät salli pyyntöä tälle prosessille. `EPERM`
tarkoittaa, että operaatio vaatii etuoikeuden, jota prosessilla ei
ole, bittien arvosta riippumatta:

```{.c tiedosto="esimerkit/09-oikeudet.c" osa="eperm"}
```

```{.tuloste tiedosto="esimerkit/09-oikeudet.odotettu" rivit="12-14"}
```

Tiedoston omistajaa ei saa vaihtaa edes omistaja itse, koska muuten
levykiintiön ja vastuun voisi siirtää toiselle. Signaaleissa sääntö on
samaa lajia: `kill` onnistuu, kun lähettäjän todellinen tai tehollinen
UID on sama kuin kohteen todellinen tai tallennettu UID (luku 13).

### Pääkäyttäjä ja esimerkkien ajaminen

Kaavion ensimmäinen ehto ohittaa bitit kokonaan: pääkäyttäjän
prosessi saa lukea ja kirjoittaa mitä tahansa. Siksi edellä näytetyt
kokeet on ajettava tavallisena käyttäjänä. Esimerkit testataan sekä
tavallisena käyttäjänä että kehityskontissa, jossa ne käynnistyvät
pääkäyttäjänä, joten pääohjelma tekee kokeet lapsiprosessissa, joka
luopuu ensin oikeuksistaan:

```{.c tiedosto="esimerkit/09-oikeudet.c" osa="main"}
```

Oikeusbitit ovat *harkinnanvaraista pääsynvalvontaa* (engl.
discretionary access control, DAC): omistaja päättää tiedostonsa
oikeuksista itse. Niiden rinnalla Linuxissa on kaksi laajennusta.
*Pääsylistat* (POSIX ACL, `setfacl`) antavat oikeuksia nimetyille
käyttäjille ja ryhmille kolmea luokkaa tarkemmin. *Pakollinen
pääsynvalvonta* (MAC; SELinux, AppArmor) tarkistaa lisäksi koko
järjestelmän säännöstön, jota tiedoston omistaja ei voi ohittaa, ei
edes pääkäyttäjänä. Ytimessä nämä kytkeytyvät samoihin kohtiin kuin
bittien tarkistus (Linux Security Modules).

## Setuid-ohjelmat ja oikeuksien pudotus

Joskus tavallisen käyttäjän on tehtävä jotain, mihin hänen
oikeutensa eivät riitä: salasanan vaihto kirjoittaa tiedostoon, jonka
vain pääkäyttäjä saa avata. Unixin ratkaisu on tiedoston
*setuid-bitti* (tila 4000). Kun ydin suorittaa `exec`-kutsulla
ohjelman, jossa bitti on asetettu, prosessin teholliseksi ja
tallennetuksi tunnisteeksi tulee *tiedoston omistaja*; todellinen
tunniste säilyy. Ohjelmat `passwd` ja `sudo` toimivat näin.

Tällainen ohjelma ajaa jonkun toisen syötteellä pääkäyttäjän
oikeuksin, joten jokainen virhe siinä on virhe pääkäyttäjän
oikeuksilla. Siksi ohjelma tekee etuoikeutetun työnsä heti alussa ja
luopuu sitten oikeuksista. Esimerkin lapsiprosessi asetetaan
`setresuid`-kutsulla samaan tilaan, jossa pääkäyttäjän omistama
setuid-ohjelma käynnistyy, ja se käy läpi molemmat pudotustavat:

```{.c tiedosto="esimerkit/09-tunnisteet.c" osa="setuid"}
```

```{.tuloste tiedosto="esimerkit/09-tunnisteet.odotettu" rivit="1-12"}
```

Tulosteesta näkyy kolme asiaa:

- **Ydin tarkistaa tehollisella tunnisteella.** Käynnistyksessä avaus
  onnistuu, vaikka käynnistäjä on tavallinen käyttäjä. `access` käyttää
  poikkeuksellisesti todellista tunnistetta: sillä setuid-ohjelma voi
  kysyä, saisiko käynnistäjä itse avata tiedoston. Kysymyksen ja
  avauksen välissä tiedosto voi kuitenkin vaihtua, joten luotettavampi
  tapa on pudottaa oikeudet ja avata tiedosto.
- **Tilapäinen pudotus on peruttavissa.** `seteuid` vaihtaa vain
  tehollisen tunnisteen, ja koska tallennettu on yhä 0, paluu onnistuu.
  Tämä suojaa ohjelman omilta virheiltä mutta ei tilanteessa, jossa
  ohjelman hallinta on menetetty.
- **Pysyvä pudotus ei ole.** Kun pääkäyttäjä kutsuu `setuid`-funktiota,
  kaikki kolme tunnistetta vaihtuvat, eikä takaisin ole paluuta.

Pudotuksen järjestys on tarkka: ensin lisäryhmät, sitten ryhmä ja
viimeisenä käyttäjä. Esimerkkien yhteinen apufunktio tekee sen näin:

```{.c tiedosto="esimerkit/kayttaja.h" osa="pudotus"}
```

Jos käyttäjä vaihdetaan ensin, ryhmän vaihto epäonnistuu ja prosessi
jää ajamaan pääkäyttäjän ryhmässä:

```{.c tiedosto="esimerkit/09-tunnisteet.c" osa="jarjestys"}
```

```{.tuloste tiedosto="esimerkit/09-tunnisteet.odotettu" rivit="13-15"}
```

Virhe jää huomaamatta, jos paluuarvoa ei tarkisteta, ja juuri siksi
jokaisen tunnisteita vaihtavan kutsun tulos on tarkistettava.

Setuid-ohjelma perii käynnistäjältään ympäristömuuttujat, avoimet
kuvaajat ja työhakemiston, joihin se ei voi luottaa. Dynaaminen
linkittäjä jättää siksi setuid-ohjelmassa huomiotta muuttujat kuten
`LD_PRELOAD` (ks. taito *Objektitiedostot, linkitys ja ABI*), ja
liitosvalinta `nosuid` poistaa bitin vaikutuksen kokonaan esimerkiksi
siirrettäviltä levyiltä.

Tunnisteita vaihtavat esimerkit tarvitsevat alkuun pääkäyttäjän
oikeudet. Tavallisena käyttäjänä käynnistettynä ne käynnistävät
itsensä uudelleen `sudo`-komennolla, joka on itse setuid-ohjelma:

```{.c tiedosto="esimerkit/kayttaja.h" osa="sudo"}
```

## Kyvyt

Setuid-ohjelma saa kaikki pääkäyttäjän oikeudet, vaikka se
tarvitsisi niistä yhden. Linux jakaa pääkäyttäjän oikeudet noin
neljäänkymmeneen *kykyyn* (engl. capability), ja ytimen tarkistukset
kysyvät yksittäistä kykyä, eivät tunnistetta 0:

| Kyky | Sallii |
|------------------------|------------------------------------------------|
| `CAP_DAC_OVERRIDE` | tiedostojen oikeusbittien ohituksen |
| `CAP_CHOWN` | tiedoston omistajan vaihdon |
| `CAP_KILL` | signaalin lähettämisen kenen tahansa prosessille |
| `CAP_NET_BIND_SERVICE` | sitoutumisen portteihin alle 1024 |
| `CAP_SYS_NICE` | prioriteetin noston ja reaaliaikaluokat (luku 4) |
| `CAP_SETUID` | tunnisteiden vapaan vaihdon |
| `CAP_SYS_ADMIN` | liitokset, nimiavaruudet ja suuri joukko muuta |

Jokaisella säikeellä on *sallittu* joukko (kyvyt, jotka se voi ottaa
käyttöön) ja *tehollinen* joukko (kyvyt, joita ydin juuri nyt
tarkistaa). Pääkäyttäjän prosessilla molemmat ovat täynnä. Kun
kaikki tunnisteet vaihtuvat nollasta muuksi, ydin tyhjentää joukot,
ellei prosessi ole pyytänyt säilyttämään sallittua joukkoa
(`PR_SET_KEEPCAPS`). Esimerkin apufunktiot lukevat ja asettavat joukot
järjestelmäkutsuilla `capget` ja `capset`:

```{.c tiedosto="esimerkit/09-kyvyt.c" osa="joukot"}
```

Kolme lapsiprosessia yrittää samaa kahta asiaa: lähettää signaalin 0
(pelkkä oikeuksien tarkistus) pääkäyttäjän prosessille ja avata
tiedoston, jonka vain pääkäyttäjä saa lukea:

```{.c tiedosto="esimerkit/09-kyvyt.c" osa="lapset"}
```

```{.tuloste tiedosto="esimerkit/09-kyvyt.odotettu"}
```

Kolmas prosessi on tavallinen käyttäjä, jolla on täsmälleen yksi
pääkäyttäjän oikeus. Sama ajatus toimii tiedostoissa: ohjelmatiedostoon
voi liittää kykyjä (`setcap`), jolloin `exec` antaa ne prosessille
ilman setuid-bittiä. Esimerkiksi `ping` tarvitsi aikanaan
setuid-bitin raakasokettia varten; nykyään riittää yksi kyky tai ei
sitäkään.

Kyky ei silti ole automaattisesti pieni oikeus. `CAP_SETUID`,
`CAP_DAC_OVERRIDE` ja `CAP_SYS_ADMIN` riittävät kukin käytännössä koko
järjestelmän hallintaan, joten palvelulle annetaan vain ne kyvyt,
joita sen tehtävä vaatii. *Rajaava joukko* (engl. bounding set)
asettaa lisäksi katon sille, mitä kykyjä prosessi ja sen jälkeläiset
voivat koskaan saada; kontit käynnistetään tyypillisesti supistetulla
rajaavalla joukolla.

## Resurssirajat

Oikeudet kertovat, mihin prosessi saa koskea. *Resurssirajat* kertovat,
kuinka paljon se saa kuluttaa. Jokaisella rajalla on kaksi arvoa:
*pehmeä* raja on voimassa oleva, ja *kova* raja on katto, johon asti
prosessi saa pehmeää nostaa. Kovaa rajaa tavallinen prosessi voi vain
laskea. Rajat asetetaan `setrlimit`-kutsulla (kuoressa `ulimit`), ja
ne periytyvät lapsille:

| Raja | Rajoittaa | Ylitys |
|-----------------|-----------------------------------|------------------------|
| `RLIMIT_NOFILE` | avointen kuvaajien määrää | `EMFILE` |
| `RLIMIT_NPROC` | käyttäjän prosessien määrää | `fork`: `EAGAIN` |
| `RLIMIT_AS` | osoiteavaruuden kokoa | `mmap`: `ENOMEM` |
| `RLIMIT_STACK` | pääsäikeen pinon kokoa | `SIGSEGV` |
| `RLIMIT_FSIZE` | luotavan tiedoston kokoa | `SIGXFSZ`, `EFBIG` |
| `RLIMIT_CORE` | muistivedoksen kokoa | vedos katkaistaan |

```{.c tiedosto="esimerkit/09-rajat.c" osa="koko"}
```

```{.c tiedosto="esimerkit/09-rajat.c" osa="kova"}
```

```{.tuloste tiedosto="esimerkit/09-rajat.odotettu"}
```

Kirjoitus katkesi rajalle (osittainen kirjoitus, luku 8), ja seuraava
epäonnistui. Kovan rajan nosto vaatii kyvyn `CAP_SYS_RESOURCE`.
Resurssirajat koskevat yhtä prosessia kerrallaan (`RLIMIT_NPROC`
käyttäjää), joten ne eivät rajoita sitä, mitä sata lapsiprosessia
kuluttaa yhteensä. Siihen tarvitaan seuraavan osion cgroupit.

## Eristys: nimiavaruudet, cgroupit ja seccomp

Tunnisteet ja oikeusbitit vastaavat kysymykseen *saako tämä käyttäjä
koskea tähän*. Kun samalla koneella ajetaan toisistaan
riippumattomia palveluja, halutaan lisäksi rajata, mitä prosessi
ylipäätään näkee ja mitä kutsuja se voi tehdä. Linuxin ytimessä
siihen on kolme mekanismia.

**Nimiavaruudet** (engl. namespaces) antavat prosessiryhmälle oman
näkymän johonkin ytimen nimistöön. Niitä luodaan kutsuilla `clone` ja
`unshare`:

| Nimiavaruus | Oma näkymä |
|-------------|-----------------------------------------------------|
| liitos (mount) | liitetyt tiedostojärjestelmät, juurihakemisto |
| PID | prosessinumerot; ensimmäinen prosessi on PID 1 |
| verkko | verkkolaitteet, osoitteet, reititys, portit |
| käyttäjä | UID- ja GID-numerot sekä kyvyt |
| IPC, UTS, cgroup, aika | jaettu muisti ja jonot, konenimi, cgroup-puu, kellot |

Käyttäjänimiavaruudessa prosessi voi olla UID 0 ja omistaa kaikki
kyvyt, vaikka se on ulkopuolelta katsoen tavallinen käyttäjä. Sen
kyvyt koskevat vain kyseisen nimiavaruuden omia resursseja.

**Cgroupit** (engl. control groups) mittaavat ja rajoittavat
prosessiryhmän yhteistä kulutusta: suoritinaikaa (luvun 4
ryhmävuorontaminen), muistia (ylitys herättää ryhmän sisäisen OOM
killerin), levy-I/O:ta ja prosessien määrää. Ryhmät muodostavat
puun tiedostojärjestelmässä `/sys/fs/cgroup`.

**Seccomp** rajaa, mitä järjestelmäkutsuja prosessi saa tehdä. Prosessi
asentaa itselleen suodattimen, pienen BPF-ohjelman, jonka ydin ajaa
jokaisen kutsun alussa. Suodatin voi sallia kutsun, palauttaa virheen
tai lopettaa prosessin. Suodatinta ei voi poistaa, ja se periytyy
lapsille:

```{.c tiedosto="esimerkit/09-seccomp.c" osa="suodatin"}
```

```{.c tiedosto="esimerkit/09-seccomp.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/09-seccomp.odotettu"}
```

Näin ohjelma, joka käsittelee epäluotettavaa syötettä, voi alustuksen
jälkeen luopua kaikesta, mitä se ei enää tarvitse: selaimet rajaavat
sivuja piirtävät prosessinsa, ja OpenSSH rajaa kirjautumista
edeltävän vaiheen. Oikeat suodattimet kirjoitetaan sallittujen
kutsujen luettelona, jolloin uusi tuntematon kutsu on oletuksena
kielletty.

Kutsun on läpäistävä kaikki kerrokset, eikä yksikään niistä korvaa
toista. Seccomp päättää, saako kutsun tehdä lainkaan, ja nimiavaruus,
mihin tiedostoon polku tässä näkymässä osoittaa. Sen jälkeen
tarkistetaan tunnisteet, oikeusbitit ja kyvyt, sitten pakollisen
pääsynvalvonnan säännöt, ja lopuksi kuvaajan on mahduttava
resurssirajoihin:

```{.dot otsikko="Tarkistukset, jotka open-kutsu kohtaa. Järjestys on periaatteellinen; olennaista on, että jokainen kerros voi kieltää kutsun yksin."}
digraph {
  rankdir=LR; node [shape=box];
  a [label="seccomp"]; b [label="nimiavaruus"];
  c [label="tunnisteet,\nbitit, kyvyt"]; d [label="SELinux tai\nAppArmor"];
  e [label="resurssirajat,\ncgroupit"]; f [label="kuvaaja", shape=ellipse];
  a -> b -> c -> d -> e -> f;
}
```

*Kontti* on tavallinen prosessi, jolle on annettu omat nimiavaruudet,
cgroup, supistetut kyvyt ja seccomp-suodatin. Kontin rakentaminen
näistä osista käsin on taidon *Virtualisointi* aihe, ja konttien käyttö
taidon *Kontit ja pilvi-infrastruktuuri*.

## Käytännössä

- **Pienin riittävä oikeus:** aja palvelu omalla tunnisteellaan, anna
  sille vain tarvittavat kyvyt ja avaa etuoikeutetut resurssit ennen
  pudotusta.
- **Pudota oikeudet pysyvästi ja oikeassa järjestyksessä:** lisäryhmät,
  ryhmä, käyttäjä. Tarkista jokainen paluuarvo ja varmista lopuksi,
  ettei paluu onnistu.
- **Avaa, älä kysy:** `access`-kutsun ja avauksen välissä tilanne voi
  muuttua. Tee operaatio niillä oikeuksilla, joilla se kuuluu tehdä,
  ja käsittele virhe.
- **Hakemiston oikeudet ovat osa tiedoston suojaa:** kirjoitusoikeus
  hakemistoon riittää tiedoston korvaamiseen toisella.
- **`EACCES` vai `EPERM`:** ensimmäinen korjataan oikeusbiteillä,
  jälkimmäinen vaatii etuoikeuden tai toisen suunnittelun.
- **Aseta rajat ennen kuin niitä tarvitaan:** kuvaajien ja prosessien
  määrän raja pysäyttää vuodon ennen kuin se kaataa koko koneen.

## Itsearviointi

- Osaat selittää prosessin todellisen, tehollisen ja tallennetun
  tunnisteen ja kertoa, mitä niistä ydin käyttää oikeuksien
  tarkistukseen.
- Osaat ennustaa, salliiko ydin tiedoston avauksen, kun tiedät
  prosessin tunnisteet sekä tiedoston ja polun hakemistojen bitit.
- Osaat selittää hakemiston luku-, kirjoitus- ja hakuoikeuden sekä
  umaskin vaikutuksen.
- Osaat erottaa virheet `EACCES` ja `EPERM`.
- Osaat kuvata setuid-ohjelman toiminnan ja pudottaa oikeudet
  pysyvästi oikeassa järjestyksessä.
- Osaat selittää, mitä kyvyt ovat ja miksi ne korvaavat setuid-bitin.
- Osaat asettaa resurssirajan ja kertoa pehmeän ja kovan rajan eron.
- Osaat kuvata, mitä nimiavaruudet, cgroupit ja seccomp rajaavat ja
  miten kontti rakentuu niistä.
