# Kellotusalueet käytännössä

Kun suunnitelmassa on useampi kello, jokainen signaali kellosta toiseen
on kellotusalueen ylitys (clock domain crossing, CDC). Tahdistinten
teoria, metastabiilius ja rakenteet käsitellään taidon
*RTL-suunnittelu* luvussa *Kellotusalueiden ylitys*. Tämä luku
näyttää, mitä ylitykselle tapahtuu FPGA-vuossa: mihin se syntetisoituu,
mitä ajoitusraportti siitä kertoo ja mitä jää suunnittelijan
vastuulle.

## Missä kellotusalueita syntyy

FPGA-suunnitelmassa ylityksiä tulee vastaan useammin kuin ensin
luulisi:

- **Asynkroniset tulot.** Painike, UART-linja ja ulkoisen piirin
  keskeytys eivät noudata FPGA:n kelloa. Ne ovat ylityksiä, vaikka
  suunnitelmassa olisi vain yksi kello. Luvun 10 UART-vastaanotin
  tahdistaa linjan kahdella kiikulla ennen kuin katsoo sitä.
- **Ulkoiset liitännät omalla kellollaan.** Kameran pikselikello,
  Ethernet-PHY:n vastaanottokello ja USB-sillan kello.
- **PLL:n eri lähdöt.** Samasta PLL:stä saadut kellot ovat
  vaihelukittuja, mutta jos niiden suhde ei ole kokonaisluku,
  ylitykset on käsiteltävä kuten asynkronisten kellojen välillä.
- **Nollaus.** Asynkroninen nollaus on tahdistettava jokaiseen
  kellotusalueeseen erikseen (luku 7).

## Asynkroninen FIFO

Tiedon siirtoon kellotusalueiden välillä tavallisin rakenne on
asynkroninen FIFO. Esimerkin FIFO on sama kuin RTL-suunnittelun
luvussa: Grayn koodatut osoittimet, jotka tahdistetaan kahdella
kiikulla vastakkaiselle puolelle.

```{.systemverilog tiedosto="esimerkit/08-kaksi-kelloa/async_fifo.sv" osa="liitanta"}
```

Testipenkki ajaa kirjoituspuolta 12 MHz:n ja lukupuolta noin 50 MHz:n
kellolla. Jaksojen suhde ei ole kokonaisluku, joten reunat liukuvat
toistensa suhteen, kuten oikeilla, toisistaan riippumattomilla
kelloilla:

```{.systemverilog tiedosto="esimerkit/08-kaksi-kelloa/testipenkki.sv"}
```

```{.tuloste tiedosto="esimerkit/08-kaksi-kelloa.odotettu"}
```

Simulaatio todistaa, että logiikka toimii, mutta ei sitä, että
ylitys on turvallinen. RTL-simulaatiossa kiikku ei koskaan ole
metastabiili, joten tahdistimen puuttuminen ei näy testissä. Ylitykset
tarkistetaan katselmoinnilla tai erillisellä CDC-tarkistustyökalulla.

## Synteesin tulos

Vuo ajaa FIFOn kahdella 48 MHz:n kellolla:

```{.tuloste tiedosto="esimerkit/raportit/kaksi-kelloa.odotettu"}
```

Kahdeksan kantosolua ovat osoitinten summaimet. Tilastoissa on
lisäksi 128 kiikkua `SB_DFFE`: koko 16 × 8 bitin muisti on rakennettu
kiikuista, ja suunnitelma vie lähes 300 logiikkasolua. Syy on sama
kuin luvun 4 muistissa: FIFOn lukuportti on kombinatorinen
(`tieto_ulos = muisti[l_bin]`), joten lohko-RAM ei kelpaa.

Lohko-RAMiin FIFO saadaan rekisteröimällä luku. Silloin tieto tulee
ulos jaksoa myöhemmin kuin lukupulssi, ja FIFOn liitäntä muuttuu:
käyttäjän on odotettava jakso tai FIFOon lisätään ennakkoluku
(first-word fall-through), joka hakee seuraavan sanan valmiiksi.
Valmistajien FIFO-generaattorit tarjoavat molemmat tilat. Pieni FIFO
kannattaa usein jättää kiikkuihin, suuri kuuluu aina lohko-RAMiin.

## Mitä ajoitusraportti näkee

nextpnr analysoi kummankin kellon polut erikseen ja raportoi lisäksi
polut kellotusalueiden välillä ja IO-nastoihin (`<async>`). Lokin
rivit ovat tässä kellojen nimet lyhennettyinä:

```text
Info: Max frequency for clock 'clk_k$SB_IO_IN_$glb_clk': 56.04 MHz
      (PASS at 48.00 MHz)
Info: Max frequency for clock 'clk_l$SB_IO_IN_$glb_clk': 57.04 MHz
      (PASS at 48.00 MHz)

Info: Max delay <async>                         -> posedge clk_k...: 14.65 ns
Info: Max delay <async>                         -> posedge clk_l...: 14.97 ns
Info: Max delay posedge clk_k... -> <async>                        : 22.10 ns
Info: Max delay posedge clk_k... -> posedge clk_l...               :  4.39 ns
Info: Max delay posedge clk_l... -> <async>                        : 22.81 ns
Info: Max delay posedge clk_l... -> posedge clk_k...               :  4.39 ns
```

Kellojen väliset 4,39 ns:n polut ovat Gray-osoittimien johtimia
lähtökiikusta tahdistimen ensimmäiseen kiikkuun. Raportti kertoo
niiden viiveen, mutta ei vertaa sitä mihinkään, koska kellojen
välillä ei ole tunnettua vaihesuhdetta. Polku ei ole "PASS" eikä
"FAIL".

Viiveellä on silti merkitystä. Gray-koodaus takaa, että osoitin
muuttuu yhdellä bitillä kerrallaan, mutta vain jos bittien viiveet
eroavat toisistaan vähemmän kuin kohdekellon jakso. Jos yksi bitti
viipyy reitityksessä pitkään, tahdistin voi nähdä kaksi peräkkäistä
muutosta yhtä aikaa. Pienessä piirissä viiveet ovat muutamia
nanosekunteja, ja ehto täyttyy helposti. Suuressa piirissä
reititys voi kuitenkin kiertää, ja silloin ehto on annettava
työkalulle rajoitteena.

## Rajoitteet suurissa työkaluissa

AMD:n ja Intelin työkaluissa kellojen suhde kerrotaan SDC/XDC-
rajoitteilla:

| Rajoite | Tarkoitus |
|---------|-----------|
| `set_clock_groups -asynchronous` | kellot ovat riippumattomia; välisiä polkuja ei ajoiteta |
| `set_max_delay -datapath_only` | Gray-osoittimen bittien enimmäisviive, yleensä yksi kohdekellon jakso |
| `ASYNC_REG`-attribuutti (AMD) | tahdistimen kiikut vierekkäin, ei optimointia niiden välillä |
| CDC-raportti (`report_cdc`) | luettelee ylitykset ja varoittaa tahdistamattomista |

Väärä polku (`set_false_path`) kaikille kellojen välisille poluille on
yleinen virhe: se poistaa myös Gray-osoittimien viiverajan, ja
työkalu voi reitittää ne miten tahansa. Kellot erotetaan
ryhmiksi, ja tahdistettavat väylät rajoitetaan erikseen.

nextpnr:n iCE40-tuessa näitä rajoitteita ei ole. Pienessä piirissä
riittää, että ylitykset tehdään vain tunnetuilla rakenteilla
(tahdistin, kättely, asynkroninen FIFO) ja raportin kellojen väliset
viiveet tarkistetaan silmämääräisesti.

## Metastabiiliuden todennäköisyys

Kahden kiikun tahdistin ei poista metastabiiliutta vaan tekee siitä
epätodennäköistä. Keskimääräinen aika vikojen välillä (MTBF) kasvaa
eksponentiaalisesti sen ajan funktiona, jonka kiikku saa asettua:

$$\text{MTBF} = \frac{e^{t_r / \tau}}{T_0 \, f_{\text{kello}} \, f_{\text{data}}}$$

missä $t_r$ on asettumiseen jäävä aika (noin kellojakso miinus
reititys ja asetusaika) ja $\tau$ ja $T_0$ ovat piiriteknologian
vakioita. Korkeilla taajuuksilla $t_r$ lyhenee, ja kolmas kiikku voi
olla tarpeen. AMD:n työkalut laskevat MTBF:n tahdistimille, kun ne on
merkitty `ASYNC_REG`-attribuutilla. Samasta syystä tahdistimen kiikkujen
välillä ei saa olla logiikkaa: jokainen LUT syö asettumisaikaa.

## Käytännössä

- **Luettele ylitykset.** Jokainen kellojen välinen signaali kuuluu
  listaan, jossa on sen tahdistustapa. Lista on osa suunnitelman
  dokumentaatiota ja katselmointia.
- **Vain tunnetut rakenteet.** Yksi bitti tahdistimella, pulssi
  vaihtosignaalina, monibittinen arvo kättelyllä tai FIFOlla. Ei
  koskaan monibittistä väylää pelkillä tahdistimilla.
- **Tahdistimen kiikut peräkkäin ilman logiikkaa.** Ensimmäisen
  kiikun lähtö menee vain toiseen kiikkuun.
- **Älä tee kaikista kellojen välisistä poluista vääriä polkuja.**
  Erota kellot ryhmiksi ja rajoita Gray-väylien viive.
- **FIFOn muisti lohko-RAMiin, kun syvyyttä on paljon.** Rekisteröity
  luku tai ennakkoluku; pieni FIFO saa olla kiikuissa.

## Itsearviointi

- Osaat tunnistaa FPGA-suunnitelman kellotusalueiden ylitykset,
  myös asynkroniset tulot ja nollauksen.
- Osaat selittää, miksi simulaatio ei todista ylitystä turvalliseksi.
- Osaat lukea nextpnr:n raportista kellojen väliset polut ja kertoa,
  miksi niitä ei verrata kellojaksoon.
- Osaat kertoa, miten kellot ja Gray-osoittimet rajoitetaan SDC/XDC-
  työkaluissa ja miksi pelkkä väärä polku ei riitä.
