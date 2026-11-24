# Sanaleveyden valinta ja virhebudjetti

Sanaleveyksien valinta on optimointia: liian kapea datapolku ei täytä
tarkkuusvaatimusta, liian leveä kuluttaa pinta-alaa ja tehoa turhaan.
Kokeilemalla ja simuloimalla löytää toimivan ratkaisun, mutta
järjestelmällinen menetelmä on *virhebudjetti*: tarkkuusvaatimus jaetaan
kohinalähteiden kesken, ja jokaisen lähteen osuus lasketaan
kohinamallista.

## Kohinalähteet

FIR-suodattimessa on kolme toisistaan riippumatonta virhelähdettä:

1. **Syötteen kvantisointi.** Syötteen pyöristysvirheen varianssi
   $q_x^2/12$ kulkee suodattimen läpi ja kertautuu kertoimien neliösummalla
   $\sum_k h_k^2$.
2. **Kertoimien kvantisointi.** Kertoimien virhe $\delta h_k$ toimii
   kuin rinnakkainen virhesuodatin, jonka ulostulon varianssi on
   $\sigma_x^2 \sum_k \delta h_k^2$, kun syöte on valkoista kohinaa.
3. **Tuloksen pyöristys.** Kertymän pyöristys tulokseen lisää
   varianssin $q_y^2/12$.

Kertymä on leveä eikä pyöristä, joten se ei tuota virhettä. Riippumattomien
lähteiden varianssit summautuvat:

$$\sigma_e^2 = \frac{q_x^2}{12}\sum_k h_k^2 + \sigma_x^2 \sum_k \delta h_k^2 + \frac{q_y^2}{12}.$$

```{.python tiedosto="esimerkit/09-budjetti.py" osa="malli"}
```

## Ennuste ja mittaus

Ennustetta verrataan bittitarkkaan simulointiin, joka laskee
kokonaisluvuilla kuten laitteisto. Testisignaali on valkoista kohinaa,
koska kertoimien virhetermi olettaa sellaisen:

```{.python tiedosto="esimerkit/09-budjetti.py" osa="simulointi"}
```

```{.python tiedosto="esimerkit/09-budjetti.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/09-budjetti.odotettu"}
```

Ennuste osuu mittaukseen muutaman desimaalin tarkkuudella. Taulukosta
näkee myös, mikä lähde rajoittaa: 12-bittiset kertoimet rajaavat SQNR:n
noin 54 dB:iin riippumatta syötteen ja tuloksen leveydestä, ja 12-bittinen
tulos rajaa sen noin 64 dB:iin. Kun yksi lähde dominoi, muiden
leventäminen on hukkaa.

## Optimointi mallilla

Koska malli on nopea, sillä voi käydä läpi kaikki yhdistelmät ja valita
halvimman, joka täyttää vaatimuksen. Tässä hinta on yksinkertaisesti
bittien summa; oikeassa suunnittelussa kertoimen ja kertojan bitit
painotetaan kertojan pinta-alalla:

```{.python tiedosto="esimerkit/09-budjetti.py" osa="haku"}
```

Haku löytää 80 dB:n vaatimukselle yhdistelmän, jossa kertoimet ovat
leveimmät. Se on odotettua, koska kertoimien virhe ei pienene
tulos- tai syötebittejä lisäämällä. Bittitarkka simulointi vahvistaa
valinnan. Laitteistossa leveydet pyöristetään usein ylöspäin valmiiden
kertojalohkojen leveyksiin (esimerkiksi FPGA:n 18 × 27 -kertojat), jolloin
ylimääräiset bitit ovat ilmaisia.

## Käytännössä

- **Aloita vaatimuksesta.** Tarkkuusvaatimus (SQNR, bittivirhesuhde,
  estokaistan vaimennus) tulee järjestelmätasolta, ja jokainen lohko saa
  siitä osuutensa. Ilman vaatimusta sanaleveydet valitaan tottumuksesta.
- **Tee budjetti ennen RTL:ää.** Kohinamalli kertoo, mikä lähde
  dominoi, ja bittitarkka simulointi vahvistaa tuloksen. RTL:n
  leventäminen jälkikäteen on kallista.
- **Tasapainota lähteet.** Kun lähteet ovat samaa suuruusluokkaa,
  yhden leventäminen hyödyttää vähän. Kannattaa leventää dominoivaa
  lähdettä, kunnes se ei enää dominoi.
- **Huomioi kohdealusta.** FPGA:n DSP-lohkot ja ASIC-kirjaston
  kertojat ovat tietyn levyisiä. Leveys valitaan budjetin ja alustan
  rajojen leikkauksesta.

## Itsearviointi

- Osaat jakaa FIR-suodattimen kohinan syötteen, kertoimien ja
  tuloksen kvantisoinnin osuuksiin ja laskea ne kohinamallista.
- Osaat verrata kohinamallin ennustetta bittitarkkaan simulointiin.
- Osaat tunnistaa dominoivan kohinalähteen ja valita sanaleveydet
  vaatimuksen täyttämiseksi.
- Osaat selittää, miksi kertymä ei tuota virhettä, kun se on riittävän
  leveä.
