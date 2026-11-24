---
title: Renderöinnin perusteet
subtitle: Pikaopas · muunnokset, rasterointi, syvyys, valaistus ja tekstuurit
lang: fi
---

# Putki

| Vaihe | Tulos | Huomio |
|-------|-------|--------|
| verteksivarjostin | leikkausavaruus $(x, y, z, w)$ | `P * V * M * p`, $w = 1$ pisteille |
| hylkäys | kolmio pois | kaikki kärjet saman tason ulkopuolella |
| leikkaus | 0–9 kärkeä | lähitaso $z + w \ge 0$, muut suojakaista |
| jako $w$:llä | NDC $[-1, 1]^3$ | säilytä $1/w$ korjausta varten |
| näkymäportti | pikselit, syvyys 0–1 | $y_r = (1 - y_n) K / 2$ |
| karsinta | takapinta pois | etupinta vastapäivään |
| rasterointi | painot $\lambda_i$ | keskipiste, vasen-ylä-sääntö |
| syvyystesti | hylkäys ennen varjostusta | $z < \text{puskuri}$ |
| fragmenttivarjostin | väri | lineaarinen valo |
| kirjoitus | sRGB-tavut | koodaus vasta lopuksi |

# Värit

- **sRGB-koodaus:** $s = 12{,}92\,v$, kun $v \le 0{,}0031308$, muuten
  $1{,}055\,v^{1/2.4} - 0{,}055$.
- **Puolet valosta** on tavu 188; tavu 128 on 22 % valosta.
- **Lineaarisesti:** valaistus, sekoitus, suodatus, mipmapit,
  ylinäytteistyksen keskiarvo.
- **sRGB:nä:** värikuvat ja näyttö; normaali- ja datakartat
  lineaarisina.

# Kolmion rasterointi

- **Reunafunktio:** $E_{ab}(p) = (p_x - a_x)(b_y - a_y) - (p_y - a_y)(b_x - a_x)$
  (ruudun $y$ alas). Vastapäiväisen kolmion sisällä kaikki $E \ge 0$.
- **Barysentriset:** $\lambda_0 = E_{bc}(p) / E_{ab}(c)$ jne.,
  $\sum \lambda_i = 1$.
- **Vasen-ylä-sääntö:** $E = 0$ hyväksytään vain ylä- ja vasemmalla
  reunalla. Vastapäiväisessä kolmiossa (ruutu, $y$ alas): yläreuna
  $\Delta y = 0, \Delta x < 0$; vasen reuna $\Delta y > 0$.
- **Kiinteä pilkku:** kärjet $\times 256$ kokonaisluvuiksi ennen testiä.

# Matriisit

- **Mallimatriisi:** $M = T R S$ (oikealta vasemmalle: skaalaus,
  kierto, siirto).
- **Näkymä:** kameran akselit riveinä, siirto $-a \cdot \text{silmä}$.
- **Perspektiivi:** $f = 1/\tan(\theta/2)$; rivit
  $(f/a, 0, 0, 0)$, $(0, f, 0, 0)$,
  $(0, 0, \frac{k + l}{l - k}, \frac{2kl}{l - k})$, $(0, 0, -1, 0)$;
  $a$ = kuvasuhde, $l$ = lähi-, $k$ = kaukotaso.
- **Normaalit:** $(M^{-1})^{\mathsf T}$ eli kofaktorimatriisi ja
  normalisointi.

# Perspektiivi ja syvyys

- **Korjattu interpolointi:**
  $v = \sum \lambda_i v_i / w_i \;/\; \sum \lambda_i / w_i$.
- **Syvyys** $d = (z/w + 1)/2 = A - B/e$, $B = kl/(k - l)$:
  lineaarinen $1/w$:n suhteen, ei korjata.
- **Syvyyden porras** etäisyydellä $e$: $e^2 / (B \cdot 2^{\text{bitit}})$.
- **Z-taistelu:** lähitaso kauas, käänteinen syvyys (float, kaukana 0),
  syvyyssiirtymä.

# Valaistus

| Malli | Kaava | Huomio |
|-------|-------|--------|
| Lambert | $k_d \max(0, n \cdot l)$ | mattapinta |
| Phong | $k_s \max(0, r \cdot v)^s$ | $r = 2 (n \cdot l) n - l$ |
| Blinn–Phong | $k_s \max(0, n \cdot h)^s$ | $h = (l + v)/\lvert l + v \rvert$, noin $4s$ |
| ympäristö | vakio $k_a$ | epäsuoran valon paikkaus |

- **Tasainen:** kolmion normaali. **Gouraud:** valo kärjissä.
  **Pikseleittäin:** normaali interpoloidaan ja normalisoidaan.

# Tekstuurit

- **Tekselin keskipiste:** $(i + 0{,}5) / L$.
- **Bilineaarinen:** $x = uL - 0{,}5$, neljä tekseliä, painot
  murto-osista.
- **Mipmap-taso:** $\log_2 \rho$, $\rho$ = pikselin askel
  tekseleinä derivaatoista. Trilineaarinen: kaksi tasoa ja niiden
  välillä lineaarisesti.
- **Anisotrooppinen:** useita näytteitä viistoille pinnoille.
- **Ketjun muisti:** $+1/3$.

# Reunanpehmennys

| Menetelmä | Peitto | Varjostus |
|-----------|--------|-----------|
| ei | 1 näyte | 1 / pikseli |
| SSAA $n$ | $n$ näytettä | $n$ / pikseli |
| MSAA $n$ | $n$ näytettä | 1 / pikseli ja kolmio |
| FXAA, SMAA | jälkikäsittely | 1 / pikseli |
| TAA | näytteet ajassa | 1 / pikseli |

- **Kierretty kuvio:** 4 näytettä, 5 tasoa vaaka- ja pystyreunoille.

# Virheiden etsintä

- **Liian tumma, kova valo:** sRGB-koodaus puuttuu.
- **Saumat tai tuplapikselit:** vasen-ylä-sääntö tai kiinteä pilkku.
- **Tekstuuri taittuu lävistäjällä:** perspektiivikorjaus puuttuu.
- **Kolmio katoaa tai peilautuu lähellä:** lähitason leikkaus.
- **Välkyntä kaukana:** mipmapit puuttuvat tai z-taistelu.
- **Kappale puuttuu kokonaan:** kiertosuunta ja karsinta.
- **Valaistus väärä kierretyssä mallissa:** normaali väärässä
  koordinaatistossa tai normalisoimatta.
