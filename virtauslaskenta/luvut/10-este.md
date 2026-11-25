# Virtaus esteen ohi

Tähänastiset virtaukset ovat asettuneet tasapainoon. Useimmat todelliset
virtaukset eivät asetu: tylpän kappaleen takana pyörteet irtoavat
vuorotellen kummaltakin puolelta ja muodostavat **pyörreradan**. Ilmiö
soittaa puhelinlankoja tuulessa ja värähdyttää savupiippuja ja siltojen
kaapeleita. Tässä luvussa se lasketaan, sen taajuus mitataan, ja samalla
nähdään käytännössä, mitä luvun 5 numeerinen diffuusio tekee oikealle
virtaukselle.

## Tehtävä

Asetelma on sama kuin luvun 8 herkkyyskokeessa, mutta Reynoldsin luku
esteen sivun mukaan on nyt 100. Tasapainotilan pyörrepari on tällä
Reynoldsin luvulla epästabiili: pienikin häiriö kasvaa, ja pyörteet
alkavat irrota.

```{.python tiedosto="esimerkit/10-este.py" osa="tehtava"}
```

Este on tahallaan yhden ruudun verran sivussa kanavan keskilinjalta.
Täysin symmetrisessä tehtävässä laskettu virtaus pysyisi symmetrisenä,
kunnes pyöristysvirheet rikkovat symmetrian, ja irtoamisen alkamishetki
riippuisi koneesta ja kääntäjästä. Todellisessa virtauksessa häiriöitä
on aina, joten pieni epäsymmetria on mallina rehellisempi kuin
täydellinen symmetria.

Tasapainoon marssiva silmukka ei tässä kelpaa, koska tasapainoa ei ole.
Lasku ajetaan kiinteään loppuaikaan, ja esteen takaa tallennetaan
pystynopeus jokaisella askeleella.

```{.python tiedosto="esimerkit/10-este.py" osa="ajo"}
```

## Pyörrerata ja Strouhalin luku

![Pyörteisyys ajan lopussa kolmella advektiokaaviolla hilalla, jossa
esteen sivulla on kuusi ruutua, ja pystynopeus mittapisteessä esteen
takana. Ruskea pyörii vastapäivään, sininen
myötäpäivään.](kuvat/este.png){width=95%}

Esteen ylä- ja alareunasta lähtee leikkauskerros, joissa pyörteisyys on
vastakkaismerkkistä. Kerrokset kiertyvät vuorotellen pyörteiksi, jotka
irtoavat ja kulkeutuvat virran mukana. Mittapisteen pystynopeus
värähtelee säännöllisesti, kun alkutilan häiriö on kasvanut täyteen
mittaansa.

Irtoamisen taajuus $f$ ilmoitetaan dimensiottomana **Strouhalin
lukuna**

$$\mathrm{St} = \frac{f\,d}{U},$$

jossa $d$ on kappaleen leveys ja $U$ virtauksen nopeus. Tylpille
kappaleille se on laajalla Reynoldsin luvun alueella suuruusluokkaa
0,2: pyörre irtoaa aina, kun virtaus on kulkenut noin viisi kappaleen
leveyttä. Tarkka arvo riippuu kappaleen muodosta ja siitä, kuinka
ahtaassa kanavassa se on. Suunnittelijaa luku kiinnostaa, koska
irtoavat pyörteet ravistelevat kappaletta taajuudella $f$, ja jos se
osuu rakenteen ominaistaajuuteen, värähtely voimistuu.

```{.python tiedosto="esimerkit/10-este.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/10-este.odotettu"}
```

## Kolme kaaviota, kolme vastausta

Sama tehtävä samalla hilalla antaa kolme eri Strouhalin lukua sen mukaan,
miten advektiovuo lasketaan.

**Vastavirta.** Pyörrerata on kuvassa kalpea, ja mittapisteen värähtely
on viidesosa keskeisdifferenssin tuloksesta ja yhä kasvamassa. Taajuus
on 27 prosenttia pienempi. Syy on numeerinen viskositeetti. Nopeudella 1
se on $Uh/2 = 0{,}017$, yli kahdeksan kertaa nesteen oma viskositeetti
0,002. Kaavio laskee siis paljon sitkeämmän nesteen virtausta kuin
pyydettiin. Tulos on silti sileä ja uskottavan näköinen.

**Keskeisdifferenssi.** Pyörteet ovat teräviä ja värähtely voimakasta.
Esteen etupuolella näkyy kuitenkin ruudun levyistä sahalaitaa. Hilan
Reynoldsin luku $Uh/\nu$ on 17, selvästi yli luvun 5 rajan kaksi, ja
keskeisdifferenssi heilahtelee siellä, missä nopeus muuttuu jyrkästi.

**Sekoitus** kertoimella 0,3 poistaa sahalaidan, ja pyörrerata säilyy.
Hinta on taajuus, joka on kymmenen prosenttia keskeisdifferenssin tulosta
pienempi.

Mikä näistä on oikein? Yksi hila ei vastaa siihen, joten lasketaan
keskeisdifferenssillä myös tiheämmällä hilalla. Strouhalin luku muuttuu
arvosta 0,227 arvoon 0,230 eli reilun prosentin. Keskeisdifferenssin
tulos on siis lähes hilasta riippumaton, ja muut kaksi kaaviota ovat
samalla hilalla kymmenen ja lähes kolmekymmentä prosenttia siitä sivussa.
Värähtelyn voimakkuus sen sijaan muuttuu vielä neljänneksen, eli se
vaatisi tiheämmän hilan kuin taajuus.

Tästä seuraa kolme opetusta, jotka pätevät valmiisiin ohjelmiin
sellaisinaan.

- Ensimmäisen kertaluvun vastavirtakaavio voi muuttaa virtauksen
  luonnetta, ei vain sen yksityiskohtia. Riittävän karkealla hilalla
  se voi sammuttaa pyörreradan kokonaan ja tuottaa siistin tasapainotilan,
  jota ei ole olemassa.
- Heilahtelu on rehellinen virhe: se näkyy ja kertoo, missä hila on
  liian harva. Numeerinen diffuusio on epärehellinen: se ei näy.
- Eri suureet suppenevat eri tahtiin. Taajuus on valmis ennen
  amplitudia, ja kappaleeseen kohdistuva voima suppenee vielä
  hitaammin.

## Ajasta riippuvan tuloksen käsittely

Ajasta riippuva lasku tuottaa aikasarjan, ja siitä on erotettava
kolme osaa.

1. **Alkutransientti** riippuu alkutilasta ja häiriöstä, eikä siitä
   raportoida mitään. Esimerkissä hylätään 60 prosenttia ajasta.
2. **Jaksollinen tai tilastollisesti vakaa osa** on tulos. Siitä
   lasketaan keskiarvot, vaihteluvälit ja taajuudet. Taajuus mitataan
   useasta jaksosta: esimerkki käyttää nollanylitysten välejä,
   pidemmistä sarjoista lasketaan spektri.
3. **Riittävyys.** Jos tulos muuttuu, kun keskiarvoistusaikaa
   pidennetään, sarja on liian lyhyt. Taulukon vastavirtarivin
   värähtely ei ole vielä asettunut, joten sen vaihteluväli ei ole
   lopullinen arvo.

## Käytännössä

- **Kysy, onko virtaus ajasta riippuva.** Jos tasapainoratkaisija ei
  suppene tai jäännös jää heilumaan, syy voi olla fysiikka: virtaus ei
  halua asettua. Silloin lasketaan ajassa.
- **Älä pakota symmetriaa.** Symmetriataso tai tarkalleen symmetrinen
  alkutila voi estää ilmiön, joka luonnossa syntyy aina.
- **Hylkää alkutransientti ja keskiarvoista riittävän pitkään.**
  Kymmenen jaksoa on vähimmäismäärä taajuudelle, voimien keskiarvoille
  tarvitaan enemmän.
- **Aika-askel erottaa ilmiön.** Jaksoa kohden tarvitaan kymmeniä
  askelia. Stabiilisuusraja takaa tämän eksplisiittisessä laskussa,
  implisiittisessä askel on valittava itse.
- **Vertaa kaavioita ja hiloja.** Jos toisen kertaluvun kaavio ja
  vastavirta ovat eri mieltä taajuudesta, vastavirran tulos on
  hilan ominaisuus.

## Itsearviointi

- Osaat selittää, miten pyörrerata syntyy ja miksi sen laskeminen vaatii
  ajasta riippuvan ratkaisun.
- Osaat määritellä Strouhalin luvun ja mitata sen lasketusta
  aikasarjasta.
- Osaat selittää, miksi vastavirtakaavio muuttaa pyörreradan taajuutta
  ja voimakkuutta, ja arvioida numeerisen viskositeetin suuruuden.
- Osaat erottaa aikasarjasta alkutransientin ja varsinaisen tuloksen.
- Osaat perustella, kumpaan kahdesta ristiriitaisesta tuloksesta
  kannattaa luottaa, kun käytössä on hilan tihennys.
