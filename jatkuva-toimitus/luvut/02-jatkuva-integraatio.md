# Jatkuva integraatio

Kun kaksi ihmistä muuttaa samaa ohjelmaa, muutokset on jossain
vaiheessa sovitettava yhteen. Jatkuva integraatio on päätös tehdä se
heti eikä myöhemmin. Tämä luku näyttää, miksi myöhemmin on kalliimpaa,
ja mitä käytäntö tarkalleen vaatii.

## Integraation ongelma

Versionhallinta yhdistää rinnakkaiset muutokset automaattisesti, kun ne
osuvat eri kohtiin. Esimerkki tekee kolme yhdistämistä oikealla
Gitillä. Jokaisessa on yhteinen lähtötilanne, yksi muutos haarassa ja
yksi rungossa. Yhdistyksen jälkeen ohjelma ajetaan.

```{.python tiedosto="esimerkit/luku02/yhdistys.py" osa="yhdistys"}
```

```{.tuloste tiedosto="esimerkit/luku02/yhdistys.odotettu"}
```

Kaksi ensimmäistä tapausta ovat tuttuja tutoriaalista
*Versionhallinta (Git)*. Kolmas on tämän luvun kannalta tärkein.
Rungossa funktio `summa` nimettiin uudelleen ja kaikki sen kutsut
korjattiin. Haarassa lisättiin samaan aikaan uusi tiedosto, joka kutsuu
funktiota vanhalla nimellä. Muutokset eivät osu samoille riveille,
joten Git yhdistää ne siististi, ja tulos on rikki.

Tällaista kutsutaan **semanttiseksi ristiriidaksi**. Versionhallinta
vertaa tekstiä, ei merkitystä, joten se ei voi havaita sitä. Ainoa
keino on kääntää ja testata yhdistetty tulos. Tästä seuraa jatkuvan
integraation ensimmäinen periaate: *yhdistetty koodi on eri ohjelma
kuin kumpikaan haara, ja se on testattava erikseen.*

## Haaran ikä

Ristiriidan todennäköisyys kasvaa haaran iän mukana kahdesta suunnasta
yhtä aikaa: haaraan kertyy muutoksia, ja runko liikkuu sen alta.
Seuraava malli tekee tästä laskettavan. Repositoriossa on joukko
tiedostoja, haara ja runko muuttavat satunnaisia rivejä, ja ristiriita
syntyy, kun haaran muuttaman rivin kohdalla tai vieressä on rungossa
muutos.

```{.python tiedosto="esimerkit/toimitus/haarat.py" osa="malli"}
```

Malli on yksinkertaistus, joten sen ristiriitasääntö tarkistetaan ensin
oikeaa Gitiä vasten: kahteentoista satunnaiseen tapaukseen tehdään
samat muutokset oikeaan repositorioon ja katsotaan, onnistuuko
`git merge`.

```{.python tiedosto="esimerkit/luku02/haaran_ika.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/luku02/haaran_ika.odotettu"}
```

Malli ja Git ovat samaa mieltä kaikissa kahdessatoista tapauksessa.
Taulukon luvut eivät ole suoraan verrannollisia ikään. Koska sekä
haaran että rungon muutosmäärä kasvaa ajan mukana, odotettu
ristiriitojen määrä kasvaa iän *neliössä*: kahden päivän haarassa
ristiriitakohtia on keskimäärin noin neljä kertaa niin paljon kuin
päivän haarassa ja kahdeksan päivän haarassa yli kuusikymmentä kertaa
niin paljon.

![Ristiriidan todennäköisyys haaran iän mukaan kolmella rungon
muutostahdilla. Mitä vilkkaampi runko, sitä nopeammin haara
vanhenee.](kuvat/haaran-ika.png){width=62%}

Todellinen koodi ei muutu satunnaisesti. Muutokset kasautuvat samoihin
tiedostoihin, joten ristiriitoja syntyy todellisuudessa mallia
herkemmin, ja toisaalta hyvin modularisoidussa koodissa tiimit törmäävät
harvemmin. Mekanismi on silti sama: yhdistämisen vaikeus ei ole
vakiohinta, joka maksetaan kerran, vaan se kasvaa odottaessa
kiihtyvästi. Malli laskee lisäksi vain tekstuaaliset ristiriidat.
Semanttiset tulevat päälle, ja nekin yleistyvät iän mukana.

## Erän koko ja vian etsintä

Toinen syy integroida usein on vian paikantaminen. Oletetaan, että
jokainen muutos rikkoo jotain kahden prosentin todennäköisyydellä.
Kun muutoksia yhdistetään erä kerrallaan, erän koko määrää sekä sen,
kuinka usein yhdistys on rikki, että sen, kuinka monesta muutoksesta
syytä on etsittävä.

```{.python tiedosto="esimerkit/luku02/eran_koko.py" osa="era"}
```

```{.tuloste tiedosto="esimerkit/luku02/eran_koko.odotettu"}
```

Yhden muutoksen erä on rikki harvoin, ja kun on, syyllinen tiedetään.
Kahdensadan muutoksen erä on rikki lähes varmasti, ja syyn etsintä
vaatii kahdeksan puolitusta, joista jokainen on käännös ja testiajo.
Puolitushaku (`git bisect`) toimii lisäksi vain, jos vikoja on yksi.
Suuressa erässä niitä on usein monta, ja ne peittävät toisiaan.

## Mitä jatkuva integraatio vaatii

Käytäntö on peräisin Extreme Programming -menetelmästä 1990-luvun
lopulta, ja Martin Fowlerin artikkeli *Continuous Integration* on sen
tunnetuin kuvaus. Määritelmässä on kolme osaa.

1. **Jokainen yhdistää työnsä runkoon vähintään kerran päivässä.**
   Runko on yhteinen päähaara, Gitissä tavallisesti `main`.
2. **Jokainen yhdistys tarkistetaan automaattisesti.** Ohjelma
   rakennetaan ja testit ajetaan yhdistetylle koodille.
3. **Rikkinäinen runko korjataan heti.** Punainen runko estää kaikkia
   muita integroimasta, joten sen korjaaminen ohittaa muun työn.

Jez Humblen tunnettu testi kysyy saman kolmena kysymyksenä: yhdistävätkö
kaikki runkoon päivittäin, käynnistääkö jokainen yhdistys automaattisen
rakennuksen ja testit, ja korjataanko rikkinäinen rakennus tavallisesti
noin kymmenessä minuutissa. Jos vastaus johonkin on ei, kyse on jostain
muusta kuin jatkuvasta integraatiosta, vaikka CI-palvelin olisi
käytössä.

Määritelmä asettaa työlle vaatimuksia, jotka eivät näy siitä suoraan.

| Vaatimus | Miksi |
|---------------------|----------------------------------------------|
| kaikki versionhallinnassa | rakennus onnistuu puhtaasta kloonista: koodi, testit, rakennusskriptit, skeema, konfiguraatio |
| rakennus yhdellä komennolla | sama komento kehittäjän koneella ja putkessa |
| itsensä testaava rakennus | testit kuuluvat rakennukseen, ja epäonnistunut testi kaataa sen |
| nopea rakennus | hidasta ei ajeta usein; tavoite on noin kymmenen minuuttia |
| työ pilkotaan päivän paloihin | jokainen pala jättää ohjelman toimivaksi |
| näkyvä tila | kaikki näkevät, onko runko vihreä |

Vaativin näistä on työn pilkkominen. Se on taito, joka opitaan
tekemällä, ja luku 3 käsittelee sen tekniikat.

## Ennen yhdistämistä ja sen jälkeen

Kehittäjän päivittäinen kierros on lyhyt.

1. Hae rungon uusin tila ja sovita oma työ sen päälle.
2. Aja tarkistukset paikallisesti samalla komennolla kuin putki.
3. Yhdistä runkoon.
4. Seuraa putken tulos. Työ on valmis vasta, kun runko on vihreä.

Askel 2 ei korvaa askelta 4. Paikallinen kone eroaa putken ympäristöstä,
ja joku muu on voinut yhdistää väliin. Paikallinen ajo karsii
suurimman osan virheistä halvalla, ja putki on lopullinen tuomari.

Jos tiimi käyttää yhdistämispyyntöjä (*pull request*), putki ajetaan jo
pyynnölle. Silloin on tarkistettava, mitä se testaa: haaran kärkeä vai
haaran ja rungon yhdistettä. Vain jälkimmäinen havaitsee semanttisen
ristiriidan, ja sekin vanhenee, kun runko liikkuu. Vilkkaissa
repositorioissa käytetään siksi **yhdistämisjonoa** (*merge queue*):
jono yhdistää pyynnöt yksi kerrallaan rungon tuoreimpaan tilaan, ajaa
testit yhdisteelle ja päästää runkoon vain läpäisseet. Periaate on
vanha: runkoon päästetään vain koodia, jonka testit on ajettu juuri
siinä muodossa, johon runko päätyy.

## Kun runko hajoaa

Runko hajoaa joskus, ja se on hyväksyttävää. Olennaista on, mitä sen
jälkeen tapahtuu.

- **Korjaus alkaa heti.** Rikkoja tai kuka tahansa paikalla oleva
  ottaa asian, ja muut tietävät sen.
- **Peru ensin, tutki sitten.** Jos syy ei selviä muutamassa
  minuutissa, muutos perutaan (`git revert`) ja korjataan rauhassa.
  Rungon vihreys on tärkeämpi kuin yksittäisen muutoksen pysyminen.
- **Punaisen päälle ei yhdistetä.** Uusi muutos rikkinäisen rungon
  päällä tekee syyn selvittämisestä vaikeampaa, koska putki ei enää
  erota vanhaa vikaa uudesta.
- **Syy poistetaan.** Jos sama asia hajoaa toistuvasti, putkeen
  lisätään tarkistus tai testi siirretään aikaisempaan vaiheeseen.

Käytäntö on sukua Toyotan tuotantojärjestelmän periaatteelle pysäyttää
linja vian ilmetessä: vikaa ei päästetä eteenpäin, koska sen korjaaminen
kallistuu jokaisella askeleella.

Rungon rikkomisesta ei rangaista. Jos rikkominen on häpeä, ihmiset
alkavat yhdistää harvemmin ja suuremmissa erissä, ja se on juuri se
käytös, jota jatkuva integraatio yrittää poistaa.

## Rajat ja kritiikki

Jatkuva integraatio ei ole ilmainen, eikä se sovi sellaisenaan joka
paikkaan.

- **Se edellyttää testejä.** Ilman kattavia automaattisia testejä
  päivittäinen yhdistäminen levittää viat nopeammin. Testit tulevat
  ensin.
- **Se edellyttää luottamusta.** Avoimen lähdekoodin projektissa
  tuntemattoman tekijän muutosta ei voi päästää runkoon tarkastamatta.
  Yhdistämispyyntö ja katselmointi ovat siellä perusteltuja, ja
  viive hyväksytään.
- **Se ei poista suunnittelun tarvetta.** Kaksi kehittäjää voi
  integroida päivittäin ja rakentaa silti yhteensopimattomia
  ratkaisuja. Integraatio paljastaa ristiriidan aikaisin, mutta ei
  ratkaise sitä.
- **Hidas rakennus tekee siitä raskaan.** Jos täysi tarkistus kestää
  tunteja, kuten suurissa sulautetuissa järjestelmissä tai
  piirisuunnittelussa, tarkistus on porrastettava: nopea osajoukko
  jokaiselle muutokselle ja täysi ajo harvemmin.

Mikään näistä ei kumoa mekanismia. Ne kertovat, mitä on rakennettava
ensin ja missä päivittäisestä tahdista on perusteltua tinkiä.

## Käytännössä

- Mittaa haarojen ikä. Yksinkertaisin jatkuvan integraation mittari
  on, kuinka vanha vanhin yhdistämätön haara on.
- Tee rakennuksesta ja testeistä yksi komento ja aja sama komento
  putkessa.
- Varmista, että putki testaa yhdistetyn tuloksen eikä pelkkää haaraa.
- Sovi, mitä tapahtuu, kun runko on punainen: kuka korjaa, milloin
  perutaan ja ettei päälle yhdistetä.
- Aloita testeistä, jos niitä ei ole. Jatkuva integraatio ilman
  testejä on jatkuvaa yhdistämistä.

## Itsearviointi

- Osaat selittää, miksi siisti yhdistys voi tuottaa rikkinäisen
  ohjelman, ja antaa esimerkin semanttisesta ristiriidasta.
- Osaat perustella mallin avulla, miksi yhdistämisen vaikeus kasvaa
  haaran iän mukana nopeammin kuin lineaarisesti.
- Osaat kertoa jatkuvan integraation kolme vaatimusta ja erottaa
  käytännön CI-palvelimesta.
- Osaat kuvata, miten rikkinäinen runko käsitellään ja miksi peruminen
  on usein oikea ensimmäinen toimi.
- Osaat nimetä tilanteita, joissa päivittäisestä yhdistämisestä on
  perusteltua poiketa.
