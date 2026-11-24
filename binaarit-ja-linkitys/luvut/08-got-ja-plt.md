# Paikkariippumaton koodi, GOT ja PLT

Jaettu kirjasto ladataan eri prosesseissa eri osoitteisiin, mutta sen
koodisivut halutaan jakaa: sama fyysinen muisti kaikille prosesseille.
Koodiin ei siis voi kirjoittaa latausosoitteesta riippuvia arvoja.
*Paikkariippumaton koodi* (*position-independent code*, PIC) ratkaisee
tämän kahdella periaatteella:

1. Saman tiedoston sisällä viitataan `rip`-suhteellisesti: etäisyys
   koodista dataan on vakio, latausosoitteesta riippumatta.
2. Muihin tiedostoihin viitataan taulukon kautta, joka on
   kirjoitettavassa datassa. Lataaja täyttää taulukon, ja koodi pysyy
   muuttumattomana.

Taulukoita on kaksi. **GOT** (*global offset table*) sisältää
muuttujien ja funktioiden osoitteet. **PLT** (*procedure linkage
table*) on joukko pieniä hyppykoodeja, yksi kutakin ulkoista funktiota
kohti; jokainen hyppää GOT:ssa olevaan osoitteeseen.

## Kirjasto, jonka symbolit voi korvata

Esimerkin mittauskirjasto laskee kutsunsa ja pyöristää tuloksen
apufunktiolla:

```{.c tiedosto="esimerkit/07-got-plt/mittari.c" osa="mittari"}
```

Kun tiedosto käännetään valitsimella `-fPIC`, relokaatiot näyttävät,
miten kääntäjä viittaa omaan muuttujaansa ja funktioonsa:

```{.bash tiedosto="esimerkit/07-got-plt/aja.sh" osa="pic"}
```

```{.bash tiedosto="esimerkit/07-got-plt/aja.sh" osa="nakyvyys"}
```

```{.tuloste tiedosto="esimerkit/07-got-plt/odotettu"}
```

Tulos voi yllättää: `kutsuja` ja `pyorista` ovat *samassa
tiedostossa*, mutta `mittaa` hakee muuttujan osoitteen GOT:sta
(`mov ...(%rip),%rax` ja sitten `addl $0x1,(%rax)`) ja kutsuu
apufunktiota PLT:n kautta (`jmp <pyorista@plt>`, häntäkutsuna). Kääntäjä
ei myöskään upottanut lyhyttä `pyorista`-funktiota.

Syy on *symbolien korvattavuus* (*symbol interposition*). ELF:n
sääntöjen mukaan globaali symboli jaetussa kirjastossa voidaan korvata:
jos ohjelma tai aiemmin ladattu kirjasto määrittelee saman nimen,
dynaaminen linkkeri sitoo *kaikki* viittaukset siihen, myös kirjaston
omat (luku 10). Kääntäjän on varauduttava siihen, että `kutsuja` ja
`pyorista` eivät ole ne, jotka se näkee.

## Näkyvyys: mikä on rajapintaa

Valitsin `-fvisibility=hidden` tekee kaikista symboleista oletuksena
*piilotettuja*: ne ovat globaaleja kirjaston sisällä mutta eivät näy
sen ulkopuolelle. Makro `VIENTI` merkitsee julkisen rajapinnan
näkyväksi (`visibility("default")`). Toisessa käännöksessä kääntäjä
tietää, ettei kukaan voi korvata symboleita `kutsuja` ja `pyorista`,
joten muuttujaa kasvatetaan suoraan `rip`-suhteellisesti ja
`pyorista` upotetaan kokonaan (kertolasku `0x66666667`:llä on
jakolasku kymmenellä).

Piilottamisella on neljä hyötyä:

- **Nopeampi koodi**: suorat viittaukset, upotus ja muut
  optimoinnit kirjaston sisällä.
- **Nopeampi käynnistys**: dynaamisessa symbolitaulussa on vähemmän
  symboleita, ja lataaja tekee vähemmän relokaatioita.
- **Hallittu ABI**: vain merkityt symbolit ovat rajapintaa, joten
  sisäisiä funktioita voi muuttaa vapaasti (luku 9).
- **Ei törmäyksiä**: sisäinen apufunktio ei voi sekoittua toisen
  kirjaston samannimiseen funktioon (luku 10).

| Keino | Vaikutus | Käyttö |
|-------|----------|--------|
| `-fvisibility=hidden` ja vientimakro | vain merkityt symbolit näkyvät | uudet kirjastot |
| versioskripti `local: *;` | piilottaa linkityksessä | olemassa oleva koodi |
| `-fno-semantic-interposition` | kääntäjä saa olettaa, ettei korvata | GCC 5+, Python käyttää |
| `-Wl,-Bsymbolic` | linkkeri sitoo sisäiset viittaukset itseensä | rikkoo `LD_PRELOAD`-kääreet |
| `static` | paikallinen, ei rajapintaa | aina, kun mahdollista |

Sama makro kirjoitetaan yleensä niin, että se toimii myös Windowsilla,
jossa vienti merkitään `__declspec(dllexport)`. CMake tuottaa
tällaisen otsakkeen komennolla `generate_export_header`, ja
`CXX_VISIBILITY_PRESET hidden` asettaa valitsimen.

## Miten PLT toimii

Ohjelman kutsu `mittaa(14)` kääntyy kutsuksi `call mittaa@plt`. PLT:n
merkintä on hyppy GOT:n paikkaan (`objdump -d oletus`, osoitteet
poistettu):

```text
<mittaa@plt>:
    endbr64
    jmp    *SIIRTYMA(%rip)    # osoite GOT:n paikasta
    nopw   0x0(%rax,%rax,1)
```

`endbr64` on epäsuoran hypyn kohdemerkintä (Intel CET, `-fcf-protection`),
ja `nopw` täyttää merkinnän 16 tavuun.

Kun ohjelma käynnistyy, lataaja kirjoittaa funktion `mittaa`
todellisen osoitteen GOT:n paikkaan. Sen jälkeen jokainen kutsu on
epäsuora hyppy: yksi lisämuistiviittaus kutsua kohti, jonka
haarautumisennustin oppii nopeasti.

*Laiska sidonta* (*lazy binding*) lykkää osoitteen ratkaisemista
ensimmäiseen kutsuun. GOT:n paikassa on aluksi osoite takaisin
PLT:hen, josta hypätään lataajan ratkaisijaan (`_dl_runtime_resolve`).
Ratkaisija etsii symbolin, kirjoittaa osoitteen GOT:iin ja hyppää
funktioon. Seuraavat kutsut menevät suoraan. Esimerkin ohjelma
kirjoittaa merkkirivit ennen ja jälkeen ensimmäisen kutsun, ja
`LD_DEBUG=bindings` näyttää, milloin `mittaa` sidottiin:

```{.c tiedosto="esimerkit/07-got-plt/main.c"}
```

```{.bash tiedosto="esimerkit/07-got-plt/aja.sh" osa="oletus"}
```

```{.bash tiedosto="esimerkit/07-got-plt/aja.sh" osa="laiska"}
```

Ubuntun GCC linkittää oletuksena valitsimella `-z now`: lippu
`BIND_NOW` käskee lataajaa sitomaan kaikki symbolit käynnistyksessä,
ja sidonta tapahtuu ennen ensimmäistä merkkiriviä. Valitsimella
`-z lazy` sidonta tapahtuu vasta ensimmäisessä kutsussa.

Välitön sidonta yhdessä RELRO:n kanssa (*full RELRO*: `-z relro -z
now`) on turvallisempi. Kun kaikki osoitteet on kirjoitettu, lataaja
suojaa GOT:n kirjoitukselta, eikä muistivirhettä voi käyttää
funktio-osoitteiden ylikirjoittamiseen. Laiskassa sidonnassa GOT:n
funktiopaikkojen on pysyttävä kirjoitettavina koko ajon ajan.
Lisäksi puuttuva symboli paljastuu heti käynnistyksessä eikä vasta,
kun harvinainen koodipolku ajetaan. Laiska sidonta nopeuttaa
käynnistystä vain ohjelmilla, joilla on tuhansia tuontisymboleita ja
joista käytetään pientä osaa.

Valitsin `-fno-plt` poistaa PLT:n kokonaan: kääntäjä tuottaa
kutsukohtaan `call *mittaa@GOTPCREL(%rip)`. Tämä säästää yhden
hypyn mutta vaatii välittömän sidonnan.

## Käytännössä

- **Käännä kirjastot `-fvisibility=hidden`:llä** ja merkitse rajapinta
  vientimakrolla. Se on suurin yksittäinen parannus jaetun kirjaston
  nopeuteen, kokoon ja ABI:n hallintaan.
- **Pidä oletuksena välitön sidonta ja täysi RELRO.**
  `readelf -d ohjelma | grep FLAGS` näyttää `BIND_NOW`, ja
  `readelf -lW` näyttää `GNU_RELRO`-segmentin.
- **Älä käytä `-Bsymbolic`:ia sokeasti.** Se nopeuttaa kirjastoa
  mutta estää symbolien korvaamisen, jota muistinhallintakirjastot ja
  kääreet tarvitsevat. Näkyvyys on tarkempi keino.
- **Mittaa ennen kuin poistat PLT:n.** `-fno-plt` ja
  linkitysaikainen optimointi auttavat vain kuumissa kutsupoluissa.

## Itsearviointi

- Osaat selittää, miksi jaetun kirjaston koodi viittaa omiin
  globaaleihin muuttujiinsa GOT:n kautta.
- Osaat kuvata PLT:n ja GOT:n yhteistyön sekä laiskan ja välittömän
  sidonnan eron.
- Osaat käyttää näkyvyysattribuutteja ja `-fvisibility=hidden`:ia ja
  tunnistaa niiden vaikutuksen konekielestä.
- Osaat kertoa, miksi täysi RELRO edellyttää välitöntä sidontaa ja
  miten sen tarkistaa.
