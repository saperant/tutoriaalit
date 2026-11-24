# Johdanto {.runko-johdanto}

Taito *Signaalit ja järjestelmät* opetti analysoimaan suotimia:
impulssivaste, Z-muunnos, navat ja nollat, taajuusvaste ja spektri.
Tämä tutoriaali kääntää suunnan. Lähtökohtana on **vaatimus**, kuten
"päästä 1 kHz:iin asti, vaimenna 1,5 kHz:stä ylöspäin 60 dB". Siitä
suunnitellaan suodin, jonka kertoimet tarkistetaan, ja suodin
toteutetaan C:llä niin, että se toimii reaaliajassa lohko kerrallaan.
Lopuksi toteutusta verrataan Python-referenssiin numeerisella
toleranssilla.

Sama työnkulku toistuu kaikissa luvuissa:

| Vaihe | Työkalu | Tulos |
|------------|------------------------------|----------------------------------------|
| vaatimus | luku tai taulukko | kaistat, aaltoilu, vaimennus, viive, laskentabudjetti |
| suunnittelu | SciPy (`firwin`, `remez`, `ellip`) | kertoimet |
| tarkistus | `freqz`, oma tarkistusfunktio | vaatimukset täyttyvät tai eivät |
| toteutus | C, tila kutsujan muistissa | funktio, joka käsittelee lohkon |
| vertailu | ctypes, pytest | ero referenssiin toleranssin sisällä |
| kiinteä pilkku | C ja bittitarkka Python-malli | sama tulos bitilleen |

Python on suunnittelun ja referenssin kieli, koska SciPy sisältää
alan menetelmät valmiina ja koska tulosta on helppo tutkia. C on
toteutuksen kieli, koska signaalinkäsittely ajetaan lopulta
mikrokontrollerissa, äänikortin ajurissa tai radiolaitteessa, jossa ei
ole Python-tulkkia eikä muistinvarausta reaaliaikasilmukassa.

## Ensimmäinen suodin

Tehtävä: 8 kHz:n näytetaajuudella mitatusta signaalista poistetaan yli
1,5 kHz:n häiriöt, mutta 1 kHz:iin asti kaikki taajuudet säilyvät.
Vaatimukset kirjoitetaan ensin muuttujiksi:

```{.python tiedosto="esimerkit/01-ensimmainen.py" osa="vaatimukset"}
```

Suunnitellaan FIR-suodin Kaiserin ikkunamenetelmällä. `kaiserord`
laskee vaatimuksista kertoimien määrän ja ikkunan parametrin, ja
`firwin` laskee kertoimet. Menetelmä selitetään luvussa 3.

```{.python tiedosto="esimerkit/01-ensimmainen.py" osa="suunnittelu"}
```

Suunnitelmaan ei luoteta sokeasti, vaan taajuusvaste lasketaan ja
vaatimukset tarkistetaan:

```{.python tiedosto="esimerkit/01-ensimmainen.py" osa="tarkistus"}
```

Lopuksi suodinta käytetään: 440 Hz:n siniin lisätään 2,5 kHz:n häiriö
ja valkoista kohinaa. Suodin viivästää signaalia ryhmäviiveensä
$(N-1)/2$ verran, joten vertailussa ulostuloa siirretään saman verran.

```{.python tiedosto="esimerkit/01-ensimmainen.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/01-ensimmainen.odotettu"}
```

Suodin täyttää vaatimukset: aaltoilu on paljon alle 0,1 dB:n ja
vaimennus hieman yli 60 dB. Signaali–kohinasuhde paranee 4,8 dB:stä
16,4 dB:iin. Parannus ei ole suurempi, koska osa kohinasta on
päästökaistalla, eikä mikään lineaarinen suodin poista sitä
vahingoittamatta signaalia. Vaatimus on siis kirjoitettava sen mukaan,
mitä suotimella voi saavuttaa.

## Kenelle ja mitä tarvitaan

Lukija tuntee Z-muunnoksen, navat ja nollat, taajuusvasteen, DFT:n,
ikkunat ja vuotamisen sekä lohkokäsittelyn tilan (taito *Signaalit ja
järjestelmät*, jonka luvut ovat tämän suoria edeltäjiä). C-kielestä
tarvitaan osoittimet, rakenteet ja taulukot (taito *C-kieli*). Kiinteän
pilkun Q-formaatit, pyöristys ja saturaatio esitellään taidossa *Lukujen
esitys ja kiinteän pilkun aritmetiikka*; tässä niitä käytetään.

| Luku | Kysymys |
|-------------------------|--------------------------------------------------|
| Vaatimukset ja toleranssit | Miten vaatimus tarkistetaan, ja kuinka paljon C ja Python saavat erota? |
| FIR: ikkunamenetelmä | Miten kertoimet saadaan ideaalisesta suotimesta? |
| FIR: optimaaliset menetelmät | Mikä on lyhin suodin, joka täyttää vaatimuksen? |
| FIR-suodin C:llä | Miten suodatus tehdään lohkoittain ilman muistinvarausta? |
| IIR-suunnittelu | Miten analogisesta prototyypistä tehdään digitaalinen? |
| IIR-toteutus | Miksi toisen asteen lohkot, ja mitä kvantisointi tekee? |
| FFT | Miten FFT toimii, ja milloin konvoluutio kannattaa tehdä FFT:llä? |
| Monitaajuuskäsittely | Miten näytetaajuutta vaihdetaan tehokkaasti? |
| Adaptiiviset suotimet | Miten suodin oppii kertoimensa itse? |
| Reaaliaikakäsittely | Mitä reaaliaika vaatii koodilta, ja miten se testataan? |

## Työkalut

| Työkalu | Käyttö |
|--------------------|----------------------------------------|
| NumPy | taulukot, FFT (`numpy.fft`) |
| SciPy (`scipy.signal`) | suunnittelu, suodatus, taajuusvaste, monitaajuus |
| scipy-stubs, mypy | SciPyn tyyppitarkistus (`--strict`) |
| pytest | C-toteutusten parametrisoidut vertailutestit |
| GCC 14, Clang 20 | C23, varoitukset virheinä, AddressSanitizer ja UBSan |
| ctypes | C-kirjaston kutsuminen Pythonista vertailua varten |
| matplotlib | kuvat (vain kuvitukseen) |

Esimerkkien tulosteet ovat testattuja. Kun luku on pyöristetty tai
tulostetaan vain tieto toleranssin alittumisesta, syy on se, että
viimeiset bitit voivat vaihdella prosessorin ja kirjaston mukaan
(luku 2).

Merkinnät noudattavat edeltävää taitoa: $f_s$ on näytetaajuus,
$\omega = 2\pi f/f_s$ normitettu kulmataajuus, $h[n]$ impulssivaste ja
$H(z)$ siirtofunktio. SciPyn funktioille annetaan aina `fs=fs`, jolloin
taajuudet ovat hertsejä.
