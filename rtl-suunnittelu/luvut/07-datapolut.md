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

Varjorekisterin vaikutus näkyy alla olevassa simulaatiossa, jossa
jakso on lyhennetty kahdeksaan askeleeseen (`W = 3`) ja `tick` on
jatkuvasti ykkönen. `suhde` vaihtuu kahdesta kuuteen kesken jakson,
mutta `voimassa` muuttuu vasta, kun `vaihe` palaa nollaan. Meneillään
oleva jakso pysyy kahden askeleen pulssina, ja kuuden askeleen pulssi
alkaa seuraavasta jaksosta.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/07-pwm.json" otsikko="PWM: uusi pulssisuhde tulee voimaan vasta jakson rajalla"}
```

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

Tässä liukuhihnassa ei ole vastapainetta: jokainen tulos otetaan
vastaan sillä jaksolla, jolla se valmistuu.

## Vastapaine: kättelyvaihe ja skid-puskuri

Kun kuluttaja voi pysäyttää virran (`valmis = 0`), pelkkä
kelvollisuusbitti ei riitä: vaiheen on pidettävä sanansa, kunnes
seuraava vaihe ottaa sen. Jokainen vaihe käyttää luvun 6
kelvollinen/valmis-kättelyä kumpaankin suuntaan. Seuraavissa
moduuleissa `s_`-alkuiset portit ovat sisääntulon ja `u_`-alkuiset
ulostulon kättely.

Vaihe saa ottaa uuden sanan, kun se on tyhjä tai kun kuluttaja vie
nykyisen sanan samalla reunalla:

```{.systemverilog tiedosto="esimerkit/07-kattely/kattelyvaihe.sv" osa="vaihe"}
```

Rakenne on yksinkertainen, mutta `s_valmis` riippuu kombinatorisesti
`u_valmis`-signaalista. Kun vaiheita on peräkkäin kymmenen, viimeisen
kuluttajan `valmis` kulkee yhden jakson aikana kaikkien kymmenen läpi,
ja polusta tulee kriittinen. *Skid-puskuri* katkaisee polun:
tuottajalle näkyvä `s_valmis` tulee suoraan kiikusta. Hinta on, että
tuottaja kuulee pysähdyksestä jakson myöhässä ja ehtii lähettää vielä
yhden sanan. Puskurissa on tälle sanalle varapaikka:

```{.systemverilog tiedosto="esimerkit/07-kattely/skid_puskuri.sv" osa="skid"}
```

Testipenkki kytkee skid-puskurin ja kättelyvaiheen peräkkäin. Tuottaja
pitää taukoja ja kuluttaja pysäyttää virran näennäissatunnaisesti.
Tuottaja noudattaa kättelyn toista sääntöä, eli se vaihtaa dataa vasta
siirron jälkeen:

```{.systemverilog tiedosto="esimerkit/07-kattely/testipenkki.sv" osa="tuottaja"}
```

Tarkistin laskee vain toteutuneet siirrot. Koska sanat ovat juoksevia
numeroita, kadonnut, kahdentunut tai väärään järjestykseen joutunut
sana jää heti kiinni:

```{.systemverilog tiedosto="esimerkit/07-kattely/testipenkki.sv" osa="tarkistin"}
```

```{.tuloste tiedosto="esimerkit/07-kattely.odotettu"}
```

Kaksi viimeistä riviä ovat testin laadun mittareita: jos virta ei
olisi pysähtynyt kertaakaan tai varapaikkaa ei olisi käytetty, testi
ei olisi koetellut juuri sitä, mitä varten moduulit on tehty.

Alla on jakso samasta simulaatiosta. Kuluttaja laskee `u_valmis`-
signaalin kahdeksi jaksoksi, jolloin `u_data` pysyy arvossa 16.
Tuottaja näkee pysähdyksen vasta seuraavalla jaksolla (`s_valmis`
laskee jakson myöhässä), ja sillä välin lähetetty sana 17 jää
varapaikkaan (`vara_kelv`). Tuottajan seuraava sana 18 odottaa
paikallaan, kunnes `s_valmis` nousee. Kun virta jatkuu, varapaikka
tyhjenee ensin, eikä yksikään sana katoa tai vaihda paikkaa.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/07-kattely.json" otsikko="Vastapaine: data pysyy paikallaan ja skid-puskurin varapaikka täyttyy"}
```

## Kättely rajapintana: interface

Kättelyn kolme signaalia kulkevat aina yhdessä, ja jokainen moduuli
luettelee ne porteissaan uudelleen. SystemVerilogin `interface` niputtaa
signaalit yhdeksi nimetyksi kokonaisuudeksi, ja `modport` kertoo
suunnat kummankin osapuolen näkökulmasta:

```{.systemverilog tiedosto="esimerkit/07-rajapinta.sv" osa="rajapinta"}
```

Moduulin portiksi kirjoitetaan rajapinta ja sen `modport`, ja
signaaleihin viitataan pisteellä:

```{.systemverilog tiedosto="esimerkit/07-rajapinta.sv" osa="vaihe"}
```

Ylemmällä tasolla rajapinnasta luodaan instanssi kuten moduulista, ja
kaksi vaihetta kytketään yhdellä nimellä kolmen sijasta:

```{.systemverilog tiedosto="esimerkit/07-rajapinta.sv" osa="kytkenta"}
```

```{.tuloste tiedosto="esimerkit/07-rajapinta.odotettu"}
```

Rajapinta lyhentää porttiluetteloita ja estää kytkemästä `valmis`-
signaalia väärin päin. Työkalutuki on kuitenkin epätasaista: osa
synteesi- ja lint-työkaluista tukee vain osaa ominaisuuksista, ja
rajapintaportti ylimmän tason nastoissa tai Verilog-2005-moduulin
rajalla ei onnistu. Siksi moni tyyliopas, esimerkiksi lowRISCin,
sallii rajapinnat testipenkeissä mutta kirjoittaa suunnitelman portit
auki tai niputtaa ne pakattuun rakenteeseen (luku 3). Tämän
tutoriaalin muut esimerkit käyttävät erillisiä portteja.

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
- **Vastapaine suunnitellaan alusta asti.** Kättelyn lisääminen
  valmiiseen liukuhihnaan on työlästä, koska jokaisen vaiheen on
  osattava pysähtyä. Jos kuluttaja voi joskus olla varattu, rajapintaan
  tulee `valmis` heti. Kuluttaja, joka on aina valmis, sitoo sen
  ykköseksi.
- **Skid-puskuri sinne, missä `valmis`-polku on pitkä.** Jokainen
  kättelyvaihe ei tarvitse sitä. Tavallinen paikka on moduulin
  rajapinta, jolloin moduulin sisäinen logiikka ei näy naapurin
  ajoituspolussa.
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
- Osaat kirjoittaa liukuhihnan vaiheen, joka pysähtyy vastapaineesta,
  ja selittää, minkä polun skid-puskuri katkaisee ja miksi se tarvitsee
  varapaikan.
- Osaat niputtaa kättelyn `interface`-rakenteeksi ja kertoa, miksi
  sitä ei aina käytetä suunnitelman porteissa.
- Osaat valita rakenteen ehdollisella `generate`-lohkolla ja hylätä
  virheelliset parametrit `$error`-kutsulla.
- Osaat käyttää varjorekisteriä ohjausarvon turvalliseen vaihtamiseen.
