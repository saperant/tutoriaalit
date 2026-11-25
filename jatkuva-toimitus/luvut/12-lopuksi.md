# Lopuksi {.runko-lahteet}

Tutoriaali seurasi muutosta kehittäjän koneelta käyttäjälle:
integraatio runkoon, toimitusputki, artefakti ja ympäristöt,
julkaisu lippujen ja strategioiden avulla, tietokannan ja
infrastruktuurin muutokset sekä mittarit, joilla kokonaisuutta
arvioidaan. Yhteinen lanka oli erän koko. Lähes jokainen käytäntö on
keino tehdä muutoksesta pienempi tai sen palautteesta nopeampi.

## Nyrkkisäännöt

1. **Kipeä asia tehdään useammin.** Tiheä toisto pakottaa
   automatisoimaan ja pienentää erää.
2. **Yhdistä runkoon päivittäin.** Yhdistämisen vaikeus kasvaa
   odottaessa kiihtyvästi.
3. **Yhdistetty koodi testataan.** Siisti yhdistys ei tarkoita
   toimivaa ohjelmaa.
4. **Rikkinäinen runko korjataan heti.** Peru ensin, tutki sitten.
5. **Commit-vaihe kymmenessä minuutissa.** Hidas palaute jää
   käyttämättä.
6. **Punainen tarkoittaa vikaa.** Epävakaa testi korjataan tai
   poistetaan, ei ajeta uudelleen.
7. **Rakenna kerran.** Sama muuttumaton artefakti jokaiseen
   ympäristöön; asetukset tulevat ulkoa.
8. **Putki on ainoa tie tuotantoon.** Myös hätäkorjaukselle,
   asetuksille ja infrastruktuurille.
9. **Käyttöönotto ei ole julkaisu.** Vie koodi tuotantoon piilossa ja
   avaa se erikseen.
10. **Lippu on velkaa luontihetkestä.** Omistaja, poistopäivä, ei
    uudelleenkäyttöä.
11. **Altista vähän käyttäjiä kerrallaan**, jos mittarisi näkevät
    vian ja liikennettä on riittävästi.
12. **Kaksi peräkkäistä versiota ovat aina yhteensopivia.** Laajenna,
    siirrä, supista.
13. **Peruminen harjoitellaan.** Ja tiedetään, mitä ei voi perua.
14. **Ympäristö on koodia.** Haluttu tila versionhallinnassa,
    suunnitelma ennen toteutusta, ei muutoksia käsin.
15. **Mittarit luetaan yhdessä ja omaan käyttöön.** Tavoitteeksi
    muutettu mittari lakkaa mittaamasta.

## Mistä aloittaa

Käytännöt riippuvat toisistaan, joten järjestyksellä on väliä.
Seuraava polku etenee edellytyksistä seurauksiin.

```{.dot otsikko="Käytäntöjen riippuvuudet: jokainen rakentuu vasemmalla olevien varaan"}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.25;
  node [margin="0.07,0.05"];
  v [label="versionhallinta,\nyksi rakennus-\nkomento"];
  t [label="automaattiset\ntestit"];
  ci [label="jatkuva\nintegraatio"];
  p [label="toimitusputki\nja artefakti"];
  k [label="automaattinen\nkäyttöönotto"];
  j [label="liput ja\nasteittainen\njulkaisu"];
  m [label="mittarit ja\nseuranta"];
  v -> ci; t -> ci; ci -> p -> k; k -> m; k -> j;
}
```

1. **Versionhallinta ja yksi rakennuskomento.** Puhtaasta kloonista
   saadaan toimiva ohjelma yhdellä komennolla.
2. **Testit.** Ilman niitä mikään muu ei ole turvallista.
3. **Putki rungolle.** Jokainen yhdistys rakennetaan ja testataan,
   ja tulos näkyy kaikille.
4. **Haarojen lyhentäminen.** Viikoista päiviin, päivistä päivään.
5. **Artefakti ja automaattinen käyttöönotto testiympäristöön.**
   Sama paketti, sama skripti.
6. **Sama käyttöönotto tuotantoon.** Aluksi napin painalluksella.
7. **Julkaisun seuranta ja peruminen.** Mittarit, savutestit,
   harjoiteltu paluu.
8. **Liput, asteittainen julkaisu ja yhteensopivat
   tietokantamuutokset**, kun julkaisutahti sitä vaatii.

Jokainen askel on hyödyllinen ilman seuraavia. Moni organisaatio
pysähtyy perustellusti kohtaan 6, ja se on jo jatkuvaa toimitusta.

Tavallisin virhe on aloittaa lopusta: hankitaan lippupalvelu tai
GitOps-työkalu, vaikka testit puuttuvat ja haarat elävät viikkoja.
Työkalu ei korvaa käytäntöä, jonka varaan se on suunniteltu.

## Mallien ja yleistysten rajat

Tutoriaalin mallit ovat pieniä. Haarojen ristiriitamalli olettaa
satunnaiset muutokset, julkaisumalli tasaisen liikenteen ja
välittömän havainnon, ja mittariesimerkin historia on keksitty. Mallit
näyttävät mekanismin ja sen suunnan. Omat luvut saadaan vain omasta
repositoriosta, putkesta ja valvonnasta.

Käytännöt on kehitetty pääosin verkkopalveluissa, joissa tuottaja
hallitsee tuotantoa ja julkaisu on halpa. Muualla ne pätevät
soveltaen.

- **Sulautetut järjestelmät ja laitteet.** Jatkuva integraatio ja
  putki pätevät sellaisinaan, ja laitteisto testeissä tuo putkeen
  omat vaiheensa. Julkaisu kentälle on harvinaisempi ja peruminen
  vaikeaa, joten paino on putken alkupäässä.
- **Säännellyt alat.** Vaatimus on yleensä jäljitettävyys ja
  hyväksyntä, ei hitaus. Putki tuottaa todisteet paremmin kuin käsin
  täytetty lomake, mutta tämä on osoitettava tarkastajalle.
- **Asennettavat tuotteet.** Asiakas päättää päivityksestä. Jatkuva
  toimitus tarkoittaa silloin, että julkaisukelpoinen versio on aina
  olemassa, vaikka sitä julkaistaisiin neljännesvuosittain.
- **Pienet projektit.** Yhden hengen projektissa integraatio-ongelmaa
  ei ole. Putki, artefakti ja automaattinen käyttöönotto kannattavat
  silti, koska ne poistavat käsin tehtävät virheet.

## Jatkotaidot

- *Tietoturva kehitystyössä* käsittelee putken ja toimitusketjun
  suojaamisen: salaisuudet, riippuvuudet, SBOM ja allekirjoitukset.
- *Kontit ja pilvi-infrastruktuuri* näyttää putken, Helmin ja
  Terraformin käytännössä.
- *Skaalautuvien järjestelmien suunnittelu* käsittelee valvonnan,
  palvelutasotavoitteet ja virhebudjetin.
- *Integraatiotestaus ja Testcontainers* syventää putken hitaampien
  vaiheiden testejä.
- *Tiimit ja organisaatiomallit* käsittelee DevOpsia ja SRE:tä
  organisaation rakenteena ja sitä, kuka omistaa putken ja alustan.
- *Tekninen dokumentaatio* soveltaa samoja käytäntöjä
  dokumentaatioon: lähteet versionhallinnassa, tarkistus putkessa.

## Lähteet

Alkuperäislähteet ja alan perusteokset aiheittain. Verkossa vapaasti
luettavat on merkitty.

**Jatkuva integraatio ja toimitus**

- Humble, J. & Farley, D. (2010). *Continuous Delivery: Reliable
  Software Releases through Build, Test, and Deployment Automation*.
  Addison-Wesley. Toimitusputken käsitteen lähde ja alan perusteos.
- Fowler, M. *Continuous Integration*. martinfowler.com. Käytännön
  tunnetuin kuvaus; artikkelia on päivitetty useaan kertaan. Vapaasti
  luettavissa.
- Duvall, P., Matyas, S. & Glover, A. (2007). *Continuous Integration:
  Improving Software Quality and Reducing Risk*. Addison-Wesley.
- Beck, K. & Andres, C. (2004). *Extreme Programming Explained: Embrace
  Change*. 2. painos. Addison-Wesley. Jatkuva integraatio ja kymmenen minuutin
  rakennus XP:n käytäntöinä.

**Haarautumismallit**

- Hammant, P. *Trunk Based Development*. trunkbaseddevelopment.com.
  Mallin perusteellisin kuvaus muunnelmineen. Vapaasti luettavissa.
- Driessen, V. (2010). *A successful Git branching model*. nvie.com.
  GitFlow'n alkuperäinen kuvaus ja tekijän myöhempi huomautus sen
  soveltuvuudesta. Vapaasti luettavissa.
- Fowler, M. *Branch By Abstraction* ja *Semantic Conflict*.
  martinfowler.com. Vapaasti luettavissa.
- Wilsenach, R. (2021). *Ship / Show / Ask*. martinfowler.com.
  Vapaasti luettavissa.

**Artefaktit ja konfiguraatio**

- Wiggins, A. *The Twelve-Factor App*. 12factor.net. Konfiguraatio
  ympäristössä, rakennuksen ja ajon erottaminen. Vapaasti luettavissa.
- Reproducible Builds. reproducible-builds.org. Toistettavan
  rakennuksen määritelmä ja käytännöt, mukaan lukien
  `SOURCE_DATE_EPOCH`. Vapaasti luettavissa.
- Preston-Werner, T. *Semantic Versioning*. semver.org. Vapaasti
  luettavissa.

**Liput ja julkaisustrategiat**

- Hodgson, P. (2017). *Feature Toggles (aka Feature Flags)*.
  martinfowler.com. Lippujen lajit ja toteutustavat. Vapaasti
  luettavissa.
- Fowler, M. *Blue Green Deployment* ja Sato, D. *Canary Release*.
  martinfowler.com. Vapaasti luettavissa.
- U.S. Securities and Exchange Commission (2013). Hallinnollinen
  päätös asiassa Knight Capital Americas LLC. Vuoden 2012 häiriön
  viranomaisselvitys.

**Tietokantamuutokset**

- Ambler, S. & Sadalage, P. (2006). *Refactoring Databases:
  Evolutionary Database Design*. Addison-Wesley.
- Sato, D. *Parallel Change*. martinfowler.com. Laajenna–supista
  yleisenä mallina. Vapaasti luettavissa.

**Infrastruktuuri koodina ja GitOps**

- Morris, K. *Infrastructure as Code*. O'Reilly. Aiheen perusteos;
  useita painoksia.
- OpenGitOps. *GitOps Principles*. opengitops.dev. GitOpsin neljä
  periaatetta. Vapaasti luettavissa.

**Mittarit, DevOps ja luotettavuus**

- Forsgren, N., Humble, J. & Kim, G. (2018). *Accelerate: The Science
  of Lean Software and DevOps*. IT Revolution. Neljä mittaria ja
  niiden taustalla oleva tutkimus.
- DORA. *State of DevOps* -raportit. dora.dev. Vuosittainen
  kyselytutkimus. Vapaasti luettavissa.
- Kim, G., Humble, J., Debois, P. & Willis, J. (2016). *The DevOps
  Handbook*. IT Revolution.
- Beyer, B., Jones, C., Petoff, J. & Murphy, N. R. (toim.) (2016).
  *Site Reliability Engineering: How Google Runs Production Systems*.
  O'Reilly. Julkaisutekniikka, virhebudjetti ja jälkiarvioinnit.
  Vapaasti luettavissa osoitteessa sre.google.
