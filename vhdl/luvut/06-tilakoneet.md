# Tilakoneet

Tilakone on ohjauslogiikan perusrakenne: protokollat, kättelyt,
sekvenssit ja virhetilanteiden käsittely. VHDL:n luettelotyypit
sopivat tilakoneille erityisen hyvin, koska tilat ovat nimiä,
kääntäjä tarkistaa `case`-lauseen kattavuuden ja synteesi valitsee
koodauksen. Tilakoneiden suunnittelu yleisesti (Moore ja Mealy,
tilakaaviot, lähtöjen rekisteröinti) on taidoissa *Digitaalitekniikka*
ja *RTL-suunnittelu SystemVerilogilla*; tässä keskitytään
VHDL-toteutukseen.

## Tila luettelotyyppinä

```{.vhdl tiedosto="esimerkit/06-uart-rx/sarjavastaanotin.vhd" osa="tila"}
```

Tilan bittikoodausta ei kirjoiteta. Synteesityökalu tunnistaa
tilakoneen ja valitsee koodauksen, FPGA:ssa yleensä *one-hot*
(yksi kiikku tilaa kohden) ja ASIC-piirissä binäärisen tai
Gray-koodauksen. Koodauksen voi pakottaa työkalukohtaisella
attribuutilla, kuten Vivadon `fsm_encoding` tai Synplifyn
`syn_encoding`. Simulaattori ja aaltomuotojen katselin näyttävät
tilan nimenä, mikä helpottaa virheiden etsintää.

## Esimerkki: UART-vastaanotin

UART-kehys alkaa aloitusbitillä 0, jota seuraa kahdeksan databittiä
vähiten merkitsevä ensin ja lopetusbitti 1. Vastaanotin odottaa
aloitusbitin reunaa, siirtyy bitin puoliväliin ja näytteistää sen
jälkeen bitin keskeltä bittiajan välein:

```{.vhdl tiedosto="esimerkit/06-uart-rx/sarjavastaanotin.vhd" osa="entiteetti"}
```

```{.vhdl tiedosto="esimerkit/06-uart-rx/sarjavastaanotin.vhd" osa="prosessi"}
```

Tilakaavio tiivistää prosessin. Jokaisessa tilassa ajastin laskee
nollaan, ja siirtymä tapahtuu vasta sitten (paitsi lepotilasta, joka
reagoi heti aloitusbitin reunaan).

```{.dot otsikko="UART-vastaanottimen tilakone"}
digraph {
  rankdir=LR; nodesep=0.4;
  LEPO [shape=circle, width=0.95, fixedsize=true];
  ALOITUS [shape=circle, width=0.95, fixedsize=true];
  DATA [shape=circle, width=0.95, fixedsize=true];
  LOPETUS [shape=circle, width=0.95, fixedsize=true];
  LEPO -> ALOITUS [label="rx = 0"];
  ALOITUS -> DATA [label="puoliväli,\nrx = 0"];
  ALOITUS -> LEPO [label="puoliväli, rx = 1\n(häiriöpiikki)"];
  DATA -> DATA [label="bittiaika,\nbitti < 7"];
  DATA -> LOPETUS [label="bittiaika,\nbitti = 7"];
  LOPETUS -> LEPO [label="bittiaika: valmis\ntai kehysvirhe"];
}
```

Tilakone on kirjoitettu *yhden prosessin* tyyliin: tilasiirtymät ja
lähdöt ovat samassa kellotetussa prosessissa, ja kaikki lähdöt ovat
rekistereitä. Rakenteen yksityiskohdat:

- **Pulssien oletusarvot.** `valmis` ja `kehysvirhe` nollataan
  jokaisella jaksolla ja nostetaan vain sillä jaksolla, jolla tapahtuma
  sattuu. Ne ovat siis tarkalleen yhden jakson pulsseja.
- **Ajastin tilan sisällä.** Bittiajan laskuri on rajattu
  kokonaisluku, joka ladataan tilasiirtymässä ja lasketaan nollaan.
  Generic `KELLOJA_BITTIIN` asettaa bittiajan, joten sama lohko toimii
  millä tahansa kellotaajuuden ja nopeuden yhdistelmällä.
- **Häiriöpiikin hylkäys.** Tila `ALOITUS` tarkistaa aloitusbitin
  vielä sen puolivälissä. Lyhyt häiriö linjalla palauttaa koneen lepoon
  eikä tuota väärää tavua.
- **Virhetila on lähtö.** Rikottu kehys raportoidaan, eikä sitä
  hiljaa hylätä. Ylempi taso päättää, mitä virheelle tehdään.

Testipenkissä lähettäjän malli on proseduuri, joka kirjoittaa kehyksen
bitti kerrallaan. Valinnainen parametri `lopetus` tekee rikotun
kehyksen. Erillinen seurantaprosessi tulostaa vastaanotetut tavut ja
virheet aikaleimoineen:

```{.vhdl tiedosto="esimerkit/06-uart-rx/testipenkki.vhd" osa="lahetys"}
```

```{.tuloste tiedosto="esimerkit/06-uart-rx.odotettu"}
```

Testipenkki käyttää 16 kellojakson bittiaikaa, jotta simulointi on
nopea. Oikeassa käytössä arvo on esimerkiksi 868 (100 MHz, 115 200
bit/s). Lohkon tulo `rx` oletetaan tahdistetuksi; ylempi taso lisää
tahdistimen (luku 5).

## Yksi vai kaksi prosessia

Toinen yleinen tyyli on *kahden prosessin* tilakone: kombinaatioprosessi
laskee seuraavan tilan ja lähdöt, ja kellotettu prosessi vain
rekisteröi tilan.

| | Yksi prosessi | Kaksi prosessia |
|-|---------------|-----------------|
| Lähdöt | rekisteröityjä, jakson viive | kombinaatiollisia, ei viivettä |
| Salpojen vaara | ei | on, jos oletussijoitus unohtuu |
| Luettavuus | kaikki yhdessä paikassa | seuraava tila erikseen nähtävissä |
| Mealy-lähdöt | hankalia | luontevia |

Yhden prosessin tyyli on hyvä oletus: rekisteröidyt lähdöt eivät
välkehdi, ne katkaisevat ajoituspolut ja salpoja ei synny. Kahden
prosessin tyyliä käytetään, kun lähdön on reagoitava tuloon samalla
jaksolla, esimerkiksi virtauksenohjauksen `valmis`-signaalissa.
Mooren lähdön voi myös laskea tilasta rinnakkaisella sijoituksella,
kuten seuraavan esimerkin `pyynto` ja `siirto`.

## Kattavuus ja uudet tilat

VHDL vaatii, että `case` kattaa kaikki valitsimen arvot. Kun
luettelotyyppiin lisätään tila, jokainen `case`, joka ei sitä
käsittele, lakkaa kääntymästä:

```{.vhdl tiedosto="esimerkit/06-kattavuus.ei-kaanny.vhd" osa="tilat"}
```

GHDL ilmoittaa `no choice for TAUKO`. Korjattu malli toimii:

```{.tuloste tiedosto="esimerkit/06-kattavuus.odotettu"}
```

Tarkistus toimii vain, jos `case`-lauseessa ei ole `when others`
-haaraa: `others` hyväksyy uuden tilan hiljaa. Luettelotyypin tilat
kannattaa siksi luetella kaikki.

## Turvallinen tilakone

Luettelotyypillä ei ole laittomia arvoja simuloinnissa, mutta
laitteistossa on: säteily tai häiriö voi kääntää one-hot-koodatun
tilarekisterin bitin, jolloin kone on tilassa, jota ei ole olemassa, ja
voi jäädä siihen pysyvästi. Kun toimintavarmuus on vaatimus (ilmailu,
avaruus, turvallisuuskriittiset järjestelmät), synteesityökalulle
kerrotaan attribuutilla, että tilakone on toteutettava turvallisena
(esim. Vivadon `fsm_safe_state`). Työkalu lisää palautuksen nollatilaan
tai virheenkorjaavan koodauksen. VHDL-koodin `when others` ei yksin
riitä, koska synteesi poistaa sen saavuttamattomana.

## Käytännössä

- **Tila luettelotyyppinä, koodaus työkalulle.** Nimetyt tilat
  näkyvät aaltomuodoissa, ja kääntäjä tarkistaa kattavuuden. Bittikoodaus
  kirjoitetaan käsin vain, jos tila on rajapinnassa tai rekisterissä,
  jonka ohjelmisto lukee.
- **Yhden prosessin tilakone oletuksena.** Lähdöt rekisteröidään, ja
  pulssien oletusarvot asetetaan prosessin alussa.
- **Ajastimet ja laskurit tilakoneen viereen.** Bittiajan tai
  aikakatkaisun laskuri on rajattu kokonaisluku, jonka tilasiirtymä
  lataa. Ajat ovat generic-parametreja tai vakioita, eivät maagisia
  lukuja.
- **Virheet ovat tiloja tai lähtöjä.** Protokollavirhe, aikakatkaisu ja
  odottamaton syöte käsitellään ja raportoidaan, eikä niiden oleteta
  olevan mahdottomia.
- **Testaa virhepolut.** Testipenkki tuottaa myös rikotut kehykset,
  häiriöpiikit ja aikakatkaisut, ei pelkkää onnistunutta tapausta.

## Itsearviointi

- Osaat toteuttaa tilakoneen luettelotyypillä ja yhden prosessin
  tyylillä niin, että lähdöt ovat rekistereitä.
- Osaat kertoa, milloin kahden prosessin tyyli on tarpeen ja mitä
  sen kanssa on varottava.
- Osaat kertoa, miksi `when others` luettelotyypin `case`-lauseessa
  heikentää kääntäjän tarkistusta.
- Osaat kirjoittaa testipenkkiin protokollan lähettäjän proseduurina.
