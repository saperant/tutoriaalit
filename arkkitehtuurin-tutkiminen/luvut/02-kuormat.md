# Kuormien karakterisointi

Arkkitehtuuri suunnitellaan kuormille: ohjelmille, joita laitteiston on
tarkoitus ajaa. Ennen kuin mallintaa laitetta, on tiedettävä, mitä kuorma
siltä vaatii. *Karakterisointi* kuvaa kuorman ominaisuuksilla, jotka
eivät riipu siitä koneesta, jolla kuorma mitattiin: käskyjakauma,
laskentaintensiteetti, muistiviittausten paikallisuus ja vaiheet. Samoja
ominaisuuksia voi sitten syöttää malleihin, joissa kone vaihtelee.

Tämän luvun kuormat ovat neljä pientä laskentaydintä, jotka edustavat
tyypillisiä muistikäyttäytymisiä:

| Ydin | Mitä tekee | Paikallisuus |
|------|------------|--------------|
| virta | `a[i] = b[i] + s*c[i]` kolmella 16 KiB:n taulukolla | peräkkäinen, ei uudelleenkäyttöä kierroksen sisällä |
| naiivi | matriisitulo 32 × 32 ijk-järjestyksessä | B luetaan sarakkeittain |
| lohkottu | sama 8 × 8 -lohkoina | uudelleenkäyttö lohkon sisällä |
| lista | linkitetty lista, solmut satunnaisessa järjestyksessä | ei ennustettavaa paikallisuutta |

## Instrumentointi

Kuorman tiedot kerätään *instrumentoinnilla*: ohjelmaa ajettaessa
kirjataan jokainen tapahtuma, joka kiinnostaa. Oikeat työkalut
instrumentoivat käännetyn binäärin. Pin ja DynamoRIO kirjoittavat koodin
uudelleen ajon aikana, Valgrind ajaa sen omassa virtuaalikoneessaan, ja
gem5 ja QEMU emuloivat koko järjestelmän. Tässä instrumentointi on tehty
käsin: ytimet käyttävät taulukkoa, joka kirjaa jokaisen luvun ja
kirjoituksen osoitteen.

```{.cpp tiedosto="esimerkit/02-kuormat/main.cpp" osa="jalki"}
```

Osoitteet ovat mallin omia: taulukot sijoitetaan sivun rajoille
kiinteästä alkuosoitteesta. Silloin jälki on sama joka ajolla ja joka
koneella, mikä ei päde, jos kirjataan ohjelman todelliset osoitteet
(osoiteavaruuden satunnaistus, ASLR, muuttaa niitä joka ajolla).
Operaatiot lasketaan luokittain samaan tapaan kuin käskyjakaumassa:

```{.cpp tiedosto="esimerkit/02-kuormat/main.cpp" osa="laskuri"}
```

Ytimet laskevat oikean tuloksen, ja instrumentointi on niiden
sisällä. Esimerkiksi lohkottu matriisitulo, jonka rakenne `Matriisit`
varaa ja alustaa kolme 32 × 32 -matriisia:

```{.cpp tiedosto="esimerkit/02-kuormat/main.cpp" osa="lohkottu"}
```

Linkitetyn listan solmut järjestetään Fisherin ja Yatesin sekoituksella
kiinteästä siemenestä, joten seuraavan solmun osoite selviää vasta
latauksesta:

```{.cpp tiedosto="esimerkit/02-kuormat/main.cpp" osa="lista"}
```

## Käskyjakauma ja intensiteetti

Pääohjelma ajaa ytimet, kirjoittaa jäljet ja tulostaa operaatioiden
jakauman:

```{.cpp tiedosto="esimerkit/02-kuormat/main.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/02-kuormat/odotettu"}
```

Jakauma kertoo, mitä ydintä kuorma rasittaa. Kaikissa neljässä
latauksia on kolmannes tai enemmän, joten muistihierarkia ratkaisee.
Haaroja on 14–20 %, mutta kaikki ovat silmukoiden ehtoja, jotka
ennustin arvaa lähes aina oikein; jakauma ei kerro ennustettavuudesta
mitään. Viimeinen sarake on laskentaintensiteetti L1-tasolla, eli
liukulukuoperaatiot jaettuna luettujen ja kirjoitettujen tavujen
määrällä. Se on kaikilla alle 0,2 FLOP/B, mutta luvussa 3 nähdään, että
välimuistien takana tilanne on aivan toinen.

Käskyjakauman huomaamaton heikkous on, että se ei riipu järjestyksestä.
Naiivi ja lohkottu matriisitulo tekevät lähes saman jakauman ja saman
tuloksen, mutta niiden suorituskyky eroaa monikertaisesti. Ero on
siinä, *missä järjestyksessä* osoitteisiin viitataan.

## Uudelleenkäyttöetäisyys

*Uudelleenkäyttöetäisyys* (*reuse distance*, myös *pinoetäisyys*) on
niiden eri välimuistirivien määrä, joihin viitataan kahden saman rivin
viittauksen välissä. Jos rivi A, sitten B ja C ja taas A, A:n etäisyys
on 2. Ensimmäinen viittaus riviin on etäisyydellä ääretön.

Etäisyys on hyödyllinen, koska se ei riipu välimuistista: täysin
assosiatiivinen LRU-välimuisti, johon mahtuu $C$ riviä, osuu
täsmälleen niihin viittauksiin, joiden etäisyys on pienempi kuin $C$.
Mattson ym. (1970) huomasivat, että LRU-pino antaa etäisyydet suoraan:
pinon päällä on viimeksi käytetty rivi, ja viitatun rivin syvyys pinossa
on sen etäisyys.

```{.python tiedosto="esimerkit/arkki/jalki.py" osa="mattson"}
```

Pinoalgoritmi on hidas, jos pino on syvä, koska rivi etsitään
lineaarisesti. Nopeampi menetelmä pitää merkin kunkin rivin viimeisimmän
viittauksen kohdalla aikajanalla. Etäisyys on merkkien määrä edellisen
ja nykyisen viittauksen välissä, ja sen saa binääri-indeksoidusta
puusta (Fenwick-puu) ajassa $O(\log N)$:

```{.python tiedosto="esimerkit/arkki/jalki.py" osa="fenwick"}
```

Kumpikin algoritmi antaa saman tuloksen, ja testi tarkistaa sen
satunnaisella jäljellä ja käsin lasketulla esimerkillä:

```{.python tiedosto="esimerkit/testit/test_jalki.py" osa="esimerkki"}
```

Ytimien etäisyysjakaumat luokiteltuina, rivi 64 tavua:

```{.python tiedosto="esimerkit/02-uudelleenkaytto.py" osa="luokat"}
```

```{.tuloste tiedosto="esimerkit/02-uudelleenkaytto.odotettu"}
```

Jakaumista näkee kuorman luonteen ennen yhtäkään välimuistisimulointia:

- **Virta** palaa samaan riviin heti, kun kahden muun taulukon rivit
  on käytetty (etäisyys 2), kunnes rivin kahdeksan lukua on luettu.
  Seuraavan kerran rivi tulee vasta toisella kierroksella, kun 767 muuta
  riviä on käyty läpi (≥ 512).
- **Naiivin** matriisitulon viittauksista puolet on etäisyydellä 8–63:
  B:n sarake käy 32 riviä läpi ennen kuin sama rivi tulee uudelleen.
- **Lohkotulla** puolet on samassa luokassa, mutta lohkon sarake on vain
  8 riviä, joten etäisyydet ovat luokan alapäässä. Yli 64 rivin
  etäisyydet lähes katoavat (6,0 % → 1,1 %).
- **Listan** joka toinen viittaus on samaan riviin (solmun arvo ja
  seuraava osoite), loput tulevat vasta seuraavalla kierroksella.

Luokkarajat ovat karkeita: naiivin ja lohkotun ero näkyy kunnolla vasta,
kun etäisyyksiä verrataan välimuistin kokoon.

## Hutikäyrä

Koska osuminen riippuu vain etäisyydestä, yksi läpikäynti antaa hudit
*kaikille* välimuistin koille. Tämä *hutikäyrä* (*miss ratio curve*) on
kuorman tärkein yksittäinen tunnusluku arkkitehdille:

```{.python tiedosto="esimerkit/arkki/jalki.py" osa="hutikayra"}
```

```{.python tiedosto="esimerkit/02-hutikayra.py" osa="kayra"}
```

```{.tuloste tiedosto="esimerkit/02-hutikayra.odotettu"}
```

![Hutikäyrät. Lohkottu matriisitulo putoaa jo 1 KiB:n välimuistilla,
naiivi vasta 4 KiB:llä. Virta ja lista hyötyvät vasta, kun koko
taulukko mahtuu välimuistiin.](kuvat/hutikayra.png){width=100%}

Käyrän *polvet* ovat kohtia, joissa työjoukko mahtuu välimuistiin.
Lohkotun matriisitulon polvi on 1 KiB:ssä: kolme 8 × 8 -lohkoa
(1,5 KiB) mahtuvat melkein. Naiivin polvi on 4 KiB:ssä, kun koko B:n
sarake (32 riviä) ja A:n rivi mahtuvat. Virralle ja listalle välimuisti
on hyödytön, kunnes koko data (48 KiB ja 64 KiB) mahtuu siihen. Niille
auttaa vain esihaku tai kaista, ei koko.

Täysin assosiatiivinen LRU on idealisointi. Oikea välimuisti on
joukkoassosiatiivinen, ja *konfliktihudit* tulevat lisäksi. Ne näkee
vain suoralla simuloinnilla:

```{.python tiedosto="esimerkit/arkki/jalki.py" osa="lru"}
```

```{.python tiedosto="esimerkit/02-hutikayra.py" osa="konfliktit"}
```

Naiivin matriisitulon hudit 4 KiB:n välimuistissa kahdeksankertaistuvat,
kun assosiatiivisuus putoaa täydestä kahdeksaan tiehen. Syy on
askelpituus: B:n sarakkeen peräkkäiset alkiot ovat 256 tavun eli neljän
rivin päässä toisistaan, ja 64 rivin 8-tievälimuistissa on 8 joukkoa, joten
sarake osuu vain kahteen joukkoon. Virran kolme taulukkoa alkavat 16 KiB:n
välein ja osuvat samoihin joukkoihin; kahdella tiellä ne heittävät
toisensa ulos joka viittauksella. Hutikäyrä kertoo siis kapasiteetin
tarpeen, ja joukkoassosiatiivinen simulointi kertoo, kuinka paljon
tarvitaan lisäksi assosiatiivisuutta tai osoitteiden hajautusta.

## Työjoukko

Denningin *työjoukko* on eri rivien määrä aikaikkunassa. Se kertoo
saman asian kuin hutikäyrä, mutta ajan funktiona:

```{.python tiedosto="esimerkit/arkki/jalki.py" osa="tyojoukko"}
```

```{.tuloste tiedosto="esimerkit/02-tyojoukko.odotettu"}
```

Lohkotun matriisitulon työjoukko kasvaa hitaimmin: 4096 viittauksen
ikkunassa se käsittelee 5 KiB, naiivi lähes kaksinkertaisen määrän.
Lista ja virta kasvattavat työjoukkoaan lineaarisesti, eli ne eivät
palaa vanhaan dataan ikkunan aikana. Työjoukko on hyödyllinen
moniytimissä: jaetun välimuistin on mahduttava kaikkien ytimien
samanaikaisiin työjoukkoihin.

## Vaiheet ja edustavuus

Oikeat ohjelmat eivät ole yhtä ydintä. Ne kulkevat *vaiheissa*:
alustus, laskenta, tulostus, ja laskennan sisällä eri algoritmit.
Karakterisointi koko ajosta keskiarvoistaa vaiheet ja voi antaa
tunnusluvut, joita mikään vaihe ei oikeasti ole. Luvussa 6 vaiheet
tunnistetaan peruslohkovektoreista ja ajosta valitaan edustavat
intervallit.

Kuormajoukko on aina valinta. Standardikuormat, kuten SPEC CPU,
PARSEC, MLPerf ja EEMBC, ovat vertailukelpoisia, mutta ne eivät
välttämättä vastaa omaa käyttöä. Omat kuormat ovat edustavia, mutta
niiden tuloksia ei voi verrata kirjallisuuteen. Hyvä käytäntö on
kumpikin: standardikuormat mallin kalibrointiin ja omat päätöksentekoon.

## Käytännössä

- **Karakterisoi koneesta riippumatta.** Uudelleenkäyttöetäisyys,
  käskyjakauma ja intensiteetti eivät riipu mittauskoneesta, joten ne
  kelpaavat malleihin, joissa kone vaihtelee. Mitattu IPC tai hutiosuus
  tietyllä koneella ei kelpaa.
- **Yksi läpikäynti, monta kokoa.** Hutikäyrä
  uudelleenkäyttöetäisyyksistä korvaa kymmeniä välimuistisimulointeja.
  Simuloi erikseen vain assosiatiivisuuden ja korvausalgoritmin
  vaikutus.
- **Jäljet ovat suuria.** Oikean ohjelman jälki on gigatavuja.
  Tallenna vain tarvittava (rivinumero, ei tavuosoitetta), pakkaa, tai
  laske tunnusluvut instrumentoinnin aikana ilman jälkeä. Näytteistys
  (luku 6) pienentää jälkiä kertaluokilla.
- **Determinismi.** Satunnaisuus kiinteästä siemenestä ja osoitteet
  mallin omasta osoiteavaruudesta. Muuten jäljet eroavat ajoittain, eikä
  muutoksen vaikutusta voi erottaa kohinasta.
- **Kerää kuorma kuten sitä ajetaan.** Kääntäjän optimointitaso,
  syötteen koko ja säikeiden määrä muuttavat kuormaa. Kirjaa ne
  jäljen yhteyteen.

## Itsearviointi

- Osaat kerätä kuormasta käskyjakauman ja muistijäljen ja selittää,
  miksi jäljen osoitteiden on oltava deterministisiä.
- Osaat laskea uudelleenkäyttöetäisyydet Mattsonin pinoalgoritmilla ja
  Fenwick-puulla ja selittää, miksi etäisyys ennustaa täysin
  assosiatiivisen LRU-välimuistin osumat.
- Osaat tulkita hutikäyrän polvet työjoukkojen kokoina ja päätellä,
  hyötyykö kuorma suuremmasta välimuistista.
- Osaat selittää, mistä konfliktihudit syntyvät ja miksi hutikäyrä ei
  näe niitä.
