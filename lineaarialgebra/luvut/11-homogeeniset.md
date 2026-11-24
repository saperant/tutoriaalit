# Homogeeniset koordinaatit

Siirto ei ole lineaarikuvaus, koska se liikuttaa origoa. Grafiikka
haluaa silti esittää kaikki muunnokset matriiseina, jotta ne voidaan
yhdistää yhdeksi matriisiksi ja suorittaa näytönohjaimella samalla
tavalla. Ratkaisu on lisätä koordinaatti: tason piste $(x, y)$
kirjoitetaan muotoon $(x, y, 1)$ ja avaruuden piste $(x, y, z)$
muotoon $(x, y, z, 1)$. Näissä **homogeenisissa koordinaateissa** siirto
on matriisitulo:

$$\begin{pmatrix} 1 & 0 & d_x \\ 0 & 1 & d_y \\ 0 & 0 & 1
\end{pmatrix}
\begin{pmatrix} x \\ y \\ 1 \end{pmatrix} =
\begin{pmatrix} x + d_x \\ y + d_y \\ 1 \end{pmatrix}.$$

Kierrot ja skaalaukset saavat oman lohkonsa vasempaan yläkulmaan, ja
siirto tulee viimeiseen sarakkeeseen. Tällaista kuvausta kutsutaan
**affiiniksi**.

## Tason muunnokset

```{.python tiedosto="esimerkit/11-tasossa.py" osa="muunnokset"}
```

Pelihahmon kääntäminen sen oman keskipisteen ympäri on kolmen
muunnoksen yhdistelmä: siirretään keskipiste origoon, käännetään ja
siirretään takaisin. Homogeenisissa koordinaateissa se on yksi matriisi:

```{.python tiedosto="esimerkit/11-tasossa.py" osa="keskipiste"}
```

## Pisteet ja suunnat

Viimeinen koordinaatti $w$ erottaa pisteet ja suunnat. Pisteellä
$w = 1$, joten siirto vaikuttaa siihen. Suunnalla (nopeus, normaali,
valon suunta) $w = 0$, joten siirto ei vaikuta, mutta kierto vaikuttaa.
Tämä vastaa fysiikkaa: kappaleen nopeus ei muutu, jos kappale siirretään
toiseen paikkaan.

```{.python tiedosto="esimerkit/11-tasossa.py" osa="suunta"}
```

```{.tuloste tiedosto="esimerkit/11-tasossa.odotettu"}
```

Kahden pisteen erotus on suunta ($1 - 1 = 0$), ja pisteen ja suunnan
summa on piste. Kahden pisteen summalla ei ole geometrista merkitystä,
ja homogeenisissa koordinaateissa se näkyy arvona $w = 2$.

## Kolmiulotteinen kamera

3D-grafiikassa pisteet kulkevat koordinaatistosta toiseen
$4 \times 4$-matriisien ketjuna:

$$p_{\text{leike}} = P \cdot V \cdot M \cdot p_{\text{malli}}.$$

Mallimatriisi $M$ sijoittaa kappaleen maailmaan, näkymämatriisi $V$
muuntaa maailman kameran koordinaatteihin ja projektiomatriisi $P$
tuottaa leikekoordinaatit. Näkymämatriisi on kameran asennon
käänteismatriisi. Se rakennetaan suoraan kolmesta kohtisuorasta
akselista, jotka saadaan ristitulolla katsesuunnasta ja
ylössuunnasta:

```{.python tiedosto="esimerkit/11-kamera.py" osa="katse"}
```

Kierto-osa on ortonormaali, joten sen käänteismatriisi on transpoosi:
akselit tulevat matriisin **riveiksi**, ja siirto-osa on kameran
paikka kierrettynä ja vastaluvuksi muutettuna.

## Perspektiivi

Perspektiivissä kaukaiset asiat näkyvät pienempinä: kuvapisteen
$x$-koordinaatti on verrannollinen arvoon $x / z$. Jakolasku ei ole
lineaarinen, mutta homogeeniset koordinaatit hoitavat senkin.
Projektiomatriisi kopioi syvyyden koordinaattiin $w$, ja lopuksi
kaikki koordinaatit jaetaan $w$:llä (**perspektiivijako**). Näytönohjain
tekee jaon automaattisesti.

```{.python tiedosto="esimerkit/11-kamera.py" osa="perspektiivi"}
```

```{.python tiedosto="esimerkit/11-kamera.py" osa="projisointi"}
```

```{.tuloste tiedosto="esimerkit/11-kamera.odotettu"}
```

Kauempana olevan pisteen $x$ on lähempänä nollaa (keskustaa), vaikka
sen maailmakoordinaatti on sama. Syvyysarvo ei ole lineaarinen
etäisyyden suhteen: suurin osa syvyyspuskurin tarkkuudesta käytetään
lähitasoon. Siksi lähitasoa ei kannata asettaa liian lähelle: arvolla
0,001 kaukaisten pintojen syvyydet sulautuvat yhteen ja pinnat
välkkyvät (*z-fighting*).

## Käytännössä

- **Pidä $w$ oikein.** Pisteille $w = 1$, suunnille $w = 0$. Jos normaali
  muunnetaan kuin piste, se siirtyy ja valaistus menee pieleen.
- **Normaalit muunnetaan käänteismatriisin transpoosilla.** Kun
  mallimatriisi skaalaa epätasaisesti, normaalit lakkaavat olemasta
  kohtisuorassa pintaan, jos niihin sovelletaan samaa matriisia.
  Oikea matriisi on $(M^{-1})^T$ ilman siirto-osaa.
- **Sovi rivi- ja sarakekäytännöstä.** Tämä tutoriaali ja OpenGL
  käyttävät sarakevektoreita ($Mp$); DirectX ja osa pelimoottoreista
  rivivektoreita ($pM$), jolloin matriisit ovat transponoituja ja
  järjestys käänteinen. Tarkista kirjaston dokumentaatio.
- **Valitse lähi- ja kaukotaso huolella.** Syvyyden tarkkuus riippuu
  lähinnä niiden suhteesta. Käänteinen syvyys (*reversed-Z*)
  liukulukupuskurilla on nykyaikainen ratkaisu.
- **Jatka renderöintiin.** Taito *Renderöinnin perusteet* rakentaa
  näiden matriisien päälle rasteroinnin ja valaistuksen, ja
  *GPU-ohjelmointi* näyttää, miten matriisit annetaan varjostimille.

## Itsearviointi

- Osaat kirjoittaa siirron, kierron ja skaalauksen homogeenisina
  matriiseina ja yhdistää ne oikeassa järjestyksessä.
- Osaat kiertää kuvion annetun pisteen ympäri yhdellä matriisilla.
- Osaat selittää, miksi pisteillä $w = 1$ ja suunnilla $w = 0$.
- Osaat rakentaa näkymämatriisin katsesuunnasta ja selittää
  perspektiivijaon ja syvyyden epälineaarisuuden.
