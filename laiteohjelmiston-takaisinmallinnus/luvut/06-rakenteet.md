# Kääntäjän tuottamat rakenteet

Kääntäjä tuottaa tunnistettavia kuvioita korkean tason rakenteista:
taulukot muuttuvat osoitinaritmetiikaksi, `switch` hyppytauluksi ja
tietueet kiinteiksi siirtymiksi. Kun kuviot tunnistaa, rakenteen voi
lukea konekielestä takaisin. *Takaisinmallinnus* käy samat kuviot
läpi x86-64:llä; tässä ne katsotaan ARM-koodissa.

## Tietuetaulukot

Komentotulkin ja tehtävävuorottajan rakenne on usein taulukko
tietueita, joissa on nimi, ohjeteksti ja käsittelijäfunktion osoite.
Taulukko erottuu datasta säännöllisenä kuviona: samanmuotoiset tietueet
peräkkäin. `taulut`-työkalu luokittelee jokaisen sanan (osoitin
merkkijonoon, osoitin funktioon, nolla, pieni luku) ja etsii toistuvia
tietueita:

```{.python tiedosto="esimerkit/tyokalut/taulut.py" osa="sopii"}
```

```{.bash tiedosto="esimerkit/06-rakenteet/aja.sh" osa="taulut"}
```

```{.tuloste tiedosto="esimerkit/06-rakenteet/odotettu" osa="s1"}
```

Kolmesta eri taulukosta kaksi on vektoritaulun jäänteitä (pelkkiä
funktio-osoittimia), mutta kaksi on selkeitä tietueita: komentotaulu
(nimi, ohje, käsittelijä) ja tehtävätaulu (nimi, jakso, käsittelijä).
`huolto`- ja `lue`-komentojen ohjekenttä on nolla — ne ovat
piilokomentoja, joita ohje ei näytä. `huolto` kysyy salasanaa, ja
luku 9 näyttää, miksi salasana ei suojaa komentoa. Nyt
tiedetään laitteen komennot ja jaksolliset tehtävät nimineen ilman,
että yhtäkään käsittelijää on luettu.

## Hyppytaulut

`switch`-lause, jossa on monta peräkkäistä tapausta, kääntyy
*hyppytauluksi*: indeksillä haetaan taulukosta hypyn kohde. Cortex-M:ssä
tämä on `tbb`-käsky (*table branch byte*): taulukko alkaa heti käskyn
jälkeen, ja kukin tavu on hypyn pituus puolisanoina. `thumb`-moduuli
lukee taulukon ja laskee kohteet; alkioiden määrä tulee edeltävästä
`cmp`-käskystä:

```{.python tiedosto="esimerkit/tyokalut/thumb.py" osa="hyppytaulu"}
```

```{.bash tiedosto="esimerkit/06-rakenteet/aja.sh" osa="hyppy"}
```

```{.tuloste tiedosto="esimerkit/06-rakenteet/odotettu" osa="s2"}
```

Funktio `0x10810` sisältää viiden tapauksen hyppytaulun. Komentotaulun
`kehys`-komennon käsittelijä kutsuu sitä, joten se on kehysten
käsittelijä ja hyppytaulu `switch` kehyksen tyypin mukaan. Hyppytaulun käskykuvio ja sitä edeltävä rajatarkistus:

```{.bash tiedosto="esimerkit/06-rakenteet/aja.sh" osa="tbb"}
```

```{.tuloste tiedosto="esimerkit/06-rakenteet/odotettu" osa="s3"}
```

`cmp r3, #4` ja `bhi` ohjaavat liian suuren indeksin oletustapaukseen,
ja `tbb [pc, r3]` hyppää taulukon mukaan. Taulukon tavut (`03 0b 24 2c
2f`) ovat hyppyjen pituudet. Disassemblerin on osattava ohittaa taulukko
koodina; muuten se tulkitsee datan käskyiksi.

Nimeämiset tarkistettuna vastausavainta vastaan:

```{.tuloste tiedosto="esimerkit/06-rakenteet/odotettu" osa="s4"}
```

## Käytännössä

- **Tunnista taulukot säännöllisyydestä.** Samanmuotoisten tietueiden
  jono datassa on taulukko. Osoitin + osoitin + funktio on tyypillinen
  komentotaulu; osoitin + luku + funktio tehtävä- tai tilataulu.
- **Hyppytaulu paljastaa `switch`-lauseen.** `tbb`/`tbh` ja sitä
  edeltävä `cmp`/`bhi` antavat tapausten määrän ja kohteet. Taulukko
  on dataa heti käskyn jälkeen; älä pura sitä käskyinä.
- **Taulukot nopeuttavat analyysia.** Komentotaulu kertoo koko
  käyttöliittymän ja käsittelijöiden osoitteet kerralla, ilman että
  pääsilmukkaa tarvitsee seurata.
- **Puolustus:** piilokomento (ohjeeton rivi komentotaulussa) ei ole
  piilossa — se näkyy taulukossa yhtä selvästi kuin muutkin. Toiminnon
  turvallisuus ei saa perustua siihen, ettei sitä mainosteta.

## Itsearviointi

- Osaat tunnistaa tietuetaulukon konekielestä ja lukea sen kentät.
- Osaat tunnistaa `switch`-lauseen hyppytaulusta ja laskea sen
  tapausten kohteet.
- Osaat selittää, miksi hyppytaulun data ei saa päätyä puretuksi
  koodina.
- Osaat käyttää komento- ja tehtävätaulua laitteen toiminnan
  kartoittamiseen.
