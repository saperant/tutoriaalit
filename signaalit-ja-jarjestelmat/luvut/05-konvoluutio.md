# Konvoluutio järjestelmissä

Taidossa *Kompleksiluvut ja Fourier-analyysi* konvoluutio määriteltiin
ja toteutettiin silmukoilla, sen yhteys Fourier-muunnokseen todistettiin,
ja syklinen konvoluutio erotettiin lineaarisesta. Tässä luvussa
konvoluutiota käytetään järjestelmän ulostulon laskentaan kolmella
käytännön tavalla: matriisitulona, virtaavana lohkokäsittelynä ja
korrelaationa, joka etsii tunnetun signaalin kohinan seasta.

## Konvoluutio matriisitulona

Konvoluutio on lineaarinen kuvaus syötejonosta ulostulojonoon, joten
äärellisillä jonoilla se on matriisitulo $y = Hx$. Matriisin
sarakkeet ovat impulssivasteen siirrettyjä kopioita, ja jokaisella
lävistäjällä on sama arvo. Tällainen matriisi on **Toeplitz-matriisi**,
ja aikainvarianssi näkyy juuri tässä rakenteessa.

```{.python tiedosto="esimerkit/05-matriisi.py" osa="toeplitz"}
```

Matriisiesitys ei ole tehokas tapa laskea konvoluutiota, mutta se tuo
lineaarialgebran työkalut käyttöön. Jos kanava $h$ tunnetaan ja
ulostulo on mitattu, syöte voidaan ratkaista pienimmän neliösumman
tehtävänä. Tämä on **dekonvoluutio**, ja sitä käytetään esimerkiksi
kanavan taajuuskorjauksessa ja kuvan terävöinnissä.

```{.python tiedosto="esimerkit/05-matriisi.py" osa="dekonvoluutio"}
```

```{.tuloste tiedosto="esimerkit/05-matriisi.odotettu"}
```

Ehtoluku (taito *Lineaarialgebra*) kertoo, kuinka paljon mittauskohina
voimistuu ratkaisussa.
Tässä se on pieni, koska kanava ei vaimenna mitään taajuutta voimakkaasti.
Jos kanavan taajuusvasteessa on nolla, vastaava taajuus on kadonnut
lopullisesti, ehtoluku kasvaa rajatta, ja dekonvoluutio vahvistaa
kohinaa. Silloin ratkaisua on regularisoitava, mistä esimerkki on
Wiener-suodin.

## Virtaava käsittely lohkoittain

Reaaliaikainen ohjelma ei näe koko signaalia kerralla. Äänikortti
toimittaa lohkon, esimerkiksi 128 näytettä, ja ohjelman on palautettava
saman verran suodatettuja näytteitä ennen seuraavan lohkon saapumista.
Konvoluution tulos on pidempi kuin syöte: lohkon $L$ näytettä ja
impulssivasteen $M$ kerrointa tuottavat $L + M - 1$ näytettä. Viimeiset
$M - 1$ näytettä kuuluvat seuraavan lohkon alkuun. **Overlap-add** tallettaa
tämän hännän ja lisää sen seuraavan lohkon alkuun:

```{.python tiedosto="esimerkit/05-lohkot.py" osa="overlap-add"}
```

SciPyn `lfilter` hoitaa saman toisin. Se palauttaa suotimen
**tilan** `zi`, joka sisältää kaiken, mitä suodin muistaa menneestä, ja
seuraava kutsu jatkaa siitä. Tila on se, mikä tekee lohkoittaisesta
suodatuksesta täsmälleen saman kuin kerralla suodatuksen.

```{.python tiedosto="esimerkit/05-lohkot.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/05-lohkot.odotettu"}
```

Viimeinen rivi näyttää yleisen virheen: kun jokainen lohko suodatetaan
erikseen, suodin unohtaa edellisen lohkon, ja jokaisen lohkon alkuun
tulee $M - 1$ väärää näytettä. Äänessä virhe kuuluu napsahduksina
lohkon välein, ja mittausdatassa se näkyy jaksollisena häiriönä, jonka
jakso on lohkon pituus. Pitkillä impulssivasteilla lohkot lasketaan
FFT:llä (luku 9).

## Korrelaatio ja viiveen arviointi

**Ristikorrelaatio** mittaa, kuinka paljon kaksi jonoa muistuttavat
toisiaan eri siirroilla:

$$r_{xy}[l] = \sum_n x[n + l]\,y[n].$$

Se on konvoluutio, jossa toinen jono on käännetty ympäri:
$r_{xy} = x * y[-n]$. Siksi korrelaatio on myös LTI-suodatus, ja sen
suodinta kutsutaan **sovitetuksi suotimeksi**: tunnetun pulssin
käännetty kopio maksimoi signaali–kohinasuhteen hetkellä, jolloin pulssi
on kokonaan vastaanotettu. Tutka, kaikuluotain, GPS ja langattoman
kehyksen tahdistus etsivät kaikki tunnettua pulssia korrelaatiolla.

```{.python tiedosto="esimerkit/05-korrelaatio.py" osa="korrelaatio"}
```

```{.tuloste tiedosto="esimerkit/05-korrelaatio.odotettu"}
```

Yksittäisen näytteen signaali–kohinasuhde on negatiivinen, joten pulssia
ei näe silmällä. Korrelaatio summaa 400 näytteen energian, ja
käsittelyvahvistus $10\log_{10} 400 \approx 26$ dB nostaa huipun
selvästi kohinan yläpuolelle. Pulssina on taajuuspyyhkäisy, koska sen
autokorrelaatio on kapea: huippu on terävä, ja viive saadaan näytteen
tarkkuudella. `scipy.signal.correlation_lags` antaa jokaista
korrelaation alkiota vastaavan siirron, joten indeksejä ei tarvitse
laskea käsin.

## Käytännössä

- **Säilytä suotimen tila lohkojen välillä.** Käytä `lfilter`-funktion
  `zi`-argumenttia tai overlap-add-tekniikkaa, ja testaa, että
  lohkoittainen tulos on sama kuin kerralla laskettu.
- **Testaa lohkokäsittely useilla lohkopituuksilla**, myös pituudella 1
  ja lohkolla, joka on lyhyempi kuin impulssivaste.
- **Käytä korrelaatiota tunnetun signaalin etsimiseen.** Valitse
  pulssi, jonka autokorrelaatio on kapea (pyyhkäisy, pseudosatunnainen
  jono), ja muunna indeksit siirroiksi `correlation_lags`-funktiolla.
- **Varo dekonvoluutiota.** Jos kanava vaimentaa jotain taajuutta
  voimakkaasti, suoran ratkaisun kohina räjähtää. Tarkista ehtoluku.

## Itsearviointi

- Osaat muodostaa konvoluutiomatriisin `scipy.linalg.toeplitz`-funktiolla
  ja selittää, miksi aikainvarianssi tuottaa Toeplitz-rakenteen.
- Osaat toteuttaa lohkoittaisen FIR-suodatuksen overlap-add-tekniikalla
  ja `lfilter`-funktion tilalla sekä tunnistaa tilan unohtamisen
  aiheuttaman virheen.
- Osaat arvioida viiveen ristikorrelaatiolla ja selittää sovitetun
  suotimen käsittelyvahvistuksen.
