# Ominaisuusliput

Edelliset luvut veivät koodin tuotantoon. Tämä ja seuraava luku
käsittelevät sitä, miten uusi toiminnallisuus annetaan käyttäjille.
Lähtökohta on erottaa kaksi asiaa, jotka perinteisesti tapahtuvat
samalla hetkellä.

- **Käyttöönotto** (*deployment*) on tekninen tapahtuma: uusi versio
  ohjelmasta on asennettu ja käynnissä tuotannossa.
- **Julkaisu** (*release*) on liiketoiminnan tapahtuma: käyttäjä saa
  uuden ominaisuuden.

Kun nämä erotetaan, käyttöönotosta tulee rutiinia, jota voi tehdä
monta kertaa päivässä, koska se ei muuta mitään käyttäjälle. Julkaisun
ajankohdan päättää tuotteen omistaja, ja se voidaan tehdä asteittain
ja perua ilman uutta käyttöönottoa. Ominaisuuslippu (*feature flag*,
*feature toggle*) on väline tähän: ajon aikana luettava asetus, joka
valitsee, kumpaa koodipolkua käytetään.

## Lippujen lajit

Lippu on yksinkertainen mekanismi, jota käytetään neljään eri
tarkoitukseen. Pete Hodgsonin jaottelu erottaa ne eliniän ja sen
mukaan, kuka lippua kääntää.

| Laji | Tarkoitus | Elinikä | Kuka kääntää |
|-----------------|--------------------------------|-------------|---------------|
| julkaisulippu | keskeneräinen ominaisuus rungossa piilossa; asteittainen julkaisu | päiviä tai viikkoja | kehitystiimi |
| koelippu | kahden vaihtoehdon vertailu käyttäjillä (A/B-testi) | kokeen ajan | tuotetiimi |
| operointilippu | raskaan toiminnon sulkeminen kuormassa tai häiriössä | pysyvä | ylläpito |
| oikeuslippu | toiminto vain tietyille asiakkaille tai tilaustasoille | pysyvä | myynti, tuki |

Lajit kannattaa pitää erillään, koska niiden vaatimukset eroavat.
Julkaisulippu on tilapäinen ja poistetaan, kun ominaisuus on kaikilla.
Operointilippu on pysyvä osa järjestelmää, ja sen on toimittava myös
silloin, kun moni muu asia ei toimi. Oikeuslippu on käytännössä
tuotteen ominaisuus, ja se kuuluu usein pikemmin käyttöoikeuksien
hallintaan kuin lippujärjestelmään.

## Lipun toteutus

Lipun ydin mahtuu muutamaan riviin. Asteittaista julkaisua varten
käyttäjät jaetaan sataan lokeroon, ja lippu on päällä niille, joiden
lokero on pienempi kuin lipun osuus.

```{.python tiedosto="esimerkit/toimitus/liput.py" osa="lippu"}
```

Lokero lasketaan tiivisteellä lipun nimestä ja käyttäjän tunnisteesta.
Valinnalla on kolme seurausta, jotka esimerkki tarkistaa
kymmenellätuhannella käyttäjällä.

```{.python tiedosto="esimerkit/luku07/kayttoonotto.py" osa="portaat"}
```

```{.tuloste tiedosto="esimerkit/luku07/kayttoonotto.odotettu"}
```

**Jako on tasainen.** Yhden prosentin osuudella ominaisuuden saa noin
sata käyttäjää kymmenestätuhannesta, eikä esimerkiksi ensimmäiset sata
rekisteröitynyttä, jotka eivät edusta muita.

**Jako on pysyvä.** Sama käyttäjä saa saman vastauksen joka pyynnöllä
ja jokaisella palvelimella ilman, että valintaa tallennetaan mihinkään.
Kun osuutta kasvatetaan, mukana olleet pysyvät mukana: sarake
*pysyivät* tarkistaa, että jokainen porras sisältää edellisen.
Käyttäjälle, jolta ominaisuus välillä katoaa, kokemus on huonompi kuin
kummallakaan vaihtoehdolla.

**Liput ovat toisistaan riippumattomia.** Koska lipun nimi on mukana
tiivisteessä, kaksi 50 prosentin lippua osuvat molemmat neljäsosalle
käyttäjistä. Jos lokero laskettaisiin pelkästä käyttäjästä, samat
käyttäjät saisivat aina kaikki uutuudet, ja kokeiden tulokset
sekoittuisivat toisiinsa.

Luettelo `sallitut` kytkee lipun päälle nimetyille käyttäjille osuudesta
riippumatta. Sillä tiimi kokeilee ominaisuutta tuotannossa ennen kuin
kukaan muu näkee sitä.

## Hätäkatkaisu

Kun asteittain julkaistu ominaisuus osoittautuu vialliseksi, se
suljetaan kääntämällä lippu pois. Uutta käyttöönottoa ei tarvita, ja
vaikutus on välitön. Tämä on lippujen suurin käytännön hyöty: perumisen
aika lyhenee putken kestosta sekunteihin.

Hätäkatkaisulla on yksi ehto, joka unohtuu helposti: **vanhan polun on
yhä toimittava.** Jos uusi ominaisuus on ehtinyt kirjoittaa tietoa
muodossa, jota vanha koodi ei ymmärrä, lipun kääntäminen ei palauta
toimivaa tilaa. Tiedon muodon muutokset vaativat siksi oman
menettelynsä (luku 9).

Operointilippu on sama mekanismi pysyvässä käytössä: raskas raportti,
suosittelut tai muu toiminto, josta voidaan luopua kuorman alla, jotta
ydintoiminnot pysyvät pystyssä. Ylikuorman hallintaa käsittelee
*Skaalautuvien järjestelmien suunnittelu*.

## Lippuvelka

Liput eivät ole ilmaisia. Jokainen lippu on ehtolause, joka kaksinkertaistaa
koodin mahdolliset tilat. Kuusi lippua tuottaa 64 yhdistelmää, eikä
kukaan testaa niitä kaikkia. Lippu, joka on ollut kaikilla päällä
puoli vuotta, on kuollutta koodia, joka on yhä luettava ja
ylläpidettävä, ja jonka vanhaa polkua kukaan ei ole ajanut kuukausiin.

Varoittava esimerkki on Knight Capital -välitysyhtiön häiriö vuonna
2012. Yhdysvaltain arvopaperimarkkinavalvojan selvityksen mukaan uusi
ohjelmisto otti käyttöön vanhan lipun uuteen tarkoitukseen, ja
käyttöönotto jäi yhdeltä palvelimelta tekemättä. Sillä palvelimella
lippu käynnisti vuosia käyttämättä olleen vanhan toiminnon, joka lähetti
markkinoille virheellisiä toimeksiantoja. Yhtiö menetti alle tunnissa
yli 400 miljoonaa dollaria. Tapauksessa yhdistyi kolme asiaa, joita
tämä tutoriaali käsittelee: poistamatta jäänyt koodi, lipun
uudelleenkäyttö ja käsin tehty, epätäydellinen käyttöönotto.

Velan hallintaan riittää kolme käytäntöä.

**Rekisteri.** Jokaisella lipulla on nimi, omistaja, laji ja
luontipäivä. Rekisteristä voi laskea, mitkä liput pitäisi jo poistaa.

```{.python tiedosto="esimerkit/toimitus/liput.py" osa="velka"}
```

```{.tuloste tiedosto="esimerkit/luku07/lippuvelka.odotettu"}
```

Kuudesta lipusta kolme on poistettavissa, ja siivous pudottaa
yhdistelmien määrän kahdeksasosaan. Operointilippu `raskas-raportti`
on merkitty pysyväksi, joten se ei ole velkaa.

**Poisto kuuluu työhön.** Kun julkaisulippu luodaan, sen poistaminen
kirjataan tehtäväksi samalla. Ominaisuus on valmis vasta, kun lippu ja
vanha koodipolku on poistettu. Jotkin tiimit asettavat lipuille
vanhenemispäivän, jonka jälkeen putki varoittaa tai kaatuu.

**Lippua ei käytetä uudelleen.** Uusi tarkoitus saa uuden nimen.

## Liput ja testaus

Lipun takana oleva koodi on testattava molemmissa asennoissa niin
kauan kuin molemmat ovat mahdollisia.

- Yksikkötestit ajetaan kummallekin polulle. Tämä on helppoa, jos
  lippu luetaan yhdessä paikassa ja valinta välitetään eteenpäin
  parametrina, kuten luvun 3 funktiossa `valitse`.
- Putken hyväksymistestit ajetaan vähintään kahdella asetelmalla:
  tuotannon nykyisillä lipuilla ja sillä, johon ollaan siirtymässä.
- Kaikkia yhdistelmiä ei testata. Riittää, että toisistaan riippuvat
  liput tunnistetaan ja niiden yhdistelmät katetaan.

Lippujen arviointi kannattaa keskittää. Jos sama lippu tarkistetaan
kymmenessä paikassa, sen poistaminen on kymmenen muutosta ja
puolivalmis tila on mahdollinen. Parempi rakenne on tehdä valinta
kerran pyynnön alussa ja valita sillä toteutus.

## Missä lippujen arvot ovat

Yksinkertaisimmillaan lippu on ympäristömuuttuja tai asetustiedoston
rivi, ja sen muuttaminen vaatii uudelleenkäynnistyksen. Se riittää
julkaisulipulle pienessä järjestelmässä. Jos lippuja halutaan kääntää
sekunneissa ja kohdistaa käyttäjäryhmiin, arvot haetaan
lippupalvelusta, joka voi olla oma taulu tietokannassa tai erillinen
tuote. OpenFeature on toimittajasta riippumaton rajapintamäärittely
lippujen lukemiseen.

Lippupalvelu on riippuvuus, joka voi olla poissa käytöstä. Jokaisella
lipulla on siksi oltava koodissa oletusarvo, ja oletuksen on oltava
turvallinen: julkaisulipulla pois, operointilipulla se asento, jossa
järjestelmä kestää.

Lipun muutos on tuotantomuutos. Sillä voi kaataa palvelun yhtä hyvin
kuin käyttöönotolla, joten muutokset kirjataan, niillä on tekijä ja
merkittävät muutokset tehdään asteittain.

## Rajat

- **Lippu ei ole tietoturvaraja.** Selaimeen tai mobiilisovellukseen
  toimitettu koodi on käyttäjän luettavissa lipun asennosta
  riippumatta, ja julkistamaton ominaisuus voi paljastua sieltä.
  Pääsy rajataan palvelimella.
- **Kaikkea ei voi liputtaa.** Tietokannan rakenteen muutos,
  riippuvuuden päivitys tai laaja refaktorointi ei mahdu ehtolauseen
  taakse. Niihin käytetään luvun 3 ja luvun 9 tekniikoita.
- **Liput siirtävät monimutkaisuutta.** Ne poistavat pitkäikäiset
  haarat versionhallinnasta ja tuovat ne koodiin ehtolauseina. Kauppa
  on yleensä hyvä, koska ehtolause on näkyvissä ja testattavissa,
  mutta vain jos liput poistetaan.

## Käytännössä

- Erota käyttöönotto ja julkaisu: vie koodi tuotantoon lippu pois
  päältä ja avaa se erikseen.
- Jaa käyttäjät lokeroihin tiivisteellä lipun nimestä ja käyttäjästä,
  jotta jako on pysyvä ja liput toisistaan riippumattomia.
- Anna jokaiselle lipulle omistaja ja poistopäivä luontihetkellä.
- Älä käytä lipun nimeä uudelleen.
- Lue lippu yhdessä paikassa ja testaa molemmat polut.
- Varmista, että vanha polku toimii niin kauan kuin lipun voi kääntää
  takaisin.

## Itsearviointi

- Osaat erottaa käyttöönoton ja julkaisun ja kertoa, mitä erottelulla
  saavutetaan.
- Osaat nimetä lippujen neljä lajia ja kertoa, miten niiden elinikä ja
  vaatimukset eroavat.
- Osaat toteuttaa asteittaisen julkaisun niin, että jako on tasainen,
  pysyvä ja lipusta toiseen riippumaton.
- Osaat selittää, miksi poistamaton lippu on velkaa, ja kuvata
  käytännöt, joilla velka pidetään kurissa.
- Osaat kertoa, mitä hätäkatkaisu edellyttää vanhalta koodipolulta.
