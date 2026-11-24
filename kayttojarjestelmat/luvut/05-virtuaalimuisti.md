# Virtuaalimuisti ja muistikartoitukset

Tietokonearkkitehtuurin luvussa *Virtuaalimuisti* nähtiin, miten
laitteisto muuntaa virtuaalisen osoitteen fyysiseksi: sivutaulu,
Sv32:n kaksitasoinen haku ja TLB. Laitteisto ei kuitenkaan päätä,
mitä sivutauluihin kirjoitetaan. Sen tekee ydin, ja sen keinot ovat
sivuvirhe ja laiska varaus. Tässä luvussa katsotaan virtuaalimuistia
ytimen ja ohjelmoijan puolelta.

## Osoiteavaruuden alueet

Ydin ei pidä kirjaa prosessin muistista sivu kerrallaan vaan
*alueina* (Linuxissa `vm_area_struct`, VMA): yhtenäinen virtuaalinen
väli, jolla on oikeudet (luku, kirjoitus, suoritus), tyyppi (jaettu
tai yksityinen) ja tausta (tiedosto tai anonyymi muisti). Sivutaulut
ovat vain välimuisti alueiden kuvauksesta: ne täytetään vähitellen,
kun sivuja käytetään. Alueet näkyvät tiedostossa `/proc/<pid>/maps`.

Esimerkin funktio `alue` lukee tiedoston rivi kerrallaan ja etsii
rivin, jonka osoiteväliin annettu osoite kuuluu. Osoitteet vaihtuvat
joka ajossa osoiteavaruuden satunnaistuksen (ASLR) takia, joten
tulostetaan vain oikeudet ja alueen alkuperä:

```{.c tiedosto="esimerkit/05-kartta.c" osa="kartta"}
```

```{.tuloste tiedosto="esimerkit/05-kartta.odotettu"}
```

Ohjelmatiedosto on kartoitettu useana alueena: koodi luku- ja
suoritusoikeuksin, vakiot vain luettavaksi ja muuttujat
kirjoitettavaksi. Kirjain `p` tarkoittaa yksityistä kartoitusta.
`mprotect` muuttaa alueen oikeuksia, ja ydin jakaa alueen tarvittaessa
kahtia. Tiedoston kartoittamisesta alueiksi kertoo tarkemmin taito
*Objektitiedostot, linkitys ja ABI*.

## mmap

`mmap` luo uuden alueen. Sen tärkeimmät valinnat ovat:

| Lippu | Merkitys |
|------------------|------------------------------------------------------|
| `MAP_ANONYMOUS` | ei tiedostoa; sivut alkavat nollina |
| `MAP_PRIVATE` | omat muutokset eivät näy muille (copy-on-write) |
| `MAP_SHARED` | muutokset näkyvät muille kartoittajille ja tiedostossa |
| `MAP_FIXED` | täsmälleen annettuun osoitteeseen (korvaa vanhan) |
| `MAP_POPULATE` | täytä sivutaulut heti, ei laiskasti |

Anonyymi yksityinen kartoitus on ohjelman tavallista muistia: suuret
`malloc`-varaukset tehdään sillä, ja säikeiden pinot ovat sellaisia.

### Laiska varaus ja sivuvirheet

`mmap` varaa osoiteavaruutta, ei fyysistä muistia. Sivu syntyy vasta,
kun sitä käytetään ensimmäisen kerran: MMU ei löydä sivutaulusta
merkintää ja nostaa sivuvirheen, ydin toteaa osoitteen kuuluvan
alueeseen, varaa nollatun kehyksen, kirjoittaa sivutaulumerkinnän ja
palaa uusimaan käskyn. Ohjelma ei huomaa mitään muuta kuin viiveen.

Esimerkki käyttää kahta mittaria. `mincore` kertoo sivu kerrallaan,
onko sivu fyysisessä muistissa, ja `getrusage` laskee prosessin
sivuvirheet. Virheet jaetaan *pieniin* (engl. minor), jotka ratkeavat
ilman levyä, ja *suuriin* (major), jotka odottavat levyltä lukua.
Esimerkin apufunktiot `muistissa` ja `sivuvirheet` lukevat nämä:

```{.c tiedosto="esimerkit/05-mmap.c" osa="anonyymi"}
```

`MADV_NOHUGEPAGE` pyytää ydintä käyttämään vain tavallisia 4 KiB:n
sivuja. Muuten ydin voisi täyttää alueen 2 MiB:n jättisivuilla
(transparent huge pages), jolloin yksi sivuvirhe toisi muistiin 512
sivua kerralla. `MADV_DONTNEED` palauttaa sivut ytimelle; seuraava
luku saa uuden nollasivun.

Laiska varaus mahdollistaa *ylivarauksen* (engl. overcommit): Linux
antaa oletuksena varata enemmän muistia kuin koneessa on, koska
harva ohjelma koskee kaikkeen varaamaansa. Jos sivuja kuitenkin
tarvitaan enemmän kuin niitä on, ydin valitsee uhrin ja lopettaa sen
(OOM killer). Käytäntöä säätää `/proc/sys/vm/overcommit_memory`.

### Tiedoston kartoitus

Tiedoston voi kartoittaa muistiin, jolloin luku ja kirjoitus ovat
tavallisia muistioperaatioita. Sivut tulevat ytimen sivuvälimuistista
(engl. page cache): samaa tiedostoa kartoittavat prosessit näkevät
samat fyysiset sivut, eikä dataa kopioida käyttäjän puskuriin.
Jaetussa kartoituksessa kirjoitus päätyy tiedostoon; yksityisessä
kirjoittaja saa oman kopion sivusta:

```{.c tiedosto="esimerkit/05-mmap.c" osa="tiedosto"}
```

```{.tuloste tiedosto="esimerkit/05-mmap.odotettu"}
```

Yksityinen kartoitus näkee jaetun kirjoituksen niin kauan, kuin se
ei ole kirjoittanut sivuun itse – se jakaa saman sivun
sivuvälimuistista. Ensimmäinen kirjoitus kopioi sivun, ja siitä
alkaen sen muutokset ovat omia. `msync` pakottaa likaiset sivut
levylle; ilman sitä ydin kirjoittaa ne aikanaan itse. Näin
dynaaminen linkittäjä kartoittaa jaetut kirjastot: koodisivut ovat
kaikille yhteisiä, ja vain muutetut datasivut kopioidaan.

## Copy-on-write ja fork

`fork` ei kopioi vanhemman muistia. Ydin kopioi vain sivutaulut ja
merkitsee kirjoitettavat yksityiset sivut molemmissa vain luettaviksi.
Kun jompikumpi kirjoittaa, syntyy suojausvirhe; ydin huomaa, että
alue sallii kirjoituksen ja sivu on copy-on-write, kopioi sivun ja
antaa kirjoittajalle oman kirjoitettavan kopion. Jos sivulla on enää
yksi käyttäjä, kopiota ei tarvita, ja merkintä vain palautetaan
kirjoitettavaksi.

```{.c tiedosto="esimerkit/05-cow.c" osa="cow"}
```

```{.tuloste tiedosto="esimerkit/05-cow.odotettu"}
```

Lapsen lukeminen ei aiheuta kopioita, kirjoittaminen aiheuttaa yhden
sivuvirheen sivua kohti, ja vanhemman data säilyy. Siksi `fork`
suurestakin prosessista on nopea, ja `fork` + `exec` ei kopioi juuri
mitään. Copy-on-write on myös syy siihen, että Redisin kaltaiset
palvelut voivat ottaa tilannevedoksen muistista forkkaamalla: lapsi
näkee jäädytetyn kopion, ja vain muuttuneet sivut kopioidaan.

## Suojausvirhe

Jos osoite ei kuulu mihinkään alueeseen tai alue ei salli
operaatiota, ydin ei voi korjata virhettä. Se lähettää prosessille
signaalin `SIGSEGV`, joka oletuksena lopettaa prosessin. Laitteiston
kannalta tämä on sama sivuvirhe kuin laiska varaus; ero on vain
siinä, mitä ydin löytää aluekuvauksista.

```{.c tiedosto="esimerkit/05-suojaus.kaatuu.c" osa="suojaus"}
```

AddressSanitizer sieppaa signaalin ja kertoo, että kyseessä oli
kirjoitus:

```text
==1234==ERROR: AddressSanitizer: SEGV on unknown address 0x7f2688...
==1234==The signal is caused by a WRITE memory access.
```

Sama mekanismi tekee pinon ylivuodosta turvallisen: pinon alapuolella
on suojasivu ilman oikeuksia, ja siihen osuminen kaatuu heti eikä
turmele muuta muistia.

## Sivuvirheen käsittely kokonaisuudessaan

| Tilanne | Ytimen toiminta | Signaali |
|---------|-----------------|----------|
| alue on, sivua ei vielä ole (anonyymi) | nollattu kehys | – |
| alue on, sivu tiedostossa | sivuvälimuisti tai levyltä luku | – |
| kirjoitus copy-on-write-sivuun | kopio tai oikeuden palautus | – |
| sivu sivutettu heittovaihtoon | luku swap-alueelta | – |
| ei aluetta tai oikeus puuttuu | – | `SIGSEGV` |
| tiedosto lyheni kartoituksen alta | – | `SIGBUS` |

Taulukon tapaukset päätöspuuna, siinä järjestyksessä kuin ydin ne
tutkii:

```{.dot otsikko="Sivuvirheen käsittely"}
digraph {
  node [fontsize=9];
  edge [fontsize=8];
  virhe [label="sivuvirhe\n(osoite, luku/kirjoitus)"];
  alue [label="kuuluuko osoite\njohonkin alueeseen?", shape=diamond, style=filled];
  oik [label="salliiko alue\nkäytön?", shape=diamond, style=filled];
  segv [label="SIGSEGV", fillcolor="#F2D4D4"];
  cow [label="kirjoitus\nCOW-sivuun?", shape=diamond, style=filled];
  kopio [label="kopioi kehys\ntai palauta oikeus"];
  tausta [label="sivun lähde?", shape=diamond, style=filled];
  nolla [label="nollattu\nkehys"]; tied [label="sivuvälimuisti\ntai levy"];
  swap [label="heittovaihto-\nalue"];
  valmis [label="päivitä sivutaulu,\njatka käskystä"];
  virhe -> alue;
  alue -> segv [label="ei"]; alue -> oik [label="kyllä"];
  oik -> segv [label="ei"]; oik -> cow [label="kyllä"];
  cow -> kopio [label="kyllä"]; cow -> tausta [label="ei"];
  tausta -> nolla [label="anonyymi"]; tausta -> tied [label="tiedosto"];
  tausta -> swap [label="sivutettu"];
  kopio -> valmis; nolla -> valmis; tied -> valmis; swap -> valmis;
}
```

Muistiin mahtumattomat sivut ydin voi kirjoittaa heittovaihtoalueelle
(engl. swap) tai, jos sivu on muuttumaton tiedoston sivu, yksinkertaisesti
hylätä. Se, mitkä sivut valitaan, on luvun 6 aihe.

## Käytännössä

- **Varaus ei ole käyttöä:** RSS (fyysinen muisti) ja VSZ
  (osoiteavaruus) eroavat suuresti, eikä suuri VSZ ole ongelma.
- **Kartoita suuret tiedostot:** `mmap` välttää kopion käyttäjän
  puskuriin ja jakaa sivut prosessien kesken. Varo `SIGBUS`ia, jos
  tiedosto voi lyhentyä.
- **Muista `msync` ja `munmap`:** jaetun kartoituksen muutokset eivät
  ole levyllä ennen synkronointia.
- **Mittaa sivuvirheillä:** suuri määrä pieniä sivuvirheitä alussa on
  normaalia; suuret sivuvirheet kesken ajon kertovat muistipulasta.
- **`fork` on halpa, kirjoittaminen sen jälkeen ei:** lapsi, joka
  kirjoittaa koko keon yli, kopioi sen sivu kerrallaan.

## Itsearviointi

- Osaat selittää, miten ydin kuvaa osoiteavaruuden alueina ja miten
  ne näkyvät tiedostossa `/proc/<pid>/maps`.
- Osaat käyttää `mmap`-kutsua anonyymiin ja tiedostoon perustuvaan
  kartoitukseen ja valita jaetun tai yksityisen kartoituksen.
- Osaat kuvata laiskan varauksen ja sivuvirheen käsittelyn sekä
  mitata sivuvirheet.
- Osaat selittää copy-on-writen toiminnan forkissa ja yksityisessä
  tiedostokartoituksessa.
- Osaat erottaa korjattavan sivuvirheen suojausvirheestä ja kertoa,
  milloin syntyy `SIGSEGV` ja milloin `SIGBUS`.
