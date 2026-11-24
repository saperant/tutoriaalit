# FIR: taajuusnäytteistys ja Parks–McClellan

Ikkunamenetelmä lähtee ideaalisesta alipäästöstä. Kaksi muuta
menetelmää lähtee suoraan halutusta taajuusvasteesta: taajuusnäytteistys
sopii mielivaltaisille vasteille, ja Parks–McClellanin algoritmi
tuottaa lyhimmän suotimen, joka täyttää annetut toleranssit. Lisäksi
luku käy läpi lineaarivaiheisten suotimien neljä tyyppiä ja sen, miksi
kaikki tyypit eivät sovi kaikkiin suotimiin.

## Taajuusnäytteistys

Jos halutun vasteen arvot tunnetaan $N$ tasavälisessä pisteessä,
käänteinen DFT antaa suoraan $N$ kerrointa, joiden vaste kulkee täsmälleen
näiden pisteiden kautta. Lineaarinen vaihe saadaan, kun jokaiseen
näytteeseen liitetään viivettä $(N-1)/2$ vastaava vaihe
$e^{-i\pi k (N-1)/N}$.

```{.python tiedosto="esimerkit/04-taajuusnaytteistys.py" osa="suora"}
```

Pisteissä vaste on oikein, mutta niiden välissä se aaltoilee, koska
äkillinen muutos vasteessa tarkoittaa pitkää impulssivastetta, joka
katkeaa $N$:ään. Ongelma on sama kuin ikkunamenetelmässä, ja ratkaisukin
on sama. SciPyn `firwin2` interpoloi halutun vasteen tiheään hilaan,
tekee käänteismuunnoksen ja ikkunoi tuloksen. Sillä tehdään
taajuuskorjaimia ja muita suotimia, joiden vaste ei ole pelkkiä
päästö- ja estokaistoja.

```{.python tiedosto="esimerkit/04-taajuusnaytteistys.py" osa="korjain"}
```

```{.tuloste tiedosto="esimerkit/04-taajuusnaytteistys.odotettu"}
```

Korjain korostaa 1–3 kHz:n kaistaa 6 dB ja jättää muut taajuudet
ennalleen. Taulukon pisteet määräävät myös siirtymät: 800 Hz:stä
1 kHz:iin vahvistus nousee lineaarisesti.

## Parks–McClellan ja tasavärähtely

Ikkunamenetelmän virhe on suurin kaistojen reunoilla ja pienenee niistä
poispäin. Estokaistan kaukaiset osat on siis vaimennettu enemmän kuin
vaatimus edellyttää, ja nämä ylimääräiset desibelit maksetaan
kertoimina. **Optimaalinen** suodin jakaa virheen tasan: sen
estokaistan kaikki sivukeilat ovat yhtä korkeita. Tätä kutsutaan
**tasavärähtelyksi** (*equiripple*).

Parks–McClellanin algoritmi (1972) etsii tasavärähtelevän suotimen
Remezin vaihtoalgoritmilla. Se minimoi painotetun virheen suurimman
arvon:

$$\min_h \max_{f \in \text{kaistat}} W(f)\,\bigl|H(f) - D(f)\bigr|,$$

missä $D$ on haluttu vaste ja $W$ paino. Painoilla määrätään, kuinka
tarkasti kukin kaista toteutuu. Jos päästökaistalla sallitaan
$\delta_p$ ja estokaistalla $\delta_s$, painojen suhde on
$\delta_p/\delta_s$, jolloin molemmat toleranssit täyttyvät samalla
pituudella. Pituudelle on Kaiserin arvio

$$N \approx \frac{-20\log_{10}\sqrt{\delta_p \delta_s} - 13}
{14{,}6\,\Delta f} + 1.$$

```{.python tiedosto="esimerkit/04-remez.py" osa="painot"}
```

Algoritmi ei takaa, että annettu pituus riittää. Pituutta kasvatetaan
arviosta, kunnes vaatimus täyttyy, samoin kuin Kaiserin ikkunalla.

```{.python tiedosto="esimerkit/04-remez.py" osa="etsi"}
```

```{.python tiedosto="esimerkit/04-remez.py" osa="tasavarahtely"}
```

```{.tuloste tiedosto="esimerkit/04-remez.odotettu"}
```

Luvun 1 vaatimus täyttyy 46 kertoimella, kun Kaiserin ikkuna tarvitsi
61. Säästö on neljännes laskennasta. Kuvasta näkyy syy: Kaiser-suotimen
sivukeilat laskevat taajuuden mukana kohti −75 dB:ä, mutta
tasavärähtelevä suodin käyttää koko sallitun −60 dB:n.

![Luvun 1 vaatimus (mustat rajat) Kaiserin ikkunalla ja
Parks–McClellanin algoritmilla.](kuvat/fir.png){width=100%}

Algoritmilla on heikkouksia. Se voi jättää siirtymäkaistalle huipun,
koska siellä ei ole vaatimuksia, ja hyvin pitkillä suotimilla (yli noin
500 kerrointa) se ei aina suppene. Siirtymäkaistan huippu havaitaan
tarkistamalla vaste myös siellä. Pitkissä suotimissa käytetään
ikkunamenetelmää tai pienimmän neliösumman menetelmää `firls`, joka
minimoi virheen energian eikä huippua.

| Menetelmä | Funktio | Vahvuus | Heikkous |
|----------------|----------|------------------------------|------------------------------|
| ikkuna | `firwin` | ennustettava, nopea, toimii aina | $\delta_p = \delta_s$, pidempi |
| taajuusnäytteistys | `firwin2` | mielivaltainen vaste | ei optimaalinen |
| Parks–McClellan | `remez` | lyhin annetuilla toleransseilla | voi epäonnistua, tarkista siirtymä |
| pienin neliösumma | `firls` | pieni kokonaisvirhe, vakaa | suurin poikkeama ei hallinnassa |

## Lineaarivaiheiset tyypit

Symmetrinen tai antisymmetrinen FIR on lineaarivaiheinen. Pituuden
parillisuus ja symmetrian laji jakavat suotimet neljään tyyppiin.
Symmetria pakottaa nollia pisteisiin $z = 1$ (taajuus 0) tai $z = -1$
(Nyquistin taajuus):

| Tyyppi | Pituus | Symmetria | Pakotettu nolla | Ei sovi |
|--------|----------|-----------|----------------|-------------------------|
| I | pariton | parillinen | ei | (kaikki käy) |
| II | parillinen | parillinen | $z = -1$ | ylipäästö, kaistanesto |
| III | pariton | pariton | $z = \pm 1$ | alipäästö, ylipäästö |
| IV | parillinen | pariton | $z = 1$ | alipäästö |

Antisymmetrisiä tyyppejä III ja IV käytetään derivaattoreissa ja
Hilbert-muuntimissa, joissa vaste nollataajuudella kuuluukin olla nolla.
Tarkistetaan väitteet satunnaisilla kertoimilla:

```{.python tiedosto="esimerkit/04-tyypit.py" osa="tyypit"}
```

```{.python tiedosto="esimerkit/04-tyypit.py" osa="ylipaasto"}
```

```{.tuloste tiedosto="esimerkit/04-tyypit.odotettu"}
```

Satunnaisillakin kertoimilla pakotetut nollat ovat paikallaan, ja
ryhmäviive on tasan $(N-1)/2$ kaikilla taajuuksilla. Tyypin II ja IV
viive on puolikas näyte. Siitä on haittaa, kun suodatettu signaali
yhdistetään suodattamattomaan: puolen näytteen siirtoa ei voi korjata
kokonaislukuviiveellä. `firwin` kieltäytyy tekemästä parillisen
pituuden ylipäästöä, koska vaste Nyquistin taajuudella olisi pakosta
nolla.

## Käytännössä

- **Käytä `remez`-funktiota**, kun laskenta maksaa, ja anna painot
  toleranssien suhteena $\delta_p/\delta_s$.
- **Tarkista myös siirtymäkaista** Parks–McClellanin suotimesta;
  algoritmi ei rajoita sitä.
- **Käytä `firwin2`-funktiota** taajuuskorjaimiin ja muihin vasteisiin,
  jotka eivät ole päästö- ja estokaistoja.
- **Valitse tyyppi I**, ellei ole syytä muuhun: se sopii kaikkiin
  suotimiin, ja viive on kokonaisluku.
- **Säilytä kertoimet symmetrisinä.** Lineaarinen vaihe säilyy myös
  kvantisoinnin jälkeen, kun symmetriset kertoimet pyöristetään samaan
  arvoon.

## Itsearviointi

- Osaat suunnitella mielivaltaisen amplitudivasteen
  taajuusnäytteistyksellä ja selittää, miksi vaste aaltoilee pisteiden
  välissä.
- Osaat selittää tasavärähtelyn ja sen, miksi tasavärähtelevä suodin on
  lyhyempi kuin ikkunoitu.
- Osaat laskea Parks–McClellanin painot toleransseista ja etsiä
  lyhimmän vaatimuksen täyttävän pituuden.
- Osaat nimetä lineaarivaiheisten suotimien tyypit ja kertoa, mihin
  suotimiin kukin ei sovi.
