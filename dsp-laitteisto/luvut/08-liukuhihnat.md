# Liukuhihnoitus ja resurssien jakaminen

Edellisten lukujen rakenteet ottivat vastaan näytteen joka
kellojaksolla, ja niiden kellotaajuus oli näytetaajuus. Usein suhde
on toinen. Äänen näytetaajuus on 48 kHz ja FPGA:n kello 48 MHz:
jokaiselle näytteelle on tuhat kellojaksoa, ja yksi kertoja ehtii
laskea tuhannen kertoimen suotimen. Ohjelmistoradiossa taas
näytetaajuus voi olla suurempi kuin yhden kertojan kellotaajuus, ja
silloin liukuhihnaa on pidennettävä. Tämä luku käsittelee molemmat
suunnat sekä vastapaineen, joka sitoo vaiheet yhteen.

## Kriittinen polku

Synkronisen piirin suurin kellotaajuus määräytyy pisimmästä polusta
rekisteristä rekisteriin:

$$f_{\max} = \frac{1}{t_{\mathrm{clk \to q}} + t_{\mathrm{logiikka}}
+ t_{\mathrm{reititys}} + t_{\mathrm{setup}}}.$$

Polun voi lyhentää lisäämällä rekisterin sen keskelle. FIR-suotimessa
rekisterin voi lisätä mihin tahansa *etenevään* polkuun, koska jokainen
näyte kulkee saman määrän rekistereitä ja vain latenssi kasvaa.
Suoran muodon summainpuuhun lisätään rekisteririvi jokaisen
puutason jälkeen, jolloin kriittinen polku on yksi summain ja
latenssi kasvaa $\lceil \log_2 N \rceil$ jaksolla. Takaisinkytkettyyn
polkuun rekisteriä ei voi lisätä (luku 4).

Synteesityökalut osaavat siirtää rekistereitä logiikan läpi
(*retiming*), kun rekisterit on kirjoitettu polun alkuun tai loppuun.
Taito *FPGA-toteutus* näytti, että Yosysin `-retime` nosti kertojan
kellotaajuutta. Retiming ei kuitenkaan lisää rekistereitä eikä ylitä
takaisinkytkentöjä, joten liukuhihnan syvyys on suunnittelijan päätös.

## Vastapaine

Kun liukuhihnan ulostulossa on näyte, jota vastaanottaja ei ota,
jotakin on tehtävä. Luvun 3 suotimet pysäyttävät koko liukuhihnan
yhdellä signaalilla:

```{.systemverilog tiedosto="esimerkit/rtl/fir_suora.sv" osa="pysaytys"}
```

Ratkaisu on oikea ja yksinkertainen, ja sen hinta on kaksi asiaa:

- `s_ready` riippuu yhdistelmälogiikalla `m_ready`-signaalista. Kun
  lohkoja ketjutetaan, valmiussignaali kulkee koko ketjun läpi
  samassa jaksossa ja muodostaa pitkän polun taaksepäin.
- `eteen` ohjaa jokaisen rekisterin sallintaa. Leveässä
  liukuhihnassa signaalilla on satoja kuormia, ja suuri
  haarautuminen hidastaa sitä.

Kun nämä rajoittavat, käytetään joustavaa liukuhihnaa. Sen yleisin
osa on *liukupuskuri* (*skid buffer*): kahden paikan puskuri, jonka
`ready` on rekisteröity. Kun vastaanottaja pysähtyy, jo lähetetty
näyte mahtuu puskurin toiseen paikkaan, ja pysähdys etenee taaksepäin
vasta seuraavalla jaksolla. Toinen tapa on antaa liukuhihnan kulkea
aina ja varata ulostuloon FIFO, johon mahtuu latenssin verran
näytteitä; lähettäjä lähettää vain, kun FIFOssa on tilaa (*luotot*,
*credits*). Taito *RTL-suunnittelu* käsitteli valid/ready-kättelyn
säännöt; tärkein niistä on, että `valid` ei saa riippua `ready`:stä.

Vastapainetta ei ole aina. Moni DSP-ketju on *valid-ohjattu*: A/D
-muunnin tuottaa näytteen tasaisesti, eikä mikään voi pysäyttää sitä.
Silloin ready-signaali jätetään pois, ja suunnittelu varmistaa, että
jokainen lohko ehtii. Tämän tutoriaalin lohkot tukevat vastapainetta,
koska se tekee niistä yleiskäyttöisiä ja koska testipenkki voi
tarkistaa sen satunnaisella vastapaineella.

## Aikamultipleksointi

Kun kellojaksoja on näytettä kohden $C$, yksi kertoja ehtii laskea
$C$ tuloa. $N$ kertoimen suodin tarvitsee silloin
$\lceil N / C \rceil$ kertojaa:

| Näytetaajuus | Kello | Jaksoja näytteelle | Kertojia 64 kertoimelle |
|--------------|-------|--------------------|-------------------------|
| 48 kHz | 48 MHz | 1000 | 1 |
| 1 MHz | 48 MHz | 48 | 2 |
| 12 MHz | 48 MHz | 4 | 16 |
| 48 MHz | 48 MHz | 1 | 64 |
| 96 MHz | 48 MHz | 0,5 | 128, kaksi rinnakkaista polkua |

Yhden kertojan toteutus kertoo vaihe kerrallaan kertoimen ja
näytteen ja lisää tulon kertymään (MAC, *multiply-accumulate*):

```{.systemverilog tiedosto="esimerkit/rtl/fir_jaettu.sv" osa="liitanta"}
```

```{.systemverilog tiedosto="esimerkit/rtl/fir_jaettu.sv" osa="ohjaus"}
```

Kertojan eteen tulee kaksi multiplekseriä, jotka valitsevat vaiheen
kertoimen ja viivelinjan paikan. Viimeisellä vaiheella tulos
kavennetaan suoraan kertymän seuraavasta arvosta, joten ulostulo
valmistuu ilman ylimääräistä jaksoa. Näytteiden väli on $N + 1 = 9$
jaksoa: yksi vastaanottoon ja kahdeksan laskentaan. Väliä voi lyhentää
$N$ jaksoon aloittamalla laskennan jo vastaanottojaksolla, mutta
selkeys on tässä arvokkaampaa kuin yksi jakso.

Tulos on bitilleen sama kuin rinnakkaisella rakenteella, koska summa
on tarkka:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fir-jaettu.odotettu"}
```

Testipenkki ei tiedä, että suodin ottaa näytteen vastaan vain joka
yhdeksännellä jaksolla. Se näkee vain `s_ready`-signaalin, joka on
nollassa laskennan ajan. Vastapaine on siis sama mekanismi, joka
kuljettaa sekä ulkoisen vastaanottajan pysähdykset että lohkon oman
laskenta-ajan.

## Taittaminen

Rinnakkaisen ja täysin jaetun rakenteen välissä on koko jatkumo.
*Taittaminen* (*folding*) jakaa $N$ kerrointa $P$ kertojalle, joista
jokainen laskee $N / P$ vaihetta. HLS-työkalut tekevät saman
automaattisesti: aloitusväli (*initiation interval*, II) kertoo,
kuinka monen jakson välein uusi näyte otetaan vastaan, ja työkalu
valitsee kertojien määrän sen mukaan. Taito *Korkean tason synteesi*
käsittelee tätä työkalun näkökulmasta. Käsin kirjoitettuna
taittaminen on laskuri, multiplekserit ja kertymä per kertoja, kuten
yllä, ja lopuksi kertymien summa.

Pitkässä suotimessa viivelinja ja kertoimet eivät mahdu rekistereihin.
Viivelinja toteutetaan silloin lohko-RAMissa rengaspuskurina, ja
kertoimet ovat toisessa lohko-RAMissa tai ROM:ssa. Kertojan
sisääntulot luetaan muisteista, ja kirjoitusosoite kiertää yhden
paikan näytettä kohden. Rakenne on sama kuin taidon *Digitaalinen
signaalinkäsittely* C-toteutuksessa: rengaspuskuri ja silmukka, nyt
laitteistona.

## Käytännössä

- Laske ensin kellojaksot näytettä kohden. Se ratkaisee rakenteen:
  rinnakkainen, taitettu vai täysin jaettu.
- Lisää rekistereitä etenevään polkuun vapaasti; latenssi on halpaa,
  kellotaajuus kallista. Takaisinkytkentään rekistereitä ei voi
  lisätä.
- Pysäytä liukuhihna yhdellä signaalilla, kun lohko on pieni. Käytä
  liukupuskuria tai luottoja, kun valmiussignaalin polku tai
  haarautuminen rajoittaa.
- Kirjoita jaettu ja rinnakkainen rakenne samalla liitännällä ja samalla
  mallilla. Silloin rakenteen voi vaihtaa näytetaajuuden muuttuessa
  ilman muita muutoksia.
- Pitkät viivelinjat ja kerroinsarjat kuuluvat lohko-RAMiin, eivät
  rekistereihin.

## Itsearviointi

- Osaat laskea kriittisen polun vaikutuksen kellotaajuuteen ja kertoa,
  mihin rekisterin voi lisätä muuttamatta tulosta.
- Osaat toteuttaa liukuhihnan pysäytyksen ja kertoa sen kaksi hintaa
  sekä vaihtoehdot.
- Osaat laskea, montako kertojaa suodin tarvitsee annetulla
  näytetaajuudella ja kellolla.
- Osaat toteuttaa aikamultipleksoidun MAC-suotimen ja selittää, miksi
  sen tulos on bitilleen sama kuin rinnakkaisen rakenteen.
