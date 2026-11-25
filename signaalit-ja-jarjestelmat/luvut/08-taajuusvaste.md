# Taajuusvaste

Edellisessä luvussa nähtiin, että jono $z_0^n$ kulkee LTI-suotimen läpi
kertoimella $H(z_0)$. Tärkein erikoistapaus on yksikköympyrä
$z = e^{i\omega}$, jolloin jono on kompleksinen sini
$e^{i\omega n}$. **Taajuusvaste** $H(e^{i\omega})$ kertoo, kuinka
paljon suodin vahvistaa kutakin taajuutta ja kuinka paljon se siirtää
sen vaihetta. Se on suotimen käytännöllisin kuvaus: suodin valitaan,
dokumentoidaan ja testataan taajuusvasteen avulla.

## Diskreettiaikainen Fourier-muunnos

Kirjallisuudessa sama lauseke esiintyy toisellakin nimellä. Jonon
$x[n]$ **diskreettiaikainen Fourier-muunnos** (DTFT) on

$$X(e^{i\omega}) = \sum_{n=-\infty}^{\infty} x[n]\,e^{-i\omega n},$$

eli Z-muunnos yksikköympyrällä. Taajuusvaste on siis impulssivasteen
DTFT. Kolme ominaisuutta kannattaa muistaa. DTFT on jatkuvan muuttujan
$\omega$ funktio, vaikka jono on diskreetti. Se on jaksollinen jaksolla
$2\pi$, koska $e^{-i(\omega + 2\pi)n} = e^{-i\omega n}$; tämä on
luvun 3 aliasointi taajuustasossa. Ja äärellisen jonon DFT on sen
DTFT:n näytteet taajuuksilla $\omega_k = 2\pi k/N$. Seuraavan luvun
nollilla täyttäminen ottaa samasta DTFT:stä näytteitä tiheämmin.

## Sini sisään, sini ulos

Reaalinen sini on kahden kompleksisen sinin summa, joten
$\cos(\omega n)$ tuottaa ulostulon
$|H(e^{i\omega})|\cos(\omega n + \arg H(e^{i\omega}))$, kun alkutransientti
on vaimentunut. Taajuus ei muutu. Amplitudi kerrotaan **amplitudivasteella**
$|H|$, ja vaihe siirtyy **vaihevasteen** $\arg H$ verran.
Lineaarinen suodin ei siis voi tuottaa uusia taajuuksia. Jos
ulostulossa on taajuuksia, joita syötteessä ei ollut, järjestelmä on
epälineaarinen.

Taajuusvaste lasketaan SciPyn funktiolla `freqz`. Se laskee
polynomien arvot yksikköympyrällä. Argumentti `worN` on joko pisteiden
määrä tai lista taajuuksia, ja kun `fs` annetaan, taajuudet ovat
hertsejä.

```{.python tiedosto="esimerkit/08-freqz.py" osa="freqz"}
```

Tarkistetaan sama mittaamalla: syötetään kosini, odotetaan transientin
vaimenemista ja mitataan ulostulon kompleksinen amplitudi
korrelaatiolla, kuten taidossa *Kompleksiluvut ja Fourier-analyysi*
mitattiin osoitin.

```{.python tiedosto="esimerkit/08-freqz.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/08-freqz.odotettu"}
```

![Saman Butterworth-suotimen amplitudivaste, vaihe ja ryhmäviive
logaritmisella taajuusakselilla. Pisteviivat osoittavat rajataajuuden
100 Hz ja −3 dB:n tason. Vaihetta ja ryhmäviivettä käsitellään
myöhemmin tässä luvussa.](kuvat/butterworth.png){width=100%}

Mittaus ja laskelma täsmäävät neljän desimaalin tarkkuudella. Toisen
asteen Butterworth-suotimen vahvistus on rajataajuudella
$1/\sqrt2$ eli $-3$ dB, ja vaihe on siellä täsmälleen $-90$ astetta.
Rajataajuuden yläpuolella vaimennus jyrkkenee 12 dB oktaavia kohti
(40 dB dekadia kohti), koska suotimen aste on kaksi.

## Desibelit ja kaistat

Amplitudivaste esitetään yleensä desibeleinä, $20\log_{10}|H|$, koska
suotimen vaimennukset ulottuvat helposti viidelle dekadille, ja koska
sarjaan kytkettyjen suotimien desibelit lasketaan yhteen. Taajuusakseli
on usein logaritminen samasta syystä.

Suotimen taajuusalue jaetaan **päästökaistaan**, jossa vahvistus on
lähellä yhtä, **estokaistaan**, jossa vaimennus on vähintään vaadittu,
ja niiden väliseen **siirtymäkaistaan**. Tyypit nimetään päästökaistan
mukaan: alipäästö, ylipäästö, kaistanpäästö ja kaistanesto. Kapea
kaistanesto on **lovisuodin**. Suotimen vaatimukset kirjoitetaan
näiden kaistojen rajoina ja vaimennuksina, ja testit tarkistavat ne
(luku 11).

## Navat, nollat ja geometria

Kun siirtofunktio kirjoitetaan tekijöinä, sen itseisarvo pisteessä
$z = e^{i\omega}$ on

$$|H(e^{i\omega})| = |k|\,\frac{\prod_m |e^{i\omega} - q_m|}
{\prod_k |e^{i\omega} - p_k|},$$

missä $q_m$ ovat nollat ja $p_k$ navat. Taajuusvaste on siis
etäisyyksien suhde. Kun yksikköympyrän piste kulkee navan ohi,
nimittäjän etäisyys on pieni, ja vahvistus on suuri. Kun se kulkee
nollan ohi, vahvistus on pieni, ja yksikköympyrällä oleva nolla poistaa
taajuuden kokonaan.

```{.python tiedosto="esimerkit/08-geometria.py" osa="geometria"}
```

```{.tuloste tiedosto="esimerkit/08-geometria.odotettu"}
```

Nolla kulmassa 0,6 radiaania tuottaa täydellisen vaimennuksen, ja napa
kulmassa 1,2 radiaania tuottaa resonanssihuipun, jonka korkeutta säätää
navan etäisyys yksikköympyrästä. Tällä geometrialla suotimia voi
suunnitella käsin: nollat sinne, mitä poistetaan, ja navat sinne, mitä
korostetaan.

## Vaihe ja ryhmäviive

Vaihevaste kertoo, kuinka paljon kukin taajuus viivästyy. Puhdas
$D$ näytteen viive on $H = e^{-i\omega D}$: vaihe on lineaarinen
taajuuden funktio, ja sen kulmakerroin on viive. Yleisesti viive
määritellään **ryhmäviiveenä**

$$\tau_g(\omega) = -\frac{d}{d\omega}\arg H(e^{i\omega}),$$

joka on kapeakaistaisen pulssin verhokäyrän viive näytteinä. Jos
ryhmäviive on sama kaikilla taajuuksilla, suodin viivästää signaalia
muuttamatta sen muotoa. Jos se vaihtelee, eri taajuudet saapuvat eri
aikaan, ja terävä pulssi leviää. Tämä on **vaihesärö**.

Symmetrinen FIR-suodin, $h[n] = h[N-1-n]$, on lineaarivaiheinen, ja
sen ryhmäviive on täsmälleen $(N-1)/2$ näytettä. IIR-suotimen ryhmäviive
vaihtelee aina, ja se on suurimmillaan rajataajuuden lähellä.

```{.python tiedosto="esimerkit/08-ryhmaviive.py" osa="vaihe"}
```

Viive näkyy myös suoraan: kapeakaistainen pulssi viivästyy
ryhmäviiveen verran. Verhokäyrä lasketaan analyyttisestä signaalista
(`scipy.signal.hilbert`).

```{.python tiedosto="esimerkit/08-ryhmaviive.py" osa="pulssi"}
```

```{.tuloste tiedosto="esimerkit/08-ryhmaviive.odotettu"}
```

Lineaarinen vaihe on tärkeä, kun signaalin muoto on tieto: EKG:ssä,
tietoliikenteen pulsseissa ja äänen transienteissa. Tallennetulle
datalle on vielä parempi vaihtoehto: `filtfilt` suodattaa signaalin
eteen- ja taaksepäin, jolloin vaiheet kumoutuvat ja viive on nolla.
Se ei ole kausaalinen, joten reaaliajassa se ei toimi.

## Lovisuodin verkkohäiriölle

Mittausjohdot poimivat verkkojännitteen 50 Hz:n häiriön, ja se on
usein suurempi kuin mitattava signaali. **Lovisuodin** poistaa yhden
taajuuden ja päästää muut läpi. Geometria kertoo rakenteen: nollat
yksikköympyrälle kulmaan $\pm\omega_0$ ja navat samaan kulmaan hieman
sisäpuolelle, säteelle $r$. Ilman napoja nollat vaimentaisivat leveän
alueen. Lähellä olevat navat kumoavat nollien vaikutuksen kaikkialla
paitsi aivan loven kohdalla, ja säde $r$ säätää loven leveyttä.

```{.python tiedosto="esimerkit/08-lovi.py" osa="lovi"}
```

![Lovisuotimen navat ja nollat sekä amplitudivaste ($f_s = 500$ Hz,
$r = 0{,}98$).](kuvat/lovi.png){width=100%}

`scipy.signal.iirnotch` suunnittelee saman suotimen hyvyysluvun $Q$
perusteella: $Q = f_0/\Delta f$, missä $\Delta f$ on loven $-3$ dB:n
leveys. Käytetään suodinta EKG:n kaltaiseen signaaliin:

```{.python tiedosto="esimerkit/08-lovi.py" osa="kayttoon"}
```

```{.tuloste tiedosto="esimerkit/08-lovi.odotettu"}
```

Häiriö pienenee yli sataankertaisesti, ja sydämen sykkeen terävä
piikki säilyy. Jäljelle jäävä virhe on suotimen pieni vaikutus itse
signaaliin. Jos verkkotaajuus poikkeaa 50 hertsistä, kapea lovi
ohittaa sen. Silloin lovea levennetään pienentämällä sädettä $r$, tai
taajuutta seurataan adaptiivisesti.

Sama kuuluu äänessä. Seuraava ohjelma soittaa kolme säveltä, joiden
päällä on voimakas 50 Hz:n hurina, ja kirjoittaa signaalin
äänitiedostoksi ennen lovisuodinta ja sen jälkeen. Hurina katoaa, ja
sävelet säilyvät ennallaan, koska ne ovat kaukana lovesta.

```{.python tiedosto="esimerkit/08-hurina.py" osa="hurina"}
```

```{.tuloste tiedosto="esimerkit/08-hurina.odotettu"}
```

## Käytännössä

- **Anna aina `fs`**, kun käytät `freqz`-, `butter`- tai
  `group_delay`-funktioita hertseillä. Normitettujen taajuuksien
  sekoittuminen on SciPy-koodin yleisin virhe.
- **Tarkista taajuusvaste mittaamalla.** Sinisyöte ja korrelaatio
  paljastavat, jos kertoimet tai toteutus eivät vastaa suunnitelmaa.
- **Valitse lineaarivaiheinen FIR**, kun aaltomuoto on tärkeä, ja
  `filtfilt`, kun data on tallennettu ja viiveen on oltava nolla.
- **Muista ryhmäviive reaaliaikajärjestelmissä.** Jyrkkä suodin on
  hidas: sen ryhmäviive rajataajuudella voi olla kymmeniä näytteitä.
- **Rakenna yksinkertaiset suotimet navoista ja nollista.** Lovi,
  resonaattori ja tasajännitteen poisto ovat kukin yksi napa–nolla-pari.

## Itsearviointi

- Osaat määritellä diskreettiaikaisen Fourier-muunnoksen ja selittää
  sen yhteyden Z-muunnokseen, taajuusvasteeseen ja DFT:hen.
- Osaat laskea suotimen taajuusvasteen `freqz`-funktiolla hertseinä ja
  varmistaa sen sinisyötteellä.
- Osaat tulkita amplitudivasteen desibeleinä sekä nimetä päästö-,
  esto- ja siirtymäkaistan.
- Osaat arvioida amplitudivasteen muodon napojen ja nollien sijainnista.
- Osaat laskea ryhmäviiveen ja selittää, miksi symmetrinen FIR on
  lineaarivaiheinen ja milloin vaihesäröllä on merkitystä.
- Osaat suunnitella lovisuotimen napojen ja nollien avulla ja
  `iirnotch`-funktiolla.
