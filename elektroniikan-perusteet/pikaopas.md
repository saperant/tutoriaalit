---
title: Elektroniikan perusteet ja SPICE
subtitle: Pikaopas · kaavat, ngspice ja Python
---

# Kaavat

| Asia | Kaava |
|------|-------|
| Ohmin laki | $U = R I$ |
| teho | $P = U I = I^2 R = U^2 / R$ |
| sarjaan / rinnan | $R_1 + R_2$ / $R_1 R_2 / (R_1 + R_2)$ |
| jännitteenjako | $U_\text{ulos} = U R_2 / (R_1 + R_2)$ |
| Thevenin | $U = U_\text{th} - R_\text{th} I$ |
| kondensaattori | $i = C\,du/dt$, $E = C U^2 / 2$ |
| kela | $u = L\,di/dt$, $E = L I^2 / 2$ |
| RC-lataus | $u = U (1 - e^{-t/RC})$; 63 % yhdessä $\tau$ |
| nousuaika 30...70 % | $RC \ln(0{,}7/0{,}3) = 0{,}85\,RC$ |
| impedanssit | $R$, $1/(j\omega C)$, $j\omega L$ |
| RC-rajataajuus | $f_c = 1 / (2\pi R C)$, −3 dB, −45° |
| resonanssi | $f_0 = 1/(2\pi\sqrt{LC})$, $Q = \sqrt{L/C}/R$ |
| tehollisarvo | sini $\hat{U}/\sqrt2$, kolmio $\hat{U}/\sqrt3$ |
| Shockley | $I = I_S (e^{U/(n U_T)} - 1)$, $U_T = 25{,}9$ mV |
| LEDin vastus | $R = (U - U_F) / I$ |
| tasasuuntaajan rippeli | $\Delta U \approx I / (2 f C)$ (yläraja) |
| MOSFET, lineaarinen | $R_{DS} \approx 1 / (K (U_{GS} - U_T))$ |

# ngspice

| Tehtävä | Netlist tai komento |
|---------|---------------------|
| eräajo | `ngspice -b piiri.cir` |
| komponentit | `R1 a b 4.7k`, `C1 a 0 100n IC=0`, `L1 a b 1m` |
| lähteet | `V1 a 0 DC 5 AC 1`, `PULSE(0 5 0 1n 1n 1m 2m)`, `SIN(0 1 1k)` |
| puolijohteet | `D1 a k malli`, `Q1 c b e malli`, `M1 d g s s malli` |
| mallit | `.include diodit.lib`, `.model D1 D(IS=2.5n N=1.75)` |
| parametrit | `.param R=1k`, käyttö `{R}`, `{R*2}` |
| aliohjelma | `.subckt nimi a b params: R=1k` ... `.ends`, `X1 ...` |
| analyysit | `op`, `dc V1 0 5 0.1`, `ac dec 50 10 1Meg`, `tran 1u 5m uic` |
| suureet | `v(x)`, `i(V1)`, `@r1[p]`, `vdb(x)`, `vp(x)` |
| mittaus | `meas tran t WHEN v(x)=2.5 RISE=1`, `FIND ... AT=` |
| tulostus | `print v(x)`, `wrdata tiedosto.dat v(x) v(y)` |
| silmukka | `foreach a 1 2 3` `alterparam P = $a` `reset` ... `end` |
| etuliitteet | `f p n u m k Meg G` (`M` = milli!) |

```{.python tiedosto="esimerkit/spice.py" osa="vertaa"}
```

# Nyrkkisäännöt

| Asia | Sääntö |
|------|--------|
| vastuksen teho | kesto vähintään 2 x häviö |
| jakajan kuormitus | jakajan virta vähintään 10 x kuorma |
| BJT-kytkin | pakotettu vahvistus 10...20 |
| MOSFET-kytkin | $R_{DS(on)}$ käytetyllä $U_{GS}$:llä |
| induktiivinen kuorma | vapaakäyntidiodi rinnalle |
| konvergenssi | DC-reitti maahan, sarjaresistanssi lähteille |
