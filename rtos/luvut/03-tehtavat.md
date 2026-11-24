# Tehtävät ja vuorontaminen

Tehtävä on RTOSin vastine säikeelle: oma ohjelmalaskuri, omat
rekisterit ja oma pino, mutta yhteinen muistiavaruus kaikkien muiden
kanssa. Muistinsuojausta ei yleensä ole, joten virheellinen tehtävä
voi kirjoittaa toisen muistiin. Taidossa *Käyttöjärjestelmät*
käsiteltiin prosessin tiloja ja vuorontamisalgoritmeja yleisesti. RTOS
käyttää niistä yhtä: **kiinteän prioriteetin etuoikeuttavaa
vuorontamista**. Tärkein valmis tehtävä ajaa aina, ja se keskeytetään
heti, kun sitä tärkeämpi tulee valmiiksi.

## Tehtävän tilat

| Tila | Merkitys | Kidessä |
|------|----------|---------|
| ajossa (*Running*) | prosessori suorittaa tehtävää | `kide_nykyinen` |
| valmis (*Ready*) | voisi ajaa, mutta tärkeämpi tai yhtä tärkeä ajaa | valmislistassa |
| odottaa (*Blocked*) | odottaa aikaa, jonoa, semaforia tai ilmoitusta | viivelistassa tai odotuslistassa |
| keskeytetty (*Suspended*) | pois vuorontamisesta, kunnes toinen palauttaa | odottaa ilman aikarajaa |

Odottava tehtävä ei kuluta prosessoriaikaa. Tämä on RTOS-ohjelman
tärkein ero pääsilmukkaan: sen sijaan, että koodi kysyisi jatkuvasti
"onko dataa", tehtävä odottaa jonossa, ja ydin herättää sen, kun data
tulee. Jos mikään tehtävä ei ole valmis, ydin ajaa *idle-tehtävää*,
jonka prioriteetti on 0 ja joka nukkuu WFI-käskyssä.

Tehtävän tiedot ovat sen ohjauslohkossa (TCB, *task control block*).
Pino-osoitin on ensimmäisenä, koska kontekstinvaihdon assembly lukee
sen osoitteesta 0 (luku 4). Kaksi listasolmua kertovat, missä listoissa
tehtävä on: `tila_solmu` valmis- tai viivelistassa ja `odotus_solmu`
jonon tai semaforin odottajana. Aikarajan kanssa odottava tehtävä on
molemmissa yhtä aikaa.

```{.c tiedosto="esimerkit/kide/kide.h" osa="tcb"}
```

## Listat

Ytimen kaikki tietorakenteet ovat kahteen suuntaan linkitettyjä
listoja, joiden solmut on upotettu tehtävän TCB:hen. Listaan lisääminen
ei siksi varaa muistia, ja poistaminen on vakioaikainen, koska solmu
tietää naapurinsa ja listansa.

```{.c tiedosto="esimerkit/kide/lista.h" osa="tyypit"}
```

## Valmislistat ja bittikartta

Jokaisella prioriteetilla on oma valmislistansa. Bittikartan bitti *p*
kertoo, onko listassa *p* tehtäviä. Seuraavan tehtävän valinta on
silloin kaksi vaihetta: korkein asetettu bitti ja sen listan ensimmäinen
tehtävä. Cortex-M3:n CLZ-käsky laskee etunollat yhdellä käskyllä, joten
valinta kestää saman ajan, oli valmiita tehtäviä kaksi tai kaksisataa.
FreeRTOS tekee saman, kun `configUSE_PORT_OPTIMISED_TASK_SELECTION` on
päällä.

```{.c tiedosto="esimerkit/kide/tehtava.c" osa="tila"}
```

```{.c tiedosto="esimerkit/kide/tehtava.c" osa="valmiit"}
```

```{.c tiedosto="esimerkit/kide/tehtava.c" osa="valinta"}
```

Ajossa oleva tehtävä pysyy valmislistansa kärjessä. Kun tärkeämpi
tehtävä keskeyttää sen, se jää kärkeen ja jatkaa ensimmäisenä, kun
tärkeämpi on valmis.

## Etuoikeutus

Esimerkissä kolme tehtävää heräävät eri aikoina ja laskevat eri
määrän. `kide_kuormita(n)` kuluttaa prosessoria, kunnes tehtävä on
ajanut *n* tikin verran. Se on esimerkkien laskentatyön malli: oikea
ohjelma laskisi samassa ajassa vaikkapa suodatinta.

```{.c tiedosto="esimerkit/03-etuoikeutus/main.c" osa="tehtava"}
```

```{.tuloste tiedosto="esimerkit/testit/03-etuoikeutus.odotettu"}
```

Aikajanan sarake *t* näyttää, kuka ajoi tikkien *t* ja *t*+1 välissä.
Matala aloittaa, keski keskeyttää sen hetkellä 2 ja korkea keskin
hetkellä 3. Kumpikaan keskeytetty ei huomaa mitään, paitsi että sen
laskenta valmistuu myöhemmin. Ajoaika on jokaisella täsmälleen
pyydetty, ja kontekstinvaihtoja on vain herätyksissä ja
valmistumisissa. Tikki ei itsessään vaihda tehtävää, jos tärkeämpää ei
herää eikä samalla prioriteetilla ole muita valmiita.

## Tikki

Tikkikeskeytys tekee kolme asiaa: kasvattaa aikaa ja ajossa olevan
tehtävän ajoaikaa, herättää tehtävät, joiden viive tai aikaraja on
täynnä, ja kierrättää saman prioriteetin tehtäviä.

```{.c tiedosto="esimerkit/kide/tehtava.c" osa="tikki"}
```

Viivelista on järjestetty herätyshetken mukaan, joten silmukka käsittelee
vain ne tehtävät, jotka todella heräävät. Muuten tikin kesto kasvaisi
odottavien tehtävien määrän mukana. Tikkikeskeytys ei itse vaihda
tehtävää vaan pyytää vaihdon (luku 4), joka tehdään keskeytyksen
päätyttyä.

## Saman prioriteetin tehtävät

Kun valmiina on useampi saman prioriteetin tehtävä, ydin voi
kierrättää niitä tikin välein (*time slicing*) tai antaa kunkin ajaa,
kunnes se odottaa tai luovuttaa vuoronsa itse (`taskYIELD`). Valinta
tehdään asetuksella `configUSE_TIME_SLICING`.

```{.c tiedosto="esimerkit/04-vuorottelu/main.c" osa="laskija"}
```

```{.tuloste tiedosto="esimerkit/testit/04-vuorottelu.odotettu"}
```

Muunnelma ilman vuorottelua:

```{.tuloste tiedosto="esimerkit/testit/04-vuorottelu-ei.odotettu"}
```

Vuorottelu tuntuu reilulta, mutta keskimääräinen valmistumisaika on
huonompi: kaikki valmistuvat hetkellä 12, kun ilman vuorottelua
keskiarvo on 8. Vuorottelusta on hyötyä, kun saman prioriteetin
tehtävät ovat pitkiä ja vuorovaikutteisia, eikä mikään niistä saa
näännyttää muita. Reaaliaikajärjestelmässä aikakriittiset tehtävät
saavat yleensä omat prioriteettinsa, eikä vuorottelulla ole niille
merkitystä.

## Idle-tehtävä ja tikitön uni

Idle-tehtävä luodaan, kun vuorontaja käynnistyy. Se ajaa
sovelluksen koukkua `vApplicationIdleHook` ja nukkuu WFI-käskyssä
seuraavaan keskeytykseen asti. FreeRTOSissa idle-tehtävä vapauttaa
lisäksi poistettujen tehtävien muistin, joten sitä ei saa estää
pysyvästi.

Tavallinen tikki herättää prosessorin tuhat kertaa sekunnissa, vaikka
millään tehtävällä ei olisi tekemistä. *Tikitön* uni (FreeRTOS:
`configUSE_TICKLESS_IDLE`) korjaa tämän: kun idle-tehtävä huomaa, että
seuraava herätys on vasta *n* tikin päässä, se pysäyttää SysTickin,
asettaa matalan virrankulutuksen ajastimen herättämään *n* tikin
päästä ja menee syvään uneen. Herättyään se lisää laskuriin nukutut
tikit. Ajastimen tarkkuus ja herääminen vievät aikaa, joten tikitön
uni lisää huojuntaa. Siksi tiukimmat järjestelmät käyttävät sitä vain,
kun kaikki tehtävät odottavat pitkään.

## Käytännössä

- **Anna prioriteetit aikarajojen, ei tärkeyden mukaan.** Lyhyin
  määräaika saa korkeimman prioriteetin (luku 9). "Tärkein" tehtävä,
  jolla on väljä aikaraja, voi hyvin olla matala.
- **Älä jätä tehtävää pyörimään.** Silmukka, joka kyselee lippua
  odottamatta, estää kaikki matalammat tehtävät. Odota jonossa,
  semaforissa tai ilmoituksessa.
- **Pidä prioriteetteja vähän.** Kolme–viisi tasoa riittää useimpiin
  järjestelmiin. Jokainen taso on suunnittelupäätös, joka pitää
  perustella.
- **Älä anna tehtäväfunktion palata.** Tehtävä, jonka työ on valmis,
  poistaa itsensä (`vTaskDelete(NULL)` FreeRTOSissa) tai odottaa
  ikuisesti. Kide pysäyttää ohjelman, jos tehtävä palaa.
- **Mittaa ajoajat.** FreeRTOSin ajoaikatilastot
  (`configGENERATE_RUN_TIME_STATS`) kertovat, mikä tehtävä vie
  prosessorin. Kide laskee ajoajan tikkeinä samaan tapaan.

## Itsearviointi

- Osaat nimetä tehtävän tilat ja kertoa, missä listassa tehtävä on
  kussakin tilassa.
- Osaat selittää, miten valmislistat ja bittikartta tekevät valinnasta
  vakioaikaisen.
- Osaat piirtää aikajanan etuoikeuttavasta vuorontamisesta, kun
  tehtävien herätykset, laskenta-ajat ja prioriteetit tunnetaan.
- Osaat kertoa, mitä tikkikeskeytys tekee ja milloin se vaihtaa
  tehtävää.
- Osaat arvioida, milloin saman prioriteetin vuorottelusta on hyötyä,
  ja selittää tikittömän unen periaatteen.
