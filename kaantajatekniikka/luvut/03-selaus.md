# Selaus

**Selaaja** (*lexer*, *scanner*) lukee lähdetekstin merkki kerrallaan
ja ryhmittelee merkit **tokeneiksi**: avainsanoiksi, tunnisteiksi,
luvuiksi ja operaattoreiksi. Samalla se ohittaa välilyönnit ja
kommentit. Selaus on oma vaiheensa, koska se yksinkertaistaa
jäsennintä: jäsentimen ei tarvitse tietää, että `<=` on kaksi merkkiä
tai että kommentti voi olla missä tahansa.

## Tokenit

Tokenilla on laji, lähdetekstin merkkijono (*lekseemi*), sijainti ja
luvuille arvo:

```{.cpp tiedosto="esimerkit/kide/lekseri.hpp" osa="laji"}
```

Sijainti on rivi ja sarake. Se kulkee tokenista syntaksipuuhun ja
sieltä virheilmoituksiin, joten se kannattaa ottaa mukaan heti
alussa; jälkikäteen lisättynä se on työläs.

```{.cpp tiedosto="esimerkit/kide/diagnostiikka.hpp" osa="sijainti"}
```

Pienen ohjelman tokenit näyttävät tältä (`--vaihe=tokenit`):

```{.rust tiedosto="esimerkit/naytteet/pieni.kide"}
```

```{.tuloste tiedosto="esimerkit/naytteet/tokenit.txt"}
```

Kommentti on kadonnut, ja jokaisella tokenilla on sijainti. Viimeinen
token on aina tiedoston loppu: jäsentimen ei tarvitse tarkistaa
taulukon rajoja, koska se pysähtyy loppumerkkiin.

## Selaaja tilakoneena

Tokenien muodot ovat **säännöllisiä kieliä**, jotka voidaan kuvata
säännöllisillä lausekkeilla:

| Token | Säännöllinen lauseke |
|-------|----------------------|
| tunniste | `[A-Za-z_][A-Za-z0-9_]*` |
| luku | `[0-9]+` |
| kommentti | `//[^\n]*` |
| operaattori | `->`, `==`, `<=` ... tai yksittäinen merkki |

Jokaista säännöllistä lauseketta vastaa **äärellinen automaatti**
(tilakone), ja automaatit voidaan yhdistää yhdeksi. Selaajageneraattorit,
kuten lex, flex ja re2c, tekevät tämän automaattisesti: ne kääntävät
säännölliset lausekkeet determinististen automaattien siirtymätauluiksi.
Käsin kirjoitettu selaaja on sama automaatti koodina: tila on se kohta
ohjelmassa, jossa suoritus on, ja siirtymät ovat ehtolauseita.

Tunnisteen automaatissa on kaksi tilaa. Alkutilasta siirrytään
kirjaimen tai alaviivan jälkeen tilaan *tunniste*, jossa pysytään niin
kauan kuin seuraava merkki on kirjain, numero tai alaviiva; muuten
token päättyy. Selaajan päälooppi tekee juuri tämän:

```{.cpp tiedosto="esimerkit/kide/lekseri.cpp" osa="selaa"}
```

Avainsanoja ei tunnisteta omalla automaatillaan. Ne selataan
tunnisteina, ja lopuksi katsotaan hajautustaulusta, onko sana varattu.
Näin automaatti pysyy pienenä, ja uuden avainsanan lisääminen on
yksi rivi taulukkoon.

## Pisin osuma

Kun merkkijono `<=` on luettu merkki kerrallaan, `<` on jo kelvollinen
token. Selaaja kuitenkin jatkaa ja valitsee **pisimmän osuman**
(*maximal munch*): `<=` on yksi token, ei `<` ja `=`. Kahden merkin
operaattorit tarvitsevat vain yhden merkin ennakoinnin:

```{.cpp tiedosto="esimerkit/kide/lekseri.cpp" osa="pisin"}
```

Pisin osuma selittää myös joitakin tunnettuja kummallisuuksia. C++03:ssa
`vector<vector<int>>` oli virhe, koska `>>` selattiin siirto-operaattoriksi;
C++11 lisäsi jäsentimeen erikoissäännön. C:ssä `x = y/*p` aloittaa
kommentin eikä jaa osoittimen kohteella.

## Tyhjä tila ja kommentit

Välilyönnit, rivinvaihdot ja kommentit ohitetaan ennen jokaista tokenia.
Kommentti tunnistetaan kahden merkin ennakoinnilla, jotta yksittäinen
`/` jää jakolaskuksi:

```{.cpp tiedosto="esimerkit/kide/lekseri.cpp" osa="tyhja"}
```

Kiden kieliopissa rivinvaihdolla ei ole merkitystä. Kielissä, joissa
sisennys on syntaksia (Python, Haskell, YAML), selaaja tuottaa
sisennyksen muutoksista omia tokeneitaan (`INDENT`, `DEDENT`), ja
jäsennin käsittelee niitä kuten aaltosulkeita.

## Luvut ja ylivuoto

Kokonaislukuliteraali muunnetaan arvoksi jo selaimessa. Muunnoksessa on
yksi vaarallinen kohta: liian suuri literaali vuotaisi yli, ja
etumerkillisen luvun ylivuoto on C++:ssa määrittelemätöntä. Tarkistus
tehdään ennen kertolaskua:

```{.cpp tiedosto="esimerkit/kide/lekseri.cpp" osa="luku"}
```

Selaaja ei tunne negatiivisia literaaleja: `-5` on kaksi tokenia,
miinusmerkki ja luku. Siksi pienintä 64-bittistä lukua
$-2^{63}$ ei voi kirjoittaa literaalina, koska $2^{63}$ ei mahdu
lukuun; ohjelma `semantiikka.kide` kirjoittaa sen muodossa
`-suurin - 1`. C:ssä on sama ilmiö, ja siksi `INT64_MIN` on
määritelty lausekkeena `(-INT64_MAX - 1)`.

## Virheet selaimessa

Selaaja raportoi tuntemattoman merkin, virheellisen luvun ja
yksinäisen `&`:n, mutta jatkaa selaamista. Virheellisestä luvusta se
tuottaa silti luku-tokenin (arvo 0) ja yksinäisestä `&`:stä `&&`-tokenin,
jotta virheestä ei synny jäsentimessä seurannaisvirheitä. Pääohjelma
lopettaa selauksen jälkeen, jos virheitä oli:

```{.rust tiedosto="esimerkit/virheet/selaus.kide"}
```

```{.tuloste tiedosto="esimerkit/virheet/selaus.virhe"}
```

Ei-tulostettava merkki näytetään heksadesimaalina. Muuten
virheilmoitus voisi sisältää ohjausmerkkejä, jotka sotkevat päätteen;
sama sääntö koskee kaikkia ohjelmia, jotka tulostavat käyttäjän syötettä.

## Käytännössä

- **Käsin kirjoitettu selaaja on tavallisin valinta.** GCC, Clang,
  Go, Rust ja V8 käyttävät käsin kirjoitettuja selaajia: ne ovat
  nopeita, virheilmoitukset ovat hyviä, eikä rakennukseen tarvita
  generaattoria. Generaattori (re2c, flex) kannattaa, kun tokenien
  muotoja on paljon tai ne muuttuvat usein.
- **Säilytä sijainnit.** Rivi ja sarake jokaisessa tokenissa maksavat
  vähän ja tekevät virheilmoituksista ja kielipalvelimesta mahdollisia.
  Isot kääntäjät tallentavat tiedostosiirtymän ja laskevat rivin
  tarvittaessa.
- **Valitse pisin osuma ja dokumentoi poikkeukset.** Kielen
  suunnittelussa kannattaa välttää tokeneita, joiden pisin osuma
  yllättää ihmisen.
- **Ole tarkka merkistön kanssa.** Kide hyväksyy tunnisteissa vain
  ASCII-kirjaimet. Unicode-tunnisteet (C++, Rust, Python) vaativat
  normalisoinnin ja luokittelun (UAX #31), muuten kaksi samannäköistä
  nimeä voivat olla eri nimiä.

## Itsearviointi

- Osaat kirjoittaa tokenien muodot säännöllisinä lausekkeina ja
  piirtää niitä vastaavan tilakoneen.
- Osaat toteuttaa käsin kirjoitetun selaajan, joka käyttää pisintä
  osumaa ja ohittaa kommentit yhden merkin ennakoinnilla.
- Osaat muuntaa numeromerkkijonon kokonaisluvuksi ilman ylivuodon
  määrittelemätöntä käytöstä.
- Osaat selittää, miksi selaaja kannattaa toipua virheistä niin, ettei
  jäsennin saa seurannaisvirheitä.
