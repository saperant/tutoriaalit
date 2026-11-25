# Tilakoneet

Tilakone (finite state machine, FSM) on rekisteri, joka muistaa tilan,
ja kombinaatiologiikka, joka laskee seuraavan tilan ja lähdöt. Sillä
toteutetaan protokollat, ohjausyksiköt ja kaikki, mikä etenee
vaiheittain. Tässä luvussa tilakone suunnitellaan alusta loppuun:
tilakaaviosta tilasiirtotauluun, tauluista logiikaksi ja lopuksi
SystemVerilogiksi.

## Moore ja Mealy

Tilakoneen lähdöt voivat riippua kahdella tavalla:

- **Moore-kone:** lähtö riippuu vain tilasta. Lähtö muuttuu vain
  kellon reunalla, joten se on vakaa ja hasarditon, jos tila on
  koodattu sopivasti.
- **Mealy-kone:** lähtö riippuu tilasta ja nykyisestä syötteestä.
  Lähtö reagoi syötteeseen samassa jaksossa, ja koneessa tarvitaan
  usein vähemmän tiloja, mutta syötteen piikit näkyvät lähdössä.

Esimerkkinä on sekvenssintunnistin, joka ilmoittaa, kun syötteessä on
nähty bitit 101 (päällekkäiset osumat sallitaan: 10101 sisältää kaksi
osumaa).

## Tilakaaviosta tauluksi

Mooren koneessa tarvitaan neljä tilaa: S0 (ei mitään), S1 (nähty 1),
S2 (nähty 10) ja S3 (nähty 101, lähtö 1). Mealyn koneessa riittää
kolme, koska viimeinen 1 tuottaa lähdön suoraan siirtymällä.

```{.dot otsikko="Mooren kone: lähtö on tilan ominaisuus (S3/1)"}
digraph {
  rankdir=LR; nodesep=0.3;
  start [shape=point, width=0.08, style=filled, fillcolor="#1F2A2E"];
  S0 [label="S0/0", shape=circle, width=0.7, fixedsize=true];
  S1 [label="S1/0", shape=circle, width=0.7, fixedsize=true];
  S2 [label="S2/0", shape=circle, width=0.7, fixedsize=true];
  S3 [label="S3/1", shape=doublecircle, width=0.7, fixedsize=true];
  start -> S0;
  S0 -> S0 [label="0"]; S0 -> S1 [label="1"];
  S1 -> S1 [label="1"]; S1 -> S2 [label="0"];
  S2 -> S3 [label="1"]; S2 -> S0 [label="0"];
  S3 -> S1 [label="1"]; S3 -> S2 [label="0"];
}
```

```{.dot otsikko="Mealyn kone: lähtö on siirtymän ominaisuus (syöte/lähtö)"}
digraph {
  rankdir=LR; nodesep=0.3;
  start [shape=point, width=0.08, style=filled, fillcolor="#1F2A2E"];
  A [shape=circle, width=0.55, fixedsize=true];
  B [shape=circle, width=0.55, fixedsize=true];
  C [shape=circle, width=0.55, fixedsize=true];
  start -> A;
  A -> A [label="0/0"]; A -> B [label="1/0"];
  B -> B [label="1/0"]; B -> C [label="0/0"];
  C -> B [label="1/1"]; C -> A [label="0/0"];
}
```

Tilakaavio kirjoitetaan tauluksi, josta jokainen siirtymä näkyy:

```{.python tiedosto="esimerkit/10-tilakone.py" osa="taulut"}
```

Taulu on tilakoneen täydellinen määrittely. Siitä voidaan tarkistaa,
että jokaisesta tilasta on siirtymä jokaisella syötteellä, ja se
toimii viitemallina testauksessa.

## Taulusta logiikaksi

Tilat koodataan biteiksi. Neljä tilaa tarvitsee kaksi bittiä
$q_1 q_0$. Seuraavan tilan bitit $d_1$ ja $d_0$ ovat funktioita
nykyisestä tilasta ja syötteestä, ja ne sievennetään luvun 4
Quine–McCluskeyllä:

```{.python tiedosto="esimerkit/10-tilakone.py" osa="koodaus"}
```

```{.python tiedosto="esimerkit/10-tilakone.py" osa="yhtalot"}
```

Toteutusta verrataan tauluun kaikilla kahdeksalla rivillä:

```{.python tiedosto="esimerkit/10-tilakone.py" osa="tarkistus"}
```

Lopuksi molemmat koneet ajetaan samalla syötteellä. Yksi silmukan
kierros on yksi kellojakso: lähtö luetaan ennen reunaa, ja tila
päivittyy reunalla.

```{.python tiedosto="esimerkit/10-tilakone.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/10-tilakone.odotettu"}
```

Mealy-kone ilmoittaa osumasta samassa jaksossa, jossa viimeinen 1
saapuu. Moore-kone ilmoittaa seuraavassa jaksossa, koska sen täytyy
ensin siirtyä tilaan S3. Tämä yhden jakson ero on Mooren hinta
vakaasta lähdöstä.

Tilakoodauksen valinta vaikuttaa logiikan kokoon. Tässä $d_0 = x$
tuli ilmaiseksi, koska tilat S1 ja S3 (joihin päädytään ykkösellä)
koodattiin niin, että alin bitti on 1. *One-hot*-koodauksessa
jokaisella tilalla on oma kiikkunsa: kiikkuja on enemmän, mutta
seuraavan tilan logiikka on yksinkertaista ja nopeaa.

## SystemVerilogilla

RTL-kuvauksessa tilat nimetään luettelotyypillä, ja koodauksen saa
valita synteesityökalu. Tilarekisteri ja seuraavan tilan logiikka
kirjoitetaan erikseen:

```{.systemverilog tiedosto="esimerkit/10-tunnistin.sv" osa="moore"}
```

```{.systemverilog tiedosto="esimerkit/10-tunnistin.sv" osa="mealy"}
```

```{.systemverilog tiedosto="esimerkit/10-tunnistin.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/10-tunnistin.odotettu"}
```

Sama ero näkyy simulaation aaltomuodossa alla. Mealy-lähtö nousee
jaksossa, jossa syötteen viimeinen 1 on linjalla, ja Moore-lähtö vasta
seuraavassa jaksossa, kun tila on päivittynyt.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/10-tunnistin.json" otsikko="Sekvenssin 101 tunnistus: Mealy-lähtö jaksoa Moore-lähtöä aikaisemmin"}
```

Laitteisto käyttäytyy täsmälleen kuten Python-malli. Testipenkki
asettaa syötteen heti reunan jälkeen ja lukee lähdöt juuri ennen
seuraavaa reunaa: näin Mealy-lähtö näkyy samassa jaksossa.

## Käytännössä

- **Taulu ensin, koodi sitten.** Tilakone suunnitellaan kaaviona tai
  tauluna ennen koodausta. Taulu on myös testipenkin viitemalli.
- **Kaksi lohkoa.** Tilarekisteri `always_ff`-lohkossa ja seuraavan
  tilan logiikka `always_comb`-lohkossa on luettava ja yleinen tyyli
  (taito *RTL-suunnittelu SystemVerilogilla*).
- **Moore lähtöihin, joita muut kellottavat.** Kun lähtö menee toiseen
  lohkoon tai piirin ulkopuolelle, Moore-lähtö (tai rekisteröity
  Mealy-lähtö) on turvallisempi, koska syötteen piikit eivät näy.
- **Kaikki tilat käsitellään.** Laittomasta tilasta (esimerkiksi
  säteilyn kääntämä bitti) palataan tunnettuun tilaan
  `default`-haaralla. Turvallisuuskriittisissä piireissä tämä on
  vaatimus.

## Itsearviointi

- Osaat selittää Moore- ja Mealy-koneen eron ja yhden jakson
  viive-eron.
- Osaat muuttaa tilakaavion tilasiirtotauluksi, koodata tilat ja johtaa
  seuraavan tilan logiikan.
- Osaat kertoa, miten tilakoodaus (binääri, one-hot) vaikuttaa
  logiikkaan ja kiikkujen määrään.
- Osaat kirjoittaa tilakoneen SystemVerilogilla kahtena lohkona ja
  testata sen viitemallia vastaan.
