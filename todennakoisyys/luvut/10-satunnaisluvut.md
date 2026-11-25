# Satunnaislukugeneraattorit ja otanta

Simulaatiot, testit ja satunnaistetut algoritmit tarvitsevat
satunnaislukuja. Generaattoria ja siementä on käytetty luvusta
*Tapahtumat ja todennäköisyys* alkaen; tämä luku avaa, mitä niiden
sisällä tapahtuu ja miten tasajakautuneista luvuista tehdään muita
jakaumia. Tietokone tuottaa satunnaisluvut yleensä deterministisellä
*näennäissatunnaisgeneraattorilla* (*PRNG*), jonka tila etenee
kaavan mukaan siemenestä alkaen. Hyvä generaattori on nopea,
toistettava ja tilastollisesti hyvä. Kryptografinen satunnaisuus on
eri asia, ja siihen käytetään `secrets`-moduulia (taito
*Kryptografia*).

## Lineaarinen kongruenssigeneraattori

Vanhin ja yksinkertaisin generaattori laskee
$x_{k+1} = (a x_k + c) \bmod m$. Se on nopea, mutta sen bitit ovat
eriarvoisia: kun $m = 2^{32}$, alimman bitin jakso on vain kaksi.

```{.python tiedosto="esimerkit/10-generaattori.py" osa="lcg"}
```

Tästä syystä lauseke `x % 2` vanhalla generaattorilla on täysin
ennustettava kolikonheitto. Nykyaikaiset generaattorit, kuten NumPyn
oletus *PCG64* ja Pythonin `random`-moduulin *Mersenne Twister*,
sekoittavat tilan bitit ennen tulostusta.

## Siemen ja rinnakkaiset virrat

Kiinteä siemen tekee simulaatiosta toistettavan: sama siemen tuottaa
saman jonon, kuten luvussa *Tapahtumat ja todennäköisyys* nähtiin.

```{.python tiedosto="esimerkit/10-generaattori.py" osa="siemen"}
```

Rinnakkaiset työt tarvitsevat toisistaan riippumattomat virrat.
Siemenet 1, 2, 3 eivät takaa sitä. `SeedSequence.spawn` johtaa
juurisiemenestä tilastollisesti riippumattomat alisiemenet:

```{.python tiedosto="esimerkit/10-generaattori.py" osa="virrat"}
```

```{.tuloste tiedosto="esimerkit/10-generaattori.odotettu"}
```

## Käänteisfunktiomenetelmä

Generaattori tuottaa tasajakautuneita lukuja väliltä $[0, 1)$. Jos
kertymäfunktio $F$ on kääntyvä, $X = F^{-1}(U)$ noudattaa haluttua
jakaumaa. Eksponenttijakaumalle $F(x) = 1 - e^{-\lambda x}$, joten
$X = -\ln(1 - U)/\lambda$. Funktio `log1p` laskee $\ln(1 + x)$
tarkasti myös pienillä $x$:

```{.python tiedosto="esimerkit/10-otanta.py" osa="kaanteis"}
```

## Hylkäysmenetelmä

Jos kertymäfunktiota ei voi kääntää, käytetään *hylkäysmenetelmää*:
arvotaan ehdotus helposta jakaumasta $g$ ja hyväksytään se
todennäköisyydellä $f(x) / (M g(x))$, jossa $M$ on niin suuri, että
$f \le M g$. Hyväksytyt arvot noudattavat tiheyttä $f$, ja
hyväksymisosuus on $1/M$.

```{.python tiedosto="esimerkit/10-otanta.py" osa="hylkays"}
```

```{.tuloste tiedosto="esimerkit/10-otanta.odotettu"}
```

## Käytännössä

- **Käytä generaattorioliota ja siementä.** `np.random.default_rng(siemen)`
  tekee simulaatiosta toistettavan; globaali tila (`np.random.seed`)
  vuotaa testien ja moduulien välillä.
- **Johda rinnakkaiset virrat siemenpuusta.** `SeedSequence.spawn` tai
  `Generator.spawn` antaa riippumattomat virrat; peräkkäiset siemenet
  eivät.
- **Älä käytä PRNG:tä salaisuuksiin.** Tunnukset, avaimet ja tokenit
  tehdään `secrets`-moduulilla; Mersenne Twisterin tila voidaan
  päätellä tulosteesta.
- **Tallenna siemen tuloksen kanssa.** Kun satunnaistettu testi
  kaatuu, siemen toistaa vian.
- **Käytä valmiita jakaumia.** NumPyn generaattorissa on kymmeniä
  valmiita jakaumia; oma otanta kannattaa vain, kun jakaumaa ei ole.

## Itsearviointi

- Osaat selittää näennäissatunnaisgeneraattorin periaatteen ja
  heikon generaattorin tyypilliset viat.
- Osaat käyttää siementä ja riippumattomia rinnakkaisia virtoja
  toistettavissa simulaatioissa.
- Osaat toteuttaa otannan käänteisfunktio- ja hylkäysmenetelmällä ja
  tarkistaa tuloksen tunnusluvuilla.
