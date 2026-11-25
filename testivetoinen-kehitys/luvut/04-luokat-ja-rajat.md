# Ekvivalenssiluokat ja raja-arvot

Funktiolla, joka ottaa kaksi kokonaislukua, on enemmän mahdollisia
syötteitä kuin koskaan ehditään kokeilla. Testaus on siksi aina otantaa,
ja kysymys kuuluu, miten otos valitaan. Tavallisten arvojen kokeilu ei
riitä: virheet asuvat siellä, missä käytös vaihtuu.

Tämän ja seuraavan luvun tekniikat ovat **mustalaatikkotekniikoita**:
testitapaukset johdetaan määrittelystä, ei koodista. Siksi niitä voi
käyttää ennen kuin koodia on, ja ne sopivat suoraan TDD:n testilistan
laatimiseen.

## Esimerkki: toimitusmaksu

Verkkokaupan toimitusmaksu riippuu paketin painosta ja tilauksen
summasta:

```{.python tiedosto="esimerkit/04-rajat/toimitus.py" osa="maksu"}
```

Jotta näkisimme, mitkä testit löytävät virheitä, rinnalle tehdään
toteutus, jossa on kaksi tavallista virhettä: vertailuoperaattori on
väärin kahdessa kohdassa.

```{.python tiedosto="esimerkit/04-rajat/toimitus_viallinen.py" osa="viat"}
```

Jokainen testi ajetaan molempia toteutuksia vasten. Pytestin fixture
`toimitusmaksu` antaa testille vuorollaan kummankin:

```{.python tiedosto="esimerkit/04-rajat/conftest.py" osa="toteutukset"}
```

Hyvä testisarja menee läpi oikealla toteutuksella ja epäonnistuu
viallisella. Sarja, joka menee läpi molemmilla, ei erota niitä
toisistaan. Luvussa 8 sama ajatus viedään pidemmälle: virheet tekee
kone.

## Tavallisten arvojen kokeilu

Ilman menetelmää testit syntyvät kokeilemalla arvoja, jotka tulevat
ensimmäisenä mieleen:

```{.python tiedosto="esimerkit/04-rajat/test_1_naiivi.py" osa="naiivi"}
```

Viisi testiä, jokainen maksuluokka ja yksi virhetilanne. Sarja näyttää
kattavalta, mutta kumpaakaan virhettä se ei löydä, kuten luvun lopun
tuloksesta näkyy.

## Ekvivalenssiluokat

**Ekvivalenssiluokka** on joukko syötteitä, joita ohjelman pitäisi
kohdella samalla tavalla. Jos 500 gramman paketti hinnoitellaan oikein,
600 gramman paketti tuskin paljastaa mitään uutta. Luokasta riittää
yksi edustaja.

Luokat johdetaan määrittelystä syöte kerrallaan. Myös kelvottomat
syötteet muodostavat luokkia:

| Syöte | Luokka | Edustaja |
|--------|------------------------------------|---------:|
| paino | kelvoton: nolla tai negatiivinen | −100 g |
| paino | pieni paketti: 1–2 000 g | 1 000 g |
| paino | iso paketti: 2 001–10 000 g | 6 000 g |
| paino | rahti: 10 001–30 000 g | 20 000 g |
| paino | kelvoton: yli 30 000 g | 45 000 g |
| summa | alle 50 euroa | 20 e |
| summa | vähintään 50 euroa | 80 e |

Kahden syötteen luokat yhdistetään. Kelvolliset luokat voi yhdistää
vapaasti, mutta kelvottomat testataan yksi kerrallaan: jos testissä on
kaksi kelvotonta arvoa, ei tiedetä, kumpi hylkäyksen aiheutti, ja
toinen tarkistus voi puuttua kokonaan.

```{.python tiedosto="esimerkit/04-rajat/test_2_luokat.py" osa="luokat"}
```

Luokittelu on jo parempi kuin arvailu: se muistuttaa yhdistelmästä
"rahti ja iso tilaus", jota naiivi sarja ei kokeillut. Tämän esimerkin
virheitä se ei silti löydä, koska edustajat ovat luokkien keskeltä.

## Raja-arvoanalyysi

Luokkien rajoilla ohjelmoija kirjoittaa vertailun, ja vertailussa on
neljä tapaa erehtyä: `<` tai `<=`, väärä vakio, käänteinen suunta tai
unohtunut ehto. **Raja-arvoanalyysi** testaa siksi jokaisen rajan
molemmilta puolilta: suurin arvo, joka kuuluu luokkaan, ja pienin, joka
ei kuulu.

| Raja | Viimeinen sisäpuolella | Ensimmäinen ulkopuolella |
|--------------------------|-------------:|-------------:|
| pienin kelvollinen paino | 1 g | 0 g |
| pieni / iso paketti | 2 000 g | 2 001 g |
| iso paketti / rahti | 10 000 g | 10 001 g |
| suurin kelvollinen paino | 30 000 g | 30 001 g |
| ilmaisen toimituksen raja | 50,00 e | 49,99 e |

```{.python tiedosto="esimerkit/04-rajat/test_3_rajat.py" osa="rajat"}
```

Kaikki kolme sarjaa molempia toteutuksia vasten:

```{.tuloste tiedosto="esimerkit/04-rajat/odotettu"}
```

Vain rajatestit erottavat toteutukset. Kaksi testiä epäonnistuu
viallisella toteutuksella, ja virheilmoitus osoittaa suoraan vikaan:
2 000 gramman paketti hinnoiteltiin isona, ja tasan 50 euron tilaus ei
saanut ilmaista toimitusta.

## Rajat, joita määrittely ei mainitse

Kaikki rajat eivät näy vaatimuksessa. Hyvä testaaja etsii myös
tietotyypin ja toteutuksen rajat:

- **Tyhjä ja yksi:** tyhjä lista, tyhjä merkkijono, yhden alkion
  kokoelma, ensimmäinen ja viimeinen alkio.
- **Nolla ja etumerkki:** 0, −1, pienin ja suurin esitettävä luku
  (kielissä, joissa kokonaisluvut vuotavat yli).
- **Aika:** vuorokauden ja kuukauden vaihde, karkauspäivä, kesäaikaan
  siirtyminen, aikavyöhykkeen raja.
- **Teksti:** välilyönti alussa tai lopussa, ääkköset, hyvin pitkä syöte.
- **Monen syötteen rajat:** kahden rajan leikkauspiste. Esimerkissä
  10 000 gramman ja 50 euron tilaus on kahden säännön rajalla yhtä aikaa.

Rajaa ei voi testata, jos sitä ei ole päätetty. Kun vaatimus sanoo
"yli 50 euron tilaukset", kysy, tarkoitetaanko myös tasan 50 euroa.
Vastaus on määrittelyn tarkennus, ja rajatesti kirjaa sen pysyvästi.

## Käytännössä

- **Aloita luokista, lisää rajat.** Luokat varmistavat, että jokainen
  käytös kokeillaan kerran. Rajat löytävät virheet, joita luokkien
  keskeltä ei löydy.
- **Taulukkotestit sopivat tähän.** `pytest.mark.parametrize` pitää
  tapaukset datana, jolloin uusi raja on yksi rivi lisää ja taulukkoa
  voi verrata määrittelyyn rivi riviltä.
- **Nimeä vakiot samoin koodissa ja määrittelyssä.** Kun raja on
  `ILMAISEN_RAJA` eikä `5000`, testin ja koodin ero näkyy
  katselmoinnissa.
- **Älä laske odotettua arvoa testissä samalla kaavalla kuin koodi.**
  Odotettu tulos on kirjattu luku, joka on johdettu määrittelystä. Jos
  testi toistaa toteutuksen kaavan, se toistaa myös sen virheen.
- **Kelvoton syöte on yhtä tärkeä kuin kelvollinen.** Tarkista myös,
  että virhe on oikea: `pytest.raises(ValueError, match="positiivinen")`
  ei mene läpi, jos poikkeus tulee väärästä tarkistuksesta.

## Itsearviointi

- Osaat jakaa funktion syötteet ekvivalenssiluokkiin määrittelyn
  perusteella, myös kelvottomat syötteet.
- Osaat valita raja-arvot jokaisen rajan molemmilta puolilta ja
  selittää, minkä virheen kukin arvo paljastaisi.
- Osaat selittää, miksi kelvottomat arvot testataan yksi kerrallaan.
- Osaat tunnistaa rajoja, joita määrittely ei mainitse.
- Osaat kirjoittaa taulukkomuotoisen testin, jonka rivit vastaavat
  määrittelyn sääntöjä.
