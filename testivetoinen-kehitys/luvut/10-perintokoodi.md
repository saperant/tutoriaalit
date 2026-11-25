# Perintökoodi ja karakterisointitestit

Tähän asti koodi on kirjoitettu testien kanssa. Useimmiten tilanne on
toinen: koodi on olemassa, se on tuotannossa, sen kirjoittaja on
vaihtanut työpaikkaa eikä testejä ole. Michael Feathers määrittelee
**perintökoodin** (*legacy code*) juuri näin: koodi ilman testejä.
Määritelmä on tarkoituksella käytännöllinen. Ilman testejä muutoksen
vaikutuksia ei voi tarkistaa, ja siksi koodia ei uskalleta muuttaa.

Tästä seuraa kehä: koodia ei voi muuttaa turvallisesti ilman testejä,
mutta testien kirjoittaminen vaatii usein koodin muuttamista. Tämä luku
näyttää, miten kehästä päästään ulos.

## Koodi, jota kukaan ei uskalla muuttaa

Verkkokaupan laskun tulostus on neljänkymmenen rivin funktio:

```{.python tiedosto="esimerkit/10-perinto/lasku_vanha.py" osa="vanha"}
```

Funktioon pitäisi lisätä uusi kampanjakoodi. Muuttujien nimet eivät
kerro mitään, alennussäännöt ovat sisäkkäisissä ehdoissa ja rahan
muotoilu on kopioitu neljään paikkaan. Määrittelyä ei ole. Ainoa
luotettava kuvaus siitä, mitä funktion pitää tehdä, on se, mitä se
tekee nyt: asiakkaat ovat saaneet näitä laskuja vuosia.

## Karakterisointitesti

**Karakterisointitesti** (*characterization test*) ei väitä, että koodi
toimii oikein. Se kirjaa, miten koodi toimii *nyt*, jotta muutos
käytöksessä huomataan. Odotettua tulosta ei johdeta määrittelystä vaan
kysytään koodilta itseltään.

Kun tuloste on tekstiä, helpoin muoto on **kultainen tiedosto**
(*golden master*, *snapshot*, *approval test*): ohjelma ajetaan
kattavalla joukolla syötteitä, tulosteet tallennetaan ja myöhemmät ajot
verrataan tallennettuun.

Syötteet valitaan luvun 5 tekniikoilla. Koodista näkyy kolme asiaa,
jotka vaikuttavat tulokseen: asiakastyyppi, kampanjakoodi ja korin
sisältö. Jokaiselle valitaan arvot, jotka osuvat koodin haaroihin, ja
kaikki yhdistelmät otetaan mukaan, koska niitä on vain 36:

```{.python tiedosto="esimerkit/10-perinto/tapaukset.py" osa="syotteet"}
```

Korit on valittu lukemalla koodin vakioita, niin että jokainen haara
tulee käytyä: kymmenen kappaleen paljousraja, 100 euron raja
kanta-asiakkaan alennukselle ja 30 sekä 50 euron rajat toimitukselle.
Erillinen skripti `tallenna.py` ajaa
vanhan funktion kaikilla tapauksilla ja kirjoittaa tulosteet tiedostoon
`kultainen.txt`. Ote tiedostosta:

```text
== tyyppi2-eikoodia-rajalla
LASKU Testi Asiakas
lahjakortti x1  100,00
Alennus 5 %  -5,00
Toimitus  0,00
YHTEENSÄ  95,00
```

Tiedosto viedään versionhallintaan. Se on nyt funktion määrittely.

Testi vertaa toteutuksen tulostetta tallennettuun jokaisella
tapauksella. Sama testi ajetaan kolmelle toteutukselle: vanhalle,
refaktoroinnin ensimmäiselle luonnokselle ja lopulliselle.

```{.python tiedosto="esimerkit/10-perinto/test_kultainen.py" osa="testi"}
```

## Mitä karakterisointi paljastaa

Kultaisen tiedoston lukeminen on jo hyödyllistä. Siitä löytyy
käytöstä, jota kukaan ei luultavasti suunnitellut:

- Tasan 100 euron tilaus ei saa kanta-asiakkaan suurempaa alennusta,
  koska ehto on `>` eikä `>=`.
- Tuntematon kampanjakoodi tulostuu laskulle sellaisenaan.
- Kymmenen kahvipaketin paljousalennus pudottaa tilauksen alle
  ilmaisen toimituksen rajan: 49,41 euron ostoksesta maksetaan
  toimitus, vaikka ilman alennusta ei maksettaisi.
- Tyhjästä korista tulostuu lasku, jonka summa on nolla.

Jokainen näistä voi olla virhe. Karakterisointivaiheessa niitä **ei
korjata**. Syitä on kaksi. Ensinnäkin joku voi nojata nykyiseen
käytökseen: kirjanpito täsmää vanhoihin laskuihin, tai sopimus sanoo
"yli 100 euron". Toiseksi refaktoroinnin ja käytöksen muutoksen
sekoittaminen vie turvaverkon: kun testi epäonnistuu, ei tiedetä,
johtuuko se tarkoitetusta muutoksesta vai vahingosta.

Löydöt kirjataan ja viedään päätettäviksi sille, joka omistaa säännöt.

## Refaktorointi turvaverkon päällä

Nyt koodia voi muuttaa pienin askelin ja ajaa testit jokaisen jälkeen:
nimetään muuttujat, erotetaan rahan muotoilu funktioksi, nostetaan
rivin hinta, alennusprosentti ja toimitusmaksu omiksi funktioikseen.
Ensimmäisessä luonnoksessa refaktoroija huomasi 100 euron rajan,
piti sitä ilmeisenä virheenä ja "korjasi" sen samalla:

```{.python tiedosto="esimerkit/10-perinto/lasku_luonnos.py" osa="korjaus"}
```

```{.tuloste tiedosto="esimerkit/10-perinto/odotettu"}
```

Kolme vertailua 108:sta epäonnistuu, kaikki luonnoksella ja kaikki
korilla `rajalla`. Testi teki tehtävänsä: se huomasi käytöksen
muutoksen, jonka koodin lukija olisi ohittanut hyväntahtoisena
siistimisenä. Muutos voi olla oikea, mutta se on eri muutos, joka
tehdään erikseen ja jonka mukana kultainen tiedosto päivitetään
tietoisesti.

Lopullinen versio säilyttää käytöksen tarkasti:

```{.python tiedosto="esimerkit/10-perinto/lasku_uusi.py" osa="saannot"}
```

```{.python tiedosto="esimerkit/10-perinto/lasku_uusi.py" osa="lasku"}
```

Säännöillä on nyt nimet, ja jokainen on puhdas funktio (luku 9). Uuden
kampanjakoodin lisääminen on muutos yhteen funktioon, ja sille voi
kirjoittaa tavallisen yksikkötestin ennen toteutusta.

## Kultaisen tiedoston rajat

Karakterisointitesti on rakennusteline, ei valmis rakennus.

- **Se lukitsee myös virheet.** Testi menee läpi, kun koodi tekee saman
  kuin ennen, oli se oikein tai väärin.
- **Se on hauras.** Yksi lisätty välilyönti tulosteeseen rikkoo
  jokaisen tapauksen. Kun kaikki testit epäonnistuvat kerralla,
  houkutus päivittää tiedosto lukematta eroja on suuri, ja silloin
  testi ei suojaa miltään.
- **Se ei kerro, miksi.** Epäonnistunut vertailu näyttää eron, ei
  sääntöä, jota rikottiin.
- **Se kattaa vain valitut syötteet.** Jos koodissa on haara, johon
  mikään tapaus ei osu, sen muutos ei näy. Kattavuusmittaus kertoo,
  mitkä haarat jäivät väliin, ja mutaatiotestaus (luku 8), huomaako
  vertailu muutokset.

Siksi kultaista tiedostoa käytetään siirtymävaiheessa. Kun säännöt on
erotettu funktioiksi, niille kirjoitetaan nimetyt yksikkötestit, ja
kultaisen tiedoston tapauksia vähennetään muutamaan, jotka varmistavat
laskun muodon.

Tilannekuvatestejä käytetään myös uudessa koodissa, esimerkiksi
käyttöliittymäkomponenttien ja kääntäjien tulosteiden testaamiseen.
Samat rajat pätevät: tilannekuva on hyödyllinen, kun joku todella lukee
erot katselmoinnissa.

## Kun koodi ei taivu testiin

Esimerkin funktio oli helppo tapaus: se otti argumentit ja palautti
merkkijonon. Usein perintökoodi lukee tietokantaa, kutsuu verkkoa ja
tulostaa suoraan. Silloin tarvitaan ensin sauma, ja sauman tekeminen
on muutos koodiin ilman testejä. Riskiä pienennetään tekemällä vain
mekaanisia muutoksia, mieluiten kehitysympäristön refaktorointitoiminnoilla:

- **Erota funktio.** Nosta laskenta omaksi funktiokseen niin, että
  alkuperäinen funktio kutsuu sitä. Uutta funktiota voi testata
  arvoilla.
- **Lisää argumentti oletusarvolla.** `def raportti(nyt=None)` säilyttää
  vanhat kutsut ja antaa testille sauman.
- **Kääri ja korvaa.** Siirrä ulkoinen kutsu omaan metodiinsa tai
  luokkaansa, jonka testi voi vaihtaa.
- **Paikkaa.** Luvun 9 `monkeypatch` on tässä oikeutettu: sillä saadaan
  ensimmäinen testi koodiin, jota ei vielä voi muuttaa.

Kun koodiin pitää lisätä uutta käytöstä eikä vanhan testaamiseen ole
aikaa, uusi koodi kirjoitetaan TDD:llä omaan funktioonsa tai luokkaansa
ja vanhasta koodista kutsutaan sitä yhdellä rivillä (Feathers: *sprout
method*). Vanha koodi ei parane, mutta testaamattoman koodin määrä ei
kasva.

Laajemmassa mitassa sama ajatus on **kuristajaviikuna** (*strangler
fig*, Martin Fowler): uusi toteutus rakennetaan vanhan viereen
ominaisuus kerrallaan, liikenne ohjataan sille vähitellen ja vanha
poistetaan, kun mikään ei enää käytä sitä. Vaihtoehto, kaiken
kirjoittaminen uudelleen kerralla, epäonnistuu usein, koska vanhan
järjestelmän käytöstä ei tunneta. Karakterisointi on tapa oppia se.

## Käytännössä

- **Ennen kuin muutat, kirjaa nykyinen käytös.** Tunnin työ
  karakterisointitesteihin säästää päiviä tuotantovirheen selvittelyä.
- **Valitse syötteet koodin haaroista ja vakioista.** Mittaa
  kattavuus: karakterisoinnissa se on oikea mittari, koska tavoite on
  osua jokaiseen haaraan.
- **Pidä refaktorointi ja käytöksen muutos eri commiteissa.** Ensin
  rakenne testien pysyessä vihreinä, sitten muutos ja sen testi.
- **Älä korjaa löytämiäsi virheitä ohimennen.** Kirjaa ne ja kysy.
- **Tee tulosteesta deterministinen ennen tallennusta.** Päivämäärät,
  tunnisteet ja järjestys vakioidaan tai suodatetaan pois, muuten
  vertailu epäonnistuu joka ajolla.
- **Lue jokainen ero ennen kuin päivität kultaisen tiedoston.**
  Päivitys on väite: "tämä muutos oli tarkoitettu."
- **Paranna sitä, mihin kosket.** Koko koodikantaa ei tarvitse saada
  testien piiriin kerralla. Usein muuttuva koodi hyötyy eniten, ja
  koodi, jota kukaan ei muuta, voi odottaa.

## Itsearviointi

- Osaat selittää, miten karakterisointitesti eroaa määrittelystä
  johdetusta testistä ja milloin kumpaakin käytetään.
- Osaat rakentaa kultaisen tiedoston: valita syötteet, tallentaa
  tulosteet ja kirjoittaa vertailevan testin.
- Osaat perustella, miksi karakterisoinnissa löydettyjä virheitä ei
  korjata refaktoroinnin yhteydessä.
- Osaat nimetä kultaisen tiedoston heikkoudet ja kertoa, millä testeillä
  se korvataan ajan mittaan.
- Osaat tehdä perintökoodiin ensimmäisen sauman mahdollisimman pienellä
  riskillä.
