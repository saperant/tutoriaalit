# Keskeytykset ja NVIC

Keskeytys on oheislaitteen tapa pyytää prosessorin huomiota: UART on
vastaanottanut tavun, ajastin on laskenut nollaan tai nastan taso on
vaihtunut. Ilman keskeytyksiä ohjelman pitäisi kysellä kaikkien
laitteiden tilaa vuorotellen, ja kiireellinen tapahtuma odottaisi,
kunnes kyselykierros ehtii siihen. Cortex-M:ssä keskeytyksiä hallitsee
ytimen osa *NVIC* (Nested Vectored Interrupt Controller). Nimi kertoo
sen kaksi ominaisuutta: keskeytykset voivat keskeyttää toisiaan
(*nested*), ja jokaisella on oma käsittelijänsä vektoritaulussa
(*vectored*), joten ohjelman ei tarvitse selvittää, mikä laite
keskeytyksen aiheutti.

## Keskeytyksen polku

Jotta keskeytys päätyy käsittelijään, sen on päästävä kolmen portin
läpi:

1. **Oheislaite** asettaa tilabitin ja nostaa keskeytyslinjan, jos
   keskeytys on sallittu laitteen omassa rekisterissä (esimerkiksi
   UART:n CTRL.RXINTEN).
2. **NVIC** merkitsee linjan *odottavaksi* (pending). Jos linja on
   sallittu (ISER), NVIC vertaa sen prioriteettia prosessorin
   nykyiseen prioriteettiin.
3. **Prosessori** ottaa keskeytyksen vastaan, ellei PRIMASK, BASEPRI
   tai meneillään oleva yhtä kiireellinen käsittelijä estä.

Alla oleva kuva näyttää samat portit ja sen, mihin keskeytys pysähtyy,
jos jokin niistä on kiinni.

```{.dot otsikko="Keskeytyksen polku oheislaitteesta käsittelijään"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.35;
  laite [label="oheislaite\nsyy + sallinta"];
  nvic [label="NVIC\nodottava, ISER,\nprioriteetti"];
  cpu [label="prosessori\nPRIMASK, BASEPRI,\naktiivinen taso"];
  kas [label="käsittelijä", style="rounded,filled,bold"];
  laite -> nvic [label="linja"];
  nvic -> cpu [label="pyyntö"];
  cpu -> kas [label="pinoaminen"];
  kas -> laite [label="kuittaus", style=dashed, constraint=false];
}
```

Kun käsittelijä alkaa, linja muuttuu odottavasta *aktiiviseksi*. Jos
oheislaite pitää linjaa yhä ylhäällä käsittelijän päättyessä,
keskeytys tulee heti uudelleen odottavaksi. Siksi käsittelijän on
kuitattava syy oheislaitteesta; luvun 6 esimerkki näyttää, mitä
unohdus maksaa.

NVIC:n rekistereissä on bitti kullekin linjalle. Sallinta ja kielto
ovat erillisissä rekistereissä (ISER, ICER), ja nollabitit jätetään
huomiotta, joten yksittäisen linjan muuttaminen on yksi kirjoitus
ilman luku–muutos–kirjoitusta.

```{.c tiedosto="esimerkit/yhteinen/mps2.h" osa="nvic"}
```

```{.c tiedosto="esimerkit/yhteinen/mps2.h" osa="nvic-apu"}
```

## Prioriteetit

Jokaisella keskeytyksellä on prioriteetti 8-bittisessä kentässä.
**Pienempi luku on kiireellisempi.** Piiri toteuttaa vain ylimmät
bitit: CMSDK:n Cortex-M3:ssa ja monissa piireissä kolme, STM32F4:ssä
neljä ja Cortex-M0+:ssa kaksi. Toteuttamattomat alabitit luetaan
nollina, joten prioriteetti kirjoitetaan siirrettynä kentän yläpäähän.
(QEMU toteuttaa kaikki kahdeksan bittiä, mutta siirretty arvo toimii
molemmissa.) Resetin, NMI:n ja HardFaultin prioriteetit ovat kiinteät
−3, −2 ja −1, eli ne ovat aina kiireellisimpiä. Järjestelmäpoikkeusten
SVCall, PendSV ja SysTick prioriteetit asetetaan SCB:n
SHPR-rekistereissä.

Säännöt ovat lyhyet:

- **Keskeyttäminen**: käsittelijän voi keskeyttää vain *kiireellisempi*
  keskeytys. Yhtä kiireellinen odottaa.
- **Valinta**: jos useampi odottaa, ajetaan kiireellisin; tasapelissä
  pienempi poikkeusnumero.
- **Ketjutus** (*tail-chaining*): jos toinen keskeytys odottaa, kun
  käsittelijä päättyy, prosessori siirtyy suoraan seuraavaan
  purkamatta ja tallentamatta kehystä välissä.
- **Myöhäinen saapuminen**: jos kiireellisempi keskeytys tulee
  kesken kehyksen tallennuksen, prosessori vaihtaa käsittelijää
  ennen ensimmäistäkään käskyä.

AIRCR-rekisterin PRIGROUP-kenttä voi jakaa prioriteettibitit kahteen
osaan, keskeyttämisprioriteettiin ja alaprioriteettiin, jolloin
alaprioriteetti vaikuttaa vain valintaan eikä keskeyttämiseen.
Oletus, jossa kaikki bitit ovat keskeyttämisprioriteettia, on yleensä
paras.

## Esimerkki: järjestys ja sisäkkäisyys

Esimerkki käyttää kolmea vapaata keskeytyslinjaa ja laukaisee ne
ohjelmallisesti kirjoittamalla ISPR-rekisteriin. Näin tapahtumat ovat
joka ajossa samassa järjestyksessä, ja käsittelijöiden tuloste
osoittaa säännöt. Linjan 14 prioriteetti on 1 (kiireellisin), linjan
13 2 ja linjan 15 3.

```{.c tiedosto="esimerkit/05-keskeytykset/main.c" osa="alustus"}
```

```{.c tiedosto="esimerkit/05-keskeytykset/main.c" osa="kasittelijat"}
```

Ensin kaikki kolme laukaistaan keskeytykset kiellettyinä (PRIMASK =
1), jolloin ne jäävät odottamaan. Kun keskeytykset sallitaan, ne
ajetaan prioriteettijärjestyksessä ketjutettuina:

```{.c tiedosto="esimerkit/05-keskeytykset/main.c" osa="vaihe1"}
```

Toisessa vaiheessa linjan 13 käsittelijä laukaisee linjat 14 ja 15.
Kiireellisempi 14 keskeyttää sen heti, vähemmän kiireinen 15 odottaa.
`muistiaita` (käskyt `dsb` ja `isb`) varmistaa, että ISPR-kirjoitus
on perillä ja prosessori on ehtinyt reagoida ennen seuraavaa käskyä.

```{.c tiedosto="esimerkit/05-keskeytykset/main.c" osa="vaihe2"}
```

Kolmannessa vaiheessa linjan 14 prioriteetti lasketaan samaksi kuin
linjan 13, eikä se enää keskeytä:

```{.c tiedosto="esimerkit/05-keskeytykset/main.c" osa="vaihe3"}
```

Neljäs vaihe käyttää BASEPRI-rekisteriä. Toisin kuin PRIMASK, joka
peittää kaiken, BASEPRI peittää vain keskeytykset, joiden prioriteetti
on yhtä suuri tai heikompi kuin sen arvo. Nolla tarkoittaa, että mitään
ei peitetä.

```{.c tiedosto="esimerkit/05-keskeytykset/main.c" osa="basepri"}
```

```{.c tiedosto="esimerkit/05-keskeytykset/main.c" osa="vaihe4"}
```

```{.tuloste tiedosto="esimerkit/testit/05-keskeytykset.odotettu"}
```

IPSR on käsittelijässä 16 + linjan numero: linja 13 on poikkeus 29.
Ensimmäisessä vaiheessa ISPR = `0x0000e000` eli bitit 13, 14 ja 15.

BASEPRI on tärkeä työkalu reaaliaikajärjestelmissä. Kriittinen osio,
joka asettaa BASEPRI:n esimerkiksi arvoon 2, estää käyttöjärjestelmän
ja tavallisten laitteiden keskeytykset mutta päästää läpi
kiireellisimmän, esimerkiksi moottorinohjauksen virranmittauksen.
FreeRTOS käyttää juuri tätä: sen asetus
`configMAX_SYSCALL_INTERRUPT_PRIORITY` on BASEPRI:n arvo, eikä
sitä kiireellisemmistä käsittelijöistä saa kutsua käyttöjärjestelmän
funktioita.

## Viive

Cortex-M3 ja -M4 aloittavat käsittelijän ensimmäisen käskyn 12
kellojaksoa keskeytyksen jälkeen, Cortex-M0+ 15:ssä; ketjutettu
siirtymä vie kuusi jaksoa. Alla oleva periaatekuva näyttää kaksi
keskeytystä, joista toinen tulee odottavaksi ensimmäisen käsittelijän
aikana. Prosessori ei palaa pääohjelmaan välillä vaan siirtyy suoraan
toiseen käsittelijään (*tail-chaining*), koska rekisterit ovat jo
pinossa.

```{.ajoituskaavio otsikko="Keskeytyksen viive ja ketjutettu siirtymä (Cortex-M3, periaate)"}
{"signal": [
  {"name": "IRQ A", "wave": "01....0............."},
  {"name": "IRQ B", "wave": "0......1....0......."},
  {"name": "suoritus", "wave": "2.3..4...5.4...3..2.",
   "data": ["main", "pinoaminen", "käsittelijä A", "ketju",
            "käsittelijä B", "palautus", "main"]},
  {"name": "pinossa", "wave": "0..1...........0...."}
], "config": {"hscale": 0.85}}
```

 Luvut pätevät, kun muisti on nollaodotus-
tilainen. Todellista viivettä pidentävät flashin odotustilat,
meneillään oleva monijaksoinen käsky ja ennen kaikkea kriittiset
osiot: jos pääohjelma pitää keskeytyksiä kiellettyinä 50 mikro-
sekuntia, pahin viive on vähintään 50 mikrosekuntia. Siksi
kriittisten osioiden on oltava lyhyitä, ja pitkät käsittelijät
kannattaa ajaa matalalla prioriteetilla.

## Käsittelijän kirjoittaminen

Cortex-M:n käsittelijä on tavallinen `void`-funktio ilman argumentteja.
Erityisiä määreitä, kuten monien muiden arkkitehtuurien
`__attribute__((interrupt))`, ei tarvita, koska laitteisto tallentaa
kutsukonvention mukaiset rekisterit. Käytännöt:

- **Kuittaa syy oheislaitteesta**, mieluiten käsittelijän alussa.
- **Pidä käsittelijä lyhyenä.** Siirrä työ pääohjelmalle lipulla,
  laskurilla tai jonolla (luku 7).
- **Älä odota käsittelijässä.** Pollaus, viiveet ja odottava tulostus
  pidentävät kaikkien vähemmän kiireisten keskeytysten viivettä.
  (Tämän luvun esimerkki tulostaa käsittelijöissä vain näyttääkseen
  järjestyksen.)
- **Tarkista nimi.** Väärin kirjoitettu käsittelijä ei ole
  käännösvirhe, koska heikko alias korvaa sen oletuskäsittelijällä.
- **Kuittauksen on ehdittävä perille.** Jos kuittaus on käsittelijän
  viimeinen kirjoitus ja oheislaite on hitaan väylän takana, käsittelijä
  voi palata ennen kuin linja laskee, ja keskeytys tulee turhaan
  uudelleen. Kuittaus alussa tai lukeminen takaisin estää tämän.

## Järjestelmäkutsu SVC ja prosessipino

Kaksi järjestelmäpoikkeusta on olemassa käyttöjärjestelmää varten.
Bare-metal-ohjelma ei yleensä tarvitse kumpaakaan, mutta ne
kannattaa tuntea, koska ne näyttävät poikkeusmallin kokonaisena ja
koska jokainen reaaliaikakäyttöjärjestelmä on rakennettu niiden
varaan.

PendSV-poikkeusta ei aiheuta mikään laite; ohjelma laukaisee sen
ICSR-rekisterin bitillä, ja sen prioriteetiksi asetetaan heikoin
mahdollinen. Silloin se ajetaan vasta, kun kaikki muut käsittelijät
ovat valmiita. Reaaliaikakäyttöjärjestelmät vaihtavat säiettä
PendSV:ssä juuri tästä syystä (taito *Reaaliaikakäyttöjärjestelmät*).

Käsky `svc #n` aiheuttaa poikkeuksen 11. Sitä käytetään
järjestelmäkutsuna: ei-etuoikeutettu koodi pyytää ydintä tekemään
jotain, mihin sillä itsellään ei ole oikeutta. Argumentit kulkevat
rekistereissä, ja koska prosessori tallentaa ne poikkeuskehykseen
(luku 2), käsittelijä löytää ne pinosta ja voi myös kirjoittaa
paluuarvon kehyksen `r0`:aan.

```{.c tiedosto="esimerkit/05-svc/main.c" osa="kutsu"}
```

Käsittelijän alku on kirjoitettava assemblynä, koska C-funktion
prologi tallentaisi rekistereitä ja siirtäisi pino-osoitinta ennen
kuin ehdimme lukea niitä. Kolme käskyä valitsee EXC_RETURNin bitin 2
perusteella oikean pinon ja siirtyy C-funktioon, jolle kehys ja
EXC_RETURN annetaan argumentteina. SVC-numero ei ole rekisterissä:
se luetaan käskystä itsestään, joka on kaksi tavua ennen
tallennettua paluuosoitetta.

```{.c tiedosto="esimerkit/05-svc/main.c" osa="svc"}
```

Pinon vaihtaminen kesken C-funktion ei onnistu, koska kääntäjä
tallentaa paluuosoitteen funktion alussa yhteen pinoon ja hakisi sen
lopussa toisesta. Siksi siirtymä prosessipinoon (PSP) tehdään pienessä
assembly-funktiossa, joka kutsuu C-funktiota uudessa pinossa ja palaa
vanhaan:

```{.c tiedosto="esimerkit/05-svc/main.c" osa="psp"}
```

Prosessipinossa ajettava funktio luopuu lopuksi etuoikeuksistaan ja
yrittää palauttaa ne itse. Kirjoitus CONTROL-rekisteriin ei-
etuoikeutetusta tilasta jää vaikutuksetta ilman virhettä, joten
etuoikeudet palautetaan järjestelmäkutsulla `svc #2`:

```{.c tiedosto="esimerkit/05-svc/main.c" osa="prosessi"}
```

```{.c tiedosto="esimerkit/05-svc/main.c" osa="main"}
```

Funktio `tila` on sama kuin luvun 2 esimerkissä: se tulostaa IPSR:n ja
CONTROL-rekisterin tulkittuina.

```{.tuloste tiedosto="esimerkit/testit/05-svc.odotettu"}
```

Tulosteesta näkyy koko malli. Käsittelijässä IPSR on 11 ja pino aina
MSP, vaikka toisella ja kolmannella kerralla kehys tallennettiin
PSP:hen: EXC_RETURN on silloin `0xfffffffd` eikä `0xfffffff9`.
Handler-tilassa CONTROL.SPSEL luetaan aina nollana, ja nPRIV ei
vaikuta, koska Handler-tila on aina etuoikeutettu. Kehyksestä luetut
`r0`–`r3` ovat kutsujan argumentit, ja summa palasi kutsujalle
kehyksen kautta.

## Käytännössä

- **Suunnittele prioriteetit kerralla koko järjestelmälle.**
  Taulukko, jossa on jokainen keskeytys, sen prioriteetti, enimmäiskesto
  ja sallittu viive, kuuluu suunnitteluun.
- **Anna tiukimman aikarajan keskeytykselle kiireellisin prioriteetti**,
  ei tärkeimmälle. Tärkeys ja kiireellisyys ovat eri asioita.
- **Käytä BASEPRI:ä PRIMASKin sijaan**, jos piirissä on keskeytyksiä,
  joiden viivettä kriittiset osiot eivät saa pidentää.
- **Laukaise keskeytyksiä ohjelmallisesti testeissä.** ISPR:n tai STIR:n
  kautta käsittelijän voi testata ilman oikeaa laitetapahtumaa.

## Itsearviointi

- Osaat nimetä kolme kohtaa, joissa keskeytys voidaan sallia tai estää,
  ja selittää odottavan ja aktiivisen tilan.
- Osaat ennustaa, missä järjestyksessä odottavat keskeytykset ajetaan
  ja milloin käsittelijä keskeytetään.
- Osaat asettaa NVIC:n prioriteetin oikein, kun piiri toteuttaa vain
  osan prioriteettibiteistä.
- Osaat selittää PRIMASKin ja BASEPRI:n eron ja sen, miksi RTOS käyttää
  BASEPRI:ä.
- Osaat luetella hyvän keskeytyskäsittelijän säännöt ja sen, miksi
  syyn kuittaus on välttämätön.
- Osaat toteuttaa järjestelmäkutsun SVC:llä niin, että argumentit ja
  paluuarvo kulkevat kehyksen kautta, ja selittää, mihin PendSV:tä ja
  prosessipinoa käytetään.
