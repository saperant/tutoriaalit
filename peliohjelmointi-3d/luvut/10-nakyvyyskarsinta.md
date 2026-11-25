# Näkyvyyskarsinta

Kamera näkee kerrallaan vain osan maailmasta. Kaiken muun lähettäminen
piirrettäväksi on hukkaa: renderöijä muuntaisi jokaisen kärjen ja
hylkäisi kolmiot vasta leikkausvaiheessa (taito *Renderöinnin
perusteet*). Peli päättää siksi itse ennen piirtoa, mitkä kappaleet
voivat näkyä. Tätä kutsutaan *näkyvyyskarsinnaksi* (*culling*), ja sen
perusmuoto on vertailu kameran näkymäkartioon.

## Näkymäkartio tasoina

*Näkymäkartio* (*view frustum*) on katkaistu pyramidi, jonka kärki on
kamerassa. Sitä rajaa kuusi tasoa: vasen, oikea, ala, ylä, lähi ja
kauka. Kappale on kartion ulkopuolella, jos se on kokonaan jonkin tason
väärällä puolella.

Tasot saa suoraan näkymä- ja projektiomatriisin tulosta. Piste on
kartiossa, kun sen leikkausavaruuden koordinaateille pätee
$-w \le x, y, z \le w$. Ehto $w + x \ge 0$ on lineaarinen maailman
pisteen suhteen: sen kertoimet ovat matriisin neljännen ja ensimmäisen
rivin summa. Sama pätee muille viidelle tasolle.

```{.cpp tiedosto="esimerkit/yhteinen/kartio.hpp" osa="tasot"}
```

Pallo on tason takana, jos sen keskipisteen etäisyys tasosta on
enemmän kuin säteen verran negatiivinen. Laatikosta riittää testata
yksi kulma: se, joka on pisimmällä tason normaalin suunnassa.

```{.cpp tiedosto="esimerkit/yhteinen/kartio.hpp" osa="testit"}
```

Testi on *varovainen*: se ei koskaan karsi näkyvää kappaletta, mutta
voi päästää läpi kappaleen, joka on kartion kulman takana jokaisen
tason oikealla puolella. Sellainen kappale piirretään turhaan, mutta
kuva on oikein. Karsinnassa virhe saa mennä vain tähän suuntaan.

## Karsinta kentällä

Esimerkissä on 2 000 palloa 200 metrin levyisellä kentällä. Kamera on
kentän keskellä ja näkee 60 metrin päähän.

```{.cpp tiedosto="esimerkit/10-karsinta.cpp" osa="kentta"}
```

Jokaisen pallon testaaminen erikseen maksaa 2 000 testiä ruutua
kohden, vaikka näkyvissä on kymmenesosa. Hierarkia auttaa samalla
tavalla kuin säteille: jos BVH:n solmun laatikko on kartion
ulkopuolella, mikään sen alla ei näy.

```{.cpp tiedosto="esimerkit/10-karsinta.cpp" osa="kamera"}
```

```{.tuloste tiedosto="esimerkit/10-karsinta.odotettu"}
```

Näkyviä palloja on katselusuunnasta riippuen noin 200. Hierarkkinen
karsinta löytää täsmälleen samat pallot noin 500 testillä 2 000:n
sijaan. Säästö kasvaa maailman mukana: kun maailma kaksinkertaistuu
mutta kamera näkee yhtä kauas, yksittäin testaaminen kaksinkertaistuu,
hierarkian testit eivät.

![Kameran kuva, kun kääntö on 45 astetta. Kaikki kuvassa näkyvä on
läpäissyt karsinnan.](kuvat/karsinta.png){width=75%}

![Sama tilanne ylhäältä. Punainen kolmio on näkymäkartion pohjapiirros
60 metrin kaukotasoon asti. Siniset pallot läpäisivät testin, harmaat
karsittiin. Kartion reunoilla on muutama pallo, joka on mukana, koska
se ulottuu kartioon vain
osittain.](kuvat/karsinta-ylhaalta.png){width=60%}

## Muut karsinnat

Näkymäkartio poistaa sen, mikä on sivussa tai takana. Se ei poista
sitä, mikä on edessä mutta toisen kappaleen takana.

| Karsinta | Mitä poistaa | Missä tehdään |
|----------|--------------|---------------|
| näkymäkartio | kartion ulkopuoliset kappaleet | peli, ennen piirtoa |
| etäisyys ja tarkkuustasot | kaukaiset pienet kappaleet; kaukaa piirretään karkeampi malli | peli |
| peittokarsinta (*occlusion*) | toisten kappaleiden peittämät | peli tai näytönohjain |
| takapinnat | kamerasta poispäin osoittavat kolmiot | renderöijä |
| syvyystesti | peittyvät pikselit | renderöijä |

Peittokarsinta on näistä vaativin. Sisätiloissa maailma jaetaan
huoneisiin ja oviaukkoihin (*portals*), jolloin huone piirretään vain,
jos sen oviaukko näkyy. Avoimessa maailmassa suuret peittäjät
piirretään ensin karkeaan syvyyspuskuriin, jota vasten muiden
kappaleiden ympäryslaatikot testataan. Menetelmät kuuluvat renderöinnin
jatko-opintoihin; pelin rakenteen kannalta olennaista on, että jokainen
niistä on kysely samaan tilarakenteeseen.

## Piirtolista

Karsinnan tulos on *piirtolista*: luettelo siitä, mitä tällä ruudulla
piirretään ja millä muunnoksilla. Lista on pelin ja renderöijän
rajapinta (taito *Peliohjelmointi*). Peli ei kutsu grafiikkarajapintaa
pelilogiikasta, eikä renderöijä tiedä pelin säännöistä. Sama karsinta
tehdään jokaiselle kameralle erikseen: jaetun ruudun pelaajille,
varjoja piirtäville valoille ja peileille.

## Käytännössä

- **Karsinta on varovainen.** Näkyvän kappaleen karsiminen on näkyvä
  virhe, näkymättömän piirtäminen vain hukkaa. Epävarmassa tapauksessa
  kappale piirretään.
- **Karsi ympäryksillä, älä tarkoilla muodoilla.** Pallo tai laatikko
  riittää; tarkka testi maksaisi enemmän kuin säästäisi.
- **Sama hierarkia, eri kysely.** Törmäyksiä varten rakennettu
  tilarakenne palvelee myös karsintaa, säteitä ja äänilähteiden hakua.
- **Varo kappaleita, jotka ulottuvat ympäryksensä ulkopuolelle.**
  Animoitu hahmo, jonka ympärys on laskettu lepoasennosta, katoaa
  ruudun reunalla, kun se ojentaa kätensä. Ympärykseen jätetään varaa.
- **Karsinta ei koske pelilogiikkaa.** Kappale, jota ei piirretä,
  liikkuu, törmää ja ääntelee silti.

## Itsearviointi

- Osaat johtaa näkymäkartion kuusi tasoa näkymä- ja
  projektiomatriisin tulosta.
- Osaat testata pallon ja akselien suuntaisen laatikon kartiota vastaan
  ja selittää, miksi testi on varovainen.
- Osaat karsia hierarkkisesti BVH:lla ja kertoa, miksi testien määrä
  ei kasva maailman koon mukana.
- Osaat nimetä muut karsinnan lajit ja sen, tehdäänkö ne pelissä vai
  renderöijässä.
