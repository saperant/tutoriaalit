# Suojaukset

Kääntäjä, linkkeri ja käyttöjärjestelmä lisäävät ohjelmaan suojauksia,
jotka eivät korjaa virheitä mutta rajaavat niiden seurauksia. Ne
muuttavat hyödynnettävän muistivirheen useimmiten hallituksi
kaatumiseksi tai ainakin tekevät hyödyntämisestä paljon työläämpää.
Tämä luku käy läpi tärkeimmät, näyttää jokaisen laukeavan ja tarkistaa,
mitkä niistä valmis ohjelma sisältää.

| Suojaus | Mitä estää | Kuka toteuttaa |
|---------|-----------|----------------|
| pinokanari | jatkuvan pinoylivuodon paluuosoitteeseen | kääntäjä |
| NX / DEP | datan suorittamisen koodina | prosessori, ydin, linkkeri |
| ASLR | osoitteiden ennustamisen | ydin, PIE-käännös |
| RELRO | GOT:n ja muiden taulujen ylikirjoituksen | linkkeri, ld.so |
| FORTIFY_SOURCE | tunnetun kokoisen puskurin ylityksen kirjastokutsuissa | glibc, kääntäjä |
| CFI, CET, PAC | ohjausvuon kaappauksen | kääntäjä, prosessori |

Pinokanari käsiteltiin luvussa 3 ja ohjausvuon eheys tulee luvussa 7.

Suojaukset ovat kerroksia, eivät vaihtoehtoja. Jokainen pysäyttää
virheen eri vaiheessa, ja seuraava kerros on sitä varten, että
edellinen pettää:

```{.dot otsikko="Puolustuksen kerrokset virheen elinkaaren mukaan. Mitä aikaisemmin virhe pysähtyy, sitä halvempi se on; tämän luvun ja luvun 7 suojaukset ovat kolmas ja neljäs kerros."}
digraph {
  nodesep=0.25; ranksep=0.22;
  node [width=2.2];
  v1 [label="virhe kirjoitetaan"]; v2 [label="virhe on koodissa"];
  v3 [label="muisti korruptoituu ajossa"];
  v4 [label="ohjausvuo yritetään kaapata"];
  v5 [label="prosessi on vieraan vallassa"];
  v1 -> v2 -> v3 -> v4 -> v5;
  node [shape=plain, style="", width=0];
  s1 [label="1. turvalliset rajapinnat, varoitukset,\lmuistiturvallinen kieli (luku 2)\l"];
  s2 [label="2. staattinen analyysi, sanitoijat, fuzzaus,\lkatselmointi (luvut 2, 8 ja 9)\l"];
  s3 [label="3. pinokanari, FORTIFY_SOURCE,\lvaraajan tarkistukset (luvut 3, 4 ja 6)\l"];
  s4 [label="4. NX, ASLR ja PIE, RELRO,\lCFI, CET, PAC (luvut 6 ja 7)\l"];
  s5 [label="5. vähimmät oikeudet, hiekkalaatikko,\lavainten erottelu\l"];
  edge [arrowhead=none, style=dashed];
  { rank=same; v1 -> s1; }
  { rank=same; v2 -> s2; }
  { rank=same; v3 -> s3; }
  { rank=same; v4 -> s4; }
  { rank=same; v5 -> s5; }
}
```

## Mitä ohjelmassa on

Paketin `tarkista.py` lukee ohjelman otsakkeen, segmentit, dynaamisen
osion, symbolit ja huomautukset `readelf`illä, samaan tapaan kuin
checksec-työkalu:

```{.python tiedosto="esimerkit/06-suojaukset/tarkista.py" osa="suojaukset"}
```

Sama pieni ohjelma käännetään kolmella tavalla: suojaukset pois,
jakelun oletukset ja kovennettuna.

```{.bash tiedosto="esimerkit/06-suojaukset/aja.sh" osa="liput"}
```

```{.tuloste tiedosto="esimerkit/06-suojaukset/odotettu" osa="t1"}
```

Ubuntun GCC:n oletuksissa on jo PIE, pinokanari, täysi RELRO ja
CET-merkinnät. FORTIFY_SOURCE puuttuu, koska se toimii vain
optimoinnin kanssa, ja oletus ilman `-O`-valitsinta on `-O0`.
Kovennettu käännös lisää sen. Rivi `heikko` näyttää, mitä vanhat
käännösohjeet tai sulautetun järjestelmän oletukset voivat tuottaa;
juuri tällaiset ohjelmat kannattaa löytää ja kääntää uudelleen.

Suojausten tarkistaminen kuuluu julkaisuputkeen: kun binäärit
tarkistetaan automaattisesti, puuttuva lippu ei jää huomaamatta
käännösjärjestelmän muutoksen jälkeen.

## ASLR ja PIE

*Osoiteavaruuden satunnaistus* (*address space layout randomization*)
sijoittaa pinon, keon, jaetut kirjastot ja PIE-ohjelman koodin eri
osoitteisiin joka käynnistyksellä. Ohjelma tulostaa osoitteet, ja
skripti ajaa sen kolmesti:

```{.bash tiedosto="esimerkit/06-suojaukset/aja.sh" osa="aslr"}
```

```{.tuloste tiedosto="esimerkit/06-suojaukset/odotettu" osa="t2"}
```

Ilman PIE:tä ohjelman oma koodi on aina samassa osoitteessa, vaikka
pino, keko ja kirjastot satunnaistetaan. Komento `setarch -R` ottaa
satunnaistuksen pois yhdeltä prosessilta, ja gdb tekee saman
oletuksena, jotta virheenjäljitys toistuisi samanlaisena; konteissa
tämä on usein estetty. Ytimen asetus
`/proc/sys/kernel/randomize_va_space` on tavallisesti 2 (kaikki
alueet).

ASLR ei estä virhettä vaan tekee osoitteista arvaamattomia. Siksi sen
teho riippuu siitä, ettei osoitteita vuoda: muotoilumerkkijonovirhe
(luku 5) tai muu tietovuoto voi kumota sen. 64-bittisessä
osoiteavaruudessa satunnaisuutta on paljon, 32-bittisessä vähän.

## NX

*NX* (*no-execute*, Windowsissa *DEP*) merkitsee muistisivut joko
kirjoitettaviksi tai suoritettaviksi mutta ei molempia. Pino ja keko
ovat dataa, joten prosessori kieltäytyy suorittamasta niitä. Ohjelma
kirjoittaa pinoon yhden `ret`-käskyn ja kutsuu sitä:

```{.c tiedosto="esimerkit/06-suojaukset/nx.c" osa="nx"}
```

```{.bash tiedosto="esimerkit/06-suojaukset/aja.sh" osa="nx"}
```

```{.tuloste tiedosto="esimerkit/06-suojaukset/odotettu" osa="t3"}
```

Oletuskäännöksessä hyppy pinoon kaatuu SIGSEGV:hen. Linkkerin
valitsin `-z execstack` merkitsee pinon suoritettavaksi, ja silloin
sama koodi toimii. Valitsinta tarvitsee nykyään lähinnä vanha koodi,
joka käyttää GCC:n sisäkkäisiä funktioita. Uudet binutils-versiot
varoittavat, jos objektitiedosto vaatii suoritettavan pinon
huomaamatta, ja uudet glibc-versiot kieltäytyvät lataamasta tällaisia
jaettuja kirjastoja `dlopen`-kutsulla. NX:n takia hyökkäykset siirtyivät
ohjelmassa jo olevan koodin uudelleenkäyttöön (luku 7).

## RELRO

Dynaamisesti linkitetyn ohjelman *GOT* (*global offset table*)
sisältää jaettujen kirjastojen funktioiden osoitteet (*Objektitiedostot,
linkitys ja ABI*). Jos taulu on kirjoitettava, muistivirhe voi
ylikirjoittaa funktio-osoitteen. *RELRO* (*relocation read-only*)
merkitsee taulut vain luettaviksi relokaatioiden jälkeen:

- *Osittainen RELRO* suojaa osan tauluista, mutta laiskasti
  sidottavien funktioiden GOT jää kirjoitettavaksi.
- *Täysi RELRO* (`-z relro -z now`) sitoo kaikki symbolit
  käynnistyksessä ja suojaa koko GOT:n. Hinta on hieman hitaampi
  käynnistys.

`tarkista.py` tunnistaa täyden RELROn segmentistä `GNU_RELRO` ja
dynaamisen osion lipusta `BIND_NOW`.

## FORTIFY_SOURCE

Kun kääntäjä tietää kohdepuskurin koon, `-D_FORTIFY_SOURCE` korvaa
`strcpy`-, `memcpy`-, `sprintf`- ja monet muut kutsut tarkistavilla
`__*_chk`-versioilla:

```{.c tiedosto="esimerkit/06-suojaukset/fortify.c" osa="fortify"}
```

```{.bash tiedosto="esimerkit/06-suojaukset/aja.sh" osa="fortify"}
```

```{.tuloste tiedosto="esimerkit/06-suojaukset/odotettu" osa="t4"}
```

Tasolla 2 koon on oltava käännösaikana tiedossa; taso 3 (GCC 12 ja
glibc 2.34 alkaen) käyttää myös ajonaikaisia kokoja, kuten muuttuvan
kokoisia varauksia. Tarkistus kattaa vain kirjastokutsut: oma
silmukka, joka kirjoittaa puskurin yli, jää sen ulkopuolelle.

## Muut kovennukset

- **`-fstack-clash-protection`** estää pinon kasvamisen suojasivun yli
  suurilla paikallisilla taulukoilla tai `alloca`-kutsuilla.
- **`-ftrivial-auto-var-init=zero`** (GCC 12, Clang) alustaa paikalliset
  muuttujat, jolloin alustamaton muisti ei vuoda vanhaa dataa.
- **`-D_GLIBCXX_ASSERTIONS`** lisää C++:n standardikirjastoon
  rajatarkistuksia (`operator[]`, iteraattorit).
- **Hiekkalaatikko ja vähimmät oikeudet**: seccomp, nimiavaruudet ja
  erillinen käyttäjä rajaavat sen, mitä kaapattu prosessi voi tehdä
  (*Virtualisointi*). Ne ovat tärkeimpiä vaikutusta rajaavia
  suojauksia, koska ne toimivat virheluokasta riippumatta.

OpenSSF:n *Compiler Options Hardening Guide for C and C++* kokoaa
suositellut valitsimet perusteluineen.

## Käytännössä

- **Tarkista binäärit automaattisesti** julkaisuputkessa:
  PIE, NX, kanari, täysi RELRO ja FORTIFY.
- **Käännä julkaisu optimoituna ja FORTIFY_SOURCE=3:lla**; debug-käännös
  ilman optimointia ei saa näitä tarkistuksia.
- **Älä käytä `-z execstack`-valitsinta** äläkä poista suojauksia
  suorituskyvyn vuoksi mittaamatta.
- **Muista, mitä suojaukset eivät tee**: ne eivät korjaa virhettä, eivät
  estä tietovuotoja eivätkä palvelunestoa. Ne ostavat aikaa ja
  rajaavat vahinkoa.

## Itsearviointi

- Osaat tarkistaa ohjelmasta PIE:n, NX:n, kanarin, RELRO:n, FORTIFY:n ja
  CET-merkinnät `readelf`illä.
- Osaat selittää ASLR:n ja PIE:n suhteen ja sen, miksi tietovuoto
  heikentää ASLR:ää.
- Osaat näyttää NX:n ja FORTIFY_SOURCEn laukeavan ja kertoa niiden
  rajat.
- Osaat valita kovennetun käännöksen valitsimet ja perustella ne.
