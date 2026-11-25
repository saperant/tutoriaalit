# Luokat ja oliot {.runko-omat-tyypit}

Javassa kaikki koodi on luokissa, joten luokan rakenne on tunnettava
ennen kuin muistimallista, kokoelmista tai virheistä voi puhua
tarkasti. Tämä luku käy läpi oliomallin perusteet: luokan osat,
kapseloinnin, rajapinnat, periytymisen, `enum`-tyypit, sisäkkäiset
luokat ja annotaatiot. Luku 8 jatkaa tästä tietueisiin (`record`),
suljettuihin hierarkioihin ja geneerisyyteen.

Pythonia osaavalle käsitteet ovat tuttuja, mutta Java tarkistaa
käännösaikana sen, minkä Python jättää sopimuksen varaan:

| Python | Java |
|--------|------|
| `class Tili:` ja `__init__(self, …)` | `class Tili { … }` ja konstruktori `Tili(…)` |
| `self.saldo`, `self` on aina parametrina | `this.saldo`; `this` on implisiittinen ja usein jätetään pois |
| kentät syntyvät sijoittamalla | kentät esitellään tyyppeineen luokan rungossa |
| `_nimi` on sopimus | `private` on kääntäjän valvoma |
| luokkamuuttuja, `@staticmethod` | `static`-kenttä ja `static`-metodi |
| `__str__`, `__eq__`, `__hash__` | `toString`, `equals`, `hashCode` |
| ankkatyypitys, `Protocol` | `interface` ja `implements`: nimellinen tyypitys |
| moniperintä, `abc.ABC` | yksi yliluokka (`extends`), monta rajapintaa; `abstract` |
| koristelija `@nimi` muuttaa funktiota | annotaatio `@Nimi` on pelkkää metatietoa |

## Luokan rakenne

Luokka kuvaa olion tilan (*kentät*) ja toiminnot (*metodit*).
*Konstruktori* on luokan niminen erikoismetodi, jonka `new` kutsuu:
se saa tyhjän olion ja alustaa sen kentät. Esimerkkinä on pankkitili,
jonka saldo ei saa mennä negatiiviseksi:

```{.java tiedosto="esimerkit/05-tili.java" osa="luokka"}
```

Huomioita:

- **Kentät** esitellään tyyppeineen. Kenttä, jolle ei anneta arvoa, saa
  oletusarvon (`0`, `false` tai `null`). `final`-kenttään sijoitetaan
  täsmälleen kerran, viimeistään konstruktorissa, ja kääntäjä tarkistaa
  sen. Paikallisella muuttujalla ei ole oletusarvoa: sen käyttö ennen
  sijoitusta on käännösvirhe.
- **`this`** viittaa käsiteltävään olioon. Sitä tarvitaan, kun
  parametrilla ja kentällä on sama nimi (`this.omistaja = omistaja`);
  muuten kenttään voi viitata pelkällä nimellä.
- **Konstruktoreita voi olla useita** (ylikuormitus). `this(…)`
  konstruktorin ensimmäisenä lauseena kutsuu saman luokan toista
  konstruktoria, jolloin tarkistukset ovat yhdessä paikassa. Jos
  luokalle ei kirjoiteta yhtään konstruktoria, kääntäjä tekee
  parametrittoman.
- **`static`-jäsen** kuuluu luokalle, ei oliolle: siitä on yksi
  kappale. `static final` on vakio, ja se nimetään isoin kirjaimin.
  Muuttuva `static`-kenttä, kuten esimerkin tilinumerolaskuri, on
  globaalia tilaa. Se riittää tähän esimerkkiin, mutta oikeassa
  ohjelmassa numerot antaa olio, joka välitetään sitä tarvitseville
  (luku 10).
- Konstruktori, joka heittää poikkeuksen, ei luo oliota. Siksi
  virheellistä tiliä ei voi olla olemassa.

## Metodit, kapselointi ja `toString`

Tilin metodit ovat ainoa tapa muuttaa saldoa, joten *invariantti*
"saldo ei ole negatiivinen" tarkistetaan yhdessä paikassa:

```{.java tiedosto="esimerkit/05-tili.java" osa="metodit"}
```

```{.java tiedosto="esimerkit/05-tili.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-tili.odotettu"}
```

Tätä kutsutaan *kapseloinniksi*: kentät ovat `private`, ja luokka
julkaisee vain toiminnot, jotka säilyttävät sen invariantit.
*Näkyvyysmääre* kertoo, kuka jäsentä saa käyttää:

- `private`: vain sama luokka
- ei määrettä: saman pakkauksen luokat (pakkaukset: luku 10)
- `protected`: sama pakkaus ja aliluokat
- `public`: kaikki.

Instanssimetodi (`tili.pane(…)`) saa olion `this`-viitteenä.
Staattinen metodi (`Tili.avattuja()`) ei liity olioon, joten se ei
voi käyttää instanssikenttiä. `saldoSnt()` on *lukumetodi*. Vanhempi
JavaBeans-käytäntö nimeää sen `getSaldoSnt()` ja lisää jokaiselle
kentälle myös `set`-metodin; uusi koodi julkaisee vain sen, mitä
kutsuja tarvitsee, eikä tee asetusmetodeja oletuksena.

Jokainen luokka perii luokan `Object`, jossa on muun muassa metodit
`toString`, `equals` ja `hashCode`. `toString` kannattaa korvata
luokissa, joita tulostetaan tai kirjataan lokiin: oletustoteutus
tulostaa vain luokan nimen ja hajautusarvon (`Tili@1b6d3586`).
Annotaatio `@Override` pyytää kääntäjää tarkistamaan, että metodi
todella korvaa perityn metodin; kirjoitusvirhe nimessä tai
parametreissa on silloin käännösvirhe. `equals` ja `hashCode`
käsitellään luvuissa 6 ja 7.

## Rajapinnat

*Rajapinta* (`interface`) luettelee metodit, jotka toteuttavan luokan
on tarjottava. Se on tyyppi: muuttujan, parametrin tai kokoelman
alkion tyypiksi kirjoitetaan rajapinta, ja koodi toimii jokaisella
toteutuksella. Esimerkin rajapinta kuvaa myyntirivien viennin
tekstiksi:

```{.java tiedosto="esimerkit/05-vienti.java" osa="rajapinta"}
```

Javan tyypitys on *nimellistä*: luokka toteuttaa rajapinnan vain, jos
se ilmoittaa sen sanalla `implements`. Pelkkä samanniminen metodi ei
riitä, toisin kuin Pythonin ankkatyypityksessä. Luokka voi toteuttaa
monta rajapintaa. Rajapinnan metodit ovat `public`, vaikka määrettä ei
kirjoiteta. Rajapinnan, jossa on yksi abstrakti metodi, voi toteuttaa
myös lambdalla (luku 4); oletusmetodit ja muut rajapinnan
lisäpiirteet ovat luvussa 8.

## Periytyminen ja `abstract`

Luokka voi *periä* yhden toisen luokan (`extends`). Aliluokka saa
yliluokan kentät ja metodit ja voi *korvata* (*override*) metodeja.
*Abstrakti luokka* (`abstract`) on keskeneräinen: siitä ei voi luoda
oliota, ja sen abstraktit metodit on toteutettava aliluokassa.
Abstrakti luokka sopii, kun toteutuksilla on yhteinen runko ja vain
osa vaiheista vaihtelee. Tässä taulukkomuotoinen vienti kulkee aina
samassa järjestyksessä, ja aliluokat päättävät muotoilun
(*mallimetodi*, *template method*):

```{.java tiedosto="esimerkit/05-vienti.java" osa="abstrakti"}
```

```{.java tiedosto="esimerkit/05-vienti.java" osa="aliluokat"}
```

```{.dot otsikko="Esimerkin tyypit. Yhtenäinen nuoli on periytyminen (`extends`), katkoviiva rajapinnan toteutus (`implements`). Abstraktista luokasta ja rajapinnasta ei voi luoda oliota."}
digraph {
  rankdir=BT; nodesep=0.35; ranksep=0.45;
  node [fontsize=9, height=0.4];
  obj [label="Object"];
  vienti [label="«interface»\nVienti", style="rounded,dashed", fillcolor="white"];
  taulukko [label="«abstract»\nTaulukkovienti", style="rounded,dashed", fillcolor="white"];
  csv [label="CsvVienti"];
  teksti [label="Tekstivienti"];
  lambda [label="lambda\nrivit -> …"];
  taulukko -> obj;
  taulukko -> vienti [style=dashed];
  csv -> taulukko; teksti -> taulukko;
  lambda -> vienti [style=dashed];
}
```

Huomioita:

- Aliluokan konstruktori kutsuu ensin yliluokan konstruktoria
  (`super(…)`). Jos kutsua ei kirjoiteta, kääntäjä lisää
  parametrittoman `super()`-kutsun.
- `super.yhteensa(…)` kutsuu yliluokan toteutusta korvatusta
  metodista.
- `protected`-jäsenet ovat aliluokkien käytössä. Kenttä `nimi` on
  silti `private`: aliluokka ei pääse yliluokan tilaan käsiksi.
- `final`-metodia ei voi korvata eikä `final`-luokkaa periä.
  `vie` on `final`, jotta aliluokka ei voi rikkoa vaiheiden
  järjestystä.

Kutsuja näkee vain rajapinnan. Kutsu `vienti.vie(…)` valitsee
toteutuksen olion todellisen luokan mukaan ajon aikana (*dynaaminen
sidonta*), ja `instanceof` kertoo, onko olio annettua tyyppiä:

```{.java tiedosto="esimerkit/05-vienti.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-vienti.odotettu"}
```

Periytyminen kytkee aliluokan yliluokan toteutukseen. Yliluokan
muutos voi rikkoa aliluokan (*fragile base class*), ja konstruktorista
kutsuttu korvattava metodi näkee keskeneräisen olion
(`-Xlint:this-escape` varoittaa). Siksi luokat tehdään `final`iksi,
ellei niitä ole suunniteltu perittäviksi, ja syvät hierarkiat
korvataan rajapinnoilla ja *koostamisella*: olio sisältää toisen
olion ja delegoi sille (luku 8). Periytymistä näkee silti paljon
vanhassa koodissa ja kirjastoissa, esimerkiksi poikkeusluokissa
(luku 9) ja kokoelmien runkoluokissa (`AbstractList`), joten se on
osattava lukea.

## `enum`

`enum` on luokka, jolla on kiinteä, nimetty joukko olioita. Luvun 4
tilakoneessa arvot olivat pelkkiä nimiä, mutta `enum`illa voi olla
kenttiä, konstruktori ja metodeja kuten muillakin luokilla:

```{.java tiedosto="esimerkit/05-toimitustapa.java" osa="enum"}
```

```{.java tiedosto="esimerkit/05-toimitustapa.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-toimitustapa.odotettu"}
```

`values()` palauttaa arvot esittelyjärjestyksessä ja `valueOf` hakee
arvon nimellä (tuntematon nimi heittää `IllegalArgumentException`in).
Jokaisesta arvosta on täsmälleen yksi olio, joten `enum`-arvoja
verrataan operaattorilla `==`. `EnumMap` ja `EnumSet` ovat nopeimmat
kokoelmat `enum`-avaimille (luku 7). `ordinal()`-arvoa ei tallenneta
tiedostoon tai tietokantaan, koska se muuttuu, kun arvojen järjestys
muuttuu; tallennetaan `name()`. `enum`, jolla on yksi arvo, on
yksinkertaisin tapa toteuttaa *singleton*
(`enum Asetukset { INSTANSSI; }`).

## Sisäkkäiset ja nimettömät luokat

Luokan voi määritellä toisen luokan sisään, kun se on olemassa vain
ulompaa luokkaa varten. Muotoja on neljä:

| Muoto | Viite ulompaan olioon | Tyypillinen käyttö |
|----------------------------------|----------------------|--------------------------------|
| staattinen sisäkkäinen luokka (`static class`) | ei | aputyyppi, rakentaja, tulostyyppi |
| sisäluokka (ilman sanaa `static`) | on | iteraattori, näkymä ulomman olion tilaan |
| paikallinen luokka (metodin sisällä) | on, jos metodi ei ole staattinen | harvinainen; paikallinen `record` välitulokselle |
| nimetön luokka (`new Tyyppi() { … }`) | kuten paikallisella | rajapinnan tai yliluokan kertakäyttöinen toteutus |

Esimerkin mittaussarja säilyttää viimeisimmät arvot taulukossa.
`Rajat` on staattinen sisäkkäinen luokka ja `Kulkija` sisäluokka,
joka lukee ulomman olion kenttiä:

```{.java tiedosto="esimerkit/05-sisakkaiset.java" osa="sarja"}
```

```{.java tiedosto="esimerkit/05-sisakkaiset.java" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-sisakkaiset.odotettu" rivit="1-1"}
```

Luokka, joka toteuttaa rajapinnan `Iterable`, kelpaa for-each-
silmukkaan. Kirjaston kokoelmat on toteutettu samalla tavalla.
Sisäluokan olio pitää ulomman olion elossa, mikä on yleinen
muistivuodon syy (luku 6). Siksi sisäkkäinen luokka kirjoitetaan
`static`-sanalla aina, kun se ei tarvitse ulomman olion tilaa.
Sisäkkäiset `record`-, `enum`- ja `interface`-tyypit ovat aina
staattisia.

Nimetön luokka määrittelee luokan ja luo siitä olion samassa
lausekkeessa. Ennen lambdoja se oli tapa välittää toiminto
parametrina, ja vanhassa koodissa sitä näkee paljon. Jos tyyppi on
funktionaalinen rajapinta, lambda tekee saman lyhyemmin:

```{.java tiedosto="esimerkit/05-sisakkaiset.java" osa="nimeton"}
```

```{.tuloste tiedosto="esimerkit/05-sisakkaiset.odotettu" rivit="2-3"}
```

Nimetöntä luokkaa tarvitaan yhä, kun korvataan luokan metodi tai
toteutetaan rajapinta, jossa on useita metodeja. Luvun 6
välimuistiesimerkki tekee näin `LinkedHashMap`ille.

## Annotaatiot

*Annotaatio* (`@Nimi`) on luokkaan, metodiin, kenttään tai parametriin
liitettyä metatietoa. Se ei itse tee mitään, toisin kuin Pythonin
koristelija: vaikutus syntyy vasta, kun jokin lukee annotaation.
Lukijoita on kolmenlaisia:

- **Kääntäjä.** `@Override` (tarkista, että metodi korvaa perityn),
  `@Deprecated` (varoita käyttäjiä), `@SuppressWarnings("unchecked")`
  (vaienna nimetty varoitus) ja `@FunctionalInterface` (tarkista, että
  rajapinnassa on täsmälleen yksi abstrakti metodi).
- **Annotaatioprosessori** käännöksen aikana. Prosessori tuottaa uutta
  koodia tai tarkistaa vanhaa: Dagger, MapStruct ja JMH (luku 12)
  toimivat näin.
- **Kirjasto ajon aikana reflektiolla.** JUnit etsii metodit, joissa
  on `@Test` (luku 12), ja Spring luokat, joissa on `@Component`
  (taito *Taustapalvelut*).

Oma annotaatio määritellään sanalla `@interface`. `@Retention` kertoo,
säilyykö annotaatio ajoon asti, ja `@Target`, mihin sen saa liittää.
Esimerkki merkitsee palvelun käynnistystarkistukset annotaatiolla ja
ajaa ne reflektiolla:

```{.java tiedosto="esimerkit/05-annotaatiot.java" osa="annotaatio"}
```

```{.java tiedosto="esimerkit/05-annotaatiot.java" osa="ajuri"}
```

```{.tuloste tiedosto="esimerkit/05-annotaatiot.odotettu"}
```

Ajuri ei tunne tarkistusten nimiä: uusi tarkistus on uusi annotoitu
metodi. Samalla periaatteella toimivat testikehykset ja
sovelluskehykset. Hintana on, että kääntäjä ei näe kutsua:
reflektiolla kutsuttu metodi näyttää käyttämättömältä, virheet
ilmenevät vasta ajossa, ja reflektio on tavallista kutsua hitaampi.
Sovelluskoodissa omia annotaatioita ja reflektiota tarvitaan harvoin;
tavallinen rajapinta ja lista olioita on yleensä selkeämpi.

## Käytännössä

- **Kentät `private` ja mieluiten `final`.** Tilaa muutetaan vain
  metodeilla, jotka säilyttävät invariantit. Muuttumaton olio on
  säieturvallinen ja kelpaa hajautusavaimeksi.
- **Validoi konstruktorissa.** Kun virheellistä oliota ei voi luoda,
  muun koodin ei tarvitse tarkistaa sitä uudelleen.
- **Rajapinta tyypiksi.** Parametrit, kentät ja paluuarvot
  kirjoitetaan rajapinnan tyyppisiksi, jolloin toteutuksen voi
  vaihtaa ja testissä korvata.
- **Luokat `final`iksi, periytyminen harkiten.** Abstrakti luokka
  sopii yhteiseen runkoon, jonka omistat itse. Kirjaston luokkaa ei
  peritä, ellei sitä ole dokumentoitu perittäväksi.
- **`@Override` aina, kun metodi korvaa perityn.** Kääntäjä huomaa
  silloin, jos yliluokan metodin nimi tai parametrit muuttuvat.
- **`static` vain vakioille ja puhtaille apumetodeille.** Muuttuva
  staattinen kenttä on globaali muuttuja: se vaikeuttaa testausta ja
  on säikeiden välillä jaettua tilaa (luku 11).
- **Sisäkkäinen luokka `static`iksi**, ellei se tarvitse ulompaa
  oliota. Nimettömän luokan tilalle lambda, kun rajapinnassa on yksi
  metodi.
- **Hinta.** Olion luonti on halpaa (luku 6). Metodikutsu rajapinnan
  tai yliluokan kautta on yleensä yhtä nopea kuin suora kutsu, koska
  JIT inlinoi kutsun, kun kutsukohdassa näkyy yksi tai kaksi
  toteutusta. Reflektiokutsu on hitaampi, ja se estää osan
  optimoinneista.

## Itsearviointi

- Osaat kirjoittaa luokan, jonka konstruktori validoi argumentit ja
  jonka kentät ovat kapseloituja.
- Osaat kertoa, mitä `this`, `static` ja `final` tarkoittavat kentässä,
  metodissa ja luokassa.
- Osaat määritellä rajapinnan, toteuttaa sen usealla luokalla ja
  käyttää toteutuksia rajapinnan kautta.
- Osaat lukea ja kirjoittaa periytymistä: `extends`, `super`,
  `abstract`, `protected` ja `@Override`, ja kertoa, miksi sitä
  käytetään säästeliäästi.
- Osaat kirjoittaa `enum`in, jolla on kenttiä ja metodeja.
- Osaat valita staattisen sisäkkäisen luokan, sisäluokan, nimettömän
  luokan ja lambdan välillä.
- Osaat kertoa, mitä annotaatio on ja kuka sen lukee.
