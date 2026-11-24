# Koneoppimisen rajapinta

Tunnistustehtävät, kuten "onko kuvassa jalankulkija" tai "mikä tuote
hihnalla on", ratkaistaan nykyään yleensä neuroverkoilla. Ne oppivat
piirteet itse aineistosta eivätkä tarvitse käsin suunniteltuja reunoja,
kulmia tai muotomittoja. Klassinen konenäkö ei silti katoa: se on
neuroverkon molemmin puolin. Ennen verkkoa kuva esikäsitellään,
rajataan ja normitetaan, ja verkon jälkeen tulokset karsitaan,
sijoitetaan maailmaan kameramallilla ja seurataan ajassa. Tässä luvussa
rakennetaan klassinen luokittelija, arvioidaan se oikein ja käydään läpi
rajapinta, jolla OpenCV ajaa valmiita malleja.

## Klassinen luokittelija

Klassinen putki on kaksivaiheinen: käsin suunnitellut piirteet ja niiden
päälle yksinkertainen luokittelija. Esimerkissä muodot luokitellaan
kolmioiksi, neliöiksi ja ympyröiksi luvun 4 piirteillä: pyöreys,
täyttöaste ympäröivässä suorakaiteessa, kuperuus ja ensimmäinen
Hu-momentti. Kaikki ovat kokoon nähden muuttumattomia, joten niiden
pitäisi toimia kaikenkokoisille muodoille.

```{.python tiedosto="esimerkit/11-luokittelu.py" osa="data"}
```

Luokittelija on **k lähintä naapuria** (*k-NN*): uusi näyte saa sen
luokan, joka on yleisin sen $k$ lähimmän opetusnäytteen joukossa.
Piirteet normitetaan ensin samaan mittakaavaan, koska muuten suurin
piirre määrää etäisyyden. Normitusparametrit lasketaan vain
opetusjoukosta. OpenCV 4:ssä k-NN oli modulissa `cv2.ml`, mutta
OpenCV 5 siirsi koneoppimisen lisämoduleihin, joten esimerkki toteuttaa
sen muutamalla NumPy-rivillä.

```{.python tiedosto="esimerkit/11-luokittelu.py" osa="opetus"}
```

```{.tuloste tiedosto="esimerkit/11-luokittelu.odotettu"}
```

## Arviointi ja jakauman muutos

Tulos opettaa luvun tärkeimmän asian. Testijoukossa, joka on samasta
jakaumasta kuin opetusjoukko, luokittelija on virheetön. Kun samat muodot
ovat pieniä (3–6 pikseliä), osuvuus putoaa 62 prosenttiin, ja ympyrät
tunnistetaan kolmioiksi ja neliöiksi. Pienet ympyrät ovat pikseleinä
monikulmioita, joten "kokoon nähden muuttumattomat" piirteet eivät
olekaan sitä pienillä kooilla.

Neuroverkoille sama pätee vielä voimakkaammin. Malli on yhtä hyvä kuin
aineisto, josta se oppi, ja arvio on yhtä hyvä kuin testijoukko, jolla se
mitattiin. Siksi:

- **Testijoukko erotetaan ennen kaikkea muuta**, eikä sillä säädetä
  mitään. Säätöön käytetään erillistä validointijoukkoa.
- **Testijoukko kuvaa käyttötilanteen**: valaistukset, kamerat, koot ja
  harvinaiset tapaukset. Satunnainen otos samasta keräyksestä ei riitä.
- **Kokonaisosuvuus kertoo vähän.** **Sekaannusmatriisi** näyttää, mitkä
  luokat sekoittuvat, ja luokkakohtaiset **tarkkuus** ja **saanti** (luku
  4) kertovat virheiden luonteen. Harvinaisen luokan tunnistin, joka
  sanoo aina "ei", saavuttaa korkean osuvuuden ja on hyödytön.

## Esikäsittely neuroverkolle

OpenCV:n `dnn`-moduli ajaa valmiiksi opetettuja malleja: ONNX-muotoisia
malleja ja useiden kehysten omia muotoja. Moduli ei opeta malleja, vaan
on päättelymoottori (*inference*), joka toimii samalla ohjelmalla
palvelimessa ja sulautetussa laitteessa. Verkon syöte on yleensä
**NCHW-taulukko**: kuvat × kanavat × korkeus × leveys, liukulukuina.
`blobFromImage` tekee tarvittavat muunnokset: koon muutoksen,
skaalauksen, keskiarvon vähennyksen ja tarvittaessa BGR–RGB-vaihdon.

```{.python tiedosto="esimerkit/11-tunnistus.py" osa="blob"}
```

Esikäsittelyn on vastattava täsmälleen sitä, jolla malli opetettiin.
Väärä värijärjestys (luku 2), väärä normitus tai väärä koko eivät
tuota virheilmoitusta, vaan hiljaa huonompia tuloksia. Malli ladattaisiin
komennolla `cv2.dnn.readNetFromONNX` ja ajettaisiin kutsuilla
`setInput` ja `forward`. Tämä tutoriaali ei lataa malleja, koska ne ovat
suuria ja niiden lisenssit vaihtelevat. Sama esikäsittely ja
jälkikäsittely toimivat millä tahansa mallilla.

## Tunnistusten jälkikäsittely

Kohteentunnistin (*object detector*) palauttaa suorakaiteita ja niiden
varmuuksia, ja samasta kohteesta tulee tyypillisesti useita päällekkäisiä
ehdokkaita. **Ei-maksimien vaimennus** (*non-maximum suppression*, NMS)
säilyttää varmimman ja poistaa ne, jotka ovat sen kanssa liian
päällekkäisiä. Päällekkäisyyden mitta on **IoU** (*intersection over
union*): leikkauksen ala jaettuna yhdisteen alalla. Samaa mittaa
käytetään arvioinnissa: tunnistus lasketaan oikeaksi, jos sen IoU
oikeaan laatikkoon ylittää rajan, tyypillisesti 0,5.

```{.python tiedosto="esimerkit/11-tunnistus.py" osa="iou"}
```

```{.tuloste tiedosto="esimerkit/11-tunnistus.odotettu"}
```

Viidestä ehdokkaasta jää kaksi: kummastakin kohteesta varmin. Viides
ehdokas karsiutui jo varmuusrajalla 0,5.

## Käytännössä

- **Aloita klassisella, jos ympäristö on hallittu.** Teollisuuden
  tarkastuksessa valaistus, kamera ja kappaleet ovat vakioita, ja
  kynnystys, mittaus ja muotopiirteet ovat nopeita, selitettäviä ja
  ilman opetusaineistoa toimivia.
- **Käytä oppivaa mallia, kun vaihtelu on suurta.** Luonnollisissa
  ympäristöissä käsin tehdyt piirteet eivät riitä, ja valmiiksi
  opetettu malli hienosäädettynä omaan aineistoon on yleensä paras
  lähtökohta.
- **Kopioi esikäsittely opetuksesta.** Koko, värijärjestys, skaalaus ja
  normitus täsmälleen kuten mallin dokumentaatio määrää. Testaa
  tunnetulla kuvalla, että tulos vastaa julkaistua.
- **Arvioi käyttötilanteen aineistolla.** Erillinen testijoukko,
  sekaannusmatriisi, luokkakohtainen tarkkuus ja saanti sekä IoU-raja
  tunnistuksille.
- **Tarkista mallien ja aineistojen lisenssit.** Monet julkiset mallit ja
  aineistot rajoittavat kaupallista käyttöä.

## Itsearviointi

- Osaat rakentaa klassisen luokittelijan muotopiirteistä ja k-NN:stä ja
  normittaa piirteet opetusjoukon perusteella.
- Osaat arvioida luokittelijan erillisellä testijoukolla
  sekaannusmatriisin avulla ja tunnistaa jakauman muutoksen.
- Osaat valmistella kuvan neuroverkon syötteeksi `blobFromImage`-funktiolla
  ja selittää, miksi esikäsittelyn on vastattava opetusta.
- Osaat laskea IoU:n ja karsia päällekkäiset tunnistukset NMS:llä.
