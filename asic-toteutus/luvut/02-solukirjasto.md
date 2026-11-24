# Standardisolut ja Liberty

Standardisolu on valmiiksi suunniteltu ja mitattu logiikkaportti:
invertteri, NAND, kiikku. Kaikki solut ovat yhtä korkeita, joten ne
voidaan asettaa riveihin vierekkäin, ja syöttöjännite ja maa kulkevat
rivien reunoja pitkin. Valmistajan prosessisuunnittelupaketti
(process design kit, PDK) sisältää solujen piirikuviot, simulointimallit
ja ajoitustiedot. Synteesi ja ajoitusanalyysi tarvitsevat vain
ajoitustiedot, jotka ovat Liberty-tiedostossa (`.lib`).

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

- Osaat lukea Liberty-tiedostosta solun pinta-alan, pinnien
  kapasitanssit ja ajoituskaaret.
- Osaat interpoloida viiveen NLDM-taulukosta siirtymäajan ja kuorman
  funktiona.
- Osaat selittää, miksi solun viive riippuu ympäristöstä eikä ole
  vakio.
- Osaat perustella, milloin heikko ajuri on parempi ja milloin vahva.
