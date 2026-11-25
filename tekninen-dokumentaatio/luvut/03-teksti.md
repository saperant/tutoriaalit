# Selkeä tekninen teksti

Tekninen teksti on käyttöesine. Sen tehtävä on siirtää tieto lukijalle
niin, että hän voi toimia, ja sen laatu mitataan siitä, onnistuiko
lukija. Tyyli on väline: hyvä tekninen teksti on huomaamatonta.

## Tärkein ensin

Lukija silmäilee. Hän lukee otsikon, ensimmäisen virkkeen ja
koodiesimerkin ja päättää niiden perusteella, lukeeko loput. Siksi
tärkein asia kirjoitetaan ensin:

- Sivun ensimmäinen kappale kertoo, mitä sivu käsittelee ja kenelle.
- Kappaleen ensimmäinen virke kertoo kappaleen asian. Loput virkkeet
  tarkentavat.
- Esimerkki tulee ennen sääntöä. Lukija ymmärtää säännön, kun hän on
  nähnyt tapauksen.
- Varoitus tulee ennen askelta, jota se koskee, ei sen jälkeen.

Otsikot ovat sisällysluettelo. Otsikko ”Asetukset” kertoo aiheen,
otsikko ”Aseman lisääminen” kertoo tehtävän. Ohjeissa tehtävää
kuvaava otsikko löytyy haulla, koska lukija hakee sillä, mitä hän
yrittää tehdä.

## Virke ja sana

Yksi virke kantaa yhden asian. Pitkä virke ei ole väärin, mutta jos
siinä on kolme sivulausetta, lukija joutuu pitämään alun mielessään
loppuun asti. Luettelo on parempi kuin virke, jossa on neljä pilkulla
erotettua kohtaa, ja numeroitu luettelo on parempi, kun järjestyksellä
on väliä.

Tekijä näkyviin. ”Asetukset ladataan käynnistyksessä” jättää
kertomatta, kuka lataa. ”Palvelu lataa asetukset käynnistyessään”
kertoo sen. Ohjeissa tekijä on lukija, ja häntä puhutellaan suoraan:
”Aja komento”, ei ”komento ajetaan” eikä ”käyttäjän tulee ajaa
komento”. Suomen passiivi on luonteva silloin, kun tekijällä ei ole
väliä (”lukemat tallennetaan tietokantaan”), mutta ohjeen askeleessa
se hämärtää, kenen pitää toimia.

Täsmällinen on parempi kuin vahva. ”Hyvin nopea” ei kerro mitään;
”vastaa alle 50 millisekunnissa” kertoo. ”Tuetaan useita muotoja” ei
auta; luettelo muodoista auttaa. Luku ilman yksikköä on puolikas tieto.

Lukijaa vähättelevät sanat pois. ”Yksinkertaisesti”, ”helposti” ja
”tietenkin” eivät tee asiasta helppoa. Lukijalle, jolle se ei ole
helppoa, ne kertovat, että vika on hänessä.

## Yksi asia, yksi nimi

Kaunokirjallisuudessa toisto on tyylivirhe, teknisessä tekstissä
synonyymi on virhe. Jos teksti puhuu ensin asemasta, sitten laitteesta
ja sitten anturista, lukija olettaa, että ne ovat kolme eri asiaa.
Termi valitaan kerran ja siinä pysytään.

Projektin sanasto on lyhyt luettelo: termi, sen määritelmä ja muodot,
joita ei käytetä. Sanasto ratkaisee etukäteen kiistat, jotka muuten
käydään jokaisessa katselmoinnissa, ja se on käännettävissä
tarkistukseksi.

Suomenkielisessä dokumentaatiossa termiongelma on kaksinkertainen,
koska englanninkielinen termi on usein tutumpi kuin suomennos.
Käytännöllinen sääntö: käytä vakiintunutta suomenkielistä termiä, jos
sellainen on (palvelin, rajapinta, haara), ja mainitse englanninkielinen
termi kerran kursiivilla, jotta lukija löytää lisätietoa
hakukoneella. Puhekielen muodot (serveri, konffi, deployata)
kuuluvat keskusteluun, eivät dokumenttiin. Koodin nimiä, komentoja
ja tiedostonimiä ei taivuteta eikä suomenneta, vaan ne ladotaan
koodina ja taivutetaan tarvittaessa pääsanan avulla: ”funktio
`jasenna_rivi` palauttaa”, ei ”`jasenna_rivi`:n palautus”.

## Esimerkit ja koodi

Esimerkki on dokumentin luetuin osa, ja se kopioidaan sellaisenaan.
Siksi sen pitää toimia sellaisenaan:

- Esimerkki on kokonainen: tuonnit mukana, muuttujat määritelty.
- Esimerkki on todellinen: oikeat kentät ja uskottavat arvot, ei
  `foo` ja `bar`.
- Tuloste näytetään, jotta lukija voi verrata omaansa siihen.
- Esimerkki ajetaan testissä (luvut 5 ja 12). Käsin kirjoitettu
  esimerkki on väärin viimeistään seuraavan muutoksen jälkeen.

Paikanvaraajat merkitään niin, ettei niitä voi luulla oikeiksi
arvoiksi: `<asema>` tai `ASEMA`, ja selitetään heti esimerkin
jälkeen.

## Tarkistus koneella

Osan näistä säännöistä voi tarkistaa mekaanisesti. Esimerkkien
tarkistin `tyokalut/proosa.py` tuntee muutaman säännön ja projektin
sanaston:

```{.python tiedosto="esimerkit/tyokalut/proosa.py" osa="saannot"}
```

Edellisen luvun sekava ohje saa kahdeksan huomautusta:

```{.tuloste tiedosto="esimerkit/naytteet/sekava-ohje.proosa.odotettu"}
```

Tarkistin ei tiedä, onko teksti hyvää. Se löytää asiat, jotka ihminen
ohittaa kymmenennellä lukukerralla: sovitun termin vastaisen sanan,
unohtuneen TODO-merkinnän ja virkkeen, joka on kasvanut liian pitkäksi.
Valmiita työkaluja ovat esimerkiksi Vale, jolle säännöt kirjoitetaan
YAML-tiedostoina, ja suomen oikolukuun Voikko. Säännöt kannattaa pitää
harvoina: tarkistin, joka huomauttaa kaikesta, kytketään pois.

## Käytännössä

- **Kirjoita ensin, karsi sitten.** Ensimmäinen versio sisältää kaiken,
  mitä kirjoittaja tietää. Toinen sisältää sen, mitä lukija tarvitsee.
- **Lue ääneen tai anna toisen lukea.** Kohta, jossa lukija pysähtyy,
  on kohta, joka pitää korjata. Kirjoittaja ei näe sitä, koska hän
  tietää, mitä tarkoitti.
- **Kokeile ohje puhtaalla koneella.** Kirjoittajan koneella on
  asennettuna asioita, joita ohje ei mainitse.
- **Sanasto versionhallintaan.** Kun termi vaihtuu, se vaihdetaan
  kaikkialta samassa muutoksessa.
- **Kuvakaappaus vanhenee nopeimmin.** Käytä tekstiä ja komentoja,
  kun voit. Kuva tarvitaan, kun asia on tilallinen: kaavio tai
  asettelu.
- **Päivämäärät ja versiot näkyviin.** ”Uusi ominaisuus” on uusi
  vuoden. ”Versiosta 1.2 alkaen” on totta aina.

## Itsearviointi

- Osaat järjestää sivun ja kappaleen niin, että tärkein on ensin.
- Osaat muuttaa passiivisen tai epämääräisen virkkeen täsmälliseksi.
- Osaat perustella, miksi teknisessä tekstissä käytetään yhtä termiä
  yhdestä asiasta, ja laatia projektille sanaston.
- Osaat kertoa, mitkä tekstin ominaisuudet kone voi tarkistaa ja
  mitkä eivät.
