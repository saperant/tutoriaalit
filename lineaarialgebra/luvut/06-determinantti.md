# Determinantti ja käänteismatriisi

Neliömatriisin determinantti on yksi luku, joka kertoo, miten kuvaus
muuttaa pinta-aloja (tasossa) tai tilavuuksia (avaruudessa).
Käänteismatriisi on kuvaus, joka kumoaa alkuperäisen. Molemmat ovat
käsitteinä tärkeitä, mutta numeerisessa laskennassa niitä lasketaan
harvemmin kuin oppikirjoista voisi päätellä.

## Determinantti geometrisesti

Yksikköneliön kuva on suunnikas, jonka sivut ovat matriisin sarakkeet.
Determinantti on suunnikkaan **etumerkillinen pinta-ala**:

$$\det \begin{pmatrix} a & b \\ c & d \end{pmatrix} = ad - bc.$$

- $|\det A|$ kertoo, kuinka moninkertaiseksi pinta-ala muuttuu.
- Negatiivinen determinantti tarkoittaa, että kuvaus kääntää suunnan:
  vastapäivään kiertävä kuvio kiertää kuvassa myötäpäivään (peilaus).
- $\det A = 0$ tarkoittaa, että kuvaus litistää tason suoralle tai
  pisteeseen. Silloin tietoa häviää, eikä kuvausta voi kumota.

```{.python tiedosto="esimerkit/06-determinantti.py" osa="det2"}
```

Kierto ja leikkaus säilyttävät pinta-alan (determinantti 1), skaalaus
kertoo sen kertoimien tulolla ja peilaus kääntää suunnan. Viimeisen
matriisin toinen sarake on ensimmäisen kaksinkertainen, joten koko taso
litistyy yhdelle suoralle.

## Determinantti eliminoinnilla

Oppikirjojen kehityskaava (alideterminanttien summa) vaatii $n!$
laskutoimitusta: jo $20 \times 20$-matriisille se on enemmän kuin
universumin ikä nanosekunteina. Käytännössä determinantti lasketaan
eliminoinnilla. Rivien lisääminen toisiinsa ei muuta determinanttia,
rivien vaihto vaihtaa etumerkin, ja kolmiomatriisin determinantti on
lävistäjän tulo:

$$\det A = (-1)^{\text{vaihtoja}} \, u_{11} u_{22} \cdots u_{nn}.$$

```{.python tiedosto="esimerkit/06-determinantti.py" osa="lu"}
```

```{.tuloste tiedosto="esimerkit/06-determinantti.odotettu"}
```

Tulon determinantti on determinanttien tulo, $\det(AB) = \det A \det B$:
peräkkäiset kuvaukset kertovat pinta-alat. Tästä seuraa myös, että
$\det(A^{-1}) = 1/\det A$.

## Käänteismatriisi

Käänteismatriisi $A^{-1}$ toteuttaa $A A^{-1} = A^{-1} A = I$, missä
$I$ on yksikkömatriisi. Se on olemassa täsmälleen silloin, kun
$\det A \neq 0$. Gaussin–Jordanin menetelmä laskee sen eliminoimalla
laajennetun matriisin $[A \mid I]$ muotoon $[I \mid A^{-1}]$: samat
rivioperaatiot, jotka muuttavat $A$:n yksikkömatriisiksi, muuttavat
yksikkömatriisin $A^{-1}$:ksi.

```{.python tiedosto="esimerkit/06-kaanteis.py" osa="gauss-jordan"}
```

```{.python tiedosto="esimerkit/06-kaanteis.py" osa="kumoaminen"}
```

```{.tuloste tiedosto="esimerkit/06-kaanteis.odotettu"}
```

Käänteismatriisilla on luontevia käyttöjä: grafiikan kameran
näkymämatriisi on kameran asentomatriisin käänteismatriisi, ja hiiren
osoittama piste muunnetaan näytöltä maailmaan käänteisellä
projektiolla. Kierron käänteismatriisi on sen transpoosi (luku 8), ja
yhdistetyn kuvauksen käänteismatriisi on
$(AB)^{-1} = B^{-1} A^{-1}$: kumotaan käänteisessä järjestyksessä.

## Miksi käänteismatriisia ei yleensä lasketa

Yhtälöryhmän $Ax = b$ voi kirjoittaa muotoon $x = A^{-1} b$, mutta
näin sitä ei kannata laskea:

- **Hitaampi.** Käänteismatriisi vaatii noin $2n^3$ laskutoimitusta,
  LU-hajotelma ja kaksi sijoitusta noin $\tfrac{2}{3} n^3$.
- **Epätarkempi.** Huonokuntoisella matriisilla $A^{-1} b$ antaa
  selvästi suuremman jäännöksen kuin suora ratkaisu (luku 12).
- **Tuhlaileva.** Harvan matriisin käänteismatriisi on yleensä tiheä,
  joten se ei edes mahdu muistiin.

Matemaattisessa tekstissä $A^{-1} b$ tarkoittaa "yhtälön ratkaisu".
Koodissa se kirjoitetaan `np.linalg.solve(A, b)`.

## Käytännössä

- **Älä käytä determinanttia singulaarisuustestinä.** Determinantin
  arvo riippuu skaalauksesta: $\det(0{,}1 \cdot I_{100}) = 10^{-100}$,
  vaikka matriisi on täydellisen hyväkuntoinen. Käytä kuntolukua
  (`np.linalg.cond`) tai astetta.
- **Suurille matriiseille `slogdet`.** Determinantti ylivuotaa
  helposti. `np.linalg.slogdet` antaa etumerkin ja logaritmin, joita
  tarvitaan esimerkiksi todennäköisyysjakaumien kaavoissa.
- **Kirjoita koodiin `solve`, ei `inv`.** Poikkeus: pieni kiinteä
  matriisi, jota sovelletaan miljooniin pisteisiin (esimerkiksi
  grafiikan $4 \times 4$), jolloin käänteismatriisi lasketaan kerran.
- **Kierron käänteismatriisi on transpoosi.** Kun tiedät matriisin
  olevan kierto, käytä transpoosia: se on tarkka ja ilmainen.

## Itsearviointi

- Osaat tulkita determinantin pinta-alan tai tilavuuden muutoksena ja
  etumerkin suunnan säilymisenä tai kääntymisenä.
- Osaat laskea determinantin eliminoinnilla ja selittää, miksi
  kehityskaava ei kelpaa suurille matriiseille.
- Osaat laskea käänteismatriisin Gaussin–Jordanin menetelmällä ja
  kumota kuvauksen sillä.
- Osaat perustella, miksi yhtälöryhmä ratkaistaan `solve`lla eikä
  käänteismatriisin avulla, ja tunnistaa poikkeukset.
