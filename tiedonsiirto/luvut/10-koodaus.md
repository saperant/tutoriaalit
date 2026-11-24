# Kanavakoodauksen perusteet

Luku 6 näytti, että koodaamattomat modulaatiot jäävät noin 9 dB
Shannonin rajasta. Kanavakoodaus kuroo väliä umpeen: lähetin lisää
dataan rakennetta, jonka avulla vastaanotin korjaa virheet. Taito
*Tietoliikennetekniikka* esitteli pariteetin, CRC:n, Hamming-koodin ja
lomituksen bittitasolla. Tässä luvussa koodit liitetään kohinaiseen
kanavaan: miten koodausvahvistus mitataan reilusti, mitä pehmeä päätös
antaa, ja miten konvoluutiokoodi puretaan Viterbi-algoritmilla.

## Reilu vertailu: energia tietobittiä kohti

Koodi, jonka **koodinopeus** on $R = k/n$, lähettää $n$ koodibittiä
jokaista $k$ tietobittiä kohti. Jos lähetysteho ja tietonopeus pysyvät
samoina, kunkin koodibitin energia on $R\,E_b$. Koodaus siis heikentää
jokaista lähetettyä bittiä, ja sen on korjattava enemmän virheitä kuin
se aiheuttaa ollakseen hyödyksi. Koodeja verrataan siksi aina samalla
$E_b/N_0$:lla, ja **koodausvahvistus** on se, kuinka monta desibeliä
vähemmän $E_b/N_0$:aa koodattu järjestelmä tarvitsee samaan
bittivirhesuhteeseen.

## Kova ja pehmeä päätös

**Kova päätös** muuttaa jokaisen näytteen ensin bitiksi ja purkaa koodin
biteistä. **Pehmeä päätös** antaa dekooderille näytteet sellaisinaan:
näyte 0,05 on lähes arvaus, näyte 1,2 varma. Pehmeä dekooderi valitsee
koodisanan, joka on lähimpänä vastaanotettuja näytteitä euklidisesti,
mikä on AWGN-kanavassa suurimman uskottavuuden päätös.

Hamming(7,4)-koodissa on vain 16 koodisanaa, joten kumpikin dekooderi
voi verrata vastaanotettua sanaa kaikkiin.

```{.python tiedosto="esimerkit/10-hamming.py" osa="koodi"}
```

```{.python tiedosto="esimerkit/10-hamming.py" osa="dekooderit"}
```

```{.python tiedosto="esimerkit/10-hamming.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/10-hamming.odotettu"}
```

Kovalla päätöksellä Hamming-koodi on 3 dB:llä ja 5 dB:llä *huonompi*
kuin koodaamaton BPSK: koodibittien heikentyminen maksaa enemmän kuin
yhden virheen korjaus tuottaa. Hyöty alkaa vasta suuremmalla
$E_b/N_0$:lla. Pehmeä päätös samalla koodilla on kymmenkertaisesti
parempi 7 dB:llä. Nyrkkisääntö on, että pehmeä päätös antaa noin 2 dB
lisää koodausvahvistusta, ja siksi nykyiset dekooderit käsittelevät
aina pehmeitä arvoja.

## Pehmeät bitit moniarvoisesta modulaatiosta

BPSK:lla pehmeä arvo on suoraan vastaanotettu näyte. QAM-symboli
kuljettaa useita bittejä, joten kullekin bitille lasketaan erikseen
**log-uskottavuussuhde** (LLR):

$$L = \ln\frac{P(b = 0 \mid r)}{P(b = 1 \mid r)}
    = \ln\frac{\sum_{s:\,b=0} e^{-|r-s|^2/N_0}}
              {\sum_{s:\,b=1} e^{-|r-s|^2/N_0}}.$$

Merkki on kova päätös ja itseisarvo luotettavuus. Käytännössä summat
korvataan usein suurimmalla termillä (*max-log*), mikä vaatii vain
etäisyydet lähimpiin pisteisiin.

```{.python tiedosto="esimerkit/10-llr.py" osa="llr"}
```

LLR:n hyvyys näkyy **kalibroinnista**: jos $L$ on oikein laskettu, bitin
virhetodennäköisyys on $1/(1 + e^{|L|})$. Kun bitit ryhmitellään
$|L|$:n mukaan, kunkin ryhmän virheosuuden pitää vastata kaavaa.

```{.python tiedosto="esimerkit/10-llr.py" osa="kalibrointi"}
```

```{.tuloste tiedosto="esimerkit/10-llr.odotettu"}
```

Lähellä nollaa olevat LLR:t ovat lähes arvauksia (38 % virheitä), ja
yli 8:n LLR:t eivät ole virheellisiä kertaakaan. Dekooderi hyödyntää
juuri tätä eroa: se luottaa varmoihin bitteihin ja korjaa epävarmoja.
Väärin skaalattu LLR (esimerkiksi väärä $N_0$) on yleinen virhe, joka
heikentää iteratiivisten dekooderien suorituskykyä huomaamatta.
Kalibrointitaulukko paljastaa sen.

## Konvoluutiokoodi

**Konvoluutiokoodi** syöttää bittivirran siirtorekisteriin ja laskee
jokaista syötebittiä kohti useamman lähtöbitin rekisterin bittien
XOR-summina. Tässä käytetty koodi on klassinen nopeuden 1/2 koodi,
jonka generaattorit ovat oktaaleina 7 ja 5 (binäärinä 111 ja 101).
Rekisterissä on kaksi edellistä bittiä, joten kooderilla on neljä
tilaa. Koodin vapaa etäisyys on 5: kahden eri syötejonon koodatut
jonot eroavat vähintään viidessä bitissä.

Koodin rakenne kuvataan **trelliksenä**: taulukkona, joka kertoo
jokaiselle tilalle ja syötebitille seuraavan tilan ja lähtöbitit.
Lohkon loppuun lisätään kaksi nollaa, jotta kooderi palaa tilaan 0.

```{.python tiedosto="esimerkit/10-viterbi/konvoluutio.py" osa="trellis"}
```

## Viterbi-algoritmi

Suurimman uskottavuuden dekooderi etsii trelliksen läpi polun, jonka
lähtö on lähimpänä vastaanotettua jonoa. Polkuja on eksponentiaalisesti,
mutta **Viterbi-algoritmi** löytää parhaan dynaamisella ohjelmoinnilla:
jokaiseen tilaan johtavista poluista vain paras voi kuulua kokonaiseen
parhaaseen polkuun, joten kussakin tilassa säilytetään vain yksi polku
ja sen kustannus. Jokaisella askeleella kustannus päivitetään
haarakohtaisella kustannuksella, ja lopuksi paras polku jäljitetään
taaksepäin tallennetuista valinnoista. Työ on lineaarinen jonon
pituudessa ja verrannollinen tilojen määrään.

Toteutus käsittelee monta lohkoa kerralla NumPy-taulukoina. Pehmeän ja
kovan päätöksen ero on vain siinä, saako dekooderi näytteet vai
niiden etumerkit.

```{.python tiedosto="esimerkit/10-viterbi/konvoluutio.py" osa="viterbi"}
```

Testit tarkistavat kooderin impulssivasteen ja vapaan etäisyyden,
kohinattoman kierroksen, kahden hajallaan olevan virheen korjautumisen
ja pehmeän päätöksen edun:

```{.python tiedosto="esimerkit/10-viterbi/test_konvoluutio.py" osa="testit"}
```

Bittivirhesuhde AWGN-kanavassa:

```{.python tiedosto="esimerkit/10-viterbi/main.py" osa="ber"}
```

## Purskevirheet ja lomitus

Viterbi-dekooderi korjaa hajallaan olevat virheet hyvin, mutta pitkä
virhepurske, esimerkiksi häipymä, ylittää koodin korjauskyvyn.
**Lomitus** sekoittaa koodibittien järjestyksen ennen lähetystä ja
palauttaa sen vastaanotossa, jolloin kanavan purske hajoaa dekooderin
näkökulmasta yksittäisiksi virheiksi. Lohkolomitin kirjoittaa bitit
taulukkoon riveittäin ja lukee ne sarakkeittain.

```{.python tiedosto="esimerkit/10-viterbi/konvoluutio.py" osa="lomitus"}
```

Kokeessa jokaiseen lohkoon osuu 12 koodibitin häipymä, jonka aikana
vastaanotin ei saa signaalista mitään tietoa (näytteet ovat nollia).
Pehmeä dekooderi käsittelee nollaa täydellisenä epävarmuutena.

```{.python tiedosto="esimerkit/10-viterbi/main.py" osa="purske"}
```

```{.tuloste tiedosto="esimerkit/10-viterbi.odotettu"}
```

AWGN-kanavassa koodi antaa pehmeällä päätöksellä 4 dB:llä
20-kertaisen parannuksen, ja 5 dB:llä virheitä on vain yksi
100 000 bitissä. Tulos on siksi vain suuntaa antava (luku 11).
Koodausvahvistus on noin 3 dB bittivirhesuhteella $10^{-3}$, ja
pienemmillä virhesuhteilla se lähestyy asymptoottista arvoa
$10\log_{10}(R\,d_\text{free}) \approx 4$ dB. Kovalla päätöksellä koodi
on 2 ja 3 dB:llä huonompi kuin koodaamaton, kuten Hamming-koodi.
Ilman lomitusta 12 bitin purske tuhoaa lähes jokaisen lohkon, mutta
lomitettuna sama purske korjautuu: 12 rivin lomitin hajottaa purskeen
yksittäisiksi bittivirheiksi 84 bitin välein.

## Nykyaikaiset koodit ja virheen havaitseminen

Konvoluutiokoodit ja Viterbi-dekooderi olivat 1970-luvulta 2000-luvulle
avaruusliikenteen, GSM:n ja WLAN:n työjuhta. Nykyään korjauksessa
käytetään koodeja, jotka pääsevät alle desibelin päähän Shannonin
rajasta:

- **Turbokoodit** (3G, 4G): kaksi rinnakkaista konvoluutiokoodia ja
  lomitin, iteratiivinen pehmeä dekoodaus.
- **LDPC-koodit** (WLAN, DVB-S2, 5G:n data, 10GBASE-T): harvat
  pariteettimatriisit ja viestinvälitys graafilla.
- **Polaarikoodit** (5G:n ohjauskanavat): ensimmäiset todistetusti
  kapasiteetin saavuttavat koodit.

Korjauksen jälkeen virheet havaitaan CRC:llä, ja virheellinen paketti
lähetetään uudelleen (ARQ, tai pehmeillä arvoilla yhdistäen HARQ).
Koodi korjaa tavalliset virheet, ja CRC varmistaa, ettei harvinainen
väärä korjaus päädy sovellukselle.

## Käytännössä

- **Vertaa koodeja samalla $E_b/N_0$:lla.** Huomioi koodinopeus
  kohinan tasossa, muuten koodausvahvistus on liian suuri $10\log_{10}(1/R)$
  desibelin verran.
- **Käytä pehmeää päätöstä.** Se on noin 2 dB:n parannus samalla
  koodilla. Ilmaisimen on tuotettava luotettavuustieto (esim. LLR)
  bittikohtaisesti myös QAM:lle.
- **Lomita, jos kanava häipyy.** Lomittimen syvyyden on oltava purskeen
  pituutta suurempi. Hinta on viive, koska koko lomitettu lohko on
  vastaanotettava ennen dekoodausta.
- **Lopeta trellis tai käytä hännän purkua.** Tunnettu lopputila
  parantaa lohkon viimeisten bittien luotettavuutta. Vaihtoehto on
  *tail-biting*, joka ei tuhlaa bittejä lopetukseen.
- **Lisää CRC korjauksen päälle.** Korjaava koodi ei kerro, onnistuiko
  korjaus.

## Itsearviointi

- Osaat verrata koodattua ja koodaamatonta järjestelmää reilusti
  samalla $E_b/N_0$:lla ja lukea koodausvahvistuksen tuloksista.
- Osaat selittää kovan ja pehmeän päätöksen eron ja toteuttaa
  kummankin pienelle lohkokoodille.
- Osaat laskea QAM-symbolin bittikohtaiset LLR:t ja tarkistaa niiden
  kalibroinnin.
- Osaat toteuttaa konvoluutiokooderin ja Viterbi-dekooderin trelliksen
  avulla ja testata ne.
- Osaat selittää lomituksen merkityksen purskevirheissä ja mitoittaa
  lohkolomittimen.
