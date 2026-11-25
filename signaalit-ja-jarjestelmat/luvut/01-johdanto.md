# Johdanto {.runko-johdanto}

Tietokone ei näe jatkuvaa signaalia. Se näkee jonon lukuja, jotka
analogia–digitaalimuunnin on mitannut tasaisin välein: äänikortin 48 000
näytettä sekunnissa, kiihtyvyysanturin sata näytettä sekunnissa tai
radiovastaanottimen miljoonat kompleksiset näytteet. Ohjelma käsittelee
jonoa ja tuottaa uuden jonon, joka on tasoitettu, suodatettu, viivästetty
tai jaettu kaistoihin. Tällainen ohjelma on **järjestelmä**, ja tämä
tutoriaali opettaa, miten järjestelmiä kuvataan, analysoidaan ja testataan.

Tutoriaali keskittyy **lineaarisiin aikainvariantteihin** eli LTI-
järjestelmiin. Ne ovat tärkeitä kahdesta syystä. Ensinnäkin lähes
kaikki käytännön suotimet ovat sellaisia: liukuva keskiarvo, eksponentiaalinen
tasoitus, kaiku, taajuuskorjain ja lovisuodin. Toiseksi niiden koko
käyttäytyminen on kuvattavissa yhdellä jonolla, **impulssivasteella**.
Kun impulssivaste tunnetaan, järjestelmän ulostulo mille tahansa syötteelle
saadaan konvoluutiolla, ja impulssivasteen Fourier-muunnos eli
**taajuusvaste** kertoo, mitä järjestelmä tekee kullekin taajuudelle.

## Ensimmäinen esimerkki: musta laatikko

Seuraava funktio on anturin tasoitin. Kuvitellaan, ettemme tunne sen
sisältöä, vaan voimme vain syöttää sille jonoja ja katsoa, mitä tulee
ulos.

```{.python tiedosto="esimerkit/01-musta-laatikko.py" osa="laatikko"}
```

Syötetään laatikolle yksi ykkösnäyte ja muuten nollia. Vastaus on
impulssivaste $h$. Sen avulla ennustetaan laatikon vastaus satunnaiseen
syötteeseen konvoluutiolla `numpy.convolve` ja verrataan ennustetta
laatikon todelliseen vastaukseen.

```{.python tiedosto="esimerkit/01-musta-laatikko.py" osa="impulssivaste"}
```

Sitten syötetään laatikolle siniaaltoja ja mitataan, kuinka paljon
niiden amplitudi pienenee. Samat luvut lasketaan impulssivasteesta
kaavalla $H(f) = \sum_k h[k]\,e^{-2\pi i f k / f_s}$.

```{.python tiedosto="esimerkit/01-musta-laatikko.py" osa="taajuusvaste"}
```

```{.tuloste tiedosto="esimerkit/01-musta-laatikko.odotettu"}
```

Ennuste osuu, ja mitattu vahvistus on sama kuin impulssivasteesta
laskettu. Laatikko päästää hitaat muutokset läpi ja vaimentaa nopeita: se
on alipäästösuodin. Kaikki tämä selvisi laatikkoa avaamatta. Koko
tutoriaali on tämän esimerkin laajennus: miksi impulssivaste riittää
(luku 4), miten se lasketaan differenssiyhtälöstä (luku 6), miten sen
napoja ja nollia luetaan (luku 7) ja miten taajuusvastetta tulkitaan
(luku 8).

## Esitiedot ja rajaus

Lukija osaa Pythonin ja NumPyn perusteet (taito *Python
työkaluohjelmointiin*) sekä kompleksiluvut, Eulerin kaavan,
Fourier-muunnoksen ja diskreetin Fourier-muunnoksen idean (taito
*Kompleksiluvut ja Fourier-analyysi*). Sen taidon konvoluutio-, DFT- ja
FFT-luvut ovat tämän tutoriaalin suoria edeltäjiä, eikä niiden asioita
toisteta. Tässä keskitytään siihen, mitä ne jättivät auki: näytteistykseen,
järjestelmien ominaisuuksiin, Z-muunnokseen ja spektrianalyysin
käytännön kysymyksiin.

Suodinsuunnittelu (FIR-ikkunamenetelmä, IIR-suotimet bilineaarimuunnoksella,
kertoimien kvantisointi ja monitaajuuskäsittely) on taidon *Digitaalinen
signaalinkäsittely* aihe. Tässä käytetään valmiita suunnittelufunktioita
(`butter`, `firwin`, `iirnotch`) ja keskitytään siihen, miten tuloksena
saatua suodinta analysoidaan. Jatkuva-aikaisia järjestelmiä ja
Laplace-muunnosta käsitellään vain sen verran kuin näytteistys vaatii;
ne sekä s-tason ja z-tason yhteys ovat taidossa *Differentiaaliyhtälöt
ja Laplace-muunnos*. Modulaatiot ja vastaanottimet ovat taitojen
*Digitaalinen tiedonsiirto* ja *Ohjelmistoradio* aiheita.

| Luku | Kysymys |
|------|---------|
| Diskreettiaikaiset signaalit | Mitä jonoja on, ja milloin sini on jaksollinen? |
| Näytteistys ja aliasointi | Milloin näytteistä saa alkuperäisen takaisin? |
| LTI-järjestelmät | Mitä lineaarisuus ja aikainvarianssi takaavat? |
| Konvoluutio järjestelmissä | Miten suodatus tehdään matriisina ja lohkoittain? |
| Differenssiyhtälöt | Miten rekursiivinen suodin toimii? |
| Z-muunnos | Mitä navat ja nollat kertovat? |
| Taajuusvaste | Mitä suodin tekee kullekin taajuudelle? |
| DFT käytännössä | Miksi spektri vuotaa, ja mitä ikkuna tekee? |
| Lyhytaikainen spektri | Miten seurataan muuttuvaa taajuutta? |
| Testaus | Miten signaalinkäsittelykoodi testataan pytestillä? |

## Merkinnät

| Merkintä | Tarkoitus |
|----------|-----------|
| $x[n]$, $y[n]$ | diskreettiaikainen jono, $n$ kokonaisluku |
| $x(t)$ | jatkuva-aikainen signaali |
| $f_s$, $T_s = 1/f_s$ | näytetaajuus (Hz) ja näyteväli (s) |
| $\delta[n]$, $u[n]$ | yksikköimpulssi ja yksikköaskel |
| $h[n]$ | impulssivaste |
| $H(z)$ | siirtofunktio (Z-muunnos) |
| $H(e^{i\omega})$ | taajuusvaste, $\omega = 2\pi f / f_s$ radiaaneina näytettä kohti |
| $b$, $a$ | differenssiyhtälön kertoimet, SciPyn nimet |

SciPy ilmoittaa taajuuden joko normitettuna (oletuksena 1 tarkoittaa
Nyquistin taajuutta $f_s/2$) tai hertseinä, jos funktiolle annetaan
argumentti `fs`. Tässä tutoriaalissa `fs` annetaan aina, kun taajuudet
ovat hertsejä, jotta normitukset eivät sekoitu.

## Työkalut

Esimerkit ovat Python 3.12 -ohjelmia, jotka käyttävät NumPya ja SciPyn
modulia `scipy.signal`. Ruff ja mypy (`--strict`, tyypitykset paketista
`scipy-stubs`) tarkistavat jokaisen esimerkin, ja testaaja ajaa sen ja
vertaa tulostetta tallennettuun. Satunnaisuus tuotetaan kiinteällä
siemenellä, ja liukulukujen vertailu tehdään toleranssilla, joten tulosteet
ovat samat joka koneella. Luvun 11 kirjasto testataan pytestillä.
Kehityskontissa (`.devcontainer/signaalit-ja-jarjestelmat`) on kaikki
tarvittava.

Yksittäinen esimerkki ajetaan komennolla
`python3 esimerkit/03-aliasointi.py`. Kaksi esimerkkiä kirjoittaa
äänitiedoston (WAV) työhakemistoon, jotta tuloksen voi kuunnella.
Tutoriaalin kuvat piirretään matplotlibilla skriptillä
`kuvat/piirra.py` (`make kuvat`), ja niiden luvut lasketaan samoin kuin
testatuissa esimerkeissä.

