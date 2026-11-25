# Standardisolut ja Liberty

Standardisolu on valmiiksi suunniteltu ja mitattu logiikkaportti:
invertteri, NAND, kiikku. Kaikki solut ovat yhtä korkeita, joten ne
voidaan asettaa riveihin vierekkäin, ja syöttöjännite ja maa kulkevat
rivien reunoja pitkin. Valmistajan prosessisuunnittelupaketti
(process design kit, PDK) sisältää solujen piirikuviot, simulointimallit
ja ajoitustiedot. Synteesi ja ajoitusanalyysi tarvitsevat vain
ajoitustiedot, jotka ovat Liberty-tiedostossa (`.lib`). Luku avaa ensin
solun sisällön, koska myöhempien lukujen käsitteet (diffuusio,
polypii, metallikerrokset, hilaoksidi) tulevat siitä, ja lukee sitten
kirjaston taulukot.

## Solun sisällä

Standardisolu on muutama transistori. CMOS-invertterissä niitä on
kaksi: PMOS vetää lähdön käyttöjännitteeseen, kun tulo on 0, ja NMOS
maahan, kun tulo on 1. NAND-portissa on kaksi kumpaakin. Kytkennät
ovat tuttuja taidosta *Digitaalitekniikka*; tässä katsotaan, miltä
ne näyttävät piillä.

Transistori on kahden kerroksen risteys. *Diffuusio* on seostettu alue
piin pinnassa, ja sen yli kulkeva *polypii*-johdin on hila. Hilan alla
on muutaman nanometrin paksuinen eriste, *hilaoksidi*. Kun hilalle
tuodaan jännite, sen alle syntyy johtava kanava diffuusioalueiden
välille. NMOS tehdään suoraan p-tyypin alustaan ja PMOS n-tyypin
*kaivoon*. Kontaktit yhdistävät diffuusion ja polypiin ensimmäiseen
metallikerrokseen. Ylemmät metallikerrokset (luku 8) ovat eristeen
erottamia johdinkerroksia, joiden välillä kuljetaan läpivienneillä.

![Invertterisolun pohjakuva ja poikkileikkaus periaatepiirroksena.
Syöttökiskot VDD ja VSS kulkevat solun ylä- ja alareunassa, joten
riviin asetetut solut kytkeytyvät niihin
itsestään.](kuvat/solu.png){width=92%}

PMOS on piirretty leveämmäksi, koska aukot kulkevat piissä hitaammin
kuin elektronit: sama virta vaatii leveämmän transistorin. Solun
korkeus on kirjaston vakio, ja leveys kasvaa transistorien määrän ja
koon mukaan. Vahvempi solu (`_X2`, `_X4`) on sama kytkentä leveämmillä
tai rinnakkaisilla transistoreilla. Piirikuvion säännöt ja tarkistus
ovat luvussa 10.

## Solun kuvaus

Liberty kertoo jokaisesta solusta pinta-alan, vuotovirran ja pinnit.
Tulopinnin kapasitanssi kuormittaa edellistä asetta; lähtöpinnin
`function` kertoo logiikan, jonka synteesi tunnistaa:

```{.text tiedosto="esimerkit/opetus.lib" osa="nand2"}
```

Ajoitus kuvataan kaarina (timing arc) tulosta lähtöön. NAND on
`negative_unate`: nouseva tulo voi aiheuttaa vain laskevan lähdön.
Jokaisella kaarella on neljä taulukkoa: viive ja lähdön siirtymäaika
erikseen nousevalle ja laskevalle lähdölle:

```{.text tiedosto="esimerkit/opetus.lib" osa="kaari"}
```

## NLDM-taulukot

Taulukot ovat ei-lineaarisia viivemalleja (non-linear delay model,
NLDM). Rivit ovat tulon siirtymäaikoja (slew, ns) ja sarakkeet lähdön
kuormia (pF), kuten kirjaston taulukkomallissa määritellään. Väliarvot
interpoloidaan bilineaarisesti ja taulukon ulkopuoliset ekstrapoloidaan
reunimmaisista väleistä:

```{.python tiedosto="esimerkit/liberty.py" osa="nldm"}
```

Jäsennin lukee kirjaston ryhminä, jotka ovat Libertyn perusrakenne:

```{.python tiedosto="esimerkit/liberty.py" osa="ryhma"}
```

```{.python tiedosto="esimerkit/liberty.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/liberty.odotettu"}
```

Viive kasvaa sekä hitaasta tulosta että suuresta kuormasta. Siksi
viiveet eivät ole solun ominaisuuksia vaan riippuvat ympäristöstä:
ajoitusanalyysi laskee jokaisen johtimen kuorman ja kuljettaa
siirtymäajat portista toiseen (luku 4).

## Viive on RC-ilmiö

Taulukon takana on yksinkertainen fysiikka. Johtava transistori on
likimain vastus, ja lähdön näkemä kuorma eli seuraavien hilojen ja
johtimen kapasitanssi varataan tai puretaan sen läpi. Lähtö ylittää
puolivälin ajassa $0{,}69 \cdot RC$, joten viive on

$$t = t_0 + 0{,}69 \cdot R \cdot C_{kuorma},$$

missä $t_0$ on solun sisäinen viive. Taulukon kulmakerroin kuorman
suhteen kertoo siis transistorin vastuksen:

```{.python tiedosto="esimerkit/02-rc.py" osa="sovitus"}
```

```{.python tiedosto="esimerkit/02-rc.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/02-rc.odotettu"}
```

Ylösveto on heikompi kuin alasveto, vaikka PMOS on leveämpi.
BUF_X4:n lähtöasteen vastus on neljäsosa, mutta solu on kaksi kertaa
suurempi ja sen tulo kuormittaa edeltäjää yli kaksi kertaa enemmän.
Opetuskirjaston taulukot ovat kuorman suhteen suoria, joten malli osuu
niihin tarkasti. Oikean kirjaston taulukot kaareutuvat, koska
transistori ei ole vakiovastus ja tulon siirtymäaika vaikuttaa; siksi
kirjasto on taulukko eikä kaava. Sama RC-ajattelu palaa johtimissa:
kellopuussa (luku 8) ja parasiittien poiminnassa (luku 10).

## Kiikun rajoitteet

Kiikulla on kaaren lisäksi rajoitteita: asetusaika (`setup_rising`) ja
pitoaika (`hold_rising`) suhteessa kellon nousevaan reunaan. Nekin ovat
taulukoita, joiden indeksit ovat kellon ja datan siirtymäajat. Ryhmä
`ff` kertoo synteesille, että solu on kiikku, ja `next_state` sen
toiminnan:

```{.text tiedosto="esimerkit/opetus.lib" osa="dff"}
```

Negatiivinen pitoaika (taulukon oikea yläkulma) on mahdollinen: hidas
data saa muuttua jo hieman ennen kellon reunaa, koska kiikun sisäinen
viive pitää vanhan arvon.

## Ajurin koko

Samasta funktiosta on yleensä useita vahvuuksia (`_X1`, `_X2`, `_X4`).
Vahvempi solu on suurempi ja kuormittaa omaa ajuriaan enemmän, mutta
sen lähtöresistanssi on pienempi:

```{.python tiedosto="esimerkit/02-ajurit.py" osa="viive"}
```

```{.python tiedosto="esimerkit/02-ajurit.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/02-ajurit.odotettu"}
```

![Vasemmalla viive kuorman funktiona kolmella ajurilla: INV_X1 on
nopein noin 13 fF:n kuormaan asti, sen jälkeen BUF_X4. Oikealla
INV_X1:n `cell_rise`-taulukko käyräparvena; pisteet ovat taulukon
arvot ja viivat interpolointia.](kuvat/ajurit.png){width=92%}

Heikko invertteri on nopeampi pienellä kuormalla, koska sen sisäinen
viive on pienempi. Haarautuman kasvaessa sen viive ja lähdön
siirtymäaika kasvavat jyrkästi, ja hidas siirtymä hidastaa myös
seuraavaa porttia. Synteesi ja sijoittelun jälkeinen optimointi
vaihtavat solujen kokoja (gate sizing) ja lisäävät puskureita juuri
tämän takia.

## Käytännössä

- **Kirjasto määrää tuloksen.** Sama RTL tuottaa eri prosesseissa
  täysin eri taajuuden ja pinta-alan. Arkkitehtuurin arviot tehdään
  kohdeprosessin kirjastolla, ei FPGA-tuloksista.
- **Kulmat ovat eri tiedostoja.** PDK:ssa on kirjasto jokaiselle
  prosessin, jännitteen ja lämpötilan yhdistelmälle (PVT-kulma, luku
  5). Kirjaston nimi kertoo kulman, esim. `ss_100C_1v60`.
- **Taulukon ulkopuolella ollaan arvailun varassa.** Ekstrapoloitu
  viive on epätarkka. Kirjaston `max_capacitance` ja
  `max_transition` ovat suunnittelusääntöjä, joiden rikkominen on
  virhe, ei varoitus.
- **Tarkemmat mallit.** Pienemmissä prosesseissa NLDM ei riitä, ja
  kirjastot sisältävät virtapohjaisia malleja (CCS, ECSM). Periaate
  on sama: taulukoista luetaan solun käyttäytyminen sen ympäristössä.

## Itsearviointi

- Osaat nimetä invertterisolun pohjakuvasta ja poikkileikkauksesta
  diffuusion, polypiin, hilaoksidin, kaivon, kontaktit ja syöttökiskot.
- Osaat lukea Liberty-tiedostosta solun pinta-alan, pinnien
  kapasitanssit ja ajoituskaaret.
- Osaat arvioida solun viiveen RC-mallilla ja selittää, mistä
  NLDM-taulukon kulmakerroin kuorman suhteen tulee.
- Osaat interpoloida viiveen NLDM-taulukosta siirtymäajan ja kuorman
  funktiona.
- Osaat selittää, miksi solun viive riippuu ympäristöstä eikä ole
  vakio.
- Osaat perustella, milloin heikko ajuri on parempi ja milloin vahva.
