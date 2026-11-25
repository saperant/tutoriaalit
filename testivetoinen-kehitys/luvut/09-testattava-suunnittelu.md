# Testattava suunnittelu

Osa koodista on helppo testata ja osa lähes mahdoton, eikä ero johdu
testaajan taidoista. Funktio, joka ottaa arvot argumentteina ja
palauttaa tuloksen, testataan yhdellä rivillä. Funktio, joka lukee
kellon, arpoo luvun ja tulostaa ruudulle, vaatii testiltä temppuja.
Tässä luvussa katsotaan, mistä vaikeus syntyy ja miten koodi
järjestetään niin, että suurin osa siitä on helppoa testata.

## Mikä tekee koodista vaikean testata

Testi tarvitsee kaksi asiaa: se asettaa testattavan koodin tunnettuun
tilanteeseen ja havaitsee, mitä tapahtui. Kumpikin vaikeutuu, kun koodi
hakee syötteensä itse tai jättää tuloksensa jonnekin muualle:

- **Piilotetut syötteet:** kellonaika, satunnaisluvut, ympäristömuuttujat,
  globaalit muuttujat, tiedostot, tietokanta ja verkko.
- **Piilotetut tulokset:** tulostus, tiedostoon tai tietokantaan
  kirjoittaminen, viestin lähetys, globaalin tilan muutos.
- **Itse luodut kumppanit:** funktio luo sisällään tietokantayhteyden
  tai HTTP-asiakkaan, jolloin testi ei pääse vaihtamaan sitä.

Esimerkki, jossa on näistä kolme. Funktio laskee tilaukselle lähtö- ja
saapumispäivän, arpoo seurantakoodin ja tulostaa vahvistuksen:

```{.python tiedosto="esimerkit/09-saumat/ennen.py" osa="ennen"}
```

Tulos riippuu siitä, milloin funktio ajetaan. Testi, joka menee läpi
tiistaina kello kymmenen, epäonnistuu perjantaina kello neljä, ja
seurantakoodi on joka kerta eri.

## Sauma

Michael Feathers kutsuu **saumaksi** (*seam*) kohtaa, jossa ohjelman
käytöstä voi muuttaa muokkaamatta itse koodia. Pythonissa lähes kaikki
on saumaa, koska moduulin nimet voi vaihtaa ajon aikana. Pytestin
`monkeypatch` tekee sen ja palauttaa alkuperäisen testin jälkeen:

```{.python tiedosto="esimerkit/09-saumat/test_ennen.py" osa="paikkaus"}
```

Testi toimii, ja joskus tämä on ainoa keino päästä alkuun (luku 10).
Sillä on kuitenkin hintansa:

- Testi tietää, *miten* funktio hakee ajan: moduulin `ennen` nimen
  `datetime` kautta. Jos toteutus vaihtaa tuontitapaa tai kutsuu
  `time.time()`, testi hajoaa tai, pahempaa, lakkaa vaikuttamasta ja
  lukee oikeaa kelloa.
- `random.choice` paikataan koko prosessille. Muukin koodi, joka arpoo
  testin aikana, saa väärennöksen.
- Yksi testi tarkistaa kaiken kerralla, koska tulos on vain merkkijono
  ruudulla. Kun se epäonnistuu, vika voi olla päivälaskennassa,
  muotoilussa tai koodin arvonnassa.
- Jokainen uusi tapaus (lauantai, tasan kello 15) tarvitsee uuden
  kellon väärennöksen.

Monissa kielissä tätä saumaa ei edes ole: käännetyssä C++- tai
Rust-ohjelmassa funktiokutsua ei vaihdeta ajon aikana. Kestävämpi
ratkaisu on tehdä riippuvuudesta näkyvä.

## Riippuvuudet argumentteina

**Riippuvuuksien injektointi** (*dependency injection*) tarkoittaa
yksinkertaisimmillaan, että funktio saa tarvitsemansa argumentteina sen
sijaan, että hakisi ne itse. Kellonaika on arvo: `datetime`.
Satunnaisuus on olio: `random.Random`, jolle voi antaa siemenen.

Sama logiikka näin kirjoitettuna:

```{.python tiedosto="esimerkit/09-saumat/jalkeen.py" osa="ydin"}
```

Jokainen funktio on **puhdas**: tulos riippuu vain argumenteista, eikä
funktio muuta mitään itsensä ulkopuolella. Lisäksi tulos on olio
`Vahvistus` eikä tuloste, joten testi voi kysyä päivämäärää
jäsentämättä tekstiä.

Kello, oikea satunnaisuus ja tulostus eivät kadonneet. Ne siirtyivät
yhteen paikkaan:

```{.python tiedosto="esimerkit/09-saumat/jalkeen.py" osa="kuori"}
```

Seurantakoodi arvotaan tuotannossa käyttöjärjestelmän
satunnaislähteestä (`SystemRandom`), koska koodin ei pidä olla
arvattavissa (taito *Tietoturva kehitystyössä*). Testi antaa tilalle
siemennetyn generaattorin. Ytimelle ne ovat sama rajapinta.

## Puhdas ydin, ohut kuori

Rakennetta kutsutaan nimellä **puhdas ydin ja imperatiivinen kuori**
(*functional core, imperative shell*; Gary Bernhardt). Ydin sisältää
päätökset ja laskennan, kuori syötön ja tulostuksen.

```{.dot otsikko="Päätökset ovat ytimessä, sivuvaikutukset kuoressa"}
digraph {
  rankdir=LR; ranksep=0.6;
  subgraph cluster_kuori {
    label="Kuori: vähän haaroja,\nmuutama integraatiotesti";
    color="#5B6B70"; fontsize=9;
    lue [label="Lue\nkello, arpa, kanta"];
    kirjoita [label="Kirjoita\ntuloste, kanta, verkko"];
  }
  ydin [label="Ydin\npuhtaat funktiot\npaljon yksikkötestejä", fillcolor="#CDE8C5"];
  lue -> ydin [label="arvot"];
  ydin -> kirjoita [label="tulos"];
}
```

Ytimen testit ovat taulukoita: syöte sisään, arvo ulos, ei paikkauksia
eikä väärennöksiä.

```{.python tiedosto="esimerkit/09-saumat/test_jalkeen.py" osa="ydintestit"}
```

```{.tuloste tiedosto="esimerkit/09-saumat/odotettu"}
```

Yhden kaiken kattavan testin tilalla on yhdeksän pientä, ja jokaisen
nimi kertoo säännön. Raja-arvot (14.59 ja 15.00, perjantai ja lauantai)
ovat rivejä taulukossa. Samalle ytimelle voi kirjoittaa
ominaisuustestin: saapumispäivä ei ole koskaan viikonloppu, eikä se ole
ennen lähtöpäivää.

Kuoressa ei ole yhtään ehtolausetta, joten sille riittää yksi testi,
joka varmistaa, että osat on kytketty oikein. Usein se on
integraatiotesti (taito *Integraatiotestaus ja Testcontainers*).

Jako ei aina ole näin siisti. Kun päätös riippuu tiedosta, joka pitää
hakea kesken laskennan, kuori ja ydin vuorottelevat: hae, päätä, hae
lisää, päätä. Silloinkin päätökset kannattaa pitää omina funktioinaan,
jotka saavat haetun tiedon argumenttina.

## Rajapinta saumana

Kaikkea ei voi antaa arvona. Maksupalvelu, sähköpostin lähetys ja
tietokanta ovat palveluja, joita kutsutaan. Niille sauma on rajapinta:
luvun 3 `Kassa` sai varaston ja maksupalvelun konstruktorissa, ja testi
antoi tilalle muistissa toimivat väärennökset.

Sama pätee kelloon silloin, kun aikaa kysytään monta kertaa, kuten
aikakatkaisuissa ja uudelleenyrityksissä. Olio saa konstruktorissa
funktion, joka palauttaa nykyhetken. Tuotannossa se on `time.monotonic`,
ja testissä väärennetty kello, jota testi siirtää eteenpäin. Näin
testin ei tarvitse odottaa oikeasti: nukkuva testi on hidas ja
epävakaa (taito *Taustapalvelut* käsittelee uudelleenyritykset).

Injektointiin ei tarvita kehystä. Konstruktorin argumentti, jolla on
järkevä oletusarvo, riittää useimpiin ohjelmiin:

```text
def __init__(self, kello: Callable[[], float] = time.monotonic) -> None:
```

## Aika ja satunnaisuus

Aika ja satunnaisuus ovat **epävakaiden testien** (*flaky tests*)
tavallisimmat lähteet. Testi, joka menee läpi useimmiten, opettaa
tiimin ajamaan epäonnistuneen ajon uudelleen, ja sen jälkeen oikeakin
virhe ohitetaan samalla tavalla.

| Lähde | Oire | Korjaus |
|------------------|------------------------------|---------------------------|
| nykyhetki | testi hajoaa viikonloppuna, kuun vaihteessa tai keskiyöllä | aika argumenttina tai kello-oliona |
| aikavyöhyke | menee läpi omalla koneella, ei CI:ssä | aikavyöhyke mukana arvossa; CI ajaa UTC:ssä |
| odottaminen | `sleep(0.1)` riittää yleensä, ei aina | väärennetty kello; odota ehtoa, älä aikaa |
| satunnaisuus | harvinainen arvo rikkoo testin | generaattori argumenttina, siemen kiinni |
| järjestys | joukon tai sanakirjan alkiot eri järjestyksessä | vertaa joukkoina tai lajittele ensin |
| jaettu tila | testi toimii yksin mutta ei sarjassa | jokainen testi luo oman tilansa |

Epävakaa testi kannattaa korjata tai poistaa heti. Sen merkitseminen
"tunnetusti epävakaaksi" on väliaikainen ratkaisu, jolle pitää olla
omistaja ja päivämäärä.

## Käytännössä

- **Erota päätös ja sivuvaikutus.** Funktio joko laskee tai tekee,
  mieluiten ei molempia. Laskevat funktiot testataan arvoilla.
- **Palauta arvo, älä tulosta.** Tulos, jonka voi palauttaa, on helpompi
  tarkistaa kuin tulos, joka pitää kaapata.
- **Anna aika ja satunnaisuus argumentteina.** `datetime.now()` ja
  `random` kuuluvat ohjelman reunalle, eivät laskentasääntöjen sekaan.
- **Injektoi palvelut konstruktorissa.** Oletusarvona oikea toteutus,
  testissä väärennös.
- **`monkeypatch` on viimeinen keino.** Se sopii perintökoodin
  ensimmäiseen testiin ja ympäristömuuttujiin. Jos uusi koodi vaatii
  sitä, suunnittelussa on korjattavaa.
- **Älä lisää rajapintoja varmuuden vuoksi.** Rajapinta jokaisen luokan
  edessä tekee koodista vaikean lukea. Sauma tarvitaan sinne, missä on
  hitautta, epädeterminismiä tai ulkoinen järjestelmä.
- **Kuuntele testiä.** Jos testi tarvitsee viisi paikkausta, se kertoo
  koodin rakenteesta, ei testikehyksen puutteista.

## Itsearviointi

- Osaat tunnistaa funktiosta piilotetut syötteet ja tulokset.
- Osaat selittää, mikä sauma on, ja antaa esimerkin sekä paikkaamalla
  että argumentilla tehdystä saumasta.
- Osaat jakaa funktion puhtaaseen ytimeen ja ohueen kuoreen ja kertoa,
  miten kumpikin testataan.
- Osaat tehdä ajasta ja satunnaisuudesta riippuvasta koodista
  deterministisesti testattavan.
- Osaat nimetä epävakaiden testien tavallisimmat syyt ja korjauksen
  kuhunkin.
