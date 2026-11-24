# Rekisterit ja laskurit

Rekisteri on joukko kiikkuja, joilla on yhteinen kello. Synkroninen
piiri on rekistereitä ja niiden välistä kombinaatiologiikkaa: jokainen
kellon reuna tallentaa logiikan laskeman seuraavan tilan. Tämä luku
näyttää tavallisimmat rekisterirakenteet.

## Synkroninen suunnittelu

Synkronisen suunnittelun säännöt ovat yksinkertaiset:

1. Kaikki kiikut käyttävät samaa kelloa ja samaa reunaa.
2. Kiikkujen välissä on vain kombinaatiologiikkaa, ei silmukoita
   ilman kiikkua.
3. Kellojakso on pidempi kuin pisin logiikkapolku (luku 11).

Kun säännöt pätevät, piirin toimintaa voi tarkastella jakso kerrallaan:
tila $s_{k+1} = f(s_k, x_k)$. Välitilat, hasardit ja viiveet eivät näy.
Kaikki tämän luvun rakenteet noudattavat sääntöjä.

## Rekisteri, jolla on sallinta ja nollaus

Kiikku näytteistää jokaisella reunalla. Jotta rekisteri voi myös
*pitää* arvonsa, sen eteen laitetaan multiplekseri, joka valitsee
uuden arvon tai vanhan (*sallinta*, enable). Nollaus on samanlainen
multiplekseri, joka valitsee nollan.

```{.systemverilog tiedosto="esimerkit/09-laskurit.sv" osa="laskuri"}
```

Laskuri on rekisteri, jonka seuraava arvo on nykyinen + 1. Summain on
yksinkertaistettu: lisättävä on vakio, joten synteesi tekee siitä
inkrementoijan, jossa on vain puolisummaimia.

Nollaus on tässä *synkroninen*: se tapahtuu kellon reunalla kuten mikä
tahansa muu arvo. *Asynkroninen* nollaus vaikuttaa heti kellosta
riippumatta. Kummallakin on paikkansa; valinta ja turvallinen
vapautus käsitellään taidossa *RTL-suunnittelu*.

## Siirtorekisteri

Siirtorekisterissä jokainen kiikku ottaa arvon edelliseltä. Sarjamuotoinen
bittivirta muuttuu rinnakkaismuotoiseksi (ja toisinpäin), mikä on
sarjaväylien (UART, SPI, I2C) ja serdes-lähetinvastaanottimien perusta:

```{.systemverilog tiedosto="esimerkit/09-laskurit.sv" osa="siirto"}
```

## Rengas- ja Johnson-laskuri

Rengaslaskuri kiertää yhtä ykköstä. Sen tila on valmiiksi one-hot, joten
dekoodausta ei tarvita: jokainen bitti ohjaa suoraan yhtä vaihetta.
Johnson-laskuri kiertää käännetyn MSB:n ja käy läpi $2N$ tilaa $N$
kiikulla. Sen peräkkäiset tilat eroavat yhdessä bitissä kuten
Gray-koodi.

```{.systemverilog tiedosto="esimerkit/09-laskurit.sv" osa="rengas"}
```

```{.systemverilog tiedosto="esimerkit/09-laskurit.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/09-laskurit.odotettu"}
```

| Laskuri | Tiloja N kiikulla | Dekoodaus | Käyttö |
|---------|-------------------|-----------|--------|
| Binääri | $2^N$ | tarvitaan | osoitteet, ajastimet |
| Rengas | $N$ | ei tarvita | vaiheiden ohjaus |
| Johnson | $2N$ | kaksi bittiä per tila | vaihesiirretyt kellot |
| Gray | $2^N$ | tarvitaan | toiselle kellolle luettava osoitin |

## Asynkroninen laskuri

Vanhoissa piireissä laskuri tehtiin kytkemällä jokaisen kiikun lähtö
seuraavan kiikun kelloon (*ripple counter*). Se tarvitsee vähemmän
logiikkaa, mutta jokainen bitti muuttuu eri aikaan, ja välitilat
näkyvät lähdössä: laskettaessa 0111 → 1000 lähtö voi hetken olla 0110,
0100 ja 0000. Lisäksi jokainen bitti on oma kellotusalueensa. Nykyään
asynkronista laskuria käytetään lähinnä kellonjakajissa piirin
kellogeneraattorin sisällä.

## Käytännössä

- **Yksi kello, sallinta hitaaseen toimintaan.** Kun jokin tapahtuu
  harvemmin kuin joka jakso, käytetään sallintaa, ei jaettua kelloa.
  Jaettu kello on uusi kellotusalue ja tuo kaikki sen ongelmat.
- **One-hot tilaan, binääri tallennukseen.** One-hot-tila on nopea
  dekoodata ja FPGA:ssa usein pienin. Laskurit ja suuret tilat ovat
  binäärisiä.
- **Kaikki nollattavat rekisterit nollataan samalla tavalla.**
  Sekoitus synkronista ja asynkronista nollausta samassa lohkossa on
  yleinen virhelähde.
- **Älä käytä kiikun lähtöä kellona.** Asynkroninen laskuri ja
  "jaetut kellot" kuuluvat kellogeneraattoriin, eivät logiikkaan.

## Itsearviointi

- Osaat luetella synkronisen suunnittelun säännöt ja kertoa, mitä ne
  takaavat.
- Osaat toteuttaa rekisterin, jolla on sallinta ja synkroninen nollaus,
  ja selittää sen multiplekserinä.
- Osaat rakentaa siirtorekisterin sekä binääri-, rengas- ja
  Johnson-laskurin ja vertailla niitä.
- Osaat kertoa, miksi asynkronista laskuria ei käytetä logiikassa.
