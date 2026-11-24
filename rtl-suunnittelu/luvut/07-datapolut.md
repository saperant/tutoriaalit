# Datapolut ja parametrointi

Datapolku on se osa suunnitelmaa, joka käsittelee dataa: laskurit,
summaimet, kertojat, siirtorekisterit ja niiden väliset rekisterit.
Tilakone ohjaa sitä. Tässä luvussa käsitellään kolmea toistuvaa
kysymystä: miten hidas toiminta tehdään nopealla kellolla, miten
laskenta jaetaan liukuhihnaksi ja miten moduulista tehdään
parametroitava ja käännösaikana tarkistettu.

## Kellon sallinta

Hitaampaa tahtia tarvitaan jatkuvasti: UART-bitti, PWM-jakso,
millisekuntiajastin. Aloittelija jakaa kellon kiikulla ja kellottaa
hitaan logiikan jaetulla kellolla. Se on virhe: jaettu kello on uusi
kellotusalue, jonka vaihe on siirtynyt, ja jokainen signaali alueiden
välillä on kellotusalueen ylitys (luku 10).

Oikea tapa on *kellon sallinta* (clock enable): koko piiri toimii
samalla kellolla, ja hidas logiikka päivittyy vain jaksoilla, joilla
yhden jakson mittainen `tick` on ykkönen.

```{.systemverilog tiedosto="esimerkit/07-pwm.sv" osa="tahti"}
```

PWM-lähtö (pulssinleveysmodulaatio) on ykkönen jakson alkuosan, jonka
pituus on `suhde`. Uusi suhde otetaan käyttöön vasta jakson alussa.
*Varjorekisteri* `voimassa` estää katkenneet pulssit, jotka
muuten syntyisivät, kun suhdetta muutetaan kesken jakson.

```{.systemverilog tiedosto="esimerkit/07-pwm.sv" osa="pwm"}
```

Testipenkki mittaa ykkösten määrän jaksoa kohden. Ensimmäinen jakso
asetuksen jälkeen käyttää vielä vanhaa arvoa, toinen uutta:

```{.tuloste tiedosto="esimerkit/07-pwm.odotettu"}
```

Testipenkin odotus `@(posedge clk iff tick)` herää vain niillä
reunoilla, joilla ehto on tosi.

## Liukuhihnat

Kun kahden rekisterin välinen logiikka on liian hidas, se jaetaan
osiin ja väliin lisätään rekisterit. Tuloksena on *liukuhihna*
(pipeline). Latenssi kasvaa, mutta kellotaajuus nousee, ja uusi syöte
voidaan ottaa vastaan joka jaksolla.

Liukuhihnan jokaisella vaiheella on *kelvollisuusbitti*, joka kulkee
datan rinnalla. Data, joka ei kulje samassa tahdissa, kulkee vaiheiden
läpi viivästettynä (tässä `c`). Kelvollisuusbitit nollataan, mutta
datarekisterit eivät tarvitse nollausta: niiden arvolla ei ole
merkitystä, kun kelvollisuusbitti on nolla.

```{.systemverilog tiedosto="esimerkit/07-liukuhihna.sv" osa="mac"}
```

Liukuhihnaa testataan *tulostaululla* (scoreboard): odotettu tulos
lasketaan syötteestä heti ja laitetaan jonoon, ja jokainen ulos tuleva
tulos verrataan jonon ensimmäiseen. Malli ei tiedä mitään latenssista,
joten testi kestää liukuhihnan muutokset.

```{.systemverilog tiedosto="esimerkit/07-liukuhihna.sv" osa="tarkistin"}
```

```{.tuloste tiedosto="esimerkit/07-liukuhihna.odotettu"}
```

Kelvollisuusbittien kulku näkyy alla olevassa kaaviossa testipenkin
alusta. Kukin syöte etenee vaiheen jaksossa, ja syötteen tauot
(`sisaan_kelv = 0`) kulkevat liukuhihnan läpi kuplina samalla
viiveellä kuin data.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/07-liukuhihna.json" otsikko="Kelvollisuusbitit kulkevat kaksivaiheisen liukuhihnan läpi"}
```

Tässä liukuhihnassa ei ole vastapainetta: jokainen tulos otetaan vastaan.
Jos kuluttaja voi pysäyttää virran (`valmis = 0`), jokaiseen vaiheeseen
tarvitaan kelvollinen/valmis-kättely ja usein *skid-puskuri*, joka
katkaisee `valmis`-signaalin pitkän kombinatorisen polun.

## Parametrit ja generate

Luvussa 2 `generate`-silmukka toisti rakenteen. Ehdollinen `generate`
(`if` tai `case` moduulin tasolla) valitsee rakenteen parametrin
perusteella. Seuraavassa LFSR:ssä (linear feedback shift register)
leveys valitsee takaisinkytkennän. Tuntematon leveys on käännösvirhe
`$error`-kutsun ansiosta.

```{.systemverilog tiedosto="esimerkit/07-lfsr.sv" osa="lfsr"}
```

Maksimipituinen LFSR käy läpi kaikki tilat nollaa lukuun ottamatta, ja
sitä käytetään näennäissatunnaislukujen tuottamiseen, testidatan
generointiin ja CRC-laskentaan. Testipenkki luo yhden LFSR:n kullekin
leveydelle `generate`-silmukalla ja mittaa jaksonpituudet:

```{.systemverilog tiedosto="esimerkit/07-lfsr.sv" osa="generate"}
```

```{.tuloste tiedosto="esimerkit/07-lfsr.odotettu"}
```

Silmukan sisällä esitellyt signaalit (`tila`, `askelia`) ovat kunkin
kierroksen omia, ja niihin viitataan hierarkkisella nimellä, kuten
`g_leveys[5].tila`.

## Parametrien tarkistus

Parametroidun moduulin kaikki parametriyhdistelmät eivät ole järkeviä.
Elaboraatioaikainen `$error` ilmaisee virheen käännöksessä eikä vasta
laboratoriossa. Seuraava baudijakaja hylkää kellotaajuuden, joka ei
jakaudu riittävän tarkasti:

```{.systemverilog tiedosto="esimerkit/07-parametri.ei-kaanny.sv"}
```

```{.tuloste tiedosto="esimerkit/07-parametri.odotettu"}
```

## Käytännössä

- **Yksi kello, monta sallintaa.** Hidas toiminta toteutetaan
  sallintapulssilla, ei jaetulla kellolla. Kellon jakaminen on
  perusteltua vain kellonhallintayksiköllä (PLL, MMCM), joka tuottaa
  uuden kellon kellopuuhun (luku 9).
- **Varjorekisteri ohjausarvoille.** Arvo, jota ohjelmisto voi muuttaa
  milloin tahansa, mutta joka saa vaikuttaa vain jakson rajalla (PWM:n
  suhde, ajastimen jakso), kirjoitetaan ensin varjorekisteriin ja
  kopioidaan käyttöön rajalla.
- **Kelvollisuusbitti datan rinnalla.** Liukuhihnan jokainen vaihe
  kuljettaa omaa `valid`-bittiään. Vain ohjausbitit nollataan, sillä
  datarekisterien nollaus kuluttaa reititystä eikä hyödytä mitään.
- **Latenssi rajapinnan ominaisuutena.** Kun latenssi on kiinteä, se
  dokumentoidaan otsikkokommenttiin. Kun se voi muuttua, rajapinnassa
  käytetään kättelyä, ja testipenkki vertaa tuloksia jonosta, ei
  laskemalla jaksoja.
- **Tarkista parametrit käännösaikana.** `$error` generate-lohkossa
  kertoo käyttäjälle, mikä yhdistelmä on kielletty. Se on halvempi kuin
  dokumentaatio, jota kukaan ei lue.
- **Kertolasku DSP-lohkoon.** FPGA:n DSP-lohkossa on kertoja,
  summain ja rekisterit. Kun kertolasku kirjoitetaan rekisterien väliin
  samassa järjestyksessä kuin lohkon sisäiset vaiheet, synteesi sijoittaa
  koko laskun lohkoon ilman lisälogiikkaa.

## Itsearviointi

- Osaat toteuttaa hitaan toiminnan sallintapulssilla ja selittää, miksi
  kelloa ei jaeta kiikulla.
- Osaat jakaa laskennan liukuhihnaksi, jossa kelvollisuusbitti kulkee
  datan rinnalla.
- Osaat testata liukuhihnaa tulostaululla, joka ei riipu latenssista.
- Osaat valita rakenteen ehdollisella `generate`-lohkolla ja hylätä
  virheelliset parametrit `$error`-kutsulla.
- Osaat käyttää varjorekisteriä ohjausarvon turvalliseen vaihtamiseen.
