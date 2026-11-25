# FIR: ikkunamenetelmä

FIR-suodin on painotettu summa viimeisistä $N$ näytteestä:

$$y[n] = \sum_{k=0}^{N-1} h[k]\,x[n-k].$$

Se on aina stabiili, ja symmetrisillä kertoimilla sen vaihe on
lineaarinen, joten se viivästää kaikkia taajuuksia yhtä paljon. Hinta on
pituus: jyrkkä FIR tarvitsee kymmeniä tai satoja kertoimia, kun
vastaava IIR-suodin selviää kymmenellä. Tämä luku johtaa yksinkertaisimman
suunnittelumenetelmän, jolla saadaan useimpiin tarpeisiin riittävä
suodin.

## Ideaalinen suodin ja katkaisu

Ideaalinen alipäästö päästää taajuudet rajaan $f_c$ asti
muuttumattomina ja poistaa kaiken sen yläpuolelta. Sen impulssivaste
saadaan käänteisellä Fourier-muunnoksella suorakaiteesta, ja se on
sinc-funktio:

$$h_{\text{id}}[n] = 2 f_c \operatorname{sinc}(2 f_c n), \qquad
f_c \text{ suhteessa näytetaajuuteen}.$$

Jono on ääretön molempiin suuntiin, joten sitä ei voi toteuttaa.
Ilmeinen ratkaisu on ottaa keskeltä $N$ näytettä ja siirtää ne
alkamaan nollasta. Siirto tekee suotimesta kausaalisen ja lisää
viiveen $(N-1)/2$.

```{.python tiedosto="esimerkit/03-gibbs.py" osa="ideaalinen"}
```

Katkaisu on kertolasku suorakaideikkunalla, ja aikatason kertolasku on
taajuustason konvoluutio. Ideaalinen suorakaide konvoloituu ikkunan
spektrin kanssa: jyrkkä reuna leviää siirtymäkaistaksi, ja ikkunan
sivukeilat näkyvät aaltoiluna. Mitataan, mitä pidentäminen tekee.

```{.python tiedosto="esimerkit/03-gibbs.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/03-gibbs.odotettu"}
```

Siirtymäkaista kapenee pituuden mukana, mutta ylitys pysyy 9 %:ssa ja
vaimennus 21 dB:ssä. Tämä on **Gibbsin ilmiö**, joka johdettiin taidossa
*Kompleksiluvut ja Fourier-analyysi*: epäjatkuvan funktion katkaistu
Fourier-sarja ylittää hypyn aina noin 9 %. Siellä katkaistiin
kanttiaallon sarja, tässä katkaistaan impulssivaste, ja ylitys näkyy
taajuusvasteessa. Pidentäminen ei siis auta vaimennukseen. Avuksi
tarvitaan toinen ikkuna.

## Ikkunat

Pehmeä ikkuna kaventaa nollaa kohti reunoillaan, jolloin sen
sivukeilat ovat matalampia ja suotimen vaimennus suurempi. Pääkeila on
kuitenkin leveämpi, joten siirtymäkaista levenee. Ikkunan valinta on
kompromissi vaimennuksen ja siirtymäkaistan välillä, ja pituus säätää
siirtymäkaistaa vaimennuksesta riippumatta.

```{.python tiedosto="esimerkit/03-ikkunat.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-ikkunat.odotettu"}
```

Sarake $\delta$ on estokaistan suurin poikkeama, ja sama poikkeama näkyy
päästökaistalla: ikkunamenetelmässä $\delta_p \approx \delta_s$.
Viimeinen sarake on siirtymäkaistan leveys kerrottuna pituudella, joten
se ei riipu $N$:stä. Taulukosta voi lukea suunnittelusäännön: Hann-ikkuna
antaa 44 dB ja siirtymäkaistan noin $3{,}2/N$, Blackman 75 dB ja
noin $6{,}9/N$. Taulukon arvot on mitattu tämän luvun määritelmillä;
kirjallisuuden luvut poikkeavat hieman, koska siirtymäkaistan reunat
määritellään eri tavoin. Luvut ovat *suotimen* vaimennuksia. Taidon
*Signaalit ja järjestelmät* ikkunataulukossa Hannin kohdalla on −31 dB,
koska siellä mitataan ikkunan oman spektrin korkein sivukeila; suotimen
estokaista syntyy, kun sivukeilat summautuvat konvoluutiossa, ja tulos
on eri luku.

![Vasemmalla suorakaidekatkaisun amplitudivaste rajataajuuden ympärillä
kolmella pituudella: reuna jyrkkenee, mutta ylitys ei pienene. Oikealla
kolme ikkunaa samalla pituudella: matalammat sivukeilat maksetaan
leveämmällä siirtymäkaistalla.](kuvat/katkaisu.png){width=95%}

Ikkunoiden vaimennus on kiinteä. Jos vaatimus on 60 dB, Hann ei riitä
ja Blackman tuhlaa kertoimia. Tähän tarvitaan säädettävä ikkuna.

## Kaiserin ikkuna

Kaiserin ikkunassa on parametri $\beta$, joka liukuu suorakaiteesta
($\beta = 0$) kohti Blackmania ja sen yli. James Kaiser johti
kokeellisesti kaavat, jotka antavat vaatimuksista suoraan ikkunan
parametrin ja pituuden. Kun vaimennus on $A$ desibeleinä ja
siirtymäkaistan leveys $\Delta f$ suhteessa näytetaajuuteen,

$$\beta = \begin{cases}
0{,}1102\,(A - 8{,}7), & A > 50,\\
0{,}5842\,(A - 21)^{0{,}4} + 0{,}07886\,(A - 21), & 21 \le A \le 50,\\
0, & A < 21,
\end{cases}
\qquad
N \approx \frac{A - 7{,}95}{2{,}285 \cdot 2\pi\,\Delta f} + 1.$$

```{.python tiedosto="esimerkit/03-kaiser.py" osa="kaavat"}
```

```{.python tiedosto="esimerkit/03-kaiser.py" osa="vertaa"}
```

SciPyn `kaiserord` laskee samat kaavat. Sen siirtymäkaista annetaan
suhteessa Nyquistin taajuuteen, mikä on tavallinen virheen lähde: sama
luku suhteessa näytetaajuuteen antaa puolet liian lyhyen suotimen.

Kaavat ovat arvioita, eivät takuita. Suodin tarkistetaan, ja tarvittaessa
pituutta kasvatetaan, kunnes vaatimus täyttyy. Pituus pidetään
parittomana, jolloin suodin on tyyppiä I (luku 4) ja viive on kokonainen
määrä näytteitä.

```{.python tiedosto="esimerkit/03-kaiser.py" osa="iteroi"}
```

```{.tuloste tiedosto="esimerkit/03-kaiser.odotettu"}
```

Arvio jäi vajaaksi 0,4 dB, ja vaimennus ei edes kasva tasaisesti
pituuden mukana: 211 kerrointa on huonompi kuin 209. Syy on se, että
sivukeilat osuvat eri pituuksilla eri kohtiin suhteessa estokaistan
reunaan. Siksi tarkistussilmukka on osa suunnittelua, ei valinnainen
lisä.

Ikkunamenetelmän vahvuudet ovat ennustettavuus ja yksinkertaisuus.
Kertoimet voi laskea jopa laitteessa ajon aikana, esimerkiksi kun
käyttäjä säätää rajataajuutta. Heikkous on se, että $\delta_p$ ja
$\delta_s$ ovat samat. Jos päästökaistalle riittäisi väljempi
toleranssi, ikkunamenetelmä ei osaa käyttää sitä hyväksi. Seuraava luku
esittelee menetelmän, joka osaa.

## Käytännössä

- **Aloita Kaiserin ikkunasta.** `kaiserord` ja `firwin` antavat
  vaatimuksista kertoimet kahdella kutsulla, ja tulos on ennustettava.
- **Tarkista aina ja iteroi pituutta.** Kaavat ovat arvioita, ja
  vaimennus vaihtelee pituuden mukana epätasaisesti.
- **Muista SciPyn taajuusyksiköt.** `kaiserord` ottaa siirtymäkaistan
  suhteessa Nyquistin taajuuteen; `firwin` ja `freqz` hertseinä, kun
  `fs` annetaan.
- **Käytä paritonta pituutta**, ellei ole syytä muuhun: kokonaislukuviive
  helpottaa signaalien kohdistamista, ja ylipäästö on mahdollinen.
- **Älä yritä parantaa vaimennusta pidentämällä suorakaideikkunaa.**
  Gibbsin ilmiö pitää sen 21 dB:ssä pituudesta riippumatta.

## Itsearviointi

- Osaat johtaa ideaalisen alipäästön impulssivasteen ja selittää, mitä
  katkaisu tekee taajuusvasteelle.
- Osaat selittää Gibbsin ilmiön ja sen, miksi pidentäminen ei poista
  sitä.
- Osaat valita ikkunan vaimennusvaatimuksen perusteella ja arvioida
  siirtymäkaistan leveyden pituudesta.
- Osaat laskea Kaiserin ikkunan parametrit kaavoista ja suunnitella
  vaatimuksen täyttävän suotimen iteroimalla.
