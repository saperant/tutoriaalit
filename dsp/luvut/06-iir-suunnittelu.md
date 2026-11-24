# IIR-suunnittelu

IIR-suodin käyttää aiempia ulostuloja, joten sen impulssivaste on
ääretön ja sen navat voivat olla muualla kuin origossa. Navat tekevät
jyrkän suotimen halvaksi: luvun 1 vaatimus täyttyy kuudennen asteen
elliptisellä suotimella 15 kertolaskulla näytettä kohti, kun FIR
tarvitsi 46.
Hintana on epälineaarinen vaihe ja mahdollinen epästabiilius. IIR-suotimia
ei yleensä suunnitella suoraan Z-tasossa, vaan analogisten suotimien
vuosikymmeniä vanhoista kaavoista, jotka muunnetaan digitaalisiksi.

## Analogiset prototyypit

Analogisen suotimen teoria on valmis: jokaiselle vaatimukselle on kaava,
joka antaa pienimmän asteen ja napojen paikat. Neljä klassista
suodinperhettä eroaa siinä, missä ne sallivat aaltoilun:

| Perhe | Päästökaista | Estokaista | Erityistä |
|----------------|--------------|--------------|------------------------------|
| Butterworth | tasainen | monotoninen | korkein aste, tasaisin vaste |
| Chebyshev I | aaltoileva | monotoninen | jyrkempi kuin Butterworth |
| Chebyshev II | tasainen | aaltoileva | nollat estokaistalla |
| elliptinen (Cauer) | aaltoileva | aaltoileva | pienin aste annetulle vaatimukselle |

SciPyssä jokaisella perheellä on suunnittelufunktio ja asteluvun
arvioija: `butter` ja `buttord`, `cheby1` ja `cheb1ord`, `cheby2` ja
`cheb2ord` sekä `ellip` ja `ellipord`. Arvioija palauttaa pienimmän
asteen ja rajataajuuden, jolla vaatimus täyttyy.

## Bilineaarimuunnos

Analoginen siirtofunktio $H_a(s)$ muunnetaan digitaaliseksi
sijoittamalla

$$s = 2 f_s \,\frac{1 - z^{-1}}{1 + z^{-1}}.$$

Muunnos kuvaa koko imaginaariakselin $s = i\Omega$ yksikköympyrälle ja
vasemman puolitason sen sisäpuolelle. Siksi stabiili analoginen suodin
tuottaa aina stabiilin digitaalisen, eikä aliasointia synny. Hinta on
taajuusakselin **vääristyminen**: analoginen taajuus $\Omega$ ja
digitaalinen $\omega$ liittyvät toisiinsa kaavalla

$$\Omega = 2 f_s \tan(\omega/2).$$

Pienillä taajuuksilla $\tan(\omega/2) \approx \omega/2$, ja kuvaus on
lähes identtinen. Nyquistin taajuutta lähestyttäessä koko äärettömän
pitkä analoginen akseli puristuu äärelliseen väliin.

```{.python tiedosto="esimerkit/06-bilineaari.py" osa="muunnos"}
```

```{.python tiedosto="esimerkit/06-bilineaari.py" osa="mittaa"}
```

```{.tuloste tiedosto="esimerkit/06-bilineaari.odotettu"}
```

Ilman korjausta 15 kHz:n RC-suodin päätyy 11,9 kHz:iin. **Esivääristys**
korjaa tärkeimmän taajuuden: analoginen rajataajuus valitaan kaavalla
$\Omega_c = 2 f_s \tan(\pi f_c / f_s)$, jolloin se kuvautuu tasan
haluttuun digitaaliseen taajuuteen. Muut taajuudet vääristyvät
edelleen, mutta rajataajuus on suotimen tärkein ominaisuus.

SciPyn suunnittelufunktiot tekevät esivääristyksen itse, kun niille
annetaan `fs`. Esivääristystä tarvitaan, kun analoginen suodin
muunnetaan itse, esimerkiksi analogisen piirin mallista tai
audiolaitteen kytkentäkaaviosta. Myös R. Bristow-Johnsonin
biquad-kaavat, joita käytetään luvussa 7, ovat esivääristettyjä
bilineaarimuunnoksia.

## Saman vaatimuksen neljä ratkaisua

Suunnitellaan luvun 1 vaatimus kaikilla neljällä perheellä ja mitataan
aste, toteutunut vaatimus ja ryhmäviive.

```{.python tiedosto="esimerkit/06-tyypit.py" osa="asteet"}
```

```{.tuloste tiedosto="esimerkit/06-tyypit.odotettu"}
```

![Neljän suodinperheen kolme suodinta saman vaatimuksen täyttävinä
(Chebyshev II on jätetty pois selkeyden vuoksi).](kuvat/iir.png){width=100%}

Elliptinen suodin on kuudetta astetta, Butterworth yhdeksättätoista.
Kaikki täyttävät vaatimuksen, mutta niiden ryhmäviive eroaa. Viive
500 Hz:llä on 5–15 näytettä, ja suurimmillaan, päästökaistan reunalla,
11–33 näytettä. Vertailun vuoksi 46 kertoimen FIR viivästää kaikkia
taajuuksia tasan 22,5 näytettä. IIR-suodin on siis myös nopeampi
matalilla taajuuksilla, mutta viive vaihtelee taajuuden mukana.

Valinta tehdään sovelluksen mukaan:

| Tarve | Valinta |
|----------------------------------------|----------------------------------------|
| pienin laskenta, vaihe yhdentekevä | elliptinen |
| tasainen päästökaista, esimerkiksi mittaus | Butterworth tai Chebyshev II |
| aaltomuoto ja tasainen viive | FIR tai Bessel |
| pieni viive matalilla taajuuksilla | IIR |
| tallennettu data, viive nolla | IIR ja `filtfilt` (taito *Signaalit ja järjestelmät*) |

Bessel-suodin (`signal.bessel`) on viides perhe. Sen ryhmäviive on
mahdollisimman tasainen, mutta vaimennus on heikko, joten sitä käytetään
pulssien muodon säilyttämiseen eikä jyrkkään suodatukseen.

## Käytännössä

- **Anna `fs` aina SciPyn IIR-funktioille.** Silloin rajataajuudet
  ovat hertsejä, ja esivääristys tehdään oikein.
- **Esivääristä itse**, kun muunnat analogisen siirtofunktion
  bilineaarimuunnoksella: $\Omega_c = 2 f_s \tan(\pi f_c/f_s)$.
- **Käytä asteluvun arvioijaa** (`ellipord` ym.) ja tarkista tulos
  samalla tarkistusfunktiolla kuin FIR-suotimet.
- **Pyydä IIR-suotimet aina muodossa `output="sos"`.** Korkea-asteinen
  siirtofunktio yhtenä polynomina on numeerisesti hauras (luku 7).
- **Valitse elliptinen**, kun laskenta ratkaisee, ja tarkista silloin,
  että ryhmäviiveen vaihtelu on sovellukselle hyväksyttävä.

## Itsearviointi

- Osaat nimetä neljä klassista suodinperhettä ja kertoa, missä kukin
  sallii aaltoilun.
- Osaat selittää bilineaarimuunnoksen, taajuusakselin vääristymisen ja
  esivääristyksen kaavan.
- Osaat suunnitella annetun vaatimuksen täyttävän IIR-suotimen
  pienimmällä asteella ja tarkistaa sen.
- Osaat valita FIR- ja IIR-suotimen välillä laskennan, viiveen ja
  vaiheen perusteella.
