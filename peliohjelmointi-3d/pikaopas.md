---
title: 3D-peliohjelmointi
subtitle: Kolmiulotteisen pelin rakenteet tiiviisti
lang: fi
---

# Sopimukset

| Asia | Tässä ja glTF:ssä |
|------|-------------------|
| akselit | oikeakätinen, y ylös |
| kamera katsoo | −z, oikea +x |
| mallin etupuoli | +z |
| yksikkö | metri, radiaani |
| tulo `A * B` | ensin B, sitten A |

Unity: vasenkätinen, y ylös. Unreal: vasenkätinen, z ylös, cm.
Blender: oikeakätinen, z ylös. Muunna tuonnissa.

# Orientaatio

| Esitys | Käyttö |
|--------|--------|
| Eulerin kulmat | kamera (kääntö + nyökkäys), editori |
| kvaternio | tila, animaatio, verkko, interpolointi |
| matriisi | renderöijä, hierarkian välimuisti |

- `q = (cos(k/2), sin(k/2) u)`; `q` ja `-q` ovat sama kierto.
- Käänteiskierto on liittoluku. Normalisoi kertyvän päivityksen jälkeen.
- Interpolointi: käännä merkki, jos pistetulo < 0. Nlerp lähekkäisille,
  slerp suurille kulmille.
- Eulerin kulmat: järjestys kuuluu sopimukseen; nyökkäys ±90° lukitsee.

# Muunnoshierarkia

```{.cpp tiedosto="esimerkit/yhteinen/kvaternio.hpp" osa="muunnos"}
```

- Paikallinen TRS on tila, maailmamatriisi välimuisti.
- Taulukko vanhemmat ennen lapsia; likaisuuslippu.
- Vanhemman vaihto: `paikallinen = kaanteinen(vanhempi) * maailma`.
- Epäyhtenäinen skaala vanhemmassa + kierto lapsessa = leikkaus.

# Törmäysmuodot

| Muoto | Testin ydin |
|-------|-------------|
| pallo | lähin piste ja säde |
| kapseli | janan lähin piste, sitten pallo |
| AABB | rajaus koordinaateittain; välit akseleittain |
| kolmio | projektio tasolle tai lähin reuna |

Kosketus = normaali + syvyys. Nollaetäisyydelle varasuunta.

# Säteet

| Kohde | Menetelmä |
|-------|-----------|
| pallo | toisen asteen yhtälö |
| AABB | laatat: myöhäisin tulo ≤ aikaisin lähtö |
| kolmio | Möller–Trumbore: u, v, t |
| liikkuva pallo | säde säteellä kasvatettua laatikkoa vastaan |

Käyttö: aseet, valinta hiirellä, näkölinja, maan haku, kameran törmäys.

# Laaja vaihe

- BVH: mediaanijako pisimmällä akselilla, lehdessä ≤ 4 kohdetta.
- Säde: ohita haara, jos laatikko on löydetyn osuman takana.
- Tarkista aina raakaa hakua vastaan; laske testien määrä.
- Staattinen maailma ja liikkuvat kappaleet eri puissa.

# Kamerat

```{.cpp tiedosto="esimerkit/08-seuranta.cpp" osa="pehmennys"}
```

- Ensimmäinen persoona: tallenna kääntö ja nyökkäys, rajaa nyökkäys, kävele
  käännön suuntaan, normalisoi vino liike.
- Kolmas persoona: kohde olkapään korkeudella; säde kohteesta kameraan,
  lähemmäs heti, kauemmas pehmeästi.
- Päivitä kamera hahmon jälkeen. Älä pehmennä hiirtä.

# Hahmo-ohjain

1. Liike: syöte + painovoima.
2. Irrotus: syvin kosketus ensin, toista. Käveltävä pinta (`n.y`
   riittävän suuri) nostaa ylös, seinä työntää vaakasuunnassa.
3. Porras: sama liike ylempää ja lasku alas; hyväksy, jos edessä on
   käveltävää.
4. Tartunta: lasku alas, jos maa on lähellä; muuten putoaminen.

# Näkyvyyskarsinta

```{.cpp tiedosto="esimerkit/yhteinen/kartio.hpp" osa="testit"}
```

Tasot matriisin riveistä: `rivi 4 ± rivi i`. Testi on varovainen.
Hierarkialla testit eivät kasva maailman koon mukana.

# Luurankoanimaatio

| Vaihe | Tulos |
|-------|-------|
| leikkeen näyte hetkellä t | poosi (TRS / nivel) |
| sekoitus painolla w | poosi |
| hierarkian läpikäynti | nivelmatriisit |
| × käänteinen sidontamatriisi | skinnausmatriisit |
| painotettu summa (≤ 4 niveltä) | kärjen paikka |

Sekoita pooseja, ei matriiseja. Painojen summa 1. Ristihäivytyksessä
molemmat leikkeet etenevät.

# glTF

| Osa | Sisältö |
|-----|---------|
| node | nimi, TRS (kvaternio x, y, z, w), lapset |
| mesh | attribuutit ja indeksit accessoreina |
| skin | nivelsolmut, käänteiset sidontamatriisit |
| animation | kanavat: solmu, ominaisuus, ajat, arvot |
| accessor → bufferView → buffer | tyyppi → pala → tavut |

Tarkista jokainen indeksi ja pituus. Lataus palauttaa virheen arvona.

# Askeleen järjestys

syöte kameran suhteen → hahmo-ohjain → pelisäännöt → animaatio →
kamera → karsinta ja piirtolista
