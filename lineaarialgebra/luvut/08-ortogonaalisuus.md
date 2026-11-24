# Ortogonaalisuus

Kohtisuorat eli **ortogonaaliset** kantavektorit tekevät laskennasta
helppoa ja tarkkaa. Kun kantavektorit ovat lisäksi yksikkövektoreita
(**ortonormaali kanta**), koordinaatit saadaan pelkillä pistetuloilla
eikä yhtälöryhmää tarvitse ratkaista:

$$v = (v \cdot q_1)\, q_1 + (v \cdot q_2)\, q_2 + \dots + (v \cdot q_n)\, q_n.$$

Jokainen termi on projektio yhdelle kantavektorille (luku 2), ja koska
kantavektorit ovat kohtisuorassa, projektiot eivät häiritse toisiaan.

## Ortogonaaliset matriisit

Neliömatriisi $Q$, jonka sarakkeet ovat ortonormaaleja, on
**ortogonaalinen**. Sen tärkein ominaisuus on

$$Q^T Q = I, \qquad\text{eli}\qquad Q^{-1} = Q^T.$$

Käänteismatriisi on transpoosi: ilmainen ja tarkka. Ortogonaalinen
matriisi säilyttää pituudet ja kulmat, koska
$(Qu) \cdot (Qv) = u^T Q^T Q v = u \cdot v$. Geometrisesti se on kierto
($\det Q = 1$) tai kierto ja peilaus ($\det Q = -1$).

```{.python tiedosto="esimerkit/08-ortogonaalinen.py" osa="sailyttaa"}
```

Numeerisesti ortogonaaliset matriisit ovat parhaita mahdollisia: ne
eivät vahvista pyöristysvirheitä, koska ne eivät venytä mitään. Siksi
luotettavat algoritmit (QR, ominaisarvot, singulaariarvohajotelma)
rakentuvat niiden varaan.

## Ajautuminen ja uudelleenortogonalisointi

Ortogonaalisuus on kuitenkin hauras ominaisuus. Kun pelin tai
simulaation kappaleen asentomatriisia päivitetään joka ruudussa pienellä
kierrolla, pyöristysvirheet kertyvät, ja matriisi alkaa vähitellen
venyttää ja leikata kappaletta. 32-bittisillä liukuluvuilla, joita
grafiikka käyttää, tämä näkyy jo minuuteissa.

```{.python tiedosto="esimerkit/08-ortogonaalinen.py" osa="ajautuminen"}
```

```{.tuloste tiedosto="esimerkit/08-ortogonaalinen.odotettu"}
```

Korjaus on palauttaa matriisi lähimmäksi kierroksi säännöllisin
välein, esimerkiksi QR-hajotelmalla. Pelimoottorit tallentavat
asennon usein kvaterniona, joka on helpompi normalisoida (jaetaan
pituudella), ja muuttavat sen matriisiksi vasta piirrettäessä.

## Gram–Schmidt

Gram–Schmidt-menetelmä muuttaa minkä tahansa lineaarisesti
riippumattoman vektorijoukon ortonormaaliksi kannaksi. Kustakin
vektorista vähennetään sen projektiot jo valmiisiin kantavektoreihin,
ja jäljelle jäävä osa normalisoidaan:

$$v_j' = a_j - \sum_{i<j} (q_i \cdot a_j)\, q_i, \qquad
  q_j = \frac{v_j'}{\lVert v_j' \rVert}.$$

Kaava on oikein, mutta numeerisesti se on huono. **Modifioitu**
Gram–Schmidt laskee täsmälleen samat vektorit eri järjestyksessä:
jokainen projektio vähennetään jo päivitetystä vektorista eikä
alkuperäisestä. Ero näkyy, kun vektorit ovat lähes samansuuntaisia:

```{.python tiedosto="esimerkit/08-gram-schmidt.py" osa="gs"}
```

```{.python tiedosto="esimerkit/08-gram-schmidt.py" osa="vertailu"}
```

Klassinen versio tuottaa vektoreita, jotka eivät ole lähelläkään
kohtisuoria, vaikka matemaattisesti algoritmi on sama. Tämä on
tutoriaalin tärkeimpiä oppeja: **matemaattisesti samat algoritmit
voivat käyttäytyä liukuluvuilla täysin eri tavoin.**

## QR-hajotelma

Gram–Schmidt kirjoittaa matriisin muotoon $A = QR$, missä $Q$:n
sarakkeet ovat ortonormaaleja ja $R$ on yläkolmiomatriisi (sen alkiot
ovat projektioiden kertoimet). Kirjastot laskevat QR-hajotelman
Householderin peilauksilla, jotka ovat vielä vakaampia kuin modifioitu
Gram–Schmidt.

```{.python tiedosto="esimerkit/08-gram-schmidt.py" osa="qr"}
```

```{.tuloste tiedosto="esimerkit/08-gram-schmidt.odotettu"}
```

QR-hajotelma on pienimmän neliösumman sovituksen (luku 9) ja
ominaisarvojen laskennan (QR-algoritmi) perusta.

## Käytännössä

- **Suosi ortonormaaleja kantoja.** Koordinaatit pistetuloilla,
  käänteismatriisi transpoosina, ei virheiden vahvistumista.
- **Käytä kierron käänteismatriisina transpoosia.** Kameran
  näkymämatriisin kierto-osa on asennon transpoosi; `inv` tuo turhaa
  pyöristysvirhettä ja laskentaa.
- **Uudelleenortogonalisoi kertyvät kierrot.** Normalisoi kvaterniot
  tai ortogonalisoi asentomatriisi säännöllisesti, varsinkin
  32-bittisessä laskennassa.
- **Älä toteuta Gram–Schmidtiä itse tuotantoon.** Käytä
  `np.linalg.qr`ää. Jos toteutat, käytä modifioitua versiota ja
  tarvittaessa toista ortogonalisointi kahdesti.

## Itsearviointi

- Osaat laskea vektorin koordinaatit ortonormaalissa kannassa
  pistetuloilla.
- Osaat tunnistaa ortogonaalisen matriisin ja selittää, miksi se
  säilyttää pituudet ja miksi sen käänteismatriisi on transpoosi.
- Osaat toteuttaa Gram–Schmidt-menetelmän ja selittää klassisen ja
  modifioidun version numeerisen eron.
- Osaat korjata pyöristysvirheen vuoksi ajautuneen kiertomatriisin.
