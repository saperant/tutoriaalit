# LTI-järjestelmät ja impulssivaste

Järjestelmä on sääntö, joka muuttaa syötejonon $x$ ulostulojonoksi
$y = T\{x\}$. Ohjelmassa se on funktio taulukolta taulukolle tai olio,
joka käsittelee näytteitä virtana. Järjestelmien ominaisuudet ratkaisevat,
mitä työkaluja voi käyttää. Lineaariselle ja aikainvariantille
järjestelmälle riittää yksi mittaus, impulssivaste, ja kaikki muu
seuraa siitä. Tässä luvussa ominaisuudet määritellään ja testataan
numeerisesti, ja impulssivasteesta johdetaan konvoluutio ja
stabiilisuuden ehto.

## Ominaisuudet

| Ominaisuus | Määritelmä |
|------------|------------|
| lineaarisuus | $T\{a x_1 + b x_2\} = a T\{x_1\} + b T\{x_2\}$ |
| aikainvarianssi | jos $y[n] = T\{x\}[n]$, niin $T\{x[\cdot - n_0]\}[n] = y[n - n_0]$ |
| kausaalisuus | $y[n]$ riippuu vain arvoista $x[k]$, $k \le n$ |
| muistittomuus | $y[n]$ riippuu vain arvosta $x[n]$ |
| stabiilisuus (BIBO) | rajoitettu syöte tuottaa rajoitetun ulostulon |

**Lineaarisuus** sanoo, että vasteet summautuvat ja skaalautuvat. Se
pätee suotimille, mutta ei esimerkiksi tasasuuntaukselle, neliöinnille
tai saturaatiolle. **Aikainvarianssi** sanoo, että järjestelmä toimii
samalla tavalla joka hetki: viivästetty syöte tuottaa samalla tavalla
viivästetyn ulostulon. Ajasta riippuva vahvistus tai harvennus rikkoo
sen. **Kausaalisuus** on reaaliaikaisuuden ehto: tulevaisuutta ei voi
käyttää. Tallennettua dataa käsittelevä ohjelma voi kuitenkin olla
ei-kausaalinen, ja esimerkiksi nollavaiheinen `filtfilt` käyttää
tulevia näytteitä tarkoituksella.

## Ominaisuuksien testaus

Ominaisuudet ovat väitteitä kaikista syötteistä, joten niitä ei voi
todistaa kokeilemalla. Yksikin vastaesimerkki kuitenkin kumoaa
väitteen, ja satunnaisilla syötteillä vastaesimerkki löytyy yleensä
heti. Tämä on **ominaisuuspohjaista testausta**, ja se on
signaalinkäsittelykoodin tehokkain testaustapa (luku 11).

Testattavat järjestelmät:

```{.python tiedosto="esimerkit/04-ominaisuudet.py" osa="jarjestelmat"}
```

Testit syöttävät satunnaisia jonoja kiinteällä siemenellä ja vertaavat
toleranssilla. Aikainvarianssitesti vertaa vain viiveen jälkeisiä
näytteitä, koska äärellinen taulukko alkaa aina jostain:
siirretyn syötteen alkuun tulevat nollat eivät kuulu alkuperäiseen
signaaliin.

```{.python tiedosto="esimerkit/04-ominaisuudet.py" osa="testit"}
```

```{.python tiedosto="esimerkit/04-ominaisuudet.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/04-ominaisuudet.odotettu"}
```

Tulokset ovat opettavaisia. Järjestelmä $y = 2x + 1$ näyttää
lineaariselta, mutta ei ole sitä, koska nollasyöte tuottaa nollasta
poikkeavan ulostulon. Se on **affiini**. Ajasta riippuva paino
$y[n] = n\,x[n]$ on lineaarinen mutta ei aikainvariantti. Edistys
$y[n] = x[n+1]$ on LTI, mutta ei kausaalinen. Summain on kaikkea kolmea,
mutta se ei ole stabiili, kuten pian nähdään.

## Impulssivaste ja konvoluutio

Olkoon $T$ lineaarinen ja aikainvariantti, ja olkoon $h = T\{\delta\}$
sen **impulssivaste**. Edellisen luvun mukaan
$x[n] = \sum_k x[k]\,\delta[n - k]$. Aikainvarianssin mukaan siirretyn
impulssin vaste on siirretty impulssivaste, ja lineaarisuuden mukaan
summan vaste on vasteiden summa. Siis

$$y[n] = \sum_k x[k]\,h[n - k] = (x * h)[n].$$

LTI-järjestelmän ulostulo on syötteen ja impulssivasteen konvoluutio.
Impulssivaste kuvaa järjestelmän täydellisesti. Konvoluution laskeminen
ja sen ominaisuudet käytiin läpi taidossa *Kompleksiluvut ja
Fourier-analyysi*; tässä sitä käytetään järjestelmien kielenä.

Kausaalisuus näkyy impulssivasteessa suoraan: LTI-järjestelmä on
kausaalinen täsmälleen silloin, kun $h[n] = 0$ kaikilla $n < 0$.
Muistiton LTI-järjestelmä on pelkkä vahvistus, $h = c\,\delta$.

**Askelvaste** $s = T\{u\}$ on usein helpompi mitata kuin impulssivaste,
koska askel on helppo tuottaa ja sen energia on suuri. Koska
$u[n] = \sum_{k \le n} \delta[k]$, askelvaste on impulssivasteen
juokseva summa: $s[n] = \sum_{k\le n} h[k]$. Esimerkiksi huoneen
akustiikka on likimain LTI-järjestelmä, jossa suoraa ääntä seuraa
heijastuksia:

```{.python tiedosto="esimerkit/04-impulssivaste.py" osa="kaiku"}
```

```{.python tiedosto="esimerkit/04-impulssivaste.py" osa="tunnistus"}
```

```{.tuloste tiedosto="esimerkit/04-impulssivaste.odotettu"}
```

Todellisessa mittauksessa impulssi on huono koesignaali, koska sen
energia on pieni ja kohina peittää vasteen. Siksi huoneita ja kanavia
mitataan pitkillä taajuuspyyhkäisyillä tai pseudosatunnaisilla
jonoilla, ja impulssivaste lasketaan korrelaatiolla (luku 5).

## BIBO-stabiilisuus

Järjestelmä on **BIBO-stabiili** (*bounded input, bounded output*), jos
jokainen rajoitettu syöte, $|x[n]| \le M$, tuottaa rajoitetun
ulostulon. LTI-järjestelmälle on yksinkertainen ehto:

$$\text{BIBO-stabiili} \iff \sum_n |h[n]| < \infty.$$

Riittävyys seuraa kolmioepäyhtälöstä:
$|y[n]| \le \sum_k |h[k]|\,|x[n-k]| \le M \sum_k |h[k]|$. Välttämättömyys
näkyy pahimmasta syötteestä. Valitaan $x[n - k] = \operatorname{sign}
h[k]$. Silloin jokainen termi on positiivinen, ja $y[n] = \sum_k
|h[k]|$. Jos summa hajaantuu, ulostulo kasvaa rajatta, vaikka syöte on
koko ajan välillä $[-1, 1]$.

```{.python tiedosto="esimerkit/04-stabiilisuus.py" osa="stabiilisuus"}
```

```{.tuloste tiedosto="esimerkit/04-stabiilisuus.odotettu"}
```

Summaimen impulssivaste on askel, eikä sen itseisarvosumma rajoitu:
vakiosyöte kasvattaa summaa loputtomasti. Vaste $1/(n+1)$ vaimenee
nollaan, mutta liian hitaasti: harmoninen sarja hajaantuu
logaritmisesti, ja pahin syöte kasvattaa ulostuloa rajatta. Vaste
$1/(n+1)^2$ on stabiili. Vaimeneminen nollaan ei siis riitä, vaan
summan on supettava. Rekursiivisten suotimien stabiilisuus luetaan
helpoimmin navoista (luku 7).

## Käytännössä

- **Tarkista, onko järjestelmä todella LTI**, ennen kuin käytät
  konvoluutiota tai taajuusvastetta. Saturaatio, kynnys, tasasuuntaus
  ja harvennus rikkovat oletukset.
- **Testaa ominaisuudet satunnaisilla syötteillä.** Lineaarisuus- ja
  aikainvarianssitesti löytää tilan nollaamatta jättämisen, globaalin
  laskurin ja indeksivirheet.
- **Mittaa askelvaste, jos impulssi on liian heikko.** Impulssivaste
  saadaan askelvasteen erotuksena: $h[n] = s[n] - s[n-1]$.
- **Integraattori ei ole stabiili.** Juokseva summa ajautuu, jos
  syötteessä on pienikin tasakomponentti. Käytännössä käytetään
  vuotavaa integraattoria, jonka napa on hieman yksikköympyrän sisällä.

## Itsearviointi

- Osaat määritellä lineaarisuuden, aikainvarianssin, kausaalisuuden ja
  BIBO-stabiiliuden sekä tunnistaa affiinin järjestelmän.
- Osaat testata järjestelmän ominaisuudet satunnaisilla syötteillä ja
  perustella, miksi testi voi vain kumota väitteen.
- Osaat johtaa konvoluution lineaarisuudesta ja aikainvarianssista sekä
  laskea askelvasteen impulssivasteesta.
- Osaat ratkaista impulssivasteen itseisarvosummasta, onko järjestelmä
  stabiili, ja muodostaa pahimman rajoitetun syötteen.
