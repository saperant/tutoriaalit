# Virheenkäsittely {.runko-virheet}

C:ssä ei ole poikkeuksia. Virheet ilmaistaan paluuarvoilla, ja kutsujan
on tarkistettava ne. Tässä luvussa käydään läpi tavallisimmat
käytännöt sekä määrittelemätön käyttäytyminen, joka on C-ohjelmien
vaikeimmin löydettävien virheiden lähde.

## Virhekoodit

Standardikirjasto käyttää useita käytäntöjä: osoittimen palauttavat
funktiot palauttavat virheessä tyhjän osoittimen (`malloc`, `fopen`),
monet kokonaisluvun palauttavat funktiot negatiivisen arvon tai `EOF`:n,
ja tarkempi syy kerrotaan muuttujassa `errno`. Omassa koodissa
kannattaa valita yksi johdonmukainen tapa. Yleinen ratkaisu on
luettelotyyppi, jossa nolla tarkoittaa onnistumista:

```{.c tiedosto="esimerkit/11-siivous.c" osa="virhekoodit"}
```

Taulukon nimetyt alustimet (`[OK] = "ok"`) pitävät tekstit ja koodit
yhdessä, vaikka luettelon järjestys muuttuisi.

## Resurssien vapauttaminen: `goto`

Kun funktio varaa useita resursseja, jokaisen virhepolun on vapautettava
juuri ne resurssit, jotka on jo varattu. Sisäkkäiset `if`-lauseet
käyvät nopeasti sekaviksi. C:ssä vakiintunut ratkaisu on hypätä
virhetilanteessa funktion loppuun, jossa kaikki resurssit vapautetaan
yhdessä paikassa. Tämä on yksi harvoista tilanteista, joissa `goto`
selkeyttää koodia; tekniikkaa käytetään laajasti esimerkiksi
Linux-ytimessä.

```{.c tiedosto="esimerkit/11-siivous.c" osa="siivous"}
```

Tekniikka toimii, koska kaikki resurssimuuttujat alustetaan tyhjiksi
funktion alussa, ja `free(nullptr)` on sallittu. `toupper` ja muut
`<ctype.h>`-funktiot vaativat argumentin, joka on `unsigned char`
-arvoalueella tai `EOF`. Siksi `char` muunnetaan ensin
`unsigned char`-tyypiksi; muuten negatiiviset merkkiarvot olisivat
määrittelemätöntä käyttäytymistä.

```{.c tiedosto="esimerkit/11-siivous.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-siivous.odotettu"}
```

## Väittämät: `assert` ja `static_assert`

Ohjelmointivirheet, kuten funktion esiehtojen rikkominen, eivät ole
ajonaikaisia virheitä, joista toivutaan. Niitä varten on makro `assert`
(`<assert.h>`), joka keskeyttää ohjelman, jos ehto ei päde. `static_assert`
tarkistaa ehdon jo käännösaikana; C23:ssa se on avainsana, eikä
viestiä tarvitse antaa.

```{.c tiedosto="esimerkit/11-assert.kaatuu.c"}
```

Ohjelma tulostaa ensin `1.5` ja kaatuu sitten toisessa kutsussa:

```{.tuloste tiedosto="esimerkit/11-assert.virhe"}
```

Virheilmoituksessa on myös tiedoston nimi, rivinumero ja funktio.
Kun ohjelma käännetään makrolla `NDEBUG` (`-DNDEBUG`), `assert`-kutsut
poistetaan kokonaan. Väittämiin ei siksi saa kirjoittaa
sivuvaikutuksia, eikä niillä pidä tarkistaa syötettä, joka voi olla
virheellistä normaalissa käytössä.

## Määrittelemätön käyttäytyminen

Standardi jättää monien virheellisten operaatioiden seuraukset
määrittelemättä. Tällaisen *määrittelemättömän käyttäytymisen*
(*undefined behavior*, UB) sisältävällä ohjelmalla ei ole mitään taattua
merkitystä: se voi kaatua, tuottaa väärän tuloksen tai toimia
odotetusti, kunnes kääntäjä, optimointitaso tai alusta vaihtuu.
Kääntäjät optimoivat koodia olettaen, ettei UB:tä esiinny. Siksi UB voi
näkyä yllättävästi, esimerkiksi tarkistus, joka "ei voi olla tosi",
poistetaan kokonaan.

Tavallisimpia määrittelemättömän käyttäytymisen lähteitä:

- taulukon tai varatun muistin rajojen ylitys
- tyhjän, alustamattoman tai vapautettuun muistiin osoittavan
  osoittimen dereferointi
- etumerkillisen kokonaisluvun ylivuoto
- jako nollalla
- alustamattoman muuttujan arvon lukeminen
- bittisiirto negatiivisella tai liian suurella määrällä
- saman muuttujan muuttaminen kahdesti ilman välissä olevaa
  järjestyspistettä, esim. `i = i++`
- merkkijonoliteraalin muuttaminen

Sanitoijat havaitsevat suuren osan näistä. Seuraavassa ohjelmassa
silmukan ehto on yhden liian suuri:

```{.c tiedosto="esimerkit/11-rajat.kaatuu.c"}
```

```{.tuloste tiedosto="esimerkit/11-rajat.virhe"}
```

Ilman sanitoijaa ohjelma luultavasti tulostaisi jonkin luvun eikä
kaatuisi. Virhe jäisi huomaamatta.

### Kokonaislukujen ylivuoto

Etumerkillisen kokonaisluvun ylivuoto on UB, jonka
UndefinedBehaviorSanitizer havaitsee:

```{.c tiedosto="esimerkit/11-ylivuoto.kaatuu.c"}
```

```{.tuloste tiedosto="esimerkit/11-ylivuoto.virhe"}
```

Ylivuodon tarkistaminen jälkikäteen ei toimi, koska ylivuoto on jo
tapahtunut, ja kääntäjä saa poistaa tarkistuksen. Tarkistus on tehtävä
ennen laskutoimitusta. C23:n otsikko `<stdckdint.h>` tarjoaa tähän
funktiot `ckd_add`, `ckd_sub` ja `ckd_mul`. Ne laskevat tuloksen
ensimmäisen argumentin osoittamaan muuttujaan ja palauttavat `true`,
jos tulos ei mahtunut tyyppiin:

```{.c tiedosto="esimerkit/11-tarkistettu.c" osa="tarkistettu"}
```

```{.c tiedosto="esimerkit/11-tarkistettu.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-tarkistettu.odotettu"}
```

Määrittelemätöntä käyttäytymistä vastaan ei ole yhtä keinoa. Parhaat
puolustukset ovat varoitukset (`-Wall -Wextra`), sanitoijat
testauksessa, staattiset analyysityökalut ja koodi, jossa koot ja
omistus ovat aina selvillä.

## Käytännössä

- **Yksi virhekäytäntö kirjastoa kohti.** Joko virhekoodi paluuarvona
  (nolla on onnistuminen) ja tulos tulosparametrissa, tai tyhjä osoitin
  ja syy `errno`ssa kuten standardikirjastossa. Johdonmukaisuus on
  tärkeämpää kuin valinta.
- **Tarkistamaton virhe varoitukseksi.** C23:n attribuutti
  `[[nodiscard]]` virhekoodin palauttavan funktion esittelyssä saa
  kääntäjän varoittamaan, jos paluuarvo jätetään käyttämättä.
- **`goto`-siivous** vapauttaa resurssit yhdessä paikassa. Malli on
  vakiintunut, koska se pitää virhepolut lyhyinä ja vapautukset
  käänteisessä järjestyksessä.
- **Kirjasto ei tulosta eikä lopeta.** Kirjastofunktio palauttaa virheen
  kutsujalle. Vain sovellus päättää, tulostetaanko viesti, yritetäänkö
  uudelleen vai lopetetaanko.
- **`assert` ohjelmointivirheille, paluuarvo ajonaikaisille.** Väittämä
  on dokumentaatiota esiehdoista; virheellinen syöte ei ole
  ohjelmointivirhe.
- **Virheen konteksti.** Jäsentimet palauttavat virhekoodin lisäksi
  sijainnin (rivi ja sarake), jotta käyttäjä voi korjata syötteen.
- **Määrittelemätön käyttäytyminen torjutaan työkaluilla:** varoitukset,
  sanitoijat testeissä, `ckd_*`-tarkistukset ja syötettä käsittelevän
  koodin sumutestaus (*fuzzing*, luku 13).

## Itsearviointi

- Osaat suunnitella virhekoodiluettelon tekstitaulukkoineen ja käyttää
  sitä johdonmukaisesti.
- Osaat kirjoittaa funktion, joka varaa useita resursseja ja vapauttaa ne
  kaikilla poluilla `goto`-siivouksella.
- Osaat erottaa ohjelmointivirheet (`assert`) ajonaikaisista virheistä
  (paluuarvo).
- Osaat luetella yleisimmät määrittelemättömän käyttäytymisen lähteet ja
  havaita ne sanitoijilla.
