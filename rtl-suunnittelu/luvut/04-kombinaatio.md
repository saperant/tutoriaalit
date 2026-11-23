# Kombinaatiologiikka

Kombinaatiologiikan ulostulo riippuu vain sen nykyisistä syötteistä:
siinä ei ole muistia eikä kelloa. Se kuvataan joko jatkuvilla
sijoituksilla (`assign`) tai `always_comb`-lohkolla. Tämän luvun
tärkein sääntö on lyhyt: *jokaisen `always_comb`-lohkossa sijoitetun
signaalin on saatava arvo jokaisella suorituspolulla.* Muuten syntyy
salpa.

## assign ja always_comb

Yksinkertainen lauseke kirjoitetaan `assign`-lauseena. Kun logiikassa on
ehtoja, välimuuttujia tai useita ulostuloja, `always_comb` on
luettavampi. Lohko näyttää peräkkäiseltä ohjelmalta, mutta kuvaa
rinnakkaista logiikkaa. Simulaattori suorittaa sen aina, kun jokin sen
lukemista signaaleista muuttuu, ja synteesi muuttaa sen
porttiverkoksi, jolla on sama käyttäytyminen.

`always_comb` korvaa Verilogin `always @*`-lohkon ja tekee kolme asiaa
paremmin:

- herkkyyslista muodostuu automaattisesti, myös kutsuttujen funktioiden
  lukemista signaaleista
- lohko suoritetaan kerran simuloinnin alussa, joten ulostulot saavat
  arvon heti
- työkalu tarkistaa, ettei samaa signaalia sijoiteta muualla ja että
  lohkosta ei synny salpaa.

Lohkossa käytetään *estävää* sijoitusta `=`: arvo päivittyy heti, ja
seuraava rivi näkee uuden arvon. Se vastaa signaalin kulkua portista
toiseen.

## Ehdot ja case

`if`–`else` tuottaa prioriteettiketjun: ensimmäinen tosi ehto voittaa.
`case` valitsee yhden haaran lausekkeen arvon perusteella, ja kun haarat
sulkevat toisensa pois, synteesi tekee siitä rinnakkaisen
multiplekserin. SystemVerilogissa on kaksi määrettä, jotka kertovat
suunnittelijan aikeen:

| Määre | Lupaus | Simulaattori tarkistaa |
|-------|--------|------------------------|
| `unique case` | täsmälleen yksi haara osuu | ei osumaa tai useita osumia |
| `priority case` | ainakin yksi haara osuu, järjestys ratkaisee | ei osumaa |
| (ei määrettä) | – | – |

`unique` sallii synteesin olettaa, että haarat ovat toisensa
poissulkevia, ja jättää prioriteettilogiikan pois. Lupaus on
tarkistettava simuloinnissa. Jos lupaus ei pidä, simuloinnin ja
synteesin tulokset eroavat. Verilator tarkistaa lisäksi jo käännöksessä,
että `case`-lause kattaa kaikki arvot.

Seuraava ALU käyttää luettelotyyppiä operaatiokoodina. Koska
`unique case` kattaa kaikki kahdeksan arvoa, `default`-haaraa ei tarvita.

```{.systemverilog tiedosto="esimerkit/04-alu.sv" osa="alu"}
```

Etumerkillinen ylivuoto tunnistetaan etumerkkibiteistä: kahden
samanmerkkisen luvun summa ei saa vaihtaa merkkiä. Sama yhteenlaskin
toimii sekä etumerkillisille että etumerkittömille luvuille, ja vain
liput tulkitaan eri tavalla. Muuttuva siirto `a << b[SW-1:0]` tuottaa
siirtoverkon, jossa on `log2(W)` multiplekseritasoa.

Testipenkki käyttää tehtävää (`task`) toistuvaan koerakenteeseen:

```{.systemverilog tiedosto="esimerkit/04-alu.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/04-alu.odotettu"}
```

## Silmukat purkautuvat

`for`-silmukka `always_comb`-lohkossa ei ole aikaa kuluttava silmukka,
vaan käännösaikainen toisto. Synteesi purkaa sen, ja jokainen kierros
tuottaa oman logiikkansa. Rajojen on oltava vakioita. Silmukka sopii
esimerkiksi prioriteettienkooderiin, jossa korkein aktiivinen pyyntö
voittaa:

```{.systemverilog tiedosto="esimerkit/04-prioriteetti.sv" osa="enkooderi"}
```

Myöhemmät kierrokset ohittavat aiemmat sijoitukset, joten korkein
indeksi voittaa. Tuloksena on N-tasoinen prioriteettiketju.
Testipenkki vertaa kaikkia 256 syötettä eri tavalla kirjoitettuun
viitemalliin:

```{.tuloste tiedosto="esimerkit/04-prioriteetti.odotettu"}
```

## Salpa: puuttuva sijoitus

Jos `always_comb`-lohkon jollakin polulla signaali jää sijoittamatta,
sen on säilytettävä edellinen arvonsa. Muistava kombinaatiologiikka on
*salpa* (latch). Se on lähes aina virhe: salpa on herkkä
ajoitusongelmille, ajoitusanalyysi ei käsittele sitä hyvin, eikä
FPGA:ssa ole sille luontevaa rakennetta. Verilator tunnistaa salvan
`LATCH`-varoituksella:

```{.systemverilog tiedosto="esimerkit/04-salpa.ei-kaanny.sv"}
```

```{.tuloste tiedosto="esimerkit/04-salpa.odotettu"}
```

Korjauksia on kaksi: jokaiseen `if`-lauseeseen `else`-haara ja jokaiseen
`case`-lauseeseen `default`, tai oletussijoitukset lohkon alkuun.
Jälkimmäinen on luotettavampi, koska se toimii myös, kun lohkoon
lisätään myöhemmin uusia haaroja.

## Käytännössä

- **Oletussijoitukset ensin.** Jokainen `always_comb`-lohko alkaa
  sijoittamalla kaikille ulostuloilleen oletusarvon. Sen jälkeen haarat
  muuttavat vain poikkeavat arvot. Malli estää salvat rakenteellisesti
  ja lyhentää koodia, kun useimmat ulostulot ovat useimmiten nollia.
- **`unique case` luettelotyypille.** Kun haarat ovat toisensa
  poissulkevia, `unique` kertoo sen lukijalle, simulaattorille ja
  synteesille. `priority` on harvinainen; tavallisesti prioriteetti
  kirjoitetaan `if`–`else if` -ketjuna.
- **`default` ei korvaa ajattelua.** `default`-haara, joka asettaa
  ulostulot nolliksi, poistaa salvan mutta voi peittää puuttuvan
  haaran. Luettelotyypin kanssa kaikkien arvojen luetteleminen ilman
  `default`-haaraa antaa lint-työkalun huomata, kun tyyppiin lisätään
  arvo.
- **Ei estäviä sijoituksia `always_ff`-lohkoon eikä ei-estäviä
  `always_comb`-lohkoon.** Sääntö on mekaaninen, ja sen rikkominen
  tuottaa eroja simuloinnin ja synteesin välille (luku 5).
- **Logiikan syvyys on ajoitusta.** Jokainen porttitaso lisää viivettä.
  Pitkä `if`-ketju, muuttuva siirto ja leveä vertailu pidentävät
  kriittistä polkua. Kombinaatiologiikan määrä kahden rekisterin välillä
  rajoittaa kellotaajuutta.
- **Viitemalli eri tavalla.** Testipenkin malli kirjoitetaan
  suoraviivaisesti ja eri rakenteella kuin suunnitelma. Saman koodin
  kopio mallina löytää vain kirjoitusvirheet.

## Itsearviointi

- Osaat kirjoittaa kombinaatiologiikan `assign`-lauseilla ja
  `always_comb`-lohkolla ja valita niiden välillä.
- Osaat selittää, milloin `always_comb` tuottaa salvan, ja estää sen
  oletussijoituksilla.
- Osaat käyttää `unique case` -lausetta ja selittää, mitä se lupaa
  synteesille.
- Osaat kirjoittaa `for`-silmukan, joka purkautuu rinnakkaiseksi
  logiikaksi, ja ennustaa sen tuottaman rakenteen.
- Osaat tunnistaa etumerkillisen ylivuodon summaimen etumerkkibiteistä.
