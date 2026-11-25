# Muistinhallinta

Mikrokontrollerissa on kymmeniä tai satoja kilotavuja RAMia, ei
virtuaalimuistia eikä sivutusta. Kun muisti loppuu, mikään
käyttöjärjestelmä ei pelasta ohjelmaa. Siksi RTOS-ohjelman muisti
suunnitellaan etukäteen: mitä varataan, milloin ja kuka vapauttaa.
Taidossa *Käyttöjärjestelmät* toteutettiin yleiskäyttöinen varaaja ja
nähtiin, miten pirstoutuminen syntyy. Tässä luvussa kysymys on, mitä
sellaisesta varaajasta uskaltaa käyttää laitteessa, jonka on toimittava
vuosia ilman uudelleenkäynnistystä.

## Staattinen ja dynaaminen varaus

Kaikki tämän tutoriaalin esimerkit varaavat tehtävät, pinot, jonot ja
semaforit staattisesti: muisti on globaaleissa muuttujissa, ja ytimen
`...CreateStatic`-funktiot vain alustavat sen. Staattisella varauksella
on kolme etua:

- **Kaikki tiedetään käännösaikana.** Linkkerin karttatiedosto kertoo
  tarkalleen, paljonko RAMia käytetään, ja jos se ei riitä, linkitys
  epäonnistuu laitteen sijaan.
- **Varaus ei voi epäonnistua ajossa**, joten virheenkäsittelyä ei
  tarvita.
- **Muisti ei pirstoudu.**

Haittana on, että muisti on varattu koko ajan, vaikka oliota
tarvittaisiin vain hetken. Turvallisuuskriittisissä järjestelmissä
(MISRA C, IEC 61508) dynaaminen varaus on yleensä kielletty
käynnistyksen jälkeen.

## FreeRTOSin keot

FreeRTOS antaa valita viidestä varaajasta, ja valinta kertoo, mitä
dynaamisesta muistista halutaan:

| Toteutus | Vapautus | Pirstoutuminen | Kesto | Käyttö |
|---------|------------------|----------------|------------------|-----------------------|
| heap_1 | ei | ei | vakio | kaikki luodaan käynnistyksessä |
| heap_2 | kyllä, ei yhdistä | kyllä | lähes vakio | vanhentunut |
| heap_3 | `malloc`/`free` | kirjaston mukaan | ei rajattu | kun C-kirjaston varaaja on pakko |
| heap_4 | kyllä, yhdistää naapurit | vähän | listan pituuden mukaan | yleiskäyttöinen |
| heap_5 | kuten heap_4 | vähän | listan pituuden mukaan | useita erillisiä muistialueita |

Kide toteuttaa heap_1:n: kasvavan osoittimen, joka ei vapauta mitään.
Se on lyhyin mahdollinen varaaja ja täysin deterministinen. Sen
käyttötapa on luoda kaikki dynaamisesti käynnistyksen aikana, kun
koot riippuvat esimerkiksi asetuksista, ja sen jälkeen ei koskaan.

```{.c tiedosto="esimerkit/kide/muisti.c" osa="keko"}
```

## Muistipooli

Kun ohjelma tarvitsee muistia ajon aikana, esimerkiksi viesteille,
yleiskäyttöistä varaajaa parempi on *muistipooli*: joukko samankokoisia
lohkoja ja vapaiden lohkojen lista. Varaus ottaa listan ensimmäisen,
vapautus palauttaa lohkon listan alkuun. Molemmat ovat vakioaikaisia,
eikä pooli pirstoudu, koska jokainen vapautunut lohko kelpaa jokaiseen
varaukseen. Jos tarvitaan muutamaa kokoa, käytetään muutamaa poolia.

Kiden esimerkissä pooliin on yhdistetty laskeva semafori, joka laskee
vapaat lohkot. Varaus voi silloin odottaa vapautumista aikarajan
kanssa samalla tavalla kuin jono.

```{.c tiedosto="esimerkit/15-muisti/pooli.h" osa="tyyppi"}
```

```{.c tiedosto="esimerkit/15-muisti/pooli.c" osa="pooli"}
```

Vapautus tarkistaa, että osoite on poolin lohkon alku. Vieras osoite
tai kaksoisvapautus (jota tämä tarkistus ei tunnista) rikkoisi
vapaalistan, ja virhe näkyisi vasta myöhemmin aivan muualla.

## Viestit osoittimina

Esimerkissä tuottaja varaa viestille lohkon poolista, täyttää sen ja
lähettää jonossa vain osoittimen. Kuluttaja käsittelee viestin ja
palauttaa lohkon pooliin. Viestiä ei kopioida kertaakaan, ja lohkon
omistus kulkee selvästi: tuottajalta jonoon, jonosta kuluttajalle ja
takaisin pooliin. Tehtävät luodaan heap_1-keosta `xTaskCreate`lla.

```{.c tiedosto="esimerkit/15-muisti/main.c" osa="viesti"}
```

```{.c tiedosto="esimerkit/15-muisti/main.c" osa="tuottaja"}
```

```{.c tiedosto="esimerkit/15-muisti/main.c" osa="kuluttaja"}
```

```{.c tiedosto="esimerkit/15-muisti/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/15-muisti.odotettu"}
```

Pooli rajaa samanaikaisten viestien määrän kolmeen. Kun lohkot ovat
lopussa, tuottaja odottaa, kunnes kuluttaja vapauttaa lohkon, ja vauhti
tasaantuu kuluttajan tahtiin. Poolin koko on siis myös vuonohjausta:
nopea tuottaja ei voi varata kaikkea muistia. Jonoon mahtuisi kahdeksan
osoitinta, mutta pooli ei koskaan anna niin montaa viestiä liikkeelle.

## Pinon mitoitus

Jokaisella tehtävällä on oma pinonsa, ja pinot ovat yleensä RTOS-
ohjelman suurin RAMin käyttäjä. Liian pieni pino vuotaa yli ja
ylikirjoittaa muistia sen alapuolelta. Liian suuri tuhlaa RAMia, jota
on vähän. Pinon tarve koostuu kolmesta osasta:

- tehtävän syvimmän kutsuketjun paikalliset muuttujat ja tallennetut
  rekisterit; GCC kertoo funktiokohtaisen käytön valitsimella
  `-fstack-usage` ja varoittaa rajan ylityksestä valitsimella
  `-Wstack-usage=`
- kontekstinvaihdon kehys, 16 sanaa (Cortex-M4F:llä
  liukulukurekistereineen 50)
- kirjastofunktiot, joiden pinonkäyttöä ei näe suoraan: `printf`-
  perhe voi viedä satoja tavuja.

Keskeytyskäsittelijät ajavat MSP:llä, mutta keskeytys tallentaa
kehyksensä sen tehtävän pinoon, jonka aikana se tulee.

Laskeminen on työlästä, joten käytännössä pino mitoitetaan väljäksi,
mitataan ajossa ja pienennetään mittauksen perusteella. Kide täyttää
uuden pinon tunnisteella `0xA5A5A5A5`, ja `uxTaskGetStackHighWaterMark`
laskee, montako sanaa pohjalta on yhä koskematta. FreeRTOS tekee
täsmälleen saman.

```{.c tiedosto="esimerkit/kide/tehtava.c" osa="vesiraja"}
```

Vesiraja on vain alaraja pahimmalle käytölle: se kertoo, mitä ajossa on
tapahtunut, ei mitä voi tapahtua. Mittauksen on käytävä läpi tehtävän
raskaimmat polut, kuten virheenkäsittely ja harvinaiset komennot. Se
riippuu myös siitä, missä kohdassa keskeytykset osuivat tehtävään:
syvimmässä kohdassa osuva keskeytys lisää käyttöön kehyksensä.
Luvun 6 komentotulkin vesiraja vaihteli siksi ajosta toiseen kahdella
sanalla sen mukaan, milloin sarjaportin tavut saapuivat, eikä
esimerkki tulosta sitä.

## Ylivuodon tunnistus

FreeRTOS tarjoaa kaksi ohjelmallista tarkistusta, jotka tehdään
jokaisessa tehtävänvaihdossa (`configCHECK_FOR_STACK_OVERFLOW`):
menetelmä 1 tarkistaa, onko tallennettu pino-osoitin pinon alapuolella,
menetelmä 2 tarkistaa, ovatko pinon alimmat sanat yhä
tunnistearvossa. Kide tekee molemmat.

```{.c tiedosto="esimerkit/16-pino/main.c" osa="kuormat"}
```

```{.c tiedosto="esimerkit/16-pino/main.c" osa="rekursio"}
```

```{.tuloste tiedosto="esimerkit/testit/16-pino.odotettu"}
```

Kevyt tehtävä käyttää 18 sanaa 128:sta, raskas 82, koska sen 256
tavun puskuri on pinossa. Rekursiivinen tehtävä vuotaa 30 sanaa pinonsa
alle, ja ydin huomaa sen, kun tehtävä seuraavan kerran vaihtuu.
Esimerkissä pinon alla on suoja-alue, joten ylivuoto ei vahingoita
muuta. Oikeassa ohjelmassa pinon alla on jonkin toisen tehtävän
pino tai muuttujat, ja ne ovat jo rikki, kun tarkistus huomaa
ylivuodon. Ohjelmallinen tarkistus on siksi kehitysvaiheen apu, ei
suoja.

Laitteistoon perustuva suoja on parempi. **MPU** voi kieltää pääsyn
32 tavun alueelle jokaisen pinon alla, jolloin ensimmäinen ylivuotava
kirjoitus aiheuttaa MemManage-vian juuri siinä kohdassa (taito
*Mikrokontrollerit ja bare-metal-ohjelmointi*). FreeRTOSin MPU-portit
tekevät tämän.
ARMv8-M-arkkitehtuurin (esimerkiksi Cortex-M33 ja M55) **PSPLIM**-rekisteri
asettaa pinolle alarajan, jonka alittaminen on vika, ja RTOS päivittää
sen jokaisessa vaihdossa.

## Käytännössä

- **Varaa staattisesti, kun voit.** Kaikki tehtävät, jonot ja
  semaforit tunnetaan yleensä käännösaikana.
- **Jos varaat dynaamisesti, tee se käynnistyksessä.** heap_1 riittää
  silloin, ja varauksen epäonnistuminen käsitellään yhdessä paikassa.
- **Käytä ajonaikaiseen varaukseen poolia**, älä yleiskäyttöistä
  varaajaa. Sovi lohkon omistuksesta ja tarkista vapautukset.
- **Mittaa pinojen vesirajat** raskaimmilla poluilla ja jätä 20–50 %
  varaa. Kirjaa vesirajat tuotantolaitteen diagnostiikkaan.
- **Älä laita isoja puskureita pinoon.** 256 tavun paikallinen
  taulukko kasvattaa tehtävän pinoa pysyvästi; staattinen puskuri tai
  poolin lohko on parempi.
- **Ota laitteistosuoja käyttöön**, jos piirissä on MPU tai PSPLIM.

## Itsearviointi

- Osaat perustella staattisen varauksen edut ja valita FreeRTOSin
  keoista tilanteeseen sopivan.
- Osaat toteuttaa muistipoolin ja selittää, miksi se ei pirstoudu.
- Osaat välittää viestejä osoittimina ja pitää lohkojen omistuksen
  selvänä.
- Osaat arvioida tehtävän pinon tarpeen, mitata sen vesirajana ja
  kertoa ohjelmallisen ylivuototarkistuksen rajat.
- Osaat kertoa, miten MPU tai PSPLIM suojaa pinon ylivuodolta.
