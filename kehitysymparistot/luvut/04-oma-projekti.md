# Oman projektin kehityskontti

Esimerkkinä on pieni Python-projekti *kesto*, joka jäsentää ja muotoilee
kestoja: `1h30m` on 5400 sekuntia. Projektissa on moduuli, sen testit ja
Makefile. Tavoite on, että uusi kehittäjä saa testit ajettua yhdellä
komennolla asentamatta mitään käsin.

```{.python tiedosto="esimerkit/projekti/kesto.py" osa="jasenna"}
```

## Kirjaa, mitä projekti tarvitsee

Ensimmäinen askel ei liity kontteihin: selvitä, mitä työkaluja
projektin rakentaminen ja testaaminen vaatii ja missä versioissa. Kesto
tarvitsee Python 3.12:n, pytestin ja `make`-ohjelman.

Samalla projektille tehdään yhdet komennot, jotka toimivat kaikkialla.
Makefile on tähän yksinkertaisin väline: kehittäjä, CI ja
kehityskontti ajavat saman `make testaa` -komennon, eikä kenenkään
tarvitse muistaa pytestin valitsimia.

```{.makefile tiedosto="esimerkit/projekti/Makefile"}
```

Kohde `ymparisto` on pieni terveystarkastus: se kertoo heti ja
selkeästi, jos jokin työkalu puuttuu, eikä vasta testin kaatuessa
oudolla virheilmoituksella.

## Valitse pohja

Vaihtoehtoja oli luvussa 3 kolme. Kestolle kävisi valmis Python-kuva,
mutta esimerkki käyttää omaa Dockerfilea, koska se on yleisin tilanne:
ennen pitkää projekti tarvitsee jonkin paketin, jota valmiissa kuvassa
ei ole.

```{.dockerfile tiedosto="esimerkit/projekti/.devcontainer/Dockerfile"}
```

Pohjana on kehityskonttien peruskuva, jossa on valmiina käyttäjä
`vscode`, Git ja `sudo`. Sen päälle asennetaan vain se, minkä edellinen kohta
listasi. Asennus on yhdessä `RUN`-käskyssä ja pakettiluettelot
poistetaan lopuksi, jotta kuva pysyy pienenä.

## Kirjoita devcontainer.json

```{.javascript tiedosto="esimerkit/projekti/.devcontainer/devcontainer.json"}
```

Tiedosto on lyhyt, koska oletukset ovat hyvät: lähdekoodi liitetään
automaattisesti, ja pääte avautuu projektin juureen. `postCreateCommand`
ajaa terveystarkastuksen, jolloin rikkinäinen ympäristö huomataan heti
kontin synnyttyä. Muuttuja `PYTHONDONTWRITEBYTECODE` estää Pythonia
kirjoittamasta `__pycache__`-hakemistoja liitettyyn lähdekoodiin.

## Kokeile

VS Codessa avaa projekti ja valitse *Reopen in Container*; päätteessä
`make testaa` ajaa testit. Komentorivityökalulla sama on kaksi komentoa
(`devcontainer up` ja `devcontainer exec`, luku 3).

Jotta näkee, ettei tiedostossa ole taikuutta, esimerkeissä on noin sadan rivin
ohjelma `aja_kontissa.py`, joka tekee olennaisen pelkällä
Dockerilla. Ensin kuva: valmis kuva käytetään sellaisenaan, muuten se
rakennetaan Dockerfilesta konfiguraation argumenteilla.

```{.python tiedosto="esimerkit/aja_kontissa.py" osa="rakenna"}
```

Sitten kontti: lähdekoodi liitetään työhakemistoon, ympäristömuuttujat
asetetaan, ja kontissa ajetaan ensin `postCreateCommand` ja sitten
pyydetty komento.

```{.python tiedosto="esimerkit/aja_kontissa.py" osa="aja"}
```

Testi ajaa projektin testit näin rakennetussa kontissa:

```text
python3 aja_kontissa.py projekti make testaa
```

```{.tuloste tiedosto="esimerkit/kontti.odotettu"}
```

Oikeat työkalut tekevät paljon muutakin: asentavat ominaisuudet,
käynnistävät Compose-palvelut, välittävät portit, sovittavat käyttäjän
tunnisteen ja pitävät kontin käynnissä editoria varten. Perusajatus on
silti tämä: *kuva, liitos, ympäristö, komento*.

## Sama ympäristö CI:ssä

Kehityskontin suurin hyöty tulee, kun CI käyttää samaa ympäristöä kuin
kehittäjät. Silloin ”CI:ssä kaatuu, minulla toimii” voi johtua enää
koodista. Tapoja on kaksi: CI ajaa testit kehityskontissa
(`devcontainer exec` tai `devcontainers/ci`), tai CI:n ja kehityskontin
työkalut asennetaan samasta lähteestä.

Tämä tutoriaalikokoelma tekee molemmat. Jokaisen tutoriaalin testit
ajetaan sen omassa kehityskontissa samanlaisella ohjelmalla kuin
`aja_kontissa.py`, ja lisäksi testi tarkistaa konfiguraatioista
muutaman säännön, jotka pätevät niihin kaikkiin:

```{.python tiedosto="esimerkit/kokoelma.py" osa="saannot"}
```

```{.tuloste tiedosto="esimerkit/kokoelma.odotettu"}
```

Sääntö ”rakennusargumentit ovat Dockerfilen tuntemia” on esimerkki
tarkistuksesta, jota mikään yleinen työkalu ei tee: Docker ei
rakennettaessa pysähdy tuntemattomaan rakennusargumenttiin, joten
kirjoitusvirhe argumentin nimessä jättäisi työkalut asentamatta, ja
virhe näkyisi vasta puuttuvana ohjelmana.

## Käytännössä

- **Yhdet komennot kaikkialle.** `make testaa` (tai `just`, `npm test`,
  `cargo test`) on rajapinta, jonka takana työkalut voivat vaihtua.
  Kehityskontti, CI ja README viittaavat samaan komentoon.
- **Kontti on kertakäyttöinen.** Kaikki pysyvä on lähdekoodissa tai
  taltiossa. Jos asennat jotain käsin kontin päätteessä, se katoaa
  seuraavassa uudelleenrakennuksessa; lisää se Dockerfileen.
- **Rakenna tyhjästä ennen kuin luotat.** Dockerin välimuisti piilottaa
  virheet. Rakenna kontti välillä ilman välimuistia (*Rebuild Without
  Cache*), ja anna CI:n tehdä se säännöllisesti.
- **Pidä kuva pienenä.** Jokainen gigatavu on jokaisen kehittäjän ja
  jokaisen CI-ajon odotusaikaa. Suuret, harvoin tarvittavat työkalut
  omaan konfiguraatioonsa.
- **Dokumentoi kontin ulkopuoli.** README kertoo, mitä kontti olettaa
  isäntäkoneelta: Docker, muisti, mahdolliset tunnukset.

## Itsearviointi

- Osaat lisätä projektiin kehityskontin: Dockerfilen tai valmiin kuvan
  ja `devcontainer.json`-tiedoston.
- Osaat selittää, mitä työkalu tekee tiedostolle: kuvan rakennus,
  lähdekoodin liitos, ympäristö ja komennot.
- Osaat perustella, miksi kehittäjien ja CI:n kannattaa käyttää samoja
  komentoja ja samaa ympäristöä.
- Osaat kertoa, mitä kontissa säilyy uudelleenrakennuksen yli ja mitä
  ei.
