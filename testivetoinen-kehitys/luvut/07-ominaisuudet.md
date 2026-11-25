# Ominaisuuspohjainen testaus

Tähän asti jokainen testi on ollut esimerkki: tämä syöte, tuo tulos.
Esimerkkitestin heikkous on, että se tarkistaa vain ne tapaukset, jotka
kirjoittaja keksi, ja kirjoittaja keksii samat tapaukset testiin ja
koodiin. **Ominaisuuspohjainen testi** (*property-based test*) kääntää
asetelman: ohjelmoija kirjoittaa väitteen, jonka pitää päteä *kaikille*
syötteille, ja kirjasto tuottaa syötteet ja etsii vastaesimerkkiä.

Tekniikka on peräisin Haskellin QuickCheck-kirjastosta (Claessen ja
Hughes, 2000). Pythonissa sen toteuttaa Hypothesis; vastaavia ovat
fast-check (JavaScript), jqwik (Java), proptest (Rust) ja RapidCheck
(C++).

## Esimerkit, jotka menevät läpi

Rahasummien apufunktiot muotoilevat sentit tekstiksi, jäsentävät tekstin
takaisin, jakavat laskun osiin ja laskevat prosenttiosuuden. Tässä on
ensimmäinen versio, jossa on kolme virhettä:

```{.python tiedosto="esimerkit/07-ominaisuudet/1-viallinen/raha.py" osa="viat"}
```

Esimerkkitestit ovat huolellisia, ja ne menevät kaikki läpi:

```{.python tiedosto="esimerkit/07-ominaisuudet/1-viallinen/test_1_esimerkit.py" osa="esimerkit"}
```

## Kolme tapaa keksiä ominaisuus

Vaikein osa on keksiä väite, joka pätee kaikille syötteille ilman, että
testi laskee oikean tuloksen itse. Kolme mallia kattaa suurimman osan
tapauksista.

**Edestakaisuus** (*round trip*): kun kaksi funktiota ovat toistensa
käänteisfunktioita, niiden yhdistelmän pitää palauttaa alkuperäinen
arvo. Malli sopii kaikkeen, missä on muotoilu ja jäsennys, pakkaus ja
purku tai tallennus ja lataus.

```{.python tiedosto="esimerkit/07-ominaisuudet/1-viallinen/test_2_ominaisuudet.py" osa="edestakaisin"}
```

`@given` kertoo, mistä syötteet tulevat. `summat` on **strategia**
`st.integers(min_value=0, max_value=10**9)`, joka tuottaa kokonaislukuja
annetulta väliltä. Hypothesis ajaa testin oletuksena sadalla eri
arvolla, tämän tutoriaalin asetuksilla kahdellasadalla.

**Invariantti**: jokin tuloksen ominaisuus säilyy syötteestä riippumatta.
Tasan jaetun laskun osien summa on alkuperäinen summa, osia on pyydetty
määrä, eivätkä ne eroa toisistaan senttiä enempää:

```{.python tiedosto="esimerkit/07-ominaisuudet/1-viallinen/test_2_ominaisuudet.py" osa="invariantti"}
```

**Oraakkeli**: tulosta verrataan toiseen toteutukseen, joka on hidas
mutta ilmeisen oikein. Kokonaislukujen pyöristyskaava on nopea ja
helppo kirjoittaa väärin; desimaaliluvuilla laskeva versio on hidas ja
helppo tarkistaa silmällä:

```{.python tiedosto="esimerkit/07-ominaisuudet/1-viallinen/test_2_ominaisuudet.py" osa="oraakkeli"}
```

Oraakkeliksi käy myös vanha toteutus uutta kirjoitettaessa, saman
algoritmin optimoimaton versio tai standardikirjaston funktio (taito
*Edistyneet algoritmit ja tietorakenteet* käyttää samaa ideaa
tietorakenteiden testaamiseen).

## Vastaesimerkki ja sen pienentäminen

Kaikki kolme ominaisuutta kaatuvat:

```{.tuloste tiedosto="esimerkit/07-ominaisuudet/1-viallinen/odotettu"}
```

Jokaisen epäonnistumisen alla on syöte, jolla väite ei pidä. Syötteet
ovat silmiinpistävän pieniä: yksi sentti, yksi sentti kahdelle,
viisikymmentä prosenttia yhdestä sentistä. Hypothesis ei löytänyt juuri
näitä ensin. Kun satunnainen syöte rikkoo väitteen, kirjasto
**pienentää** (*shrink*) sitä: se kokeilee yhä yksinkertaisempia
syötteitä niin kauan kuin väite pysyy rikki, ja raportoi
yksinkertaisimman. Pienennetty vastaesimerkki on usein valmis
vianmääritys:

- `sentit=1`: muotoilu tuottaa tekstin "0,1", jonka jäsennys lukee
  kymmeneksi sentiksi. Senttiosasta puuttuu etunolla. Esimerkkitestien
  1234 ja 99 senttiä eivät osuneet tähän.
- `summa=1, osia=2`: kokonaislukujako hukkaa jakojäännöksen, ja yksi
  sentti katoaa. Esimerkkitestin 900 senttiä kolmelle meni tasan.
- `sentit=1, prosentit=50`: puoli senttiä pyöristyy nollaan. Pythonin
  `round` pyöristää puolikkaan lähimpään parilliseen lukuun, mikä on
  tilastoissa hyödyllistä ja laskutuksessa yllätys.

Korjatussa versiossa kaikki testit menevät läpi:

```{.python tiedosto="esimerkit/07-ominaisuudet/2-korjattu/raha.py" osa="raha"}
```

```{.tuloste tiedosto="esimerkit/07-ominaisuudet/2-korjattu/odotettu"}
```

## Toistettavuus

Satunnainen testi, joka epäonnistuu joskus, on pahempi kuin ei testiä
lainkaan. Hypothesis ratkaisee tämän oletuksena tallentamalla löydetyt
vastaesimerkit tietokantaan hakemistoon `.hypothesis`: seuraava ajo
kokeilee ne ensin. Jatkuvassa integraatiossa tavallisempi valinta on
tehdä koko ajosta deterministinen. Tämän tutoriaalin esimerkit käyttävät
profiilia, jossa syötteet johdetaan testifunktiosta eikä tietokantaa ole:

```{.python tiedosto="esimerkit/07-ominaisuudet/1-viallinen/conftest.py" osa="profiili"}
```

Kumpikin tapa on perusteltu. Deterministinen ajo antaa saman tuloksen
jokaisella koneella. Satunnainen ajo kokeilee joka kerta uusia
syötteitä ja löytää ajan mittaan enemmän, kunhan löydöt tallentuvat.
Moni tiimi ajaa deterministisen profiilin jokaiselle muutokselle ja
satunnaisen, pidemmän ajon öisin.

Kun vastaesimerkki on löytynyt, se kannattaa lisätä pysyväksi
esimerkiksi koristeella `@example(sentit=1)`. Silloin juuri tämä tapaus
ajetaan aina, generaattorista riippumatta.

## Tilakonetesti

Ominaisuuden voi kirjoittaa myös toimintosarjoille. **Tilakonetestissä**
kirjasto tuottaa satunnaisia operaatiosarjoja ja tarkistaa jokaisen
askeleen jälkeen, että testattava olio vastaa yksinkertaista **mallia**.
Malli on oraakkeli, jolla on tila. Korin malliksi riittää laskuri
tuotteista määriin:

```{.python tiedosto="esimerkit/07-tilakone/test_tilakone.py" osa="kone"}
```

Jokainen `@rule` on operaatio, jonka Hypothesis voi valita seuraavaksi,
ja `@invariant` tarkistetaan jokaisen askeleen jälkeen. Rivi
`TestKori = KoriKone.TestCase` tekee koneesta pytest-testin. Sama kone
ajetaan viallista koria vasten, jonka poisto on kirjoitettu näin:

```{.python tiedosto="esimerkit/07-tilakone/kori_viallinen.py" osa="vika"}
```

```{.tuloste tiedosto="esimerkit/07-tilakone/odotettu"}
```

Vastaesimerkki on yhden operaation mittainen: tuotteen poistaminen
tyhjästä korista jättää koriin rivin, jonka määrä on nolla. Ohjelmoija
olisi luultavasti testannut tapauksen "lisää ja poista sama määrä".
Kone löysi vielä lyhyemmän polun, jota kukaan ei tullut ajatelleeksi.

Tilakonetesti sopii olioille, joilla on vähän operaatioita ja paljon
mahdollisia järjestyksiä: välimuistit, jonot, tilakoneet, tiedostomuodot
ja tietokantakerrokset.

## Missä ominaisuustesti ei auta

- **Väitettä ei aina ole.** "Hinnan pitää olla oikea" ei ole ominaisuus.
  Jos ainoa tapa ilmaista odotus on laskea se uudelleen samalla
  kaavalla, kirjoita esimerkkitestejä.
- **Liian väljä väite löytää vähän.** "Tulos ei ole negatiivinen" menee
  läpi lähes millä tahansa toteutuksella. Ominaisuustestit täydentävät
  esimerkkejä, eivät korvaa niitä.
- **Syötteiden rajaaminen on työtä.** Kelvollisen tilauksen tai
  syntaksipuun tuottava strategia voi olla pidempi kuin testi. Väärin
  rajattu strategia testaa väärää asiaa: jos `min_value=1` rajaa nollan
  pois, nollaa ei kokeilla koskaan.
- **Satunnaisuus ei korvaa rajoja.** Hypothesis kokeilee mielellään
  nollaa, ykköstä ja ääriarvoja, mutta se ei tiedä, että 5 000 senttiä
  on liiketoiminnan raja. Raja-arvotestit kirjoitetaan edelleen itse.
- **Hitaus.** Sata ajoa testiä kohden on paljon, jos yksi ajo käy
  tietokannassa. Ominaisuustestit kuuluvat nopealle, puhtaalle koodille
  (luku 9).

## Käytännössä

- **Aloita edestakaisuudesta.** Jos koodissa on jäsennin ja muotoilija,
  ensimmäinen ominaisuustesti on yhden rivin mittainen ja löytää usein
  jotain.
- **Pidä esimerkkitestit.** Ne dokumentoivat tärkeimmät tapaukset
  luettavasti. Ominaisuustesti etsii sen, mitä et tullut ajatelleeksi.
- **Lue pienennetty vastaesimerkki ennen koodia.** Se kertoo usein vian
  suoraan.
- **Tee löydöstä pysyvä esimerkki.** `@example(...)` tai tavallinen
  testi, jossa on vastaesimerkin arvot ja selittävä nimi.
- **Valitse toistettavuuden tapa tietoisesti.** Deterministinen
  profiili jokaiselle muutokselle; satunnainen ajo vain, jos löydöt
  tallentuvat ja joku lukee ne.
- **Sama ajatus toimii ilman kirjastoakin.** Silmukka, joka vertaa
  nopeaa toteutusta hitaaseen tuhannella siemenestä arvotulla syötteellä,
  on jo ominaisuustesti. Kirjasto lisää pienentämisen ja strategiat.

## Itsearviointi

- Osaat kirjoittaa ominaisuustestin kolmella mallilla: edestakaisuus,
  invariantti ja oraakkeli.
- Osaat lukea pienennetyn vastaesimerkin ja päätellä siitä vian.
- Osaat selittää, mitä pienentäminen tekee ja miksi se on tärkeää.
- Osaat tehdä satunnaistetusta testistä toistettavan ja perustella
  valitsemasi tavan.
- Osaat kuvata tilakonetestin osat: operaatiot, malli ja invariantit.
- Osaat nimetä tilanteita, joissa esimerkkitesti on ominaisuustestiä
  parempi.
