---
title: Analogiaelektroniikka
subtitle: Pikaopas · kaavat, kytkennät ja ngspice
---

# Transistorivahvistin

| Suure | Kaava |
|-------|-------|
| kannan Thevenin | $U_{th} = U_{cc} R_2/(R_1+R_2)$ |
| Thevenin-resistanssi | $R_{th} = R_1 \parallel R_2$ |
| kantavirta | $I_B = (U_{th} - U_{BE}) / (R_{th} + (\beta+1) R_e)$ |
| transkonduktanssi | $g_m = I_C / U_T$, $U_T = 25{,}9$ mV |
| piensignaali | $r_\pi = \beta/g_m$, $r_o = V_A / I_C$ |
| CE-vahvistus | $-g_m (R_c \parallel R_L \parallel r_o)$ |
| degeneroitu | $\approx -R_c / R_e'$ |
| seuraajan lähtö | $r_e + R_s/(\beta+1)$, $r_e = 1/g_m$ |
| differentiaalipari | $A_d = g_m R_c/2$, $A_{cm} \approx R_c/(2R_{ee})$ |

# Operaatiovahvistin

| Kytkentä | Vahvistus |
|----------|-----------|
| invertoiva | $-R_2/R_1$ |
| ei-invertoiva | $1 + R_2/R_1$ |
| integraattori | $-1/(sRC)$ |
| instrumentointi | $1 + 2R/R_g$ |
| suljettu silmukka | $A/(1 + A\beta)$ |
| kaistanleveys | $GBW / (1 + R_2/R_1)$ |
| nousunopeus | $2\pi f \hat{U} < SR$ |

# Suodattimet

| Asia | Kaava |
|------|-------|
| 2. kertaluku | $H = K/(s^2/\omega_0^2 + s/(Q\omega_0) + 1)$ |
| Sallen-Key, R1 = R2 | $Q = \sqrt{C_1/C_2}/2$, $\omega_0 = 1/(R\sqrt{C_1 C_2})$ |
| MFB, kaikki R | $Q = \sqrt{C_1/C_2}/3$, vahvistus $-R_2/R_1$ |
| Butterworth | $Q = 0{,}707$, ylitys 4,3 % |
| Bessel | $Q = 0{,}577$, ylitys 0,4 % |
| askelvasteen ylitys | $e^{-\pi\zeta/\sqrt{1-\zeta^2}}$, $\zeta = 1/(2Q)$ |

# Stabiilisuus ja muuntimet

| Asia | Kaava tai sääntö |
|------|------------------|
| silmukkavahvistus | $T = A\beta$; vaihevara 45...60° |
| kuorman napa | $f = 1/(2\pi R_{ulos} C_L)$ |
| vertailijan kynnys | $(U_{ref} R_2 + U_{ulos} R_1)/(R_1 + R_2)$ |
| PWM ja RC | rippeli $U D(1-D)T/\tau$ |
| LSB | $U_{ref} / 2^N$ |
| SNR | $6{,}02 N + 1{,}76$ dB |
| ENOB | $(\mathrm{SINAD} - 1{,}76)/6{,}02$ |
| näytteenotto | $t = RC \ln 2^{N+1}$ |
| sigma-delta | +9 dB / OSR:n kaksinkertaistus (1. kl.) |

# Kohina ja siirtolinjat

| Asia | Kaava |
|------|-------|
| terminen kohina | $\sqrt{4kTR}$, 1 kΩ: 4 nV/√Hz |
| kT/C | $\sqrt{kT/C}$, 1 pF: 64 µV |
| summautuminen | $\sqrt{\sum e_k^2}$ |
| heijastuskerroin | $\Gamma = (Z - Z_0)/(Z + Z_0)$ |
| siirtolinja | viive > nousuaika / 6 |

# Jännitteensäätimet

| Asia | Kaava tai sääntö |
|------|------------------|
| lähtö | $U_{ref}/\beta$, $\beta = R_2/(R_1 + R_2)$; kohina vahvistuu samoin |
| linjaregulaatio, PSRR | $\approx 1/(A\beta)$; heikkenee taajuuden kasvaessa |
| pudotusjännite | seuraaja noin 2 V; LDO $R_{DS(on)} I$ |
| häviö | $(U_{in} - U_{ulos}) I$, $\eta \le U_{ulos}/U_{in}$ |
| ESR:n nolla | $f = 1/(2\pi\,ESR\,C)$; askel $ESR \cdot \Delta I$ |
| buck, jatkuva | $U = D U_{in}$, $\Delta I_L = (U_{in} - U) D T / L$ |
| buck, rippeli ja raja | $\Delta U = \Delta I_L T/(8C)$; katkeava, kun $I < \Delta I_L/2$ |

# ngspice

| Tehtävä | Netlist tai komento |
|---------|---------------------|
| makromalli | `X1 inp inn out vcc vee OPAMP AOL=1e5 GBW=1Meg` |
| käyttäytymislähde | `B1 0 n I = 1m*tanh(v(a)-v(b))` |
| silmukan katkaisu | `Lkatko out inn 1k`, `Ckatko t inn 1k` |
| katkaisu sarjalähteellä | `Vt fb fbi AC 1`, $T = -u_{fb}/u_{fbi}$ |
| kohina | `noise v(out) Vin dec 50 1 10G`, `setplot noise2` |
| siirtolinja | `T1 a 0 b 0 Z0=50 TD=5n` |
| kytkin | `S1 a b ohj 0 KYTKIN`, `.model KYTKIN SW(RON=100)` |
| parametrisilmukka | `foreach r 1k 9k` `alterparam R2 = $r` `reset` |
