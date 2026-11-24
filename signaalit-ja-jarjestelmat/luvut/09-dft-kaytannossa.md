# DFT ja FFT käytännössä

Diskreetti Fourier-muunnos (DFT) on taidossa *Kompleksiluvut ja
Fourier-analyysi* johdettu kannanvaihtona, ja sen indeksit, taajuudet ja
normitukset sekä FFT:n idea käytiin siellä läpi. Tässä luvussa DFT:tä
käytetään mittauslaitteena. Silloin nousevat esiin kysymykset, joihin
kannanvaihto ei vastaa: kuinka lähellä toisiaan olevat taajuudet
erottuvat, miksi yksittäinen sini levittäytyy koko spektriin, mitä
ikkuna tekee, mitä nollilla täyttäminen todella hyödyttää ja miten
kohinan tehospektri arvioidaan luotettavasti.

## Taajuusresoluutio ja vuotaminen

$N$ näytteen DFT antaa spektrin taajuuksilla $k f_s/N$. Väli
$f_s/N = 1/(N T_s)$ on mittausajan käänteisluku: sekunnin mittaus antaa
yhden hertsin välit, näytetaajuudesta riippumatta. Tämä on
**taajuusresoluutio**. Näytetaajuuden kasvattaminen laajentaa
taajuusaluetta, mutta ei tihennä sitä.

DFT olettaa, että $N$ näytettä toistuvat jaksollisesti. Jos ikkunaan
mahtuu kokonainen määrä jaksoja, toisto on saumaton, ja sini osuu
täsmälleen yhteen taajuusväliin. Muuten toistossa on hyppy, ja sinin
energia leviää kaikkiin väleihin. Tämä on **spektrin vuotaminen**
(*spectral leakage*). Lisäksi huipun korkeus pienenee, kun taajuus on
kahden välin puolivälissä. Tätä **aaltoiluhäviötä** (*scalloping loss*)
on suorakaideikkunalla enimmillään noin 3,9 dB.

```{.python tiedosto="esimerkit/09-vuotaminen.py" osa="vuotaminen"}
```

Kaksi lähellä toisiaan olevaa taajuutta erottuu vain, jos niiden
erotus on suurempi kuin noin yksi resoluutioväli. Esimerkissä soitetaan
yhtä aikaa sävelet 440 Hz ja 466 Hz, jotka ovat puolisävelaskeleen
päässä toisistaan.

```{.python tiedosto="esimerkit/09-vuotaminen.py" osa="vierekkaiset"}
```

```{.tuloste tiedosto="esimerkit/09-vuotaminen.odotettu"}
```

25 näytteen ikkunalla (40 Hz:n resoluutio) sävelet sulautuvat yhdeksi
huipuksi, vaikka spektri laskettiin tiheällä hilalla. Erottelukyky
riippuu mittausajasta eikä laskentapisteiden määrästä.

## Ikkunat

Vuotaminen johtuu ikkunan reunoista: suorakaiteen muotoinen leikkaus
on kertolasku suorakaidepulssilla, ja taajuustasossa se on konvoluutio
Dirichlet'n ytimellä, jonka sivukeilat vaimenevat hitaasti. Ikkunafunktio
kavennetaan reunoilta nollaan, jolloin hyppy katoaa ja sivukeilat
pienenevät. Hinta on leveämpi pääkeila, eli huonompi erottelukyky.

```{.python tiedosto="esimerkit/09-ikkunat.py" osa="ikkunat"}
```

![Ikkunoiden spektrit: suorakaiteen sivukeilat ovat korkeat, Hannin
ja Blackmanin matalat mutta pääkeila leveämpi.](kuvat/ikkunat.png){width=100%}

| Ikkuna | Pääkeila (välejä) | Suurin sivukeila | Tyypillinen käyttö |
|--------|-------------------|------------------|--------------------|
| suorakaide | 2 | $-13$ dB | kokonaiset jaksot, transientit |
| Hann | 4 | $-31$ dB | yleiskäyttö |
| Hamming | 4 | $-42$ dB | puhe, kapeat huiput |
| Blackman | 6 | $-58$ dB | suuri dynamiikka |

Ikkunan valinta näkyy, kun vahvan signaalin vieressä on heikko.
Suorakaideikkunan vuoto peittää 60 dB heikomman komponentin, mutta
Hannin ja Blackmanin ikkunoilla se erottuu taustasta.

```{.python tiedosto="esimerkit/09-ikkunat.py" osa="heikko"}
```

```{.tuloste tiedosto="esimerkit/09-ikkunat.odotettu"}
```

Ikkuna myös pienentää signaalia. Sen **koherentti vahvistus** on
ikkunan keskiarvo, Hannin ikkunalla 0,5. Kun sinin amplitudi luetaan
spektristä, huippu jaetaan ikkunan summalla eikä näytteiden määrällä.

## Nollilla täyttäminen

Nollilla täyttäminen (`numpy.fft.rfft(x, n=L)`, $L > N$) laskee saman
spektrin tiheämmästä hilasta. Se ei lisää tietoa eikä paranna
erottelukykyä, mutta se interpoloi spektriä, jolloin huipun paikka ja
korkeus löytyvät tarkemmin. Aaltoiluhäviö pienenee, koska jokin
laskentapiste osuu lähemmäs todellista huippua.

```{.python tiedosto="esimerkit/09-amplitudi.py" osa="amplitudi"}
```

```{.tuloste tiedosto="esimerkit/09-amplitudi.odotettu"}
```

Ilman täyttöä huippu osuu 125 Hz:n väliin, ja amplitudi on 2,34.
32-kertaisella täytöllä taajuus on 123,44 Hz, eli 0,04 Hz:n päässä
oikeasta, ja amplitudi on oikea 2,500. Hilan tihentäminen on tavallisin
tapa mitata yksittäisen sinin taajuus ja amplitudi tarkasti.

## Nopea konvoluutio

Konvoluutiolauseen mukaan pitkä konvoluutio lasketaan nopeimmin
FFT:llä. Kun jonot täytetään nollilla pituuteen $L \ge N_x + N_h - 1$,
syklinen konvoluutio on sama kuin lineaarinen. `scipy.signal.fftconvolve`
tekee täytön, kertolaskun ja käänteismuunnoksen. `oaconvolve` jakaa
pitkän signaalin lohkoihin luvun 5 overlap-add-tekniikalla, jolloin
FFT:t pysyvät lyhyinä.

```{.python tiedosto="esimerkit/09-fft-konvoluutio.py" osa="tulos"}
```

Kumpi on nopeampi, riippuu pituuksista. Suora konvoluutio vaatii
$N_x N_h$ kertolaskua, FFT-menetelmä noin $3 \cdot 2L\log_2 L$
reaalikertolaskua. Ajoaikoja ei mitata, koska ne riippuvat koneesta,
mutta kertolaskujen määrä näyttää rajan:

```{.python tiedosto="esimerkit/09-fft-konvoluutio.py" osa="laskenta"}
```

```{.tuloste tiedosto="esimerkit/09-fft-konvoluutio.odotettu"}
```

Malli on karkea: oikeat FFT-toteutukset ovat tehokkaampia, ja suora
konvoluutio hyötyy vektoroinnista. Raja osuu kuitenkin samaan
suuruusluokkaan: muutaman kymmenen kertoimen suotimet lasketaan suoraan,
satojen kertoimien suotimet FFT:llä. `scipy.signal.convolve` valitsee
menetelmän automaattisesti (`method="auto"`).

## Kohinan tehospektri

Kohinalla ei ole huippuja, vaan tasainen tai muotoiltu **tehospektrin
tiheys** (PSD), jonka yksikkö on $\mathrm{V^2/Hz}$. Valkoisen kohinan, jonka
varianssi on $\sigma^2$, yksipuolinen PSD on $\sigma^2/(f_s/2)$.
Yksittäinen DFT eli **periodogrammi** on harhaton arvio, mutta sen
hajonta on yhtä suuri kuin itse arvo: pidempi mittaus antaa tiheämmän
mutta yhtä kohinaisen spektrin. **Welchin menetelmä** jakaa signaalin
limittäisiin, ikkunoituihin lohkoihin ja keskiarvoistaa niiden
periodogrammit. Hajonta pienenee lohkojen määrän neliöjuuren suhteessa,
ja hintana on resoluutio, joka määräytyy lohkon pituudesta.

```{.python tiedosto="esimerkit/09-welch.py" osa="welch"}
```

```{.tuloste tiedosto="esimerkit/09-welch.odotettu"}
```

Molemmat arviot osuvat teoreettiseen tasoon, mutta periodogrammin
suhteellinen hajonta on 1,0 ja Welchin 0,07. Welch on oikea työkalu
kohinan, värähtelyn ja häiriöiden mittaamiseen.

## Käytännössä

- **Mittausaika ratkaisee resoluution.** Kahden taajuuden erottamiseen
  tarvitaan vähintään noin $1/\Delta f$ sekuntia dataa ikkunan
  kertoimella kerrottuna.
- **Käytä ikkunaa aina**, ellei signaalissa ole tarkalleen kokonainen
  määrä jaksoja. Hann on hyvä oletus, Blackman suurelle dynamiikalle.
- **Jaa amplitudi ikkunan summalla**: $A = 2|X[k]|/\sum w$.
- **Täytä nollilla tarkkuutta, älä erottelukykyä varten.** Täyttö
  paikantaa huipun, mutta ei erota lähekkäisiä taajuuksia.
- **Arvioi kohinaa Welchin menetelmällä.** Yksittäinen periodogrammi on
  liian kohinainen tasojen vertailuun.

## Itsearviointi

- Osaat laskea DFT:n taajuusresoluution mittausajasta ja selittää,
  miksi näytetaajuuden kasvattaminen ei paranna sitä.
- Osaat selittää spektrin vuotamisen ja valita ikkunan pääkeilan ja
  sivukeilojen kompromissin perusteella.
- Osaat mitata sinin taajuuden ja amplitudin ikkunoidusta ja nollilla
  täytetystä spektristä.
- Osaat valita suoran ja FFT-konvoluution välillä ja arvioida kohinan
  tehospektrin Welchin menetelmällä.
