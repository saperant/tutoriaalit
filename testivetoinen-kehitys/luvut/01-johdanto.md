# Johdanto {.runko-johdanto}

Testi on väite ohjelman käytöksestä, jonka kone tarkistaa. Useimmat
ohjelmoijat oppivat kirjoittamaan testejä nopeasti. Vaikeampaa on
päättää, *mitä* testata ja *milloin*: mitkä syötteet valitaan
äärettömästä joukosta, mistä tietää, että testit löytäisivät virheen, ja
miten testit saadaan auttamaan suunnittelua eikä jarruttamaan sitä.

Tämä tutoriaali vastaa näihin kysymyksiin kuudella menetelmällä:

1. **Testivetoinen kehitys** (TDD, luvut 2 ja 3): testi kirjoitetaan
   ennen koodia, ja se ohjaa rajapinnan suunnittelua.
2. **Testisuunnittelutekniikat** (luvut 4 ja 5): ekvivalenssiluokat,
   raja-arvot, päätöstaulut, tilasiirtymät ja parittainen testaus
   kertovat, mitkä tapaukset kannattaa valita.
3. **Suoritettavat määrittelyt** (BDD, luku 6): vaatimus kirjoitetaan
   esimerkkeinä kielellä, jota myös tilaaja lukee, ja sama teksti
   ajetaan testinä.
4. **Ominaisuuspohjainen testaus** (luku 7): testi väittää jotain
   kaikista syötteistä, ja kone etsii vastaesimerkin.
5. **Mutaatiotestaus** (luku 8): testien laatu mitataan tekemällä koodiin
   virheitä ja katsomalla, huomaavatko testit ne.
6. **Testattava suunnittelu ja perintökoodi** (luvut 9–11): miten koodi
   järjestetään niin, että sitä voi testata, ja miten testit saadaan
   koodiin, jota ei ole suunniteltu testattavaksi.

Menetelmät esitetään perusteluineen ja rajoineen. Yksikään niistä ei ole
ihmelääke: TDD ei sovi tutkivaan koodiin, BDD ei korvaa keskustelua,
kattavuusprosentti ei kerro testien laadusta eikä mutaatiotestaus ole
ilmaista. Jokaisessa luvussa kerrotaan, milloin menetelmä kannattaa ja
milloin ei.

## Esitiedot ja rajaus

Lukija osaa Pythonin ja pytestin perusteet (taito *Python
työkaluohjelmointiin*: testifunktiot, fixturet ja parametrointi) ja
versionhallinnan (taito *Versionhallinta (Git)*). Esimerkit ovat Pythonia,
mutta menetelmät eivät riipu kielestä: sama pätee JUnitilla, Jestillä
tai Googletestillä.

Tämä tutoriaali ei toista sitä, mitä muut taidot käsittelevät:

| Aihe | Taito |
|-----------------------------------|----------------------------------|
| pytestin käyttö | *Python työkaluohjelmointiin* |
| yksikkötestit C:llä, sanitoijat, kattavuuden mittaus | *Käännösjärjestelmät, testaus ja CI* |
| testipyramidi, testit oikeaa tietokantaa vasten, sopimustestit | *Integraatiotestaus ja Testcontainers* |
| fuzzaus | *Haavoittuvuuksien analyysi ja torjunta* |
| laitteiston verifiointi ja satunnaistus | *Laitteiston verifiointi* |
| toimitusputket ja trunk-pohjainen kehitys | *Jatkuva integraatio ja toimitus* |

## Sanasto

Testauksen sanat vaihtelevat lähteestä toiseen. Tässä tutoriaalissa:

- **Testitapaus** on yksi syöte ja sille odotettu tulos.
- **Testisarja** on joukko testitapauksia, jotka ajetaan yhdessä.
- **Testattava koodi** (*system under test*) on se, mistä testi väittää
  jotain. Muu koodi, jota se tarvitsee, on sen **yhteistyökumppaneita**.
- **Testikaksoinen** (*test double*) on yhteistyökumppanin korvike
  testissä. **Väärennös** (*fake*) on yksinkertainen toimiva toteutus,
  esimerkiksi varasto muistissa. **Mock** on korvike, jolta testi kysyy
  jälkikäteen, mitä kutsuja se sai.
- **Refaktorointi** muuttaa koodin rakennetta muuttamatta sen käytöstä.
- **Regressio** on virhe, joka rikkoo aiemmin toimineen ominaisuuden.

## Esimerkkien ala ja ajaminen

Esimerkit ovat pienen verkkokaupan osia: ostoskori, toimitusmaksu,
alennukset, tilauksen tila, kassa ja lasku. Rahasummat ovat sentteinä
kokonaislukuina, koska liukuluvut eivät esitä kymmenyksiä tarkasti
(taito *Miten tietokone laskee*).

Jokainen esimerkki on hakemisto, jossa on tavallinen pytest-projekti.
Sen testit voi ajaa suoraan:

```text
cd esimerkit/04-rajat
python3 -m pytest
```

Useassa esimerkissä on **tarkoituksella epäonnistuvia testejä**. Ne
näyttävät, minkä vian menetelmä löytää: sama testisarja ajetaan sekä
oikeaa että viallista toteutusta vasten, tai testi kirjoitetaan ennen
koodia, jolloin sen kuuluukin epäonnistua. Siksi tutoriaalin oma
tarkistus ei katso pytestin paluuarvoa, vaan vertaa testien tuloksia
tallennettuihin:

```text
make -C esimerkit            # kaikki esimerkit
make -C esimerkit 04-rajat   # yksi esimerkki
```

Tekstin tulosteet ovat näitä tallennettuja tuloksia. Niissä on rivi
testiä kohden ja epäonnistuneesta testistä virheen ensimmäinen rivi.
Pitkistä ajoista näytetään yhteenveto tiedostoittain ja vain
epäonnistuneet testit.

Esimerkit tarvitsevat Python 3.12:n tai uudemman sekä kirjastot pytest,
pytest-bdd 9.0, Hypothesis 6.170 ja coverage 7.17. Kehityskontissa
`.devcontainer/testivetoinen-kehitys` ne ovat valmiina.
