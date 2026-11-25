# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Kirjaa jokaisen signaalin muoto.** Qm.n ei näy koodissa, joten se
   dokumentoidaan lohkokaavioon ja nimiin.
2. **Valitse alue ennen tarkkuutta.** Ylivuoto on pahempi kuin
   kvantisointikohina.
3. **Laske bittikasvu.** Summa $n+1$, tulo $2n$, kertymä
   $+\lceil \log_2 K \rceil$ vartijabittiä tai kertoimien $\ell_1$-normin
   mukaan.
4. **Pyöristä lähimpään, kerran, lopuksi.** Takaisinkytkennöissä
   parilliseen.
5. **Saturoi ulostulot ja takaisinkytkennät, kierrä välitulokset.**
6. **6 dB bittiä kohti, täydellä skaalalla.** Hiljainen signaali
   menettää bittejä.
7. **Tee virhebudjetti ennen RTL:ää** ja vahvista se bittitarkalla
   simuloinnilla.
8. **Kolme mallia: double, bittitarkka, RTL.** RTL vastaa bittitarkkaa
   mallia täsmälleen.
9. **Testaa ääriarvot ja käännä mallit sanitoijilla.**

## Mallit ja tekniikat

| Malli | Mihin | Luku |
|-------|-------|------|
| Q-formaatti ja muodon vaihto siirroilla | signaalien skaalaus | 2 |
| vartijabitit | kertymät, suodattimet | 3 |
| pyöristys lähimpään parilliseen | harhaton pyöristys | 4 |
| jako vakiolla käänteisluvun koodilla | skaalaus ilman jakajaa | 3 |
| Jacksonin sääntö | välitulosten kierto summissa | 5 |
| dither | särö kohinaksi matalilla bittimäärillä | 6 |
| kohinamalli $q^2/12$ | SQNR:n ennustaminen | 6 |
| bittitarkka malli ja tiiviste | RTL:n referenssi | 7 |
| CORDIC | trigonometria ilman kertojia | 7 |
| lohkoliukuluku | dynamiikka lähes ilmaiseksi | 8 |
| virhebudjetti | sanaleveyksien valinta | 9 |

## Valmiit kiinteän pilkun tyypit

Tässä tutoriaalissa muoto ja kavennukset kirjoitettiin käsin, jotta
jokainen bitti näkyy. Työkaluissa on valmiita tyyppejä, jotka pitävät
kirjaa pilkun paikasta ja tekevät kavennuksen sijoituksessa:

| Ympäristö | Tyyppi | Pyöristys ja ylivuoto |
|-----------|--------|-----------------------|
| SystemC | `sc_fixed<W, I, Q, O>` | tilat tyypin parametreina, oletus katkaisu ja kierto |
| VHDL-2008 | `sfixed`, `ufixed` (`fixed_pkg`) | funktion `resize` parametreina, oletus pyöristys ja saturaatio |
| HLS-työkalut | `ap_fixed`, `ac_fixed` | kuten `sc_fixed` |

Oletukset eroavat, joten ne luetaan dokumentaatiosta eikä päätellä
toisesta ympäristöstä. Tyypit eivät poista suunnittelutyötä: leveydet,
tilat ja kavennusten paikat valitaan samoin perustein kuin tässä.

## Jatkotaidot

- *Korkean tason mallinnus (SystemC/TLM)*: bittitarkat tietotyypit
  (`sc_fixed`) ja mallin liittäminen virtuaaliprototyyppiin.
- *DSP-algoritmien laitteistototeutus*: FIR-, IIR-, CIC- ja
  CORDIC-rakenteet RTL:nä tämän tutoriaalin bittitarkkoja malleja
  referenssinä käyttäen.
- *Korkean tason synteesi*: HLS-työkalujen kiinteän pilkun tyypit
  (`ap_fixed`, `ac_fixed`) ja niiden pyöristys- ja saturaatiotilat.
- *Digitaalinen signaalinkäsittely*: suodattimien suunnittelu, jota
  tässä käytettiin esimerkkinä.

## Lähteet

- Randy Yates: *Fixed-Point Arithmetic: An Introduction.* Digital Signal
  Labs, 2013. Lyhyt ja tarkka johdanto Q-merkintään ja aritmetiikan
  sääntöihin.
- Richard G. Lyons: *Understanding Digital Signal Processing*, 3. painos.
  Prentice Hall, 2010. Kvantisointikohina, lohkoliukuluku ja
  kiinteän pilkun suodattimet.
- Behrooz Parhami: *Computer Arithmetic: Algorithms and Hardware
  Designs*, 2. painos. Oxford University Press, 2010. Summaimien,
  kertojien ja liukulukuyksiköiden rakenne ja hinta.
- Leland B. Jackson: ”On the Interaction of Roundoff Noise and Dynamic
  Range in Digital Filters.” *Bell System Technical Journal* 49(2),
  1970. Kohinamalli ja kahden komplementin välitulosten kierto.
- Jack E. Volder: ”The CORDIC Trigonometric Computing Technique.” *IRE
  Transactions on Electronic Computers* EC-8(3), 1959.
- IEEE 754-2019: *Standard for Floating-Point Arithmetic.*
  Pyöristystavat ja vertailukohta kiinteälle pilkulle.
- Open Compute Project: *OCP Microscaling Formats (MX) Specification*
  1.0, 2023. Lohkoskaalatut koneoppimisen muodot.
- ISO/IEC 9899:2024 (C23). Kokonaislukujen korotukset, ylivuoto ja
  siirrot.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkikoodia saa käyttää
saman lisenssin ehdoin.
