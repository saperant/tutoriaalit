# Laitteet ja ajurit

Tietokonearkkitehtuurin luvussa *Ansat ja I/O* nähtiin laitteiston
puoli: muistiinkuvatut rekisterit, kysely, keskeytykset ja DMA.
Ajuri on se osa ydintä, joka puhuu laitteelle tällä tasolla ja
tarjoaa muulle ytimelle yhtenäisen rajapinnan. Käyttäjälle laite näkyy
tiedostona `/dev`-hakemistossa, ja sitä käytetään samoilla kutsuilla
kuin tavallista tiedostoa. Se, mitä `read` ja `write` laitteelle
tekevät, on ajurin päätös.

## Merkki- ja lohkolaitteet

Unix jakaa laitteet kahteen luokkaan:

| Ominaisuus | Merkkilaite | Lohkolaite |
|-------------|------------------------------|------------------------------|
| Yksikkö | tavuvirta | kiinteän kokoinen lohko |
| Hakeminen | yleensä ei (`lseek` voi olla merkityksetön) | mielivaltainen sijainti |
| Välimuisti | ei ytimen sivuvälimuistia | sivuvälimuisti ja I/O-jono |
| Esimerkit | päätteet, sarjaportit, `/dev/null`, äänikortit | levyt, SSD:t, `loop`-laitteet |

Laitetiedosto ei sisällä dataa. Sen inodessa on tyyppi (merkki tai
lohko) ja *laitenumero*, joka koostuu pää- ja alinumerosta. Pääluku
valitsee ajurin, aliluku laitteen ajurin sisällä. Laitetiedoston
avaus ohjaa kaikki kuvaajan operaatiot tälle ajurille:

```{.c tiedosto="esimerkit/11-laitteet.c" osa="numerot"}
```

Pääluku 1 on ytimen muistilaitteiden ajuri, jonka alilaitteet
toteuttavat pieniä mutta hyödyllisiä käytöksiä:

```{.c tiedosto="esimerkit/11-laitteet.c" osa="kaytos"}
```

```{.tuloste tiedosto="esimerkit/11-laitteet.odotettu"}
```

`/dev/null` nielee kaiken ja on aina lopussa. `/dev/zero` tuottaa
loputtomasti nollia; sen kartoitus muistiin oli ennen
`MAP_ANONYMOUS`-lippua tapa varata nollattua muistia. `/dev/full` on aina täynnä, joten
sillä voi testata, käsitteleekö ohjelma levyn täyttymisen. Komento
`ls -l /dev` näyttää laitenumerot koon paikalla (`1, 3`), ja tiedosto
`/proc/devices` listaa rekisteröidyt ajurit.

Nykyisessä Linuxissa laitetiedostoja ei luoda käsin `mknod`-komennolla,
vaan ydin ilmoittaa laitteista *devtmpfs*-tiedostojärjestelmään ja
`udev` lisää oikeudet ja pysyvät nimet (esimerkiksi
`/dev/disk/by-uuid/…`). Laitepuun kuvaus on hakemistossa `/sys`.

## ioctl

Kaikki laitteen ominaisuudet eivät ole tavuvirtoja. Päätteen
ikkunan koko, sarjaportin nopeus, levyn koko tai kameran resoluutio
ovat asetuksia, joita ei ole luontevaa muuttaa kirjoittamalla
dataa. `ioctl(fd,
komento, argumentti)` on yleinen pakoreitti: komento on ajurin
määrittelemä numero ja argumentti yleensä osoitin rakenteeseen.

`FIONREAD` kertoo, montako tavua on luettavissa ilman estymistä. Se
toimii putkille, soketeille ja päätteille:

```{.c tiedosto="esimerkit/11-ioctl.c" osa="fionread"}
```

### Pseudopääte

Pääte on merkkilaite, jonka ajuri (tty-kerros) hoitaa rivinmuokkauksen,
kaiutuksen, signaalimerkit kuten Ctrl-C ja ikkunan koon. Fyysiset
päätteet ovat harvinaisia, mutta *pseudopääte* (pty) on kaikkialla:
pääteohjelmat, `ssh` ja `tmux` luovat isäntä–orja-parin. Ohjelma
kirjoittaa orjapuolelle kuten päätteelle, ja pääteohjelma lukee ja
kirjoittaa isäntäpuolta. Ikkunan koko asetetaan isännästä ja luetaan
orjasta – juuri näin `ssh` välittää etäkoneelle tiedon ikkunan koon
muutoksesta:

```{.c tiedosto="esimerkit/11-ioctl.c" osa="pty"}
```

Komento, jota laite ei tue, palauttaa virheen `ENOTTY` – nimi on
peräisin ajalta, jolloin ioctl oli lähinnä päätteiden asia:

```{.c tiedosto="esimerkit/11-ioctl.c" osa="tyhja"}
```

```{.tuloste tiedosto="esimerkit/11-ioctl.odotettu"}
```

`ioctl` on käytännöllinen mutta tyypitön: argumentin tyyppi riippuu
komennosta, eikä kääntäjä voi tarkistaa sitä. Uudemmat rajapinnat
suosivat siksi erillisiä järjestelmäkutsuja, `sysfs`-tiedostoja tai
netlink-viestejä.

## Lohkolaitteet ja I/O-jono

Lohkolaitteen ja tiedostojärjestelmän välissä on ytimen lohkokerros.
Tiedostojärjestelmä lähettää sille *pyyntöjä* (`struct bio`):
laite, sektori, suunta ja muistisivut. Lohkokerros yhdistää vierekkäiset
pyynnöt, järjestää ne ja välittää laiteajurille. NVMe-asemille
lohkokerros käyttää monijonoista mallia (blk-mq), jossa jokaisella
suorittimella on oma jononsa suoraan laitteen laitteistojonoon.

Ajurin työ pyynnön valmistuttua kulkee näin: laite tekee
DMA-siirron muistiin ja nostaa keskeytyksen. Keskeytyksen käsittelijä
(*yläpuolisko*) kuittaa laitteen ja ajoittaa loput työstä
*alapuoliskoon* (softirq, tasklet tai työjono), joka suoritetaan
keskeytykset sallittuina. Lopuksi odottava prosessi herätetään
`D`-tilasta.

### Levyn vuorontaminen

Pyörivällä kiintolevyllä pyynnön hinta riippuu siitä, kuinka kauas
lukupään on liikuttava. Pyyntöjen järjestys vaikuttaa siksi
läpäisyyn moninkertaisesti. Klassiset algoritmit:

- **FCFS:** saapumisjärjestys; reilu mutta heiluu levyn päästä päähän.
- **SSTF** (shortest seek time first): lähin ensin; vähän liikettä,
  mutta kaukaiset pyynnöt voivat nääntyä.
- **SCAN** (hissialgoritmi): pää liikkuu yhteen suuntaan levyn reunaan
  asti palvellen matkan varrelta ja kääntyy sitten.
- **C-LOOK:** liikkuu vain yhteen suuntaan ja vain viimeiseen
  pyyntöön asti, sitten hyppää ensimmäiseen. Odotusajat ovat
  tasaisemmat kuin SCANissa, koska levyn keskikohta ei ole etuoikeutettu.

Simulaattori on samaa muotoa kuin luvun 4 vuorontaja: joka
askeleella algoritmi valitsee palvelemattomista pyynnöistä seuraavan,
ja liike lasketaan uran numeroiden erotuksena. Pyyntöjono on
oppikirjojen klassinen:

```{.c tiedosto="esimerkit/11-levyjono.c" osa="aja"}
```

```{.tuloste tiedosto="esimerkit/11-levyjono.odotettu"}
```

![Lukupään reitti neljällä algoritmilla (esimerkin tuloste). FCFS
heiluu levyn päästä päähän, SSTF jättää kaukaisimman pyynnön
viimeiseksi, ja SCAN käy levyn reunassa ennen
kääntymistä.](kuvat/levyjono.png){width=100%}

SSTF vie vain runsaan kolmanneksen FCFS:n liikkeestä. Se palvelee
ensin lähimmät 65 ja 67, kääntyy alas 14:ään ja nousee vasta sitten,
joten kaukaisin 183 jää viimeiseksi. SCAN liikkuu ylös levyn
reunaan (ura 199) asti ja palaa. C-LOOKin luvussa on mukana paluuhyppy
183:sta 14:ään; jos hyppy on nopea (yksi pitkä siirtymä), todellinen
hinta on pienempi.

SSD-levyillä ei ole lukupäätä, ja järjestäminen on lähes hyödytöntä.
Niiden erityispiirre on toinen: flash-muistin lohko on tyhjennettävä
kokonaan ennen uudelleenkirjoitusta, joten aseman oma ohjain
(engl. flash translation layer) kirjoittaa muutokset uuteen paikkaan,
tasaa kulumista ja siivoaa vapautuneita lohkoja taustalla.
Tiedostojärjestelmä auttaa kertomalla `TRIM`-käskyllä, mitkä lohkot
se on vapauttanut.
Linuxin vuorontajat (`mq-deadline`, `bfq`, `kyber` tai `none`)
painottavat siksi muuta: määräaikoja, jotta pyynnöt eivät nääny,
reiluutta prosessien kesken ja lukujen suosimista kirjoitusten edellä.
Nykyinen vuorontaja näkyy tiedostossa
`/sys/block/<laite>/queue/scheduler`.

## Ajurin rakenne

Ajuri rekisteröi itsensä ytimen alijärjestelmään ja täyttää taulukon
funktio-osoittimia. Merkkilaitteen ajurilla se on
`struct file_operations`: `open`, `read`, `write`, `unlocked_ioctl`,
`mmap`, `poll` ja `release`. Kun prosessi kutsuu `read` laitteen
kuvaajalle, VFS kutsuu ajurin `read`-funktiota, joka kopioi datan
laitteen puskurista käyttäjän muistiin `copy_to_user`-funktiolla.
Ajurin virhe on ytimen virhe, minkä vuoksi suuri osa
Linuxin vakausongelmista on ajureissa, ja mikroytimet ajavat ajurit
omina prosesseinaan. Ajurien kirjoittaminen on taidon *Sulautettu
Linux* aihe.

## Käytännössä

- **Käytä `/dev/null`ia, `/dev/zero`a ja `/dev/full`ia testeissä:**
  ne ovat helppo tapa tuottaa tyhjä syöte, nollia tai levyn
  täyttyminen.
- **Kysy päätteeltä, älä oleta:** `isatty` kertoo, onko kuvaaja pääte,
  ja `TIOCGWINSZ` sen koon. Putkeen kirjoittava ohjelma ei saa
  odottaa päätteen ominaisuuksia.
- **Pseudopääte vuorovaikutteisten ohjelmien testaukseen:** ohjelma
  käyttäytyy kuin ihminen kirjoittaisi sille.
- **Valitse levyn vuorontaja laitteen mukaan:** pyörivälle levylle
  `bfq` tai `mq-deadline`, nopealle NVMe:lle usein `none`.

## Itsearviointi

- Osaat erottaa merkki- ja lohkolaitteen sekä lukea laitetiedoston
  pää- ja alinumeron.
- Osaat käyttää `ioctl`-kutsua ja kertoa, miksi se on olemassa ja
  mitä `ENOTTY` tarkoittaa.
- Osaat selittää pseudopäätteen isäntä- ja orjapuolen roolit.
- Osaat laskea FCFS-, SSTF-, SCAN- ja C-LOOK-algoritmien
  lukupään liikkeen annetulle pyyntöjonolle.
- Osaat kuvata pyynnön matkan tiedostojärjestelmästä lohkokerroksen
  ja ajurin kautta laitteelle ja keskeytyksestä takaisin.
