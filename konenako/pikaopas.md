---
title: Konenäkö
subtitle: Pikaopas · OpenCV-reseptit, säännöt ja sudenkuopat
---

# Kuva ja värit

| Asia | Sääntö |
|------|--------|
| taulukko | `(korkeus, leveys[, kanavat])`, `uint8`; indeksi `[y, x]` |
| piste ja koko | OpenCV: `(x, y)` ja `(leveys, korkeus)` |
| kanavat | BGR; RGB-kirjastoihin `COLOR_BGR2RGB` |
| HSV | H 0–179 (puolikkaat asteet); punainen kahdella välillä |
| Lab | euklidinen etäisyys vastaa havaittua värieroa |
| aritmetiikka | `cv2.add` saturoi, NumPy kiertää; laske `float32` |
| kontrasti | venytys, `equalizeHist`, CLAHE, gamma `LUT`:lla |
| kynnystys | Otsu tasaiselle, `adaptiveThreshold` vaihtelevalle |

```{.python tiedosto="esimerkit/pikaopas.py" osa="kuva"}
```

# Suodatus ja reunat

| Asia | Sääntö |
|------|--------|
| `filter2D` | korrelaatio: konvoluutioon `cv2.flip(k, -1)` |
| reunat | oletus `BORDER_REFLECT_101` |
| Gauss | ydin $\approx 6\sigma + 1$; `(0, 0)` laskee koon |
| erottuva ydin | $k^2 \to 2k$ kertolaskua (`sepFilter2D`) |
| kohina | Gauss/bilateraali; impulssikohina: mediaani |
| gradientti | Sobel `CV_32F`; suunta `cartToPolar` |
| Canny | tasoita ensin; kynnykset suhteessa 1:2–1:3 |
| morfologia | avaus poistaa roskat, sulkeminen täyttää reiät |
| muoto | pyöreys $4\pi A/P^2$, `approxPolyDP`, Hu-momentit |

```{.python tiedosto="esimerkit/pikaopas.py" osa="suodatus"}
```

# Piirteet ja geometria

| Asia | Sääntö |
|------|--------|
| kulmat | `goodFeaturesToTrack` + `cornerSubPix` |
| ORB / SIFT | Hamming / L2; ratio-testi 0,75 |
| väärät parit | `findHomography(..., cv2.RANSAC, 3.0)` |
| muunnokset | siirto 2, jäykkä 3, affiini 6, homografia 8 vapausastetta |
| interpolointi | maskit NEAREST, pienennys AREA, muuten LINEAR/CUBIC |
| ketjutus | kerro matriisit, näytteistä kerran |

```{.python tiedosto="esimerkit/pikaopas.py" osa="piirteet"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="geometria"}
```

# Kamera ja stereo

| Asia | Kaava tai funktio |
|------|-------------------|
| projektio | $s\,(u, v, 1)^{\mathsf T} = K [R \mid t] (X, Y, Z, 1)^{\mathsf T}$ |
| vääristymä | $x_d = x(1 + k_1 r^2 + k_2 r^4 + \ldots)$ |
| kalibrointi | `findChessboardCorners`, `cornerSubPix`, `calibrateCamera` |
| asento | `solvePnP(kappale, kuva, K, d)` |
| epipolaari | $x_2^{\mathsf T} F x_1 = 0$, $E = [t]_\times R$ |
| liike | `findEssentialMat` + `recoverPose`; siirto vain suuntana |
| syvyys | $Z = fB/d$; SGBM antaa $16d$ |
| virtaus | `calcOpticalFlowPyrLK`; mediaani |
| seuranta | `KalmanFilter`: `predict`, `correct` |

# Sudenkuopat

| Virhe | Korjaus |
|-------|---------|
| RGB-kuva OpenCV:lle | `cvtColor(..., COLOR_RGB2BGR)` rajalla |
| `uint8`-vähennys kiertää | `cv2.subtract` tai `float32` |
| Sobel `CV_8U` | `CV_32F`: negatiiviset derivaatat katoavat |
| `resize` NEAREST pienennykseen | `INTER_AREA`: muuten aliasointi |
| toistuva `warpAffine` | yhdistä matriisit |
| kalibrointi vain kuvan keskeltä | lauta myös kulmiin ja kallistettuna |
| piirteiden määrä testissä | väljä raja: versio ja käskykanta vaihtelevat |
| pikselisilmukka Pythonissa | NumPy tai OpenCV-funktio |
| esikäsittely ei vastaa opetusta | koko, värijärjestys, normitus kuten mallissa |
