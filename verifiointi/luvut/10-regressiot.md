# Regressiot ja virheiden luokittelu

Yksittäinen läpäisty testi kertoo vähän. Verifioinnin varsinainen
tulos on *regressio*: koko testijoukko ajettuna monella siemenellä
jokaisen muutoksen jälkeen. Regressio havaitsee, kun korjaus rikkoo
jotain muuta, ja sen tuloksista nähdään verifioinnin tila: mitkä testit
epäonnistuvat, kuinka usein ja mistä syystä.

## Regression tasot

Kaikkea ei voi ajaa jokaisen muutoksen jälkeen, joten regressio jaetaan
tasoihin:

| Taso | Milloin | Sisältö | Kesto |
|------|---------|---------|-------|
| savutesti (smoke) | jokainen muutos ennen yhdistämistä | muutama testi, kiinteät siemenet, lyhyt BMC | minuutteja |
| yöajo | joka yö | kaikki testit, satoja siemeniä, kattavuuden yhdistäminen | tunteja |
| viikkoajo | viikoittain tai ennen julkaisua | pitkät testit, syvä formaali tarkistus, porttitason simulointi | vuorokausia |

Savutesti estää rikkinäisen muutoksen pääsemisen yhteiseen haaraan.
Yöajo löytää harvinaiset viat, ja sen siemenet vaihtuvat, jotta
ajot tuottavat uusia tilanteita. Kiinteät siemenet savutestissä taas
takaavat, että sama muutos tuottaa saman tuloksen.

Tämän tutoriaalin `make` on savutesti: jokainen esimerkki kiinteällä
siemenellä, tulos verrattuna odotettuun tiedostoon. Kohde `regressio`
on pieni yöajo.

## Regressio esimerkeille

Regressioskripti ajaa cocotb-testit kaikilla lohkon versioilla ja
viidellä siemenellä. Kokoonpano on tietoa, ei koodia:

```{.python tiedosto="esimerkit/tyokalut/regressio.py" osa="kokoonpano"}
```

Jokainen ajo on oma aliprosessinsa omassa rakennushakemistossaan, joten
ajot voidaan tehdä rinnakkain ja tulos ei riipu järjestyksestä.
Tulokset kootaan *vikamatriisiksi*: rivit ovat lohkon versioita,
sarakkeet testejä ja solut kertovat, monellako siemenellä testi
epäonnistui.

```{.python tiedosto="esimerkit/tyokalut/regressio.py" osa="matriisi"}
```

```{.tuloste tiedosto="esimerkit/odotetut/regressio.odotettu"}
```

Matriisista luetaan useita asioita:

- **Ehjien rivien on oltava tyhjiä.** Jos ehjä lohko epäonnistuu,
  vika on testipenkissä tai mallissa.
- **Jokainen vika löytyy jostakin.** Rivi, jossa on pelkkiä viivoja,
  tarkoittaisi vikaa, jota mikään testi ei löydä.
- **Siemenriippuvuus.** `BUGI_TYHJA` löytyy satunnaistetulla testillä
  neljällä siemenellä viidestä. Syy on luvussa 4: generaattorin oma
  arvio jonon tilasta erkanee joskus todellisesta, ja silloin se
  lukee tyhjästä jonosta. Siemen 1 ei koskaan tee niin. Myös
  `BUGI_KAKSI` jää satunnaiselta testiltä yhdellä siemenellä
  löytymättä, koska neljää samanaikaista pyyntöä ei synny.
- **Testien työnjako.** Ohjattu testi löytää vain `BUGI_TAYSI`:n,
  ja kulmatestin ja satunnaistetun testin vahvuudet ovat eri
  vioissa. Yksikään testi ei yksin löydä kaikkea.

Viimeinen kohta pätee myös menetelmiin. Kun kirjan kaikkien lukujen
tulokset kootaan samaan taulukkoon, jokainen menetelmä löytää osan
vioista eri tavalla (luku 11).

## Epäonnistumisten ryhmittely

Yöajossa voi epäonnistua satoja ajoja, mutta niiden taustalla on
yleensä muutama vika. *Luokittelu* (triage) ryhmittelee
epäonnistumiset, valitsee jokaisesta ryhmästä edustajan ja ohjaa sen
oikealle henkilölle. Ryhmittely tehdään epäonnistumisen tunnisteen
(signature) perusteella. Saman vian eri ajojen virheviestit eroavat
yleensä vain jaksonumeroiltaan ja arvoiltaan, joten luvut korvataan
paikkamerkillä:

```{.python tiedosto="esimerkit/tyokalut/regressio.py" osa="luokittelu"}
```

Jokaiselle ryhmälle tulostetaan koko, toistokomento pienimmällä
siemenellä ja opetusta varten myös ne istutetut viat, joista ryhmän
epäonnistumiset tulivat:

```{.python tiedosto="esimerkit/tyokalut/regressio.py" osa="ryhmat"}
```

Tuloste näkyy matriisin alla. Arbiterin ryhmät erottuvat siististi,
koska tarkastajan viestit alkavat luokalla (`[malli]`, `[yksikuuma]`).
FIFOn ryhmä `maara=#, mallissa #` sen sijaan sisältää kaksi eri vikaa:
alivuodon ja samanaikaisuuden vian. Molemmat näkyvät ensin vääränä
määränä. Tunniste on siis heuristiikka. Kun ryhmän edustaja on
korjattu, regressio ajetaan uudelleen, ja jäljelle jääneet
epäonnistumiset muodostavat uuden ryhmän. Tarkemmat virheviestit,
kuten "määrä muuttui samanaikaisessa kirjoituksessa ja luvussa", ja
väitteet, jotka nimeävät rikotun säännön, tekevät ryhmistä tarkempia.

## Vian tutkiminen

Ryhmän edustajan tutkiminen etenee samassa järjestyksessä joka kerta:

1. **Toista.** Aja sama testi samalla siemenellä ja varmista, että
   tulos on sama. Jos ei ole, testipenkissä on ajoitusriippuvuus,
   alustamaton muuttuja tai siemenetön satunnaisuus, ja se on
   korjattava ensin.
2. **Pienennä.** Valitse lyhin testi ja pienin siemen, joka toistaa
   vian. Jos lohkolla on formaalit ominaisuudet, BMC tuottaa usein
   lyhimmän mahdollisen vastaesimerkin suoraan (luku 8).
3. **Ensimmäinen poikkeama.** Etsi ensimmäinen jakso, jolla DUT ja
   malli eroavat. Myöhemmät virheet ovat seurauksia.
4. **Kumpi on väärässä?** Vertaa havaintoa määrittelyyn, ei malliin.
   Vika voi olla RTL:ssä, referenssimallissa, testipenkissä tai
   määrittelyssä itsessään, ja jokainen ohjataan eri henkilölle.
5. **Korjaa ja lukitse.** Korjauksen jälkeen kirjoita tilanteelle
   kattavuuskohde, väite tai ohjattu testi, joka varmistaa, että
   tilanne syntyy ja tarkistetaan jatkossakin siemenestä riippumatta.

Epäonnistumisen syyt jakautuvat tyypillisesti seuraavasti:

| Syy | Tunnusmerkki | Toimenpide |
|-----|--------------|------------|
| RTL:n vika | malli ja määrittely ovat samaa mieltä | korjaus suunnittelijalle |
| mallin tai testipenkin vika | DUT toimii määrittelyn mukaan | korjaus verifioijalle |
| määrittelyn aukko tai ristiriita | molemmat tulkinnat ovat mahdollisia | päätös arkkitehdille, määrittely päivitetään |
| ympäristö | aikakatkaisu, lisenssi, levytila, kaatunut kone | ajo uudelleen, infrastruktuurin korjaus |

## Toistettavat tulokset

Regressiota on helppo tulkita vain, jos sama ajo tuottaa aina saman
tuloksen. Simulaatio on deterministinen, kun siemen on kiinteä, mutta
tulosteeseen pääsee helposti muuttuvaa tietoa: aikaleimoja,
absoluuttisia polkuja, ajoaikoja ja työkalujen versionumeroita. Tämän
tutoriaalin työkalut poistavat ne: `vertaa.py` poistaa esimerkkien
polun ja `formaali.py` yosys-smtbmc:n aikaleimat ja sisäiset
tunnisteet. Silloin tulosteen voi verrata tallennettuun
"kultaiseen" tulosteeseen, ja jokainen ero on todellinen muutos.

*Epävakaa testi* (flaky test), joka epäonnistuu joskus samalla
syötteellä, on simulaatiossa aina vika: kilpatilanne testipenkin ja
DUT:n välillä, alustamaton muuttuja, joka saa eri arvon eri
simulaattoreilla, tai satunnaisuus ilman siementä. Sitä ei ohiteta
ajamalla testiä uudelleen.

## Raportointi

Regression tulokset viedään CI-järjestelmään. cocotb:n ajaja kirjoittaa
JUnit-muotoisen XML-tiedoston (luku 7), jonka useimmat CI-järjestelmät
näyttävät testitaulukkona. Pitkän aikavälin seurannassa tärkeimmät
mittarit ovat:

- läpäisyprosentti ja epäonnistumisryhmien määrä ajoittain;
- yhdistetty kattavuus ja sen kehitys;
- löydettyjen ja korjattujen vikojen määrä viikossa.

Kun uusia vikoja löytyy yhä harvemmin ja kattavuus on täynnä,
lohko lähestyy valmiuskriteerejä (luku 2).

## Käytännössä

- **Savutesti jokaiselle muutokselle, yöajo kaikelle.** Savutestin on
  oltava niin nopea, että kukaan ei ohita sitä.
- **Jokainen ajo omaan hakemistoonsa.** Rinnakkaiset ajot eivät saa
  jakaa käännöstuotteita, lokeja eikä tulostiedostoja.
- **Toistokomento raporttiin.** Epäonnistumisen raportissa on komento,
  joka toistaa sen: testi, siemen, lohkon versio ja asetukset.
- **Virheviestit luokiteltaviksi.** Kiinteä etuliite (luokka tai
  väitteen nimi) ja vaihtuvat arvot viestin lopussa tekevät
  ryhmittelystä luotettavaa.
- **Epävakaa testi on vika.** Deterministisessä simulaatiossa
  satunnaisesti epäonnistuva testi kertoo kilpatilanteesta tai
  alustamattomasta tilasta.
- **Korjattu vika lukitaan.** Jokaiselle korjatulle vialle jää
  regressioon tarkistus, joka toteaa sen pysyvän korjattuna.

## Itsearviointi

- Osaat jakaa regression tasoihin ja valita kullekin testit ja
  siemenet.
- Osaat lukea vikamatriisia ja tunnistaa siitä siemenriippuvuuden ja
  testien työnjaon.
- Osaat ryhmitellä epäonnistumiset tunnisteen perusteella ja
  selittää, miksi ryhmittely on heuristiikka.
- Osaat tutkia epäonnistumisen järjestyksessä: toista, pienennä,
  etsi ensimmäinen poikkeama, päätä kumpi on väärässä, korjaa ja
  lukitse.
- Osaat tehdä tulosteista toistettavia, jotta niitä voi verrata
  tallennettuihin tulosteisiin.
