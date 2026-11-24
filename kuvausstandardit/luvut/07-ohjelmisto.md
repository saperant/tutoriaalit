# Ohjelmisto ja dokumentaatio

Ohjelmistolle rekisterikartta on joukko osoitteita, bittisijainteja ja
maskeja. Ne tuotetaan samasta kuvauksesta kuin RTL, joten ajuri ja
laitteisto eivät voi erota toisistaan. Dokumentaatio tuotetaan samalla
tavalla. Tässä luvussa käytetään PeakRDL:n C-otsaketta ja HTML-sivustoa
sekä kirjoitetaan oma pieni Markdown-generaattori.

## C-otsake

`peakrdl c-header` tuottaa jokaiselle kentälle bittimaskin (`_bm`),
bittisijainnin (`_bp`), leveyden (`_bw`) ja nollausarvon (`_reset`)
sekä osoitekartasta rakenteen, jonka jäsenet ovat rekisterit oikeissa
siirtymissä:

```{.c tiedosto="esimerkit/tuotettu/ajastin.h"}
```

Rakenteen koko tarkistetaan käännösaikana (`static_assert`). Jos
rekisterien välissä on aukko, otsakkeeseen tulee täytejäsen, joten
rakenteen jäsenet osuvat aina oikeisiin osoitteisiin. Valitsimella
`-b` otsake tuottaa myös bittikenttärakenteet, mutta C:n bittikenttien
järjestys on toteutuksen määräämä, joten järjestys on annettava
erikseen. Maskit ja sijainnit ovat siirrettävämpiä.

## Ajuri

Ajuri käyttää otsakkeen nimiä eikä omia vakioitaan. Makro `KENTTA`
sijoittaa arvon kenttäänsä otsakkeen sijainnilla ja maskilla:

```{.c tiedosto="esimerkit/c/ajuri.c" osa="kentta"}
```

Ajurin alussa on lisäksi omat `static_assert`-tarkistukset niistä
siirtymistä, joihin ajuri luottaa. Ne ovat ajurin kirjoittajan
oletuksia: jos kuvausta muutetaan ja otsake tuotetaan uudelleen,
käännös kertoo, mikä oletus meni rikki. Ajuri testataan
isäntäkoneella niin, että rekisterit ovat tavallisessa muistissa.
Laitteessa osoitin asetettaisiin lohkon perusosoitteeseen, esimerkiksi
`(volatile ajastin_t *)0x40001000`, kuten taidossa *Mikrokontrollerit
ja bare-metal-ohjelmointi*.

PeakRDL tuottaa pyynnöstä (`--testcase`) myös testiohjelman, joka
tarkistaa rakenteen jäsenten siirtymät kuvausta vastaan:

```{.python tiedosto="esimerkit/06-c.py" osa="ajuri"}
```

```{.python tiedosto="esimerkit/06-c.py" osa="testcase"}
```

```{.tuloste tiedosto="esimerkit/06-c.odotettu"}
```

Nollauksen jälkeen `CTRL` on 0x100, koska `JAKAJA` alkaa arvosta 1.
Ajuri ei tiedä tätä itse, vaan lukee sen otsakkeen
`AJASTIN__CTRL__JAKAJA_reset`-arvosta. Linux-ajuria varten otsake
tuotetaan ytimen omia otsakkeita käyttäväksi (`--linux-kernel`), ja
Rust-ajureille vastaava tuotetaan SVD-tiedostosta (luku 10).

## Dokumentaatio

Rekisterikartan dokumentaatio on käsikirjan tärkein osa ja
todennäköisin vanhentumaan. Tuotettuna se on aina sama kuin RTL ja
otsake. Oma Markdown-generaattori on lyhyt, koska kääntäjä on jo
tarkistanut mallin:

```{.python tiedosto="esimerkit/kuvaus/markdown.py" osa="dokumentti"}
```

Tuotettu dokumentti:

```{.markdown tiedosto="esimerkit/tuotettu/ajastin.md"}
```

`peakrdl html` tuottaa selattavan sivuston, jossa on rekisteripuu,
haku ja jokaisen rekisterin kenttätaulukko. Esimerkki `07-dokumentit.py` tuottaa sen
väliaikaiseen hakemistoon ja vertaa sivuston rekisteritietoja (JSON)
malliin:

```{.python tiedosto="esimerkit/07-dokumentit.py" osa="html"}
```

```{.tuloste tiedosto="esimerkit/07-dokumentit.odotettu"}
```

Sivusto on itsenäinen kansio, jonka voi julkaista sellaisenaan
sisäiseen dokumentaatiopalvelimeen tai CI:n artefaktina. Markdown sopii
tekstiin upotettavaksi, esimerkiksi tämän kirjan kaltaiseen pandoc-
tai Sphinx-dokumenttiin.

## Käytännössä

- **Ajuri käyttää vain tuotettuja nimiä.** Omat vakiot rekisterien
  osoitteille ja biteille ovat kopioita, jotka vanhenevat.
- **Kirjoita ajurin oletukset tarkistuksiksi.** `static_assert`
  siirtymistä ja leveyksistä tekee kuvauksen muutoksesta
  käännösvirheen eikä ajonaikaista virhettä.
- **Maskit ja sijainnit bittikenttien sijaan.** Bittikenttien järjestys
  ja pääsyleveys ovat kääntäjän päätettävissä; maskit tekevät aina
  saman.
- **Tuota dokumentaatio,** älä kirjoita rekisteritaulukoita käsin.
  Käsin kirjoitettu teksti kuuluu lohkon toimintaa kuvaaviin lukuihin,
  ja kuvauksen `desc`-tekstit siihen, mitä yksittäinen kenttä tekee.

## Itsearviointi

- Osaat tuottaa kuvauksesta C-otsakkeen ja kirjoittaa ajurin, joka
  käyttää sen maskeja, sijainteja ja nollausarvoja.
- Osaat kirjoittaa ajurin oletukset käännösaikaisiksi tarkistuksiksi ja
  käyttää PeakRDL:n tuottamaa otsaketestiä.
- Osaat kirjoittaa oman generaattorin käännetystä mallista, esimerkiksi
  Markdown-dokumentin.
- Osaat tuottaa HTML-dokumentaation ja tarkistaa, että se vastaa
  kuvausta.
