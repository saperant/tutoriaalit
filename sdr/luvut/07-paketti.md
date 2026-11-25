# Digitaalinen pakettivastaanotin

ISM-kaistojen (433 MHz ja 868 MHz) laitteet, kuten sääasemat,
ovianturit, kaukosäätimet ja energiamittarit, lähettävät lyhyitä
paketteja satunnaisin väliajoin. Vastaanotin ei tiedä, milloin paketti
tulee, millä tarkalla taajuudella se on (lähettimen kide on epätarkka)
eikä missä vaiheessa sen bittikello on. Kaikki pitää selvittää paketin
alusta muutamassa millisekunnissa.

Luku rakentaa 2-GFSK-pakettivastaanottimen. Taidossa *Digitaalinen
tiedonsiirto* on koherentti QPSK-pakettilinkki. Tämä
vastaanotin on ei-koherentti ja yksinkertaisempi, kuten
anturiradioiden piirit, ja se toimii synteettisellä tallenteella,
jossa on useita paketteja, törmäys ja heikko lähetin.

## Kehys ja modulaatio

Kehys on tavallinen pakettiradiopiirien FSK-tilassa:

| Kenttä | Pituus | Tehtävä |
|--------------------|------------|--------------------------------|
| alkuosa `0xAA…` | 4 tavua | vahvistuksen, taajuuden ja ajoituksen haku |
| tahdistussana | 2 tavua | paketin alun tarkka paikka |
| pituus | 1 tavu | datan pituus |
| data | 0–255 tavua | hyötykuorma |
| CRC-16 | 2 tavua | virheiden tunnistus |

```{.python tiedosto="esimerkit/paketti/lahetin.py" osa="parametrit"}
```

```{.python tiedosto="esimerkit/paketti/lahetin.py" osa="crc"}
```

**GFSK** (*Gaussian frequency-shift keying*) on FSK, jossa bittien
taajuusmuutokset pehmennetään Gaussin suotimella. Taajuus ei hyppää,
joten spektri on kapeampi. Tulo $BT = 0{,}5$ kertoo suotimen
kaistanleveyden suhteessa bittinopeuteen. Modulaatioindeksi
$h = 2\Delta f/R = 1$ tekee taajuuksista helposti erotettavat
ei-koherentilla ilmaisimella.

```{.python tiedosto="esimerkit/paketti/lahetin.py" osa="gfsk"}
```

Tallenteeseen lisätään paketit valituin $E_b/N_0$-arvoin,
taajuusvirhein ja satunnaisin vaihein. Kohinan taso on 1 koko
kaistalla, ja paketin teho lasketaan siitä.

```{.python tiedosto="esimerkit/paketti/lahetin.py" osa="tallenne"}
```

## Kanava ja ilmaisu

Kanava valitaan kuten luvussa 4. Carsonin sääntö antaa kaistaksi
$2(19 + 19) = 76$ kHz, joten 50 kHz:n alipäästö (±50 kHz) jättää
marginaalia lähettimen taajuusvirheelle. Desimointi kuudella
antaa 152 kS/s eli neljä näytettä bittiä kohti.

```{.python tiedosto="esimerkit/paketti/vastaanotin.py" osa="kanava"}
```

FM-ilmaisin (luku 5) muuttaa GFSK:n takaisin taajuudeksi, joka
skaalataan poikkeaman yksiköihin: bitti 1 on $+1$, bitti 0 on $-1$.
Ilmaisin on ei-koherentti, eli kantoaallon vaihetta ei tarvitse
tietää. Taajuusvirhe näkyy lähdössä vakiosiirtona.

**Paketin haku** on normitettu ristikorrelaatio alkuosan ja
tahdistussanan odotetun taajuuskäyrän kanssa. Normitus energialla
tekee kynnyksestä riippumattoman signaalin voimakkuudesta. Pelkässä
kohinassa ilmaisimen lähtö on satunnainen, ja korrelaatio pysyy
pienenä. Kynnys 0,45 on valittu niin, että kohina ei ylitä sitä.

```{.python tiedosto="esimerkit/paketti/vastaanotin.py" osa="ilmaisu"}
```

## Taajuusvirhe, ajoitus ja purku

Korrelaatiohuippu kertoo paketin alun näytteen tarkkuudella. Se
ratkaisee samalla bittiajoituksen: bitit alkavat huipusta neljän
näytteen välein. Lyhyessä paketissa kellojen ero ei ehdi siirtää
ajoitusta. 30 ppm:n ero siirtäisi 200 bitin paketissa ajoitusta vain
0,006 bittiä.

**Taajuusvirhe** on alkuosan ilmaisinlähdön keskiarvo, koska
`1010…`-kuvion oikea keskiarvo on nolla. Bitit päätetään
**integroi ja päätä** -periaatteella: bitin neljän näytteen summa,
josta taajuusvirhe on vähennetty, verrataan nollaan.

```{.python tiedosto="esimerkit/paketti/vastaanotin.py" osa="pura"}
```

```{.python tiedosto="esimerkit/paketti/vastaanotin.py" osa="vastaanota"}
```

## Tallenteen purku

Tallenteessa on viisi pakettia. Kahdessa ensimmäisessä on eri
taajuusvirheet ja signaali-kohinasuhteet. Kolmannen kanssa samaan
aikaan lähettää toinen laite, ja viimeinen tulee kaukaa
(7 dB):

```{.python tiedosto="esimerkit/paketti/main.py" osa="tallenne"}
```

```{.python tiedosto="esimerkit/paketti/main.py" osa="vastaanota"}
```

```{.tuloste tiedosto="esimerkit/paketti.odotettu"}
```

![Tallenteen vesiputous eli spektri ajan funktiona, ohjelmistoradion
perusnäkymä. Viisi lähetystä näkyy kaistalla −150 kHz:n ympärillä:
kaksi selvää pakettia, törmäys 36 ms:n kohdalla (kaksi päällekkäistä
lähetystä eri taajuusvirheillä) ja heikko paketti
52 ms:n kohdalla.](kuvat/vesiputous.png){width=95%}

![FM-ilmaisimen lähtö ensimmäisen paketin alusta. Ennen pakettia
ilmaisin tuottaa pelkkää kohinaa. Alkuosan vuorottelevat bitit ja
tahdistussana seuraavat mallipohjaa, johon haku korreloi; käyrän pieni
siirtymä ylöspäin on lähettimen
taajuusvirhe.](kuvat/ilmaisin.png){width=95%}

Kaksi ensimmäistä pakettia puretaan oikein, ja taajuusvirheen arviot
osuvat noin 0,1 kHz:n tarkkuudella lähettimen virheisiin (+3,1 ja
−1,8 kHz). Törmäyksessä vastaanotin tahdistuu ensin alkaneeseen
pakettiin, mutta toinen lähetys on vain 2 dB heikompi, joten
CRC paljastaa virheet. Molemmat paketit menetetään. Jos toinen
lähetys olisi selvästi heikompi, FM-ilmaisin "kaappaisi" vahvemman
(*capture effect*), ja paketti selviäisi. Siksi ALOHA-tyyppiset
anturiverkot toimivat yllättävän hyvin. 7 dB:n paketti löytyy, mutta
sen biteissä on liikaa virheitä.

## Testaus

Testit tarkistavat CRC:n tunnetulla tarkistusarvolla ja kehyksen
rakenteen, GFSK:n vakioverhokäyrän ja taajuudet, taajuusvirheen
korjauksen ±10 kHz:n alueella, väärien löytöjen puuttumisen pelkässä
kohinassa ja pakettivirhesuhteen jyrkän putoamisen:

```{.python tiedosto="esimerkit/paketti/test_paketti.py" osa="kehys"}
```

```{.python tiedosto="esimerkit/paketti/test_paketti.py" osa="gfsk"}
```

```{.python tiedosto="esimerkit/paketti/test_paketti.py" osa="vastaanotin"}
```

Ortogonaalisen FSK:n ei-koherentti ilmaisu antaa teoriassa
bittivirhesuhteen $\frac{1}{2}e^{-E_b/2N_0}$. 12 dB:llä se on noin
$2 \cdot 10^{-4}$, joten paketeista, joissa on 128 purettavaa bittiä,
noin 2 % menisi rikki. 8 dB:llä lähes jokaisessa paketissa olisi virhe. Testi
varmistaa tämän muodon: 8 dB:llä yli 80 % paketeista menetetään, ja
14 dB:llä yksikään 20 paketista ei mene rikki. Pakettivirhesuhde
putoaa siis muutamassa desibelissä lähes yhdestä nollaan. Tätä
jyrkkyyttä vastaanottimen herkkyysmäärittely kuvaa (luku 10).

## Käytännössä

- **Normitettu korrelaatio hakuun.** Kynnys ei riipu signaalin
  voimakkuudesta, eikä AGC:tä tarvita hakuvaiheessa. Tarkista
  väärien löytöjen määrä pelkästä kohinasta.
- **Taajuusvirhe alkuosasta.** Tasapainoinen `1010…`-kuvio antaa
  suoraan taajuusvirheen. Pitkissä paketeissa data valkaistaan
  (*whitening*) näennäissatunnaisella jonolla, jotta pitkät ykkös- tai
  nollasarjat eivät siirrä ilmaisimen keskiarvoa.
- **CRC ei korjaa, se tunnistaa.** Rikkinäinen paketti hylätään, ja
  uudelleenlähetys on ylemmän kerroksen asia. Anturit lähettävät
  usein saman paketin kahdesti tai kolmesti.
- **Testaa törmäykset.** ISM-kaistalla on paljon lähettimiä ilman
  koordinaatiota. Vastaanottimen on toivuttava rikkinäisestä
  paketista ja löydettävä seuraava.
- **Mittaa PER, älä pelkkää BER:ää.** Käyttäjä näkee
  pakettivirhesuhteen. Ilmoita se $E_b/N_0$:n tai tulotehon funktiona.

## Itsearviointi

- Osaat selittää ISM-pakettiradion kehysrakenteen ja kenttien
  tehtävät vastaanotossa.
- Osaat toteuttaa GFSK-modulaattorin ja ei-koherentin ilmaisimen ja
  perustella modulaatioindeksin ja $BT$-tulon vaikutuksen.
- Osaat hakea paketin normitetulla korrelaatiolla ja arvioida
  taajuusvirheen ja bittiajoituksen alkuosasta.
- Osaat testata pakettivastaanottimen taajuusvirheillä, pelkällä
  kohinalla ja pakettivirhesuhteella.
