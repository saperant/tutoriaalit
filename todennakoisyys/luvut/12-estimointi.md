# Estimointi ja luottamusvälit

Mittaukset ovat otos tuntemattomasta jakaumasta. *Estimaattori* on
sääntö, joka laskee otoksesta arvion jakauman parametrille, ja
*luottamusväli* kertoo arvion epävarmuuden. Tämä luku käsittelee hyvän
estimaattorin ominaisuudet, suurimman uskottavuuden periaatteen ja
välien laskemisen sekä kaavalla että bootstrapilla.

## Harhattomuus

Estimaattori on *harhaton*, jos sen odotusarvo on oikea arvo.
Otoskeskiarvo on harhaton. Varianssin estimaattori, joka jakaa
neliöpoikkeamien summan otoskoolla $n$, aliarvioi varianssia, koska
poikkeamat lasketaan otoksen omasta keskiarvosta. Jakaja $n - 1$
(*Besselin korjaus*) poistaa harhan:

```{.python tiedosto="esimerkit/12-estimointi.py" osa="harha"}
```

NumPyssa jakajan valitsee parametri `ddof`: `x.var()` jakaa luvulla $n$
ja `x.var(ddof=1)` luvulla $n - 1$. Pienillä otoksilla ero on merkittävä.

## Suurimman uskottavuuden menetelmä

*Uskottavuusfunktio* $L(\theta)$ on havaitun aineiston todennäköisyys
(tai tiheys) parametrin $\theta$ funktiona. *Suurimman uskottavuuden
estimaatti* (*maximum likelihood*, ML) on parametri, joka tekee
havainnot todennäköisimmiksi. Eksponenttijakautuneille elinajoille
logaritminen uskottavuus on $n \ln \lambda - \lambda \sum t_i$, ja sen
maksimi on $\hat\lambda = 1/\bar t$:

```{.python tiedosto="esimerkit/12-estimointi.py" osa="ml"}
```

```{.tuloste tiedosto="esimerkit/12-estimointi.odotettu"}
```

Viidenkymmenen komponentin elinajoista saatu MTBF-arvio poikkeaa
todellisesta muutaman prosentin. Ilman luottamusväliä arviosta ei
kuitenkaan näe, onko poikkeama odotettavissa.

## Luottamusväli keskiarvolle

Keskeisen raja-arvolauseen mukaan keskiarvo on likimain
normaalijakautunut, ja sen keskihajonta (*keskivirhe*) on
$s/\sqrt{n}$. Keskiarvon 95 %:n luottamusväli on siis
$\bar x \pm 1{,}96\, s/\sqrt{n}$:

```{.python tiedosto="esimerkit/12-luottamusvali.py" osa="vali"}
```

```{.tuloste tiedosto="esimerkit/12-luottamusvali.odotettu" rivit="1-1"}
```

Luottamusvälin tulkinta koskee menetelmää: jos koe toistetaan monta
kertaa, 95 % näin lasketuista väleistä sisältää todellisen arvon.
Simulaatio tarkistaa väitteen:

```{.python tiedosto="esimerkit/12-luottamusvali.py" osa="peittavyys"}
```

```{.tuloste tiedosto="esimerkit/12-luottamusvali.odotettu" rivit="2-2"}
```

![Sata samalla tavalla toistettua 40 mittauksen koetta ja niiden 95 %:n
luottamusvälit. Pystyviiva on todellinen arvo 12. Kuusi väliä sadasta
(korostetut) ei sisällä sitä. Yksittäisestä välistä ei voi tietää,
kumpaan joukkoon se kuuluu.](kuvat/luottamusvalit.png){width=70%}

Peittävyys jää hieman alle 95 %:n, koska keskihajonta on arvioitu
samasta otoksesta. Pienillä otoksilla kerroin 1,96 korvataan
Studentin $t$-jakauman kertoimella (40 havainnolla 2,02).

## Bootstrap

Kaikille tunnusluvuille, kuten mediaanille tai persentiilille, ei ole
valmista kaavaa. *Bootstrap* korvaa kaavan laskennalla: otoksesta
poimitaan palauttaen tuhansia uusia samankokoisia otoksia, tunnusluku
lasketaan jokaisesta, ja luottamusväli luetaan tulosten persentiileistä.

```{.python tiedosto="esimerkit/12-luottamusvali.py" osa="bootstrap"}
```

```{.tuloste tiedosto="esimerkit/12-luottamusvali.odotettu" rivit="3-"}
```

Bootstrap olettaa, että otos edustaa populaatiota. Se ei korjaa
harhaista otosta, eikä se toimi ääriarvoille, kuten maksimille, joita
otos ei sisällä.

## Käytännössä

- **Ilmoita arvio ja epävarmuus yhdessä.** ”Keskimäärin 12,2 ms
  (95 %: 11,3–13,2)” on tieto; ”12,2 ms” on vain luku.
- **Käytä jakajaa $n - 1$ otosvarianssissa.** NumPyssa `ddof=1`;
  Pythonin `statistics.stdev` tekee sen oletuksena, `statistics.pstdev`
  ei.
- **Käytä $t$-kerrointa pienillä otoksilla.** Alle 30 havainnolla 1,96
  tuottaa liian kapeita välejä.
- **Bootstrap mediaanille ja persentiileille.** Se on yksinkertainen,
  yleinen ja toimii, kun kaavaa ei ole.
- **Tarkista riippumattomuus.** Kaikki välit olettavat riippumattomat
  havainnot; korreloituneet mittaukset tuottavat liian kapeita välejä.

## Itsearviointi

- Osaat selittää harhattomuuden ja käyttää harhatonta
  varianssiestimaattoria.
- Osaat johtaa ja laskea suurimman uskottavuuden estimaatin
  yksinkertaiselle jakaumalle.
- Osaat laskea keskiarvon luottamusvälin ja tulkita sen oikein.
- Osaat laskea bootstrap-luottamusvälin mediaanille tai muulle
  tunnusluvulle ja tunnet menetelmän rajat.
