# Stereo ja RDS

FM-stereo on 1960-luvun yhteensopivuusratkaisu: monovastaanotin kuulee
summasignaalin $(L + R)/2$ kuten ennenkin, ja stereovastaanotin
erottaa kanavat lisäsignaalista, jota monovastaanotin ei kuule.
Samalla periaatteella MPX-signaaliin lisättiin myöhemmin RDS-data.
Tässä luvussa rakennetaan stereodekooderi ja RDS-tyyppisen
datakanavan purku. Luvun lopussa koko vastaanotin ajetaan
synteettisellä tallenteella.

## MPX-signaalin rakenne

| Taajuus | Sisältö | Taso |
|--------------|--------------------------------|----------------|
| 0–15 kHz | summa $(L + R)/2$ | noin 90 % poikkeamasta |
| 19 kHz | pilotti | 9 % |
| 23–53 kHz | erotus $(L - R)/2$ kaksisivukaistaisena, 38 kHz:n kantoaalto vaimennettu | summan kanssa yhteensä 90 % |
| 57 kHz ± 2,4 kHz | RDS-data, BPSK 1187,5 bit/s | 2–5 % |

Erotussignaalin kantoaalto on täsmälleen pilotin kaksinkertainen ja
RDS:n kantoaalto sen kolminkertainen. Vastaanotin lukitsee itsensä
pilottiin ja tuottaa siitä kantoaallot koherenttiin ilmaisuun.

```{.python tiedosto="esimerkit/fm/lahetin.py" osa="mpx"}
```

![Synteettisen aseman MPX-signaalin spektri. Testiäänet 700 Hz
(vasen) ja 1,9 kHz (oikea) näkyvät summakaistalla ja erotuskaistan
sivukaistoina 38 kHz:n ympärillä; 19 kHz:n pilotti ja 57 kHz:n
datakanava erottuvat omina kaistoinaan.](kuvat/mpx.png){width=100%}

Lähetin lisää MPX-signaaliin esikorostuksen, FM-moduloi sen,
sijoittaa aseman 200 kHz:iin ja lisää kaistalle heikomman
naapuriaseman sekä kohinan. Lopuksi tallenne kirjoitetaan RTL-SDR:n
8-bittiseen muotoon:

```{.python tiedosto="esimerkit/fm/lahetin.py" osa="moduloi"}
```

```{.python tiedosto="esimerkit/fm/lahetin.py" osa="cu8"}
```

## Pilotin vaihelukko

Pilotti on kapea viiva, jonka taajuus ja vaihe vaihtelevat hieman.
Lähettimen kide ei ole tarkka, ja vastaanottimen näytetaajuuden virhe
siirtää viivaa (luku 3). Stereodekooderi tarvitsee pilotin vaiheen
näyte näytteeltä, koska 38 kHz:n kantoaallon vaihevirhe $\delta$
vuotaa erotussignaalia kanavasta toiseen suhteessa
$(1 - \cos 2\delta)/2$.

**Vaihelukko** (*PLL*) seuraa pilotin vaihetta. Toisen kertaluvun
silmukassa on vaiheilmaisin, verrannollinen ja integroiva haara.
Integroiva haara seuraa taajuusvirheen, joten silmukka seuraa sekä
vakiovaihetta että vakiotaajuuspoikkeamaa ilman jäännösvirhettä.
Silmukka ajetaan pienellä näytetaajuudella. Pilotti siirretään
nollaan nimellistaajuudeltaan, ja kapea alipäästö poistaa äänen ja
muut kaistat. Silmukan seurattavaksi jää muutaman hertsin
taajuusvirhe 12 kS/s:n näytetaajuudella, ja Python-silmukalla on
19 kertaa vähemmän kierroksia kuin täydellä näytetaajuudella.

```{.python tiedosto="esimerkit/fm/vastaanotin.py" osa="pll"}
```

Silmukan kaistanleveys 20 Hz on kompromissi. Kapeampi silmukka
suodattaa kohinaa paremmin mutta lukittuu hitaammin ja seuraa huonosti
nopeita muutoksia. Alipäästön viive (255 näytettä) siirtää
vaihearviota; koska viive on tunnettu ja taajuusvirhe on silmukan
integraattorissa, siirto korjataan suoraan.

## Stereodekooderi

Kun pilotin vaihe $\varphi$ tunnetaan, erotussignaali saadaan
kertomalla MPX $\cos 2\varphi$:lla ja suodattamalla 15 kHz:n
alipäästöllä. Summa- ja erotushaarassa on oltava sama suodin. Muuten
viiveet eroavat, ja haarat summautuvat väärässä vaiheessa.

```{.python tiedosto="esimerkit/fm/vastaanotin.py" osa="stereo"}
```

Luvun 5 ilmaisinvaste $\text{sinc}(f/f_s)$ vaimentaa 38 kHz:n
erotuskaistaa 228 kS/s:lla 0,4 dB eli 4,5 %. Ero näyttää pieneltä,
mutta se vuotaa kanavasta toiseen: vasen kanava saa oikeasta
$(1 - 0{,}955)/2 \approx 2{,}3$ % eli −33 dB. Kaupallisen
FM-virittimen kanavaerotus on 40–50 dB, joten tämä olisi selvästi
huonompi. Korjaus on jakaa erotushaara samalla sinc-arvolla. Testi
mittaa erotuksen molemmilla tavoilla ja varmistaa koko ketjun
toiminnan 20 dB:n CNR:llä:

```{.python tiedosto="esimerkit/fm/test_fm.py" osa="ketju"}
```

Ilman korjausta erotus jää alle 36 dB:n, korjattuna se ylittää 50 dB.
Tällaiset systemaattiset virheet löytyvät vain mittaamalla. Ne eivät
näy koodikatselmoinnissa, eikä korvakaan erota 33 dB:n ja 60 dB:n
kanavaerotusta helposti.

## RDS-tyyppinen datakanava

RDS (*Radio Data System*, IEC 62106) lähettää aseman tunnisteen,
nimen, ohjelmatyypin, kellonajan ja liikennetiedotteet 1187,5 bit/s:n
nopeudella. Bittinopeus on 57 kHz / 48, joten se on lukittu pilottiin.
Tutoriaalin datakanava käyttää RDS:n rakennetta, mutta toteuttaa vain
tarvittavan osan:

1. **Differentiaalikoodaus.** Bitti 1 vaihtaa vaiheen, bitti 0 pitää
   sen. Vastaanottimen ei tarvitse tietää BPSK:n absoluuttista
   vaihetta.
2. **Kaksivaihekoodaus** (*biphase*). Jokainen bitti on puoliksi
   $+1$ ja puoliksi $-1$, joten signaalissa ei ole tasakomponenttia,
   ja spektri on kaukana nollataajuudesta. Pilotti ja erotuskaista
   eivät siksi häiritse.
3. **Lohkot ja tarkisteet.** 16 tietobittiä ja 10 tarkistebittiä
   muodostavat 26 bitin lohkon, ja neljä lohkoa muodostaa ryhmän.

```{.python tiedosto="esimerkit/fm/lahetin.py" osa="rdskanta"}
```

### Tarkisteet ja siirtymäsanat

Tarkiste on syklisen koodin jakojäännös polynomilla
$g(x) = x^{10} + x^8 + x^7 + x^5 + x^4 + x^3 + 1$. Siihen lisätään
lohkon paikan (A, B, C tai D) kertova **siirtymäsana**. Ehjän lohkon
jakojäännös on siksi sen paikan siirtymäsana. Vastaanotin löytää
lohkorajat liu'uttamalla 26 bitin ikkunaa bitti kerrallaan, kunnes
kaksi peräkkäistä lohkoa antaa siirtymät A ja B. Erillistä
tahdistussanaa ei tarvita.

```{.python tiedosto="esimerkit/fm/rds.py" osa="koodi"}
```

Ryhmä 0A kuljettaa aseman nimen kahdeksan merkkiä kahden merkin
osissa. Lohkon B kaksi alinta bittiä kertovat, mikä osa on kyseessä,
ja lohkossa A on aseman 16-bittinen tunniste (PI).

```{.python tiedosto="esimerkit/fm/rds.py" osa="ryhma"}
```

```{.python tiedosto="esimerkit/fm/rds.py" osa="pura"}
```

Oikea RDS korjaa myös lyhyitä virhepurskeita tarkisteen avulla.
Tutoriaalin purku vain tunnistaa virheelliset lohkot ja ohittaa ne,
ja asemanimi kootaan ehjistä osista. Testit varmistavat koodin
ominaisuudet: ehjän lohkon syndrooma on siirtymäsana, jokainen yhden
bitin virhe havaitaan, ja purku löytää nimen mistä tahansa
aloituskohdasta.

```{.python tiedosto="esimerkit/fm/test_fm.py" osa="rds"}
```

### Bittien ilmaisu

Datakanava sekoitetaan kantataajuudelle pilotin kolminkertaisella
vaiheella ja desimoidaan 4750 Hz:iin, jolloin bittiä kohti on neljä
näytettä. Sovitettu suodin on aikakäännetty bittipulssi, ja
bittiajoitukseksi valitaan se neljästä vaiheesta, jossa päätökset
ovat varmimpia (suurin itseisarvojen summa). Tallenne on lyhyt, ja
bittinopeus on lukittu pilottiin, joten ajoitus ei ehdi liukua. Pitkässä
virrassa tarvittaisiin symbolitahdistus, esimerkiksi taidon
*Digitaalinen tiedonsiirto* Gardnerin ilmaisin.

```{.python tiedosto="esimerkit/fm/vastaanotin.py" osa="rdspura"}
```

## Koko vastaanotin

Vastaanottimen osat kootaan yhteen funktioon: kanava, ilmaisin,
pilotin lukitus, stereo ja RDS.

```{.dot otsikko="FM-stereovastaanottimen ketju. Pilotin vaihelukko tuottaa sekä stereon 38 kHz:n että RDS:n 57 kHz:n kantoaallon."}
digraph fm {
  rankdir=LR; nodesep=0.22; ranksep=0.3;
  node [shape=box, fontsize=10];
  iq [label="IQ", shape=plaintext];
  kanava [label="kanavan\nvalinta"];
  ilmaisin [label="FM-\nilmaisin"];
  summa [label="alipäästö\n15 kHz\n(L + R)"];
  pll [label="pilotti 19 kHz\nvaihelukko"];
  erotus [label="× 38 kHz\n(L − R)"];
  rds [label="× 57 kHz\nRDS-bitit"];
  matriisi [label="L ja R,\njälkikorostus"];
  aani [label="ääni", shape=plaintext];
  data [label="data", shape=plaintext];
  iq -> kanava -> ilmaisin;
  ilmaisin -> summa [label="MPX"];
  ilmaisin -> pll;
  ilmaisin -> erotus;
  ilmaisin -> rds;
  pll -> erotus [style=dashed];
  pll -> rds [style=dashed];
  summa -> matriisi; erotus -> matriisi;
  matriisi -> aani; rds -> data;
}
```

```{.python tiedosto="esimerkit/fm/vastaanotin.py" osa="vastaanota"}
```

Pääohjelma tekee 1,2 sekunnin tallenteen 35 dB:n CNR:llä, kirjoittaa
sen `cu8`-tiedostoksi, lukee sen takaisin ja vastaanottaa aseman:

```{.python tiedosto="esimerkit/fm/main.py" osa="tallenne"}
```

```{.python tiedosto="esimerkit/fm/main.py" osa="vastaanota"}
```

```{.tuloste tiedosto="esimerkit/fm.odotettu"}
```

Vaihelukko löytää lähettimen 1,5 Hz:n pilottivirheen. Molempien
kanavien amplitudi on oikea (0,5 ja 0,4), ja kanavaerotus on
56–61 dB. SINAD on 42–44 dB: 8 bitin kvantisointi ja kohina rajaavat
sitä, ja stereo on monoa kohinaisempi, koska erotuskaistan kohina
lisätään kumpaankin kanavaan. RDS-lohkoista kaikki 48 ovat ehjiä.

## Käytännössä

- **Lukitse pilottiin, älä nimellistaajuuteen.** Lähettimen ja oman
  laitteen taajuusvirheet ovat hertsejä, ja 38 kHz:n kantoaallon
  vaihevirhe näkyy suoraan kanavaerotuksessa.
- **Sama suodin molempiin haaroihin.** Summa- ja erotushaaran viiveiden
  ja vahvistusten on täsmättävä. Testaa kanavaerotus aina
  mittaamalla.
- **Huomioi ilmaisimen vaste.** Vaihe-eroilmaisin ja desimointisuodin
  vaimentavat erotuskaistaa, ja vaimennus korjataan vakiolla.
- **Hyödynnä koodin rakennetta tahdistuksessa.** RDS:n siirtymäsanat
  tekevät lohkotahdistuksen ilman erillistä tahdistussanaa. Samaa
  periaatetta käyttävät monet muutkin protokollat (esim. CRC-pohjainen
  kehyshaku ATM:ssä).
- **Mittaa lohkovirheet.** Ehjien ja virheellisten lohkojen suhde on
  hyvä vastaanoton laadun mittari, myös antennin suuntaukseen.

## Itsearviointi

- Osaat selittää FM-stereon MPX-signaalin rakenteen ja sen, miksi se
  on yhteensopiva monovastaanottimen kanssa.
- Osaat toteuttaa toisen kertaluvun vaihelukon pienellä
  näytetaajuudella ja kompensoida suotimen viiveen.
- Osaat toteuttaa stereodekooderin ja selittää, miten
  vaihevirhe ja ilmaisimen vaste heikentävät kanavaerotusta.
- Osaat selittää differentiaali- ja kaksivaihekoodauksen ja purkaa
  RDS-tyyppiset lohkot tarkisteiden ja siirtymäsanojen avulla.
