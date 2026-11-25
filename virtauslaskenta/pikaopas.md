---
title: Virtauslaskenta
subtitle: Pikaopas · luvut, kaaviot, rajat ja tarkistukset
---

# Yhtälöt ja luvut

Kokoonpuristumaton virtaus, tiheys jaettu pois ($p$ on $p/\rho$):

$$\nabla\cdot\mathbf u = 0, \qquad
\frac{\partial\mathbf u}{\partial t} + \nabla\cdot(\mathbf u\mathbf u)
= -\nabla p + \nu\nabla^2\mathbf u$$

| Luku | Kaava | Käyttö |
|------|-------|--------|
| Reynolds | $\mathrm{Re} = UL/\nu$ | laminaari vai turbulentti; rajakerros $\sim L/\sqrt{\mathrm{Re}}$ |
| Mach | $\mathrm{Ma} = U/c$ | $< 0{,}3$: kokoonpuristumaton |
| Péclet | $\mathrm{Pe} = UL/D$ | advektio vastaan diffuusio |
| Courant | $C = U\,\Delta t/h$ | eksplisiittinen: $C \le 1$ |
| hilan Péclet / Reynolds | $Uh/D$, $Uh/\nu$ | keskeiskaavio heilahtaa, kun $> 2$ |
| Strouhal | $\mathrm{St} = fd/U$ | pyörteiden irtoamistaajuus |
| $y^+$ | $y\,u_\tau/\nu$, $u_\tau = \sqrt{\tau_w/\rho}$ | seinän viereisen ruudun koko |

# Kontrollitilavuusmenetelmä

| Asia | Sääntö |
|------|--------|
| tase | varaston muutos = pintojen vuot + lähteet |
| säilyvyys | pinnalla yksi vuo, jota molemmat naapurit käyttävät |
| vuo | advektio $u\,c_\text{pinta}$ + diffuusio $-D\,(c_E - c_P)/h$ |
| pinnan arvo | kaavio valitsee: tarkkuus vastaan rajoittuneisuus |
| reuna | vuo reunan pinnalla; haamuruutu antaa arvon tai gradientin |

# Advektiokaaviot

| Kaavio | Kertaluku | Käytös |
|--------|-----------|--------|
| vastavirta | 1 | rajoittunut; numeerinen diffuusio $\tfrac12 Uh(1 - C)$ |
| keskeis | 2 | ei vaimenna; heilahtaa, kun hilan Pe $> 2$ |
| Lax–Wendroff | 2 | heilahtaa jyrkän rintaman takana |
| rajoitettu (van Leer ym.) | 2 sileässä, 1 ääriarvossa | rajoittunut ja terävä; käytännön valinta |

Godunov: lineaarinen rajoittunut kaavio on enintään ensimmäistä
kertalukua. Väärä diffuusio vastavirralla vinossa virtauksessa:
$D_\perp \approx \tfrac12 Uh\,\sin\alpha\cos\alpha\,(\sin\alpha +
\cos\alpha)$.

# Paine ja projektio

| Asia | Sääntö |
|-------|----------------|
| paineen tehtävä | pitää nopeuden lähteettömänä; ei omaa aikakehitystä |
| porrastettu hila | $p$ keskellä, $u$ ja $v$ pinnoilla; ei shakkilautaa |
| ennustus | $\mathbf u^* = \mathbf u^n + \Delta t\,(\text{advektio} + \text{diffuusio})$ |
| paineyhtälö | $\nabla^2\phi = \nabla\cdot\mathbf u^*$, seinällä $\partial_n\phi = 0$ |
| korjaus | $\mathbf u^{n+1} = \mathbf u^* - \nabla\phi$, $p = \phi/\Delta t$ |
| aika-askel, Euler | $\Delta t \le h^2/4\nu$ ja $\Delta t \le 2\nu/U^2$ |
| aika-askel, AB2 | $\Delta t \le h^2/8\nu$ ja $C \approx 0{,}3$ |

```{.python tiedosto="esimerkit/07-virta/virta.py" osa="askel"}
```

# Reunaehdot

| Reuna | Nopeus | Paine | Varo |
|-------|--------|-------|------|
| seinä | $\mathbf u = \mathbf u_\text{seinä}$ (haamuruutu peilaa) | $\partial_n\phi = 0$ | kulmat, liikkuva seinä |
| sisäänvirtaus | annettu profiili | $\partial_n\phi = 0$ | tasainen profiili vaatii etumatkaa |
| ulosvirtaus | $\partial_n \mathbf u = 0$ | $\phi = 0$ | takaisinvirtaus; reuna pyörteen taakse |
| symmetria | normaalinopeus 0, liukuu | $\partial_n\phi = 0$ | virtaus ei aina ole symmetrinen |

# Työnkulku

1. Kysymys: mikä suure, millä tarkkuudella.
2. Reynoldsin ja Machin luku, käsilasku suuruusluokasta.
3. Alue ja reunaehdot: reunat kauas, oikea sisäänvirtausprofiili.
4. Hila: tiheä rajakerroksiin ja vanaan; $y^+$ mallin mukaan.
5. Kaaviot: rajoitettu toinen kertaluku; aika-askel Courantin luvusta.
6. Ajo: jäännös ja kiinnostava suure näkyviin.
7. Tarkistus: tase, kolme hilaa, reunan siirto, mittaus.

# Turbulenssi

| Taso | Lasketaan | Hinta | Hilavaatimus |
|------|-----------|-------|--------------|
| DNS | kaikki pyörteet | ruutuja $\sim \mathrm{Re}^{9/4}$, työ $\sim \mathrm{Re}^3$ | Kolmogorovin mittakaava |
| LES | suuret pyörteet, pienet mallista | suuri, aina 3D ja ajasta riippuva | energiaa kantavat pyörteet |
| RANS | keskiarvovirtaus, kaikki pyörteet mallista | pieni | $y^+ \approx 1$ tai seinäfunktio $30 < y^+ < 300$ |

Kaksiulotteinen lasku suurella Reynoldsin luvulla ei ole turbulenssin
simulointi. Malli on kalibroitu: tulos validoidaan mittauksella.

# Ratkaisijat

| Asia | Sääntö |
|------|--------|
| jäännös | kertoo suunnan; seuraa myös kiinnostavaa suuretta |
| Jacobi, liittogradientti | kierrokset $\propto N^2$, $\propto N$ ($N$ ruutua sivulla) |
| monihila | kierrokset eivät riipu hilasta; työ $\propto$ tuntemattomat |
| SIMPLE | tasapainotila, alirelaksaatio (paine 0,3, nopeus 0,7) |
| PISO | ajasta riippuva, useita painekorjauksia askelta kohden |
| rakenteeton verkko | muuttujat keskellä, Rhie–Chow; vinous ja sivusuhde rajoihin |

# Tarkistukset

| Tarkistus | Löytää |
|-----------|--------|
| tase: sisään − ulos = varaston muutos | säilymättömän kaavion, vuotavan reunan |
| nopeuden divergenssi $\approx 0$ | painekytkennän ja reunaehtojen virheet |
| kertaluku tarkkaa ratkaisua vasten | diskretoinnin virheet |
| kolme hilaa: $p = \log_2\frac{Q_2 - Q_1}{Q_3 - Q_2}$, GCI | diskretointivirheen suuruuden |
| aika-askeleen puolitus | aikavirheen |
| reunan siirtäminen kauemmas | reunan paikan vaikutuksen |
| toinen advektiokaavio | numeerisen vaimennuksen osuuden |
| suure asettunut, jäännös pudonnut | kesken jääneen iteroinnin |

Iterointivirhe ensin pieneksi, sitten hilavertailu. Ilmoita tulos,
virhearvio ja oletukset yhdessä.

# Samat käsitteet OpenFOAMissa

| Käsite | Asetus |
|--------|--------|
| advektiokaavio | `fvSchemes`, `divSchemes`: `upwind`, `linear`, `linearUpwind`, `limitedLinear` |
| aikakaavio, askel | `ddtSchemes`: `Euler`, `backward`; `controlDict`: `deltaT`, `maxCo` |
| reunat | `fixedValue`, `zeroGradient`, `noSlip`, `inletOutlet` |
| paine–nopeus | `PISO` (ajassa), `SIMPLE` + `relaxationFactors` (tasapaino) |
| paineratkaisija | `fvSolution`: `GAMG` (monihila), `PCG` |
| verkko | `checkMesh`, `nNonOrthogonalCorrectors` |
| turbulenssi | `kEpsilon`, `kOmegaSST`; jälkikäsittely `yPlus` |

Nimet vaihtelevat versioittain; tarkista oman version ohjeesta.
